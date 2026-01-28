# Push 3 USB Display Protocol

### 1. Overview

```python
OVERVIEW = {
    "resolution": (960, 160),
    "pixel_format": "RGB565 Little-Endian",
    "frame_bytes_total": 327_680,   # 16 header + 327,664 framebuffer
    "usb_interface": "USB 2.0 Bulk (OUT, ep 0x01)",
    "encryption": "4-byte XOR pattern",
    "typical_latency_ms": (20, 30),
}
```

Header is sent unencrypted. Framebuffer is XOR-encrypted.

---

### 2. Frame Structure

#### 2.1 Layout

```
327,680 bytes total
├── Header: 16 bytes
└── Framebuffer: 327,664 bytes
    ├── 160 lines × 2,048 bytes
    │   ├── 1,920 bytes pixel data (960×2)
    │   └── 128 bytes padding (zeros)
```

#### 2.2 Header

```python
# 16-byte header:
# 0..3   = FF CC AA 88  (magic/sync, fixed)
# 4..15  = 00 ... 00    (payload currently zeroed)
FRAME_HEADER = bytes.fromhex('FF CC AA 88 00 00 00 00 00 00 00 00 00 00 00 00')
assert len(FRAME_HEADER) == 16
```

---

### 3. Encryption

Only the framebuffer (327,664 bytes) is encrypted. Header is not.

```python
XOR_PATTERN = (0xE7, 0xF3, 0xE7, 0xFF)

def encrypt_push_frame(data: bytes) -> bytes:
    buf = bytearray(data)
    for i in range(len(buf)):
        buf[i] ^= XOR_PATTERN[i % 4]
    return bytes(buf)
```

---

### 4. USB Transfer

#### 4.1 Identification

```python
USB_VENDOR_ID   = 0x2982
USB_PRODUCT_ID  = 0x1969  # Push 3
USB_ENDPOINT_OUT = 0x01
USB_INTERFACE    = (0, 0)  # (bInterfaceNumber, bAlternateSetting)
```

#### 4.2 Transfer Settings

```python
PUSH3_CHUNK_SIZE = 16_384   # bytes per USB bulk write
PUSH3_TARGET_FPS = 30       # frames per second

# If you use optimize_for_device('push3'), these match:
assert optimize_for_device('push3')['chunk_size'] == PUSH3_CHUNK_SIZE
assert optimize_for_device('push3')['target_fps'] == PUSH3_TARGET_FPS
```

---

### 5. Configuration
From **[Push2-Push3-Protocol.md](push2-push3-protocol.md)**

```python
# Shared frame header
FRAME_HEADER = bytes.fromhex('FF CC AA 88 00 00 00 00 00 00 00 00 00 00 00 00')

# Push 3 SysEx "Extensions" (not used by the display path, kept for consistency)
PUSH3_EXTENSIONS = {
    0x38: "RGB LED Control",
    0x3A: "Aftertouch Mode",
    0x3E: "Custom Feature TBD",
}
PUSH3_CMD_RGB_LED, PUSH3_CMD_AFTERTOUCH_MODE, PUSH3_CMD_CUSTOM = tuple(PUSH3_EXTENSIONS.keys())

def optimize_for_device(device_type):
    configs = {
        'push2': {
            'device': 'push2',
            'usb_endpoint': 0x01,
            'header': FRAME_HEADER,
            'encryption': True,
            'sysex_compatible': True,
            'midi_extensions': False,
            'extensions': {},
            'chunk_size': 512,
            'target_fps': 15,
        },
        'push3': {
            'device': 'push3',
            'usb_endpoint': 0x01,
            'header': FRAME_HEADER,
            'encryption': True,
            'sysex_compatible': True,
            'midi_extensions': True,
            'extensions': PUSH3_EXTENSIONS,
            'chunk_size': 16_384,
            'target_fps': 30,
        },
    }
    return configs.get(device_type, configs['push2'])
```

