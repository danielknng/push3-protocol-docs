#!/usr/bin/env python3
"""
Push 3 Text Renderer
Create custom text displays for Logic Pro parameter visualization.
"""

import sys
import os
import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: PIL (Pillow) module not found.")
    print("Install with: pip install pillow")
    sys.exit(1)

# Import display functionality from display_test
try:
    sys.path.insert(0, os.path.dirname(__file__))
    from display_test import Push3Display
except ImportError as e:
    print(f"Error: Could not import Push3Display: {e}")
    print("Make sure display_test.py is in the same directory and dependencies are installed")
    sys.exit(1)

# Display constants
DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 160

# Color palette (RGB888)
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 100, 255)
    GREEN = (0, 255, 100)
    RED = (255, 50, 50)
    YELLOW = (255, 255, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_BLUE = (100, 150, 255)
    ORANGE = (255, 165, 0)


class Push3TextRenderer:
    """Text rendering system for Push 3 display"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.display = Push3Display(debug=debug)
        
        # Try to load system fonts
        self.fonts = self._load_fonts()
        
    def _load_fonts(self):
        """Load system fonts with fallback to default"""
        fonts = {}
        
        # macOS font paths
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        ]
        
        # Try to load different font sizes
        sizes = {'small': 12, 'medium': 16, 'large': 24, 'huge': 32}
        
        for size_name, size in sizes.items():
            fonts[size_name] = None
            
            for font_path in font_paths:
                try:
                    if Path(font_path).exists():
                        fonts[size_name] = ImageFont.truetype(font_path, size)
                        if self.debug:
                            print(f"Loaded {size_name} font: {font_path}")
                        break
                except:
                    continue
            
            # Fallback to default font
            if fonts[size_name] is None:
                fonts[size_name] = ImageFont.load_default()
                if self.debug:
                    print(f"Using default font for {size_name}")
        
        return fonts
    
    def create_text_image(self, lines, colors=None, background=Colors.BLACK):
        """Create image with multiple lines of text"""
        if colors is None:
            colors = [Colors.WHITE] * len(lines)
        
        # Create image
        img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), background)
        draw = ImageDraw.Draw(img)
        
        # Calculate line spacing
        line_height = DISPLAY_HEIGHT // max(len(lines), 1)
        
        for i, (line, color) in enumerate(zip(lines, colors)):
            y_pos = i * line_height + 10
            
            # Choose font size based on text length
            if len(line) > 50:
                font = self.fonts['small']
            elif len(line) > 30:
                font = self.fonts['medium']
            else:
                font = self.fonts['large']
            
            draw.text((10, y_pos), line, fill=color, font=font)
        
        return img
    
    def create_parameter_display(self, track_name="Track 1", plugin_name="Channel EQ", parameters=None):
        """Create a Logic Pro parameter display"""
        if parameters is None:
            parameters = {
                "Low Gain": "+2.5 dB",
                "Low Mid": "+1.2 dB", 
                "High Mid": "-0.8 dB",
                "High Gain": "+0.5 dB"
            }
        
        img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), Colors.BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.text((10, 5), track_name, fill=Colors.WHITE, font=self.fonts['large'])
        draw.text((10, 35), plugin_name, fill=Colors.LIGHT_BLUE, font=self.fonts['medium'])
        
        # Separator line
        draw.line([(10, 60), (DISPLAY_WIDTH - 10, 60)], fill=Colors.GRAY, width=1)
        
        # Parameters (2 columns)
        param_items = list(parameters.items())
        col_width = DISPLAY_WIDTH // 2
        
        for i, (param, value) in enumerate(param_items):
            col = i % 2
            row = i // 2
            
            x_pos = 10 + col * col_width
            y_pos = 75 + row * 25
            
            # Parameter name
            draw.text((x_pos, y_pos), f"{param}:", fill=Colors.YELLOW, font=self.fonts['small'])
            
            # Parameter value
            value_x = x_pos + 100
            value_color = Colors.GREEN if '+' in value else Colors.RED if '-' in value else Colors.WHITE
            draw.text((value_x, y_pos), value, fill=value_color, font=self.fonts['small'])
        
        return img
    
    def create_mixer_display(self, track_name="Lead Vocal", volume_db=-2.1, pan_percent=0, 
                           sends=None, solo=False, mute=False, record=False):
        """Create a mixer channel display"""
        if sends is None:
            sends = {"Send 1": 35, "Send 2": 18}
        
        img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), Colors.BLACK)
        draw = ImageDraw.Draw(img)
        
        # Track name
        draw.text((10, 5), f"Track: {track_name}", fill=Colors.WHITE, font=self.fonts['large'])
        
        # Volume
        vol_text = f"Vol: {volume_db:+.1f}dB"
        draw.text((10, 40), vol_text, fill=Colors.GREEN, font=self.fonts['medium'])
        
        # Volume bar
        bar_width = int((max(0, volume_db + 60) / 60) * 200)  # -60dB to 0dB range
        draw.rectangle([(10, 65), (10 + bar_width, 75)], fill=Colors.GREEN)
        draw.rectangle([(10 + bar_width, 65), (210, 75)], outline=Colors.GRAY)
        
        # Pan
        pan_text = f"Pan: {pan_percent:+d}%"
        draw.text((10, 85), pan_text, fill=Colors.YELLOW, font=self.fonts['medium'])
        
        # Pan indicator
        pan_center = 350
        pan_pos = pan_center + (pan_percent * 100 // 100)
        draw.line([(250, 110), (450, 110)], fill=Colors.GRAY, width=2)  # Pan line
        draw.circle((pan_pos, 110), 5, fill=Colors.YELLOW)  # Pan position
        
        # Sends
        send_y = 125
        for i, (send_name, send_percent) in enumerate(sends.items()):
            x_pos = 10 + i * 200
            send_text = f"{send_name}: {send_percent}%"
            draw.text((x_pos, send_y), send_text, fill=Colors.CYAN, font=self.fonts['small'])
            
            # Send bar
            send_bar_width = int((send_percent / 100) * 80)
            draw.rectangle([(x_pos, send_y + 15), (x_pos + send_bar_width, send_y + 20)], fill=Colors.CYAN)
            draw.rectangle([(x_pos + send_bar_width, send_y + 15), (x_pos + 80, send_y + 20)], outline=Colors.GRAY)
        
        # Status indicators
        status_x = DISPLAY_WIDTH - 150
        if solo:
            draw.text((status_x, 40), "SOLO", fill=Colors.YELLOW, font=self.fonts['medium'])
        if mute:
            draw.text((status_x, 65), "MUTE", fill=Colors.RED, font=self.fonts['medium'])
        if record:
            draw.text((status_x, 90), "REC", fill=Colors.RED, font=self.fonts['medium'])
        
        return img
    
    def create_transport_display(self, bpm=120.0, playing=False, recording=False, 
                               position="1.1.1.0", time_format="bars"):
        """Create transport status display"""
        img = Image.new('RGB', (DISPLAY_WIDTH, DISPLAY_HEIGHT), Colors.BLACK)
        draw = ImageDraw.Draw(img)
        
        # BPM
        draw.text((10, 10), f"BPM: {bpm:.1f}", fill=Colors.WHITE, font=self.fonts['huge'])
        
        # Transport state
        state_color = Colors.GREEN if playing else Colors.RED if recording else Colors.GRAY
        state_text = "PLAYING" if playing else "RECORDING" if recording else "STOPPED"
        draw.text((200, 10), state_text, fill=state_color, font=self.fonts['large'])
        
        # Position
        draw.text((10, 60), f"Position: {position}", fill=Colors.LIGHT_BLUE, font=self.fonts['large'])
        
        # Time format
        draw.text((10, 100), f"Format: {time_format}", fill=Colors.GRAY, font=self.fonts['medium'])
        
        # Metronome indicator (animated dot)
        import time
        beat_phase = int(time.time() * (bpm / 60)) % 4 + 1
        draw.text((DISPLAY_WIDTH - 100, 60), f"♩ {beat_phase}/4", fill=Colors.YELLOW, font=self.fonts['large'])
        
        return img
    
    def display_image(self, img):
        """Display PIL image on Push 3"""
        # Save to temporary file
        temp_path = Path(__file__).parent / "temp_display.png"
        img.save(temp_path)
        
        try:
            self.display.connect()
            self.display.display_image(str(temp_path))
        finally:
            # Clean up
            if temp_path.exists():
                temp_path.unlink()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Create text displays for Push 3',
        epilog='Creates various text-based displays for Logic Pro integration testing.'
    )
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--type', '-t', choices=['parameter', 'mixer', 'transport'],
                       default='parameter', help='Type of display to create')
    
    args = parser.parse_args()
    
    try:
        print("Push 3 Text Renderer")
        print("=" * 30)
        
        renderer = Push3TextRenderer(debug=args.debug)
        
        if args.type == 'parameter':
            print("Creating parameter display...")
            img = renderer.create_parameter_display(
                track_name="Lead Vocal",
                plugin_name="Channel EQ",
                parameters={
                    "Low Gain": "+2.5 dB",
                    "Low Mid": "+1.2 dB",
                    "High Mid": "-0.8 dB", 
                    "High Gain": "+0.5 dB",
                    "Q Factor": "2.1",
                    "Frequency": "1.2 kHz"
                }
            )
        
        elif args.type == 'mixer':
            print("Creating mixer display...")
            img = renderer.create_mixer_display(
                track_name="Lead Vocal",
                volume_db=-2.1,
                pan_percent=15,
                sends={"Reverb": 35, "Delay": 18},
                solo=False,
                mute=False,
                record=True
            )
        
        elif args.type == 'transport':
            print("Creating transport display...")
            img = renderer.create_transport_display(
                bpm=128.5,
                playing=True,
                recording=False,
                position="4.2.3.120"
            )
        
        # Custom text display option removed
        
        print("Displaying on Push 3...")
        renderer.display_image(img)
        print("✓ Display updated successfully!")
        
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
