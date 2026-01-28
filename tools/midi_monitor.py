#!/usr/bin/env python3
"""
Push 3 MIDI Monitor
Tool for monitoring and analyzing MIDI input/output from Push 3 hardware.
"""

import sys
import time
import argparse
from datetime import datetime

try:
    import mido
except ImportError:
    print("Error: mido module not found. Install with: pip install mido python-rtmidi")
    sys.exit(1)

# Push 3 MIDI constants
MANUFACTURER_ID = [0x00, 0x21, 0x1D]
DEVICE_ID = [0x01, 0x01]

CC_BUTTON_NAMES = {
    3: "Tap Tempo",
    9: "Metronome",
    10: "Swing/Tempo", 
    11: "Jogwheel",
    15: "Swing/Tempo",
    94: "Jogwheel",
    28: "Master Track",
    29: "Stop",
    30: "Setup",
    31: "Layout",
    32: "Add",
    33: "Swap",
    34: "Session",
    35: "Convert",
    36: "1/4 Repeat",
    37: "1/4t Repeat", 
    38: "1/8 Repeat",
    39: "1/8t Repeat",
    40: "1/16 Repeat",
    41: "1/16t Repeat",
    42: "1/32 Repeat",
    43: "1/32t Repeat",
    44: "D-Pad Left",
    45: "D-Pad Right",
    46: "D-Pad Up",
    47: "D-Pad Down",
    48: "Select",
    49: "Shift",
    50: "Note",
    51: "Session",
    54: "Octave Down",
    55: "Octave Up",
    56: "Repeat",
    57: "Accent",
    58: "Scale",
    59: "User Mode",
    60: "Mute",
    61: "Solo",
    62: "Page Left",
    63: "Page Right",
    65: "Capture",
    80: "Sets",
    81: "Learn",
    82: "Save",
    83: "Lock",
    85: "Play",
    86: "Record",
    88: "Duplicate",
    89: "Automate",
    90: "Fixed Length",
    91: "D-Pad Center",
    92: "New",
    110: "Device",
    111: "Volume",
    112: "Mix",
    113: "Clip",
    116: "Quantize",
    117: "Double Loop",
    118: "Delete",
    119: "Undo",
}

# Encoder CC mappings
ENCODER_TOUCH_CCS = list(range(0, 8))  # Encoders 1-8 touch
ENCODER_TURN_CCS = list(range(71, 79))  # Encoders 1-8 rotation
SPECIAL_TOUCH_CCS = {8: "Volume Touch", 10: "Swing/Tempo Touch", 11: "Jog Wheel Touch", 12: "Touch Strip"}
SPECIAL_TURN_CCS = {14: "Swing/Tempo Turn", 70: "Jog Wheel Scroll", 79: "Volume Turn"}

# Display button CCs
UPPER_DISPLAY_CCS = list(range(102, 110))  # Upper display buttons 1-8
LOWER_DISPLAY_CCS = list(range(20, 28))    # Lower display buttons 1-8