---

## 6. Display Layer

Sends header once, encrypts framebuffer, respects `chunk_size` and `target_fps` from `optimize_for_device()`.

```python
import time

class UniversalPushDisplay:
    def __init__(self, device_type, device):
        self.device = device
        self.cfg = optimize_for_device(device_type)

    def send_frame(self, framebuffer: bytes):
        t0 = time.perf_counter()

        # Header (16 bytes, unencrypted)
        self.device.write(self.cfg['usb_endpoint'], self.cfg['header'])

        # Encrypt framebuffer if enabled
        data = encrypt_push_frame(framebuffer) if self.cfg['encryption'] else framebuffer

        # Chunked transfer
        step = self.cfg['chunk_size']
        for i in range(0, len(data), step):
            chunk = data[i:i+step]
            self.device.write(self.cfg['usb_endpoint'], chunk, timeout=1000)

        # Throttle to target_fps
        budget = 1.0 / float(self.cfg['target_fps'])
        elapsed = time.perf_counter() - t0
        sleep = budget - elapsed
        if sleep > 0:
            time.sleep(sleep)
```

---

## 7. Image Preparation

RGB888 → RGB565, line padding (128 bytes/line).

```python
import struct
from PIL import Image

def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
    r5 = (r >> 3) & 0x1F
    g6 = (g >> 2) & 0x3F
    b5 = (b >> 3) & 0x1F
    return (r5 << 11) | (g6 << 5) | b5

def rgb565_to_bytes(v: int) -> bytes:
    return struct.pack('<H', v)  # little-endian

def prepare_image_for_push3(path: str) -> bytes:
    img = Image.open(path).resize((960, 160), Image.LANCZOS).convert('RGB')
    fb = bytearray()
    for y in range(160):
        line = bytearray()
        for x in range(960):
            r, g, b = img.getpixel((x, y))
            line += rgb565_to_bytes(rgb888_to_rgb565(r, g, b))
        line += bytes(128)  # padding per line
        fb += line
    assert len(fb) == 327_664, "Invalid framebuffer size"
    return bytes(fb)
```

---

## 8. Connect to Display and Push Data

```python
import usb.core
import usb.util

USB_VENDOR_ID   = 0x2982
USB_PRODUCT_ID  = 0x1969
USB_ENDPOINT_OUT = 0x01
USB_INTERFACE    = (0, 0)

def connect_display():
    dev = usb.core.find(idVendor=USB_VENDOR_ID, idProduct=USB_PRODUCT_ID)
    if not dev:
        raise RuntimeError("Push 3 not found")
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[USB_INTERFACE]
    usb.util.claim_interface(dev, intf.bInterfaceNumber)
    return dev

# Example usage (Push 3)
device_type = 'push3'
cfg = optimize_for_device(device_type)                 # from section 5
dev = connect_display()
display = UniversalPushDisplay(device_type, dev)       # from section 6
framebuffer = prepare_image_for_push3('image.png')     # from section 7
display.send_frame(framebuffer)                        # uses cfg['chunk_size'], cfg['target_fps']
```

---

## 9. Performance

```python
PERF = {
    "frame_prep_ms": "< 1",
    "usb_transfer_ms": "15–25",
    "display_update_ms": "< 5",
    "total_frame_ms": "20–30",
}
```

---

## 10. Troubleshooting

```python
# Validate sizes
assert len(FRAME_HEADER) == 16
assert len(framebuffer) == 327_664
assert len(encrypt_push_frame(framebuffer)) == 327_664

# Endpoint and interface
assert USB_ENDPOINT_OUT == 0x01
# Ensure interface is claimed via pyusb before writing.
```

Common checks:

* Device connected and accessible (permissions, udev/driver).
* Use endpoint `0x01` (OUT).
* Send header once per frame, then the encrypted framebuffer.
* Respect `chunk_size` and `target_fps` from `optimize_for_device()`.
