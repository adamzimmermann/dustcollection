import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# Relay GPIO Pins (BCM numbering)
TOOLS = {
    "tool1": {"gate_pin": 17},
    "tool2": {"gate_pin": 27},
    "tool3": {"gate_pin": 22},
}
DUST_COLLECTOR_PIN = 23

# State tracking
current_tool = None

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(DUST_COLLECTOR_PIN, GPIO.OUT)
GPIO.output(DUST_COLLECTOR_PIN, GPIO.LOW)

for tool in TOOLS.values():
    GPIO.setup(tool["gate_pin"], GPIO.OUT)
    GPIO.output(tool["gate_pin"], GPIO.LOW)

# Tool control functions
def activate_tool(tool_name):
    global current_tool
    print(f"Activating {tool_name}")
    if tool_name not in TOOLS:
        print("Unknown tool")
        return

    for name, tool in TOOLS.items():
        GPIO.output(tool["gate_pin"], GPIO.HIGH if name == tool_name else GPIO.LOW)

    GPIO.output(DUST_COLLECTOR_PIN, GPIO.HIGH)
    current_tool = tool_name

def deactivate_system():
    global current_tool
    print("Turning off dust collection")
    for tool in TOOLS.values():
        GPIO.output(tool["gate_pin"], GPIO.LOW)

    GPIO.output(DUST_COLLECTOR_PIN, GPIO.LOW)
    current_tool = None

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("dust/+/+")

def on_message(client, userdata, msg):
    print(f"MQTT message received: {msg.topic} {msg.payload.decode()}")
    topic_parts = msg.topic.split("/")
    if len(topic_parts) != 3:
        return

    _, tool, action = topic_parts
    if action == "on":
        activate_tool(tool)
    elif action == "off":
        deactivate_system()

# MQTT Setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

tr