class Push3MIDIMonitor:
    """MIDI monitor for Push 3 device"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.input_port = None
        self.output_port = None
        self.running = False
        self.message_count = 0
        
    def find_push3_ports(self):
        """Find Push 3 MIDI input and output ports"""
        input_names = mido.get_input_names()
        output_names = mido.get_output_names()
        
        push3_input = None
        push3_output = None
        
        # Look for Push 3 ports
        for name in input_names:
            if "Push 3" in name or "Ableton Push 3" in name:
                push3_input = name
                break
        
        for name in output_names:
            if "Push 3" in name or "Ableton Push 3" in name:
                push3_output = name
                break
        
        if self.debug:
            print("Available MIDI inputs:")
            for name in input_names:
                marker = " ← Push 3" if name == push3_input else ""
                print(f"  {name}{marker}")
            
            print("\nAvailable MIDI outputs:")
            for name in output_names:
                marker = " ← Push 3" if name == push3_output else ""
                print(f"  {name}{marker}")
        
        return push3_input, push3_output
    
    def connect(self):
        """Connect to Push 3 MIDI ports"""
        input_name, output_name = self.find_push3_ports()
        
        if not input_name:
            raise RuntimeError("Push 3 MIDI input not found. Make sure Push 3 is connected.")
        
        if not output_name:
            raise RuntimeError("Push 3 MIDI output not found. Make sure Push 3 is connected.")
        
        try:
            self.input_port = mido.open_input(input_name)
            self.output_port = mido.open_output(output_name)
            
            if self.debug:
                print(f"Connected to MIDI input: {input_name}")
                print(f"Connected to MIDI output: {output_name}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MIDI ports: {e}")
    
    def format_message(self, msg):
        """Format MIDI message for display"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if msg.type == 'control_change':
            return self.format_cc_message(msg, timestamp)
        elif msg.type == 'note_on':
            return self.format_note_message(msg, timestamp, "ON")
        elif msg.type == 'note_off':
            return self.format_note_message(msg, timestamp, "OFF")
        elif msg.type == 'sysex':
            return self.format_sysex_message(msg, timestamp)
        else:
            return f"{timestamp} | {msg.type.upper()}: {msg}"
    
    def format_cc_message(self, msg, timestamp):
        """Format control change message"""
        cc = msg.control
        value = msg.value
        
        # Determine message type and name
        if cc == 111:
            # Special handling: 0 = Pressed, 127 = Released
            state = "PRESSED" if value == 0 else "RELEASED" if value == 127 else f"VAL({value})"
            return f"{timestamp} | BUTTON: Pressed (CC 111) {state} (vel: {value})"
        elif cc == 93:
            state = "NUDGE LEFT"
            return f"{timestamp} | JOGWHEEL: {state} (CC 93) (val: {value})"
        elif cc == 95:
            state = "NUDGE RIGHT"
            return f"{timestamp} | JOGWHEEL: {state} (CC 95) (val: {value})"
        elif cc in CC_BUTTON_NAMES:
            name = CC_BUTTON_NAMES[cc]
            state = "PRESSED" if value > 0 else "RELEASED"
            return f"{timestamp} | BUTTON: {name} ({cc}) {state} (vel: {value})"
        
        elif cc in ENCODER_TOUCH_CCS:
            encoder_num = cc + 1
            return f"{timestamp} | ENCODER: Encoder {encoder_num} TOUCHED"
        
        elif cc in ENCODER_TURN_CCS:
            encoder_num = cc - 70
            direction = "LEFT" if value == 127 else "RIGHT" if value == 1 else f"UNKNOWN({value})"
            return f"{timestamp} | ENCODER: Encoder {encoder_num} turned {direction}"
        
        elif cc in SPECIAL_TOUCH_CCS:
            name = SPECIAL_TOUCH_CCS[cc]
            return f"{timestamp} | TOUCH: {name}"
        
        elif cc in SPECIAL_TURN_CCS:
            name = SPECIAL_TURN_CCS[cc]
            direction = "LEFT" if value == 127 else "RIGHT" if value == 1 else f"VAL({value})"
            return f"{timestamp} | CONTROL: {name} {direction}"
        
        elif cc in UPPER_DISPLAY_CCS:
            button_num = cc - 101
            state = "PRESSED" if value > 0 else "RELEASED"
            return f"{timestamp} | DISPLAY: Upper button {button_num} {state}"
        
        elif cc in LOWER_DISPLAY_CCS:
            button_num = cc - 19
            state = "PRESSED" if value > 0 else "RELEASED"
            return f"{timestamp} | DISPLAY: Lower button {button_num} {state}"
        
        else:
            return f"{timestamp} | CC: {cc} = {value} (unknown)"
    
    def format_note_message(self, msg, timestamp, state):
        """Format note on/off message"""
        note = msg.note
        velocity = msg.velocity
        
        # Calculate pad position (assuming 8x8 grid starting at note 36)
        if 36 <= note <= 99:
            pad_index = note - 36
            row = pad_index // 8 + 1
            col = pad_index % 8 + 1
            return f"{timestamp} | PAD: Row {row}, Col {col} (note {note}) {state} vel:{velocity}"
        else:
            return f"{timestamp} | NOTE: {note} {state} vel:{velocity}"
    
    def format_sysex_message(self, msg, timestamp):
        """Format SysEx message"""
        data = list(msg.data)
        
        if len(data) >= 3 and data[:3] == MANUFACTURER_ID:
            if len(data) >= 5 and data[3:5] == DEVICE_ID:
                command = data[5] if len(data) > 5 else "??"
                return f"{timestamp} | SYSEX: Push 3 command 0x{command:02X} (len: {len(data)})"
            else:
                return f"{timestamp} | SYSEX: Ableton device (len: {len(data)})"
        else:
            return f"{timestamp} | SYSEX: Other manufacturer (len: {len(data)})"
    
    def monitor(self, duration=None):
        """Start monitoring MIDI messages"""
        print("Starting MIDI monitoring...")
        print("Press Ctrl+C to stop")
        print("=" * 80)
        
        self.running = True
        start_time = time.time()
        
        try:
            while self.running:
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Check for incoming messages
                for msg in self.input_port.iter_pending():
                    self.message_count += 1
                    formatted = self.format_message(msg)
                    print(formatted)
                    
                    if self.debug and self.message_count % 50 == 0:
                        print(f"[DEBUG] Processed {self.message_count} messages")
                
                time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print(f"\nStopping... (processed {self.message_count} messages)")
        
        self.running = False
    
    def send_test_sysex(self):
        """Send a test SysEx message to Push 3"""
        if not self.output_port:
            print("No output port available")
            return
        
        # Device inquiry command
        inquiry = mido.Message('sysex', data=MANUFACTURER_ID + DEVICE_ID + [0x01])
        
        print("Sending device inquiry...")
        self.output_port.send(inquiry)
        print("Device inquiry sent")
        
        # Wait for response
        time.sleep(0.1)
        print("Checking for response...")
        
        response_found = False
        for msg in self.input_port.iter_pending():
            if msg.type == 'sysex':
                formatted = self.format_message(msg)
                print(f"Response: {formatted}")
                response_found = True
        
        if not response_found:
            print("No response received")
    
    def disconnect(self):
        """Disconnect from MIDI ports"""
        if self.input_port:
            self.input_port.close()
        if self.output_port:
            self.output_port.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Monitor MIDI messages from Push 3',
        epilog='This tool monitors all MIDI messages from your Push 3 device.'
    )
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--duration', '-t', type=int, metavar='SECONDS',
                       help='Monitor for specified duration (seconds)')
    parser.add_argument('--test-sysex', action='store_true',
                       help='Send test SysEx message and monitor response')
    
    args = parser.parse_args()
    
    try:
        print("Push 3 MIDI Monitor")
        print("=" * 30)
        
        monitor = Push3MIDIMonitor(debug=args.debug)
        monitor.connect()
        
        if args.test_sysex:
            monitor.send_test_sysex()
        else:
            monitor.monitor(duration=args.duration)
        
        monitor.disconnect()
        
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
