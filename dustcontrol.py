# dustcontrol.py

from gpiozero import Button, OutputDevice
from signal import pause
from config import TOOLS, DUST_COLLECTOR_RELAY_PIN

class ToolController:
    def __init__(self, name, relay_pin, on_button_pin, off_button_pin):
        self.name = name
        self.gate = OutputDevice(relay_pin, active_high=False, initial_value=False)
        self.on_button = Button(on_button_pin)
        self.off_button = Button(off_button_pin)
        self.active = False

        self.on_button.when_pressed = self.turn_on
        self.off_button.when_pressed = self.turn_off

    def turn_on(self):
        print(f"[INFO] {self.name} - ON")
        self.gate.on()
        self.active = True
        DustCollectorController.update_collector_state()

    def turn_off(self):
        print(f"[INFO] {self.name} - OFF")
        self.gate.off()
        self.active = False
        DustCollectorController.update_collector_state()

class DustCollectorController:
    collector = OutputDevice(DUST_COLLECTOR_RELAY_PIN, active_high=False, initial_value=False)
    tools = []

    @classmethod
    def register_tool(cls, tool):
        cls.tools.append(tool)

    @classmethod
    def update_collector_state(cls):
        any_active = any(tool.active for tool in cls.tools)
        if any_active:
            print("[INFO] Dust collector ON")
            cls.collector.on()
        else:
            print("[INFO] No gates active, dust collector OFF")
            cls.collector.off()

def main():
    print("[INIT] Dust control system starting up...")

    for tool_cfg in TOOLS:
        tool = ToolController(
            tool_cfg["name"],
            tool_cfg["relay_pin"],
            tool_cfg["on_button_pin"],
            tool_cfg["off_button_pin"]
        )
        DustCollectorController.register_tool(tool)

    print("[READY] System is running. Awaiting button presses.")
    pause()

if __name__ == "__main__":
    main()
