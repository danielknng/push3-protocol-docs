# Push 2 vs Push 3: Protocol Comparison

This document compares the communication protocols, mappings, and features of Ableton's Push 2 and Push 3.   
Push 2 information is taken from Ableton's official documentation, while Push 3 details are based on reverse engineering.

---
## 1. USB Display Protocol Comparison

#### 1.1 USB Hardware

| Feature        | Push 2   | Push 3   | Technical Difference |
| -------------- | -------- | -------- | -------------------- |
| **Vendor ID**  | `0x2982` | `0x2982` | Same (Ableton)       |
| **Product ID** | `0x1967` | `0x1969` | Incremented by 2     |

#### 1.2 Display Specifications

| Specification    | Push 2               | Push 3               | Notes     |
| ---------------- | -------------------- | -------------------- | --------- |
| **Resolution**   | 960 x 160 pixels     | 960 x 160 pixels     | Identical |
| **Color Format** | RGB565 Little-Endian | RGB565 Little-Endian | Identical |
| **Frame Size**   | 327,680 bytes        | 327,680 bytes        | Identical |
| **Line Size**    | 2,048 bytes          | 2,048 bytes          | Identical |
| **Pixel Data**   | 1,920 bytes/line     | 1,920 bytes/line     | Identical |
| **Line Padding** | 128 bytes/line       | 128 bytes/line       | Identical |

#### 1.3 Frame Structure

```
Push 2 Frame Header:
FF CC AA 88 00 00 00 00 00 00 00 00 00 00 00 00

Push 3 Frame Header:
FF CC AA 88 00 00 00 00 00 00 00 00 00 00 00 00
```

#### 1.4 Transfer Performance

| Metric            | Push 2       | Push 3       | Improvement Factor |
| ----------------- | ------------ | ------------ | ------------------ |
| **Chunk Size**    | 512 bytes    | 16,384 bytes | 32x larger         |
| **Transfer Time** | 50-100ms     | 20-30ms      | 2-3x faster        |
| **Bandwidth**     | \~3-6 MB/s   | \~10-15 MB/s | 2-3x higher        |
| **USB Standard**  | USB 2.0 Bulk | USB 2.0 Bulk | Same               |

#### 1.5 Transfer Patterns

```python
PUSH2 = {'chunk_size': 512, 'chunks_per_frame': 640, 'transfer_time': "50-100ms"}
PUSH3 = {'chunk_size': 16384, 'chunks_per_frame': 20, 'transfer_time': "20-30ms"}
```
Push 3's larger chunk size dramatically reduces USB overhead.   
See **[Display Protocol](push3-display-protocol.md)** for more in-depth details.

#### 1.6 Push Encryption
Both devices use the same encryption.
```python
# Push XOR Pattern
XOR_PATTERN = [0xE7, 0xF3, 0xE7, 0xFF]

def encrypt_push_frame(data):
    encrypted = bytearray(data)
    for i in range(len(encrypted)):
        encrypted[i] ^= XOR_PATTERN[i % 4]
    return bytes(encrypted)
```

---

## 2. MIDI Protocol

#### 2.1 Device Identification

| Parameter           | Push 2                              | Push 3     | Compatibility |
| ------------------- | ----------------------------------- | ---------- | ------------- |
| **Manufacturer ID** | `00 21 1D`                          | `00 21 1D` | Identical     |
| **Device Family**   | `01 01`                             | `01 01`    | Identical     |
| **Device Inquiry**  | Supported                           | Supported  | Compatible    |
| **SysEx Format**    | `F0 00 21 1D 01 01 [CMD] [DATA] F7` | Same       | Compatible    |

#### 2.2 Transport Controls

| Function   | Push 2 CC | Push 3 CC | Compatible |
| ---------- | --------- | --------- | ---------- |
| **Play**   | 85        | 85        | Yes        |
| **Record** | 86        | 86        | Yes        |
| **Stop**   | 29        | 29        | Yes        |


#### 2.3 Encoders

| Encoder | Push 2 Touch | Push 3 Touch | Push 2 Turn | Push 3 Turn | Compatible |
| ------- | ------------ | ------------ | ----------- | ----------- | ---------- |
| **1**   | CC 0         | CC 0         | CC 71       | CC 71       | Yes        |
| **2**   | CC 1         | CC 1         | CC 72       | CC 72       | Yes        |
| **...** |              |              |             |             | Yes        |
| **8**   | CC 7         | CC 7         | CC 78       | CC 78       | Yes        |


#### 2.4 Pads

```python
# Both devices use identical pad mapping
PAD_MAPPING = {
    'bottom_left': 36,   # C1
    'bottom_right': 43,  # G1
    'top_left': 92,      # E6
    'top_right': 99      # D#6
}
```
Most CC mappings are identical on Push 2 and Push 3.  
For full details, see **[Interface Mapping](../interface-mapping)**.

---

## 3. SysEx Command Compatibility

#### 3.1 Confirmed Compatible Commands

