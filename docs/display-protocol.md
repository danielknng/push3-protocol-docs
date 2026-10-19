# Push 3 USB Display Protocol

960x160px display, RGB565 little-endian, USB 2.0 Bulk.

---

## 1. Frame Structure

327,680 bytes per frame, split into a 16-byte header and a 327,664-byte framebuffer.

```
327,680 bytes total
- Header:      16 bytes (unencrypted)
- Framebuffer: 327,664 bytes (XOR-encrypted)
  - 160 lines x 2,048 bytes
    - 1,920 bytes pixel data (960px x 2 bytes/px)
    - 128 bytes padding (zeros)
```

Header is fixed:

```python
FRAME_HEADER = bytes.fromhex('FF CC AA 88 00 00 00 00 00 00 00 00 00 00 00 00')
assert len(FRAME_HEADER) == 16
```

---

## 2. Encryption

Only the framebuffer is encrypted. Header goes out as-is.

```python
XOR_PATTERN = (0xE7, 0xF3, 0xE7, 0xFF)

def encrypt_push_frame(data: bytes) -> bytes:
    buf = bytearray(data)
    for i in range(len(buf)):
        buf[i] ^= XOR_PATTERN[i % 4]
    return bytes(buf)
```

---

## 3. USB

```python
USB_VENDOR_ID    = 0x2982
USB_PRODUCT_ID   = 0x1969  # Push 3 (Push 2 is 0x1967)
USB_ENDPOINT_OUT = 0x01
USB_INTERFACE    = (0, 0)  # (bInterfaceNumber, bAlternateSetting)

CHUNK_SIZE  = 16_384  # bytes per bulk write
TARGET_FPS  = 30
```

---

## 4. Image Preparation

Convert RGB888 to RGB565, add 128-byte zero padding per line.

```python
import struct
from PIL import Image

def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

def prepare_image(path: str) -> bytes:
    img = Image.open(path).resize((960, 160), Image.LANCZOS).convert('RGB')
    fb = bytearray()
    for y in range(160):
        line = bytearray()
        for x in range(960):
            r, g, b = img.getpixel((x, y))
            line += struct.pack('<H', rgb888_to_rgb565(r, g, b))
        line += bytes(128)
        fb += line
    assert len(fb) == 327_664
    return bytes(fb)
```

---

## 5. Sending a Frame

```python
import time
import usb.core
import usb.util

def connect_display():
    dev = usb.core.find(idVendor=USB_VENDOR_ID, idProduct=USB_PRODUCT_ID)
    if not dev:
        raise RuntimeError('Push 3 not found')
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[USB_INTERFACE]
    usb.util.claim_interface(dev, intf.bInterfaceNumber)
    return dev

def send_frame(dev, framebuffer: bytes):
    assert len(framebuffer) == 327_664

    t0 = time.perf_counter()

    dev.write(USB_ENDPOINT_OUT, FRAME_HEADER)
    data = encrypt_push_frame(framebuffer)
    for i in range(0, len(data), CHUNK_SIZE):
        dev.write(USB_ENDPOINT_OUT, data[i:i + CHUNK_SIZE], timeout=1000)

    elapsed = time.perf_counter() - t0
    remaining = (1.0 / TARGET_FPS) - elapsed
    if remaining > 0:
        time.sleep(remaining)
```

Usage:

```python
dev = connect_display()
fb  = prepare_image('test_image.png')
send_frame(dev, fb)
```

---

<details>
<summary>Push 2 differences</summary>

Push 2 uses the same frame format, header, and encryption. The only difference is transfer chunk size and target framerate:

```python
PUSH2_CHUNK_SIZE = 512    # vs 16,384 on Push 3
PUSH2_TARGET_FPS = 15     # vs 30 on Push 3
```

Product ID is `0x1967` (Push 3 is `0x1969`).

</details>

---

## 6. Troubleshooting

- On Linux, you need a udev rule or run as root to access the USB device.
- Claim the interface before writing, otherwise pyusb will throw a resource busy error.
- Header is always 16 bytes, framebuffer always 327,664 bytes - assert both before sending.
- Push 3 uses endpoint `0x01` OUT. Nothing else.

