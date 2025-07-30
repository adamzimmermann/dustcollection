import time
import threading
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
import yaml

# Load YAML file
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

TOOLS = config["tools"]
DUST_COLLECTOR_PIN = config["collector_pin"]

# State tracking
current_tool = None

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(DUST_COLLECTOR_PIN, GPIO.OUT)
GPIO.output(DUST_COLLECTOR_PIN, GPIO.LOW)

for tool in TOOLS:
    GPIO.setup(tool["relay_pin"], GPIO.OUT)
    GPIO.output(tool["relay_pin"], GPIO.LOW)
    GPIO.setup(tool["on_button_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(tool["off_button_pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Tool control functions
def activate_tool(index):
    global current_tool
    print(f"[GPIO/MQTT] Activating {TOOLS[index]['name']}")
    for i, tool in enumerate(TOOLS):
        GPIO.output(tool["relay_pin"], GPIO.HIGH if i == index else GPIO.LOW)
    GPIO.output(DUST_COLLECTOR_PIN, GPIO.HIGH)
    current_tool = index

def deactivate_system():
    global current_tool
    print("[GPIO/MQTT] Deactivating all tools")
    for tool in TOOLS:
        GPIO.output(tool["relay_pin"], GPIO.LOW)
    GPIO.output(DUST_COLLECTOR_PIN, GPIO.LOW)
    current_tool = None

# Button listeners
def monitor_buttons():
    while True:
        for i, tool in enumerate(TOOLS):
            if GPIO.input(tool["on_button_pin"]) == GPIO.LOW:
                activate_tool(i)
                time.sleep(0.3)
            elif GPIO.input(tool["off_button_pin"]) == GPIO.LOW:
                deactivate_system()
                time.sleep(0.3)
        time.sleep(0.1)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code", rc)
    client.subscribe("dust/+/+")

def on_message(client, userdata, msg):
    try:
        parts = msg.topic.split("/")
        if len(parts) != 3:
            return
        _, tool_id, action = parts
        for i, tool in enumerate(TOOLS):
            if tool["id"] == tool_id:
                if action == "on":
                    activate_tool(i)
                elif action == "off":
                    deactivate_system()
    except Exception as e:
        print("No tool with id of '" + tool_id + "'")
        print("MQTT message error:", e)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

button_thread = threading.Thread(target=monitor_buttons, daemon=True)
button_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    deactivate_system()
    GPIO.cleanup()
    mqtt_client.loop_stop()