```python
COMPATIBLE_COMMANDS = {
    # Display commands (Push 2 style - 16x8 limitation)
    0x18: "Display Configuration",
    0x19: "Display Brightness",
    0x1A: "Display Contrast",
    0x1B: "Display Text",
    
    # LED commands
    0x04: "Pad LED Control",
    0x05: "Button LED Control",
    0x06: "Touch Strip LED",
    
    # Device control
    0x01: "Device Inquiry",
    0x02: "Device Identity Request",
    0x03: "Device Identity Response",
    0x10: "Mode Change",
    
    # Pad control
    0x20: "Pad Velocity Curve",
    0x21: "Pad Threshold",
    0x22: "Pad Gain",
}
```

#### 3.2 Push 3 Extension Commands

```python
PUSH3_EXTENSIONS = {
    0x38: "Push 3 Specific Command A",  # Maybe RGB?
    0x3A: "Push 3 Specific Command B",  # Maybe Aftertouch Mode?
    0x3E: "Push 3 Specific Command C",  # Function TBD
}
```
More work needs to be done in order to list each compatible command.

---

## 4. From Push 2 to Push 3

#### 4.1 Handling device differences
Example of integrating both devices into a project while accounting for their differences.
```python
# Shared frame header
FRAME_HEADER = bytes.fromhex('FF CC AA 88 00 00 00 00 00 00 00 00 00 00 00 00')

# Push 3 SysEx "Extensions"
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
            'chunk_size': 16384,
            'target_fps': 30,
        },
    }
    return configs.get(device_type, configs['push2'])
```

---


#### 4.2 Display Layer

```python
import time

class UniversalPushDisplay:
    def __init__(self, device_type, device):
        self.device = device
        self.cfg = optimize_for_device(device_type)

    def send_frame(self, frame_data):
        t_start = time.perf_counter()

        # Header
        self.device.write(self.cfg['usb_endpoint'], self.cfg['header'])

        # Encrypt
        data = encrypt_push_frame(frame_data) if self.cfg['encryption'] else frame_data

        # Chunks
        chunk_size = self.cfg['chunk_size']
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self.device.write(self.cfg['usb_endpoint'], chunk)

        # Throttle to target_fps
        frame_budget = 1.0 / float(self.cfg['target_fps'])
        elapsed = time.perf_counter() - t_start
        remaining = frame_budget - elapsed
        if remaining > 0:
            time.sleep(remaining)
```

---
#### 4.3 MIDI Layer

```python
import mido

class UniversalPushMIDI:
    def __init__(self, device_type, midi_out):
        self.cfg = optimize_for_device(device_type)
        self.midi_out = midi_out

    def send_command(self, command, data):
        if self.cfg['midi_extensions'] and isinstance(command, int) and command in self.cfg['extensions']:
            return self._send_push3_command(command, data)
        return self._send_push2_command(command, data)

    def _send_push2_command(self, command, data):
        if command == 'set_led':
            cc = data['cc']
            color = max(0, min(127, data['color']))
            sysex = [0x00, 0x21, 0x1D, 0x01, 0x01, 0x05, cc, color]
            self.midi_out.send(mido.Message('sysex', data=sysex))

    def _send_push3_command(self, command, data):
        if command == PUSH3_CMD_RGB_LED:
            cc = data['cc']
            r = max(0, min(127, data['r']))
            g = max(0, min(127, data['g']))
            b = max(0, min(127, data['b']))
            sysex = [0x00, 0x21, 0x1D, 0x01, 0x01, command, cc, r, g, b]
            self.midi_out.send(mido.Message('sysex', data=sysex))
            return
        if command == PUSH3_CMD_AFTERTOUCH_MODE:
            mode = max(0, min(127, data['mode']))  # 0=poly, 1=channel
            sysex = [0x00, 0x21, 0x1D, 0x01, 0x01, command, mode]
            self.midi_out.send(mido.Message('sysex', data=sysex))
            return
        if command == PUSH3_CMD_CUSTOM:
            payload = [max(0, min(127, v)) for v in data.get('payload', [])]
            sysex = [0x00, 0x21, 0x1D, 0x01, 0x01, command, *payload]
            self.midi_out.send(mido.Message('sysex', data=sysex))
            return
        return self._send_push2_command(command, data)
```
#### 4.4 Example Usage
```python
# Open a MIDI out port (adjust name)
midi_out = mido.open_output('Ableton Push 3 User Port')

# Push 3: set aftertouch mode to channel (1)
push3 = UniversalPushMIDI('push3', midi_out)
push3.send_command(PUSH3_CMD_AFTERTOUCH_MODE, {'mode': 1})

# Push 2: set a button LED to full brightness
push2 = UniversalPushMIDI('push2', midi_out)
push2.send_command('set_led', {'cc': 85, 'color': 127})
```
---

## Key findings
1. **Minimal Changes between the two Devices** - Most code works unchanged.
2. **Optimize Transfers/Features** - Use larger chunks on Push 3 when possible; detect the hardware and gracefully degrade features for Push 2.   
---
