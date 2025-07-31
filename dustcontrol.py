import time
import threading
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
import yaml
from paho.mqtt.client import CallbackAPIVersion

# Load the configuration file.
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

# Setup global variables.
TOOLS = config["tools"]
DUST_COLLECTOR_PIN = config["collector_pin"]

# State tracking
current_tool = None

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup the dust collection relay pins.
GPIO.setup(DUST_COLLECTOR_PIN, GPIO.OUT)
GPIO.output(DUST_COLLECTOR_PIN, GPIO.LOW)

# Setup the tool relay pins.
for tool in TOOLS:
    GPIO.setup(tool["relay_pin"], GPIO.OUT)
    GPIO.output(tool["relay_pin"], GPIO.LOW)

# Activate a tool.
def activate_tool(index):
    global current_tool
    print(f"[GPIO/MQTT] Activating {TOOLS[index]['name']}")
    for i, tool in enumerate(TOOLS):
        GPIO.output(tool["relay_pin"], GPIO.HIGH if i == index else GPIO.LOW)
    GPIO.output(DUST_COLLECTOR_PIN, GPIO.HIGH)
    current_tool = index

# System Shutdown.
def deactivate_system():
    global current_tool
    print("[GPIO/MQTT] Deactivating all tools")
    # Disable all tools.
    for tool in TOOLS:
        GPIO.output(tool["relay_pin"], GPIO.LOW)
    # Disable the dust collection.
    GPIO.output(DUST_COLLECTOR_PIN, GPIO.LOW)
    current_tool = None

# MQTT On Connect.
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code", rc)
    client.subscribe("dust/+/+")

# MQTT Message Callback.
def on_message(client, userdata, msg):
    try:
        # Separate the parts of the channel.
        parts = msg.topic.split("/")
        if len(parts) != 3:
            return
            print("Incorrect MQTT channel format. Use dust/[toolid]/[action].")
        _, tool_id, action = parts
        # Validate the action.
        if action not in ["on", "off"]:
            print("Invalid action supplied. Use dust/[toolid]/on or dust/[toolid]/off.")
            return
        # Find the matching tool.
        for i, tool in enumerate(TOOLS):
            print(i)
            if tool["id"] == tool_id:
                if action == "on":
                    print(i)
                    activate_tool(i)
                    return
                elif action == "off":
                    deactivate_system()
                    return
        print("No tool with 'id' of '" + tool_id + "' found.")
    except Exception as e:
        print("MQTT message error:", e)

# Setup the MQTT client.
mqtt_client = mqtt.Client(
    protocol=mqtt.MQTTv311,
    callback_api_version=CallbackAPIVersion.VERSION2
)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

# Main Program.
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    deactivate_system()
    GPIO.cleanup()
    mqtt_client.loop_stop()
