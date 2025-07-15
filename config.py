# config.py

# Define each tool with its GPIO pins
TOOLS = [
    {
        "name": "Jointer",
        "relay_pin": 17,
        "on_button_pin": 5,
        "off_button_pin": 6
    },
    {
        "name": "Table Saw",
        "relay_pin": 27,
        "on_button_pin": 13,
        "off_button_pin": 19
    },
    {
        "name": "Planer",
        "relay_pin": 22,
        "on_button_pin": 20,
        "off_button_pin": 21
    }
]

# GPIO pin controlling the main dust collector
DUST_COLLECTOR_RELAY_PIN = 26
