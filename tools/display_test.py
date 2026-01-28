#!/usr/bin/env python3
"""
Push 3 Display Test Tool
Simple tool to display the test image on Push 3 hardware.
"""

import sys
import os
import struct
from pathlib import Path
from PIL import Image

try:
    import usb.core
    import usb.util
except ImportError:
    print("Error: pyusb module not found.")
    print("Install dependencies:")
    print("  macOS: brew install libusb && pip install pyusb pillow")
    print("  Linux: sudo apt install libusb-1.0-0-dev && pip install pyusb pillow")
    sys.exit(1)

# Push 3 USB identifiers
VENDOR_ID = 0x2982
PRODUCT_ID = 0x1969

# Protocol constants
FRAME_HEADER = bytes([
    0xFF, 0xCC, 0xAA, 0x88,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00
])
XOR_PATTERN = [0xE7, 0xF3, 0xE7, 0xFF]

# Display specifications
DISPLAY_WIDTH = 960
DISPLAY_HEIGHT = 160
LINE_PADDING = 128
CHUNK_SIZE = 16384


class Push3Display:
    """Simple Push 3 USB display controller"""
    
    def __init__(self, debug=False):
        self.device = None
        self.debug = debug
        
    def connect(self):
        """Find and connect to Push 3 device"""
        if self.debug:
            print("Searching for Push 3 device...")
            
        self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
        if self.device is None:
            raise RuntimeError("Push 3 device not found. Make sure it's connected via USB.")
        
        if self.debug:
            print(f"Found Push 3: {self.device}")
            
        # Configure device
        try:
            self.device.set_configuration()
            if self.debug:
                print("Device configured successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to configure device: {e}")
    
    def prepare_image(self, image_path):
        """Load and prepare image for Push 3 display"""
        if self.debug:
            print(f"Loading image: {image_path}")
            
        # Load and resize image
        img = Image.open(image_path)
        img = img.resize((DISPLAY_WIDTH, DISPLAY_HEIGHT), Image.LANCZOS)
        img = img.convert('RGB')
        
        if self.debug:
            print(f"Image resized to {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
        
        # Convert to RGB565 framebuffer
        framebuffer = bytearray()
        
        for y in range(DISPLAY_HEIGHT):
            line_data = bytearray()
            
            # Convert pixels to RGB565
            for x in range(DISPLAY_WIDTH):
                r, g, b = img.getpixel((x, y))
                rgb565 = self.rgb888_to_rgb565(r, g, b)
                line_data.extend(struct.pack('<H', rgb565))
            
            # Add line padding
            line_data.extend(bytes(LINE_PADDING))
            framebuffer.extend(line_data)
        
        return bytes(framebuffer)
    
    def rgb888_to_rgb565(self, r, g, b):
        """Convert 24-bit RGB to 16-bit RGB565"""
        r5 = (r >> 3) & 0x1F
        g6 = (g >> 2) & 0x3F
        b5 = (b >> 3) & 0x1F
        return (r5 << 11) | (g6 << 5) | b5
    
    def encrypt_framebuffer(self, data):
        """Apply XOR encryption to framebuffer data"""
        encrypted = bytearray(data)
        for i in range(len(encrypted)):
            encrypted[i] ^= XOR_PATTERN[i % 4]
        return bytes(encrypted)
    
    def send_frame(self, framebuffer):
        """Send complete frame to Push 3 display"""
        if not self.device:
            raise RuntimeError("Device not connected. Call connect() first.")
        
        if self.debug:
            print("Sending frame header...")
        
        # Send frame header
        self.device.write(0x01, FRAME_HEADER)
        
        # Encrypt framebuffer
        encrypted = self.encrypt_framebuffer(framebuffer)
        
        if self.debug:
            print(f"Sending {len(encrypted)} bytes in {CHUNK_SIZE}-byte chunks...")
        
        # Send framebuffer in chunks
        bytes_sent = 0
        for i in range(0, len(encrypted), CHUNK_SIZE):
            chunk = encrypted[i:i + CHUNK_SIZE]
            self.device.write(0x01, chunk)
            bytes_sent += len(chunk)
            
            if self.debug and i % (CHUNK_SIZE * 5) == 0:  # Progress every 5 chunks
                progress = (bytes_sent / len(encrypted)) * 100
                print(f"Progress: {progress:.1f}%")
        
        if self.debug:
            print("Frame sent successfully!")
    
    def display_image(self, image_path):
        """Complete workflow: load image and display on Push 3"""
        framebuffer = self.prepare_image(image_path)
        self.send_frame(framebuffer)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Display test image on Push 3',
        epilog='This tool displays the hllo_wrld.png test image on your Push 3 device.'
    )
    parser.add_argument('--debug', '-d', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    # Find the test image
    script_dir = Path(__file__).parent
    test_image = script_dir / 'hllo_wrld.png'
    
    if not test_image.exists():
        print(f"Error: Test image not found at {test_image}")
        print("Make sure hllo_wrld.png is in the same directory as this script.")
        sys.exit(1)
    
    try:
        print("Push 3 Display Test Tool")
        print("=" * 30)
        
        if args.debug:
            print("Debug mode enabled")
        
        # Initialize display
        display = Push3Display(debug=args.debug)
        display.connect()
        
        print(f"Displaying test image: {test_image.name}")
        display.display_image(str(test_image))
        
        print("✓ Test image displayed successfully!")
        print("\nThe 'Hello World' image should now be visible on your Push 3 display.")
        
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
