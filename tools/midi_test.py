#!/usr/bin/env python3
"""
Push 3 MIDI Control Test
Tool for testing MIDI control features like LED control and device communication.
"""

import sys
import time
import argparse

try:
    import mido
except ImportError:
    print("Error: mido module not found. Install with: pip install mido python-rtmidi")
    sys.exit(1)

# Push 3 MIDI constants
MANUFACTURER_ID = [0x00, 0x21, 0x1D]
DEVICE_ID = [0x01, 0x01]

# LED Colors (based on Push 2 palette)
class LEDColors:
    OFF = 0
    RED = 5
    ORANGE = 9
    YELLOW = 13
    GREEN = 17
    CYAN = 33
    BLUE = 37
    PURPLE = 41
    PINK = 45
    WHITE = 119
    GRAY_LIGHT = 118
    GRAY_DARK = 117

# Common button CCs for LED testing
TEST_BUTTONS = {
    'play': 85,
    'record': 86,
    'stop': 29,
    'solo': 61,
    'mute': 60,
    'shift': 49,
    'select': 48,
}


class Push3MIDIController:
    """MIDI controller for Push 3 device"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.input_port = None
        self.output_port = None
        
    def find_push3_ports(self):
        """Find Push 3 MIDI ports, preferring User port over Live port"""
        input_names = mido.get_input_names()
        output_names = mido.get_output_names()

        # Prefer User port
        user_input = next((name for name in input_names if "User" in name), None)
        user_output = next((name for name in output_names if "User" in name), None)

        # Fallback to any Push 3 port if User port not found
        push3_input = user_input or next((name for name in input_names if "Ableton Push 3" in name), None)
        push3_output = user_output or next((name for name in output_names if "Ableton Push 3" in name), None)

        return push3_input, push3_output
    
    def connect(self):
        """Connect to Push 3 MIDI ports"""
        input_name, output_name = self.find_push3_ports()
        
        if not output_name:
            raise RuntimeError("Push 3 MIDI output not found. Make sure Push 3 is connected.")
        
        try:
            self.output_port = mido.open_output(output_name)
            
            # Input port is optional for control testing
            if input_name:
                self.input_port = mido.open_input(input_name)
            
            if self.debug:
                print(f"Connected to MIDI output: {output_name}")
                if input_name:
                    print(f"Connected to MIDI input: {input_name}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MIDI ports: {e}")
    
    def send_sysex(self, command, data=None):
        """Send SysEx command to Push 3"""
        if not self.output_port:
            raise RuntimeError("No output port available")
        
        if data is None:
            data = []
        
        sysex_data = MANUFACTURER_ID + DEVICE_ID + [command] + data
        msg = mido.Message('sysex', data=sysex_data)
        
        if self.debug:
            hex_data = ' '.join(f'{b:02X}' for b in sysex_data)
            print(f"Sending SysEx: F0 {hex_data} F7")
        
        self.output_port.send(msg)
    
    def set_button_led(self, button_cc, color, brightness=127):
        """Set button LED color (User Port: standard MIDI CC)"""
        msg = mido.Message('control_change', control=button_cc, value=color, channel=0)
        self.output_port.send(msg)
        if self.debug:
            print(f"Set button {button_cc} LED to color {color}")
    
    def set_pad_led(self, pad_note, color, brightness=127):
        """Set pad LED color (User Port: standard MIDI note_on)"""
        msg = mido.Message('note_on', note=pad_note, velocity=color, channel=0)
        self.output_port.send(msg)
        if self.debug:
            print(f"Set pad {pad_note} LED to color {color}")
    
    def device_handshake(self):
        """Perform device handshake: standard inquiry and set user mode."""
        print("Performing device handshake...")

        # Standard MIDI device inquiry (universal non-realtime)
        inquiry = [0x7E, 0x7F, 0x06, 0x01]
        msg = mido.Message('sysex', data=inquiry)
        self.output_port.send(msg)
        print("Sent standard device inquiry.")
        time.sleep(0.5)

        # Set User Mode (manufacturer-specific)
        user_mode = MANUFACTURER_ID + DEVICE_ID + [0x0A, 0x01]
        msg = mido.Message('sysex', data=user_mode)
        self.output_port.send(msg)
        print("Sent set user mode SysEx.")
        time.sleep(0.5)

        print("Handshake complete.")
    
    def test_button_leds(self):
        """Test all button LEDs (CC 0-127) with MIDI CC messages"""
        print("Testing all button LEDs (CC 0-127)...")

        colors = [LEDColors.RED, LEDColors.GREEN, LEDColors.BLUE, LEDColors.YELLOW, LEDColors.WHITE, LEDColors.PURPLE, LEDColors.ORANGE]
        color_names = ["RED", "GREEN", "BLUE", "YELLOW", "WHITE", "PURPLE", "ORANGE"]

        for cc in range(128):
            color = colors[cc % len(colors)]
            color_name = color_names[cc % len(color_names)]
            print(f"Setting button CC {cc} to {color_name} ({color})")
            self.set_button_led(cc, color)
            time.sleep(0.08)

        time.sleep(1)

        print("Turning off all button LEDs...")
        for cc in range(128):
            self.set_button_led(cc, LEDColors.OFF)
            time.sleep(0.01)

        print("\nButton LED test complete")
    
    def test_pad_leds(self):
        """Test pad LED functionality with a simple pattern"""
        print("Testing pad LEDs...")
        
        # Test first row of pads (notes 36-43)
        test_pads = list(range(36, 44))
        colors = [LEDColors.RED, LEDColors.ORANGE, LEDColors.YELLOW, LEDColors.GREEN, 
                 LEDColors.CYAN, LEDColors.BLUE, LEDColors.PURPLE, LEDColors.PINK]
        
        # Light up pads in sequence
        print("Lighting up bottom row...")
        for pad, color in zip(test_pads, colors):
            self.set_pad_led(pad, color)
            time.sleep(0.2)
        
        time.sleep(1)
        
        # Turn off pads
        print("Turning off pads...")
        for pad in test_pads:
            self.set_pad_led(pad, LEDColors.OFF)
            time.sleep(0.1)
        
        print("Pad LED test complete")
    
    def led_chase_demo(self):
        """LED chase demo across various controls"""
        print("Running LED chase demo...")
        
        # Button chase
        print("Button chase...")
        for button_cc in TEST_BUTTONS.values():
            self.set_button_led(button_cc, LEDColors.GREEN)
            time.sleep(0.1)
            self.set_button_led(button_cc, LEDColors.OFF)
        
        # Pad chase
        print("Pad chase...")
        for pad_note in range(36, 100):  # All pads
            self.set_pad_led(pad_note, LEDColors.BLUE)
            time.sleep(0.02)
            self.set_pad_led(pad_note, LEDColors.OFF)
        
        print("Chase demo complete")
    
    def all_leds_off(self):
        """Turn off all LEDs"""
        print("Turning off all LEDs...")
        
        # Turn off all button LEDs
        for button_cc in range(128):
            self.set_button_led(button_cc, LEDColors.OFF)
        
        # Turn off all pad LEDs
        for pad_note in range(128):
            self.set_pad_led(pad_note, LEDColors.OFF)
        
        print("All LEDs turned off")
    
    def disconnect(self):
        """Disconnect from MIDI ports"""
        if self.input_port:
            self.input_port.close()
        if self.output_port:
            self.output_port.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Test MIDI control features of Push 3',
        epilog='This tool tests LED control and device communication.'
    )
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--inquiry', '-i', action='store_true',
                       help='Send device inquiry only')
    parser.add_argument('--buttons', '-b', action='store_true',
                       help='Test button LEDs only')
    parser.add_argument('--pads', '-p', action='store_true',
                       help='Test pad LEDs only')
    parser.add_argument('--chase', '-c', action='store_true',
                       help='Run LED chase demo')
    parser.add_argument('--all-off', action='store_true',
                       help='Turn off all LEDs')
    
    args = parser.parse_args()
    
    try:
        print("Push 3 MIDI Control Test")
        print("=" * 30)
        
        controller = Push3MIDIController(debug=args.debug)
        controller.connect()

        # Always perform handshake before any test
        controller.device_handshake()

        if args.inquiry:
            print("(No device inquiry implemented; handshake already performed.)")
        elif args.buttons:
            controller.test_button_leds()
        elif args.pads:
            controller.test_pad_leds()
        elif args.chase:
            controller.led_chase_demo()
        elif args.all_off:
            controller.all_leds_off()
        else:
            # Default: run all tests
            print("Running complete LED test suite...\n")

            controller.test_button_leds()
            time.sleep(1)

            controller.test_pad_leds()
            time.sleep(1)

            controller.led_chase_demo()
            time.sleep(1)

            controller.all_leds_off()

            print("\n✓ All tests completed successfully!")

        controller.disconnect()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
