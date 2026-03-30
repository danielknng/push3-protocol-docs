# Push 3 SysEx Protocol

All commands use the header `F0 00 21 1D 01 01 [CMD] [DATA] F7`.

```python
MANUFACTURER_ID = [0x00, 0x21, 0x1D]
DEVICE_ID       = [0x01, 0x01]

def send_sysex(midi_out, cmd: list):
    payload = MANUFACTURER_ID + DEVICE_ID + cmd
    midi_out.send(mido.Message('sysex', data=payload))
```

---

## Pad Sensitivity Curve

The Push 3 uses a 128-entry lookup table (LUT) to map pad pressure to MIDI velocity. Sent as a single bulk message via command `0x43`. The LUT must be monotonic and plateau at 127.

### Parameters

| Parameter | Range | Meaning |
|---|---|---|
| Threshold | 0-100 | Pads below this are always velocity 1 |
| Drive | -50 to +50 | Skews the curve (negative = softer, positive = harder) |
| Compand | -50 to +50 | S-curve shaping |
| Range | 0-100 | Pads above this are always velocity 127 |

### Building the LUT

```python
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def bias(x, b):
    # Schlick bias
    return x / ((1/b - 2) * (1 - x) + 1)

def gain(x, g):
    # Schlick gain
    if x < 0.5:
        return 0.5 * bias(2*x, 1-g)
    return 1 - 0.5 * bias(2-2*x, 1-g)

def build_curve(threshold, drive, compand, range_):
    Nt = round(clamp(threshold, 0, 100) * 16 / 100)   # leading 1s
    Nr = round(clamp(range_,    0, 100) * 103 / 100)  # trailing 127s

    Nt = min(Nt, 127)
    Nr = min(Nr, 127 - Nt)
    num_curve = max(2, 128 - Nt - Nr + 2)

    b = clamp(0.5 + drive   / 100, 0.01, 0.99)
    g = clamp(0.5 + compand / 100, 0.01, 0.99)

    curve = [0] * 128

    for i in range(Nt):
        curve[i] = 1

    for i in range(num_curve):
        x = i / (num_curve - 1)
        y = bias(gain(x, g), b)
        v = int(round(1 + y * 126))
        curve[max(0, Nt + i - 1)] = min(127, max(1, v))

    for i in range(128 - Nr, 128):
        curve[i] = 127

    for i in range(1, 128):
        if curve[i] < curve[i-1]:
            curve[i] = curve[i-1]

    return curve

def validate_curve(curve):
    assert len(curve) == 128
    assert all(0 <= v <= 127 for v in curve)
    for i in range(1, 128):
        assert curve[i] >= curve[i-1]
    idx = next((i for i, v in enumerate(curve) if v == 127), None)
    if idx is not None:
        assert all(v == 127 for v in curve[idx:])
```

### Sending

```python
def send_curve(midi_out, curve: list):
    send_sysex(midi_out, [0x43] + curve)
```

---

## Aftertouch and MPE

Command `0x1E` controls pressure mode:

```python
PRESSURE_MODE = {
    0x00: 'channel pressure',
    0x01: 'poly aftertouch',
    0x02: 'MPE',
}

send_sysex(midi_out, [0x1E, 0x01])  # poly aftertouch
send_sysex(midi_out, [0x1E, 0x02])  # MPE
send_sysex(midi_out, [0x1E, 0x00])  # channel pressure
```

---

## MPE Per-Pad Parameters

Command `0x26 0x07` followed by a parameter byte and value:

```python
def send_mpe_param(midi_out, param: int, value: int):
    send_sysex(midi_out, [0x26, 0x07, param, value, 0x00])
```

### Per-Pad Pitchbend

```python
send_mpe_param(midi_out, 0x08, 0x02)  # enable
send_mpe_param(midi_out, 0x08, 0x00)  # disable
```

### In Tune Location

Where pitch bend starts - Pad (0) or Finger (1):

```python
send_mpe_param(midi_out, 0x0E, 0x00)  # Pad
send_mpe_param(midi_out, 0x0E, 0x01)  # Finger
```

### In Tune Width

Dead zone around the in-tune position in mm:

```python
TUNE_WIDTH = {
    '0mm': 0x00, '1mm': 0x04, '2mm': 0x08, '2.5mm': 0x0C,
    '3mm': 0x10, '4mm': 0x14, '5mm': 0x18, '6mm':   0x1C,
    '7mm': 0x20, '10mm': 0x30, '13mm': 0x40, '20mm': 0x60,
}

send_mpe_param(midi_out, 0x14, TUNE_WIDTH['3mm'])
```

### Slide Height

How far up the pad sliding is active:

```python
SLIDE_HEIGHT = {
    '16mm': 0x13, '15mm': 0x19, '14mm': 0x20, '13mm': 0x27,
    '12mm': 0x2D, '11mm': 0x34, '10mm': 0x3B,
}

send_mpe_param(midi_out, 0x24, SLIDE_HEIGHT['13mm'])
```

---

## Touch Strip

Command `0x17` sets the strip mode. Position is sent as standard pitchbend on channel 0.

```python
RIBBON_MODES = {
    'pitchbend': 122,  # default
    'volume':      1,
    'pan':        17,
    'discrete':    9,
}

def set_ribbon_mode(midi_out, mode: int):
    send_sysex(midi_out, [0x17, mode])

def set_ribbon_value(midi_out, value: int):
    # 0..16383
    midi_out.send(mido.Message('pitchwheel', pitch=value - 8192, channel=0))
```

Touch detection: CC 12, velocity 127 when touched.

---

## Audio Interface

All audio commands use command `0x37` with a 13-byte zero padding suffix.

```python
ZERO_PAD = [0x00] * 13

def send_audio(midi_out, cmd: list):
    send_sysex(midi_out, [0x37] + cmd + ZERO_PAD)
```

### Pedal / CV Output

```python
PEDAL_CONFIG = {
    (False, False): 0x50,  # both footswitch
    (True,  False): 0x43,  # CV1, footswitch 2
    (False, True):  0x1C,  # footswitch 1, CV2
    (True,  True):  0x0F,  # both CV
}

def send_pedal_config(midi_out, cv1: bool, cv2: bool):
    send_audio(midi_out, [0x26, PEDAL_CONFIG[(cv1, cv2)]])
```

### Preamp Type

```python
PREAMP_TYPE = {'line': 0, 'instrument': 1, 'high': 2}

def send_preamp_type(midi_out, input_nr: int, type_: int):
    cmd = 0x1A if input_nr == 1 else 0x1B
    send_audio(midi_out, [cmd, type_])
```

### Preamp Gain

Range 0x00 (20dB) to 0x28 (0dB), steps of 2:

```python
def send_preamp_gain(midi_out, input_nr: int, gain_db: int):
    cmd = 0x02 if input_nr == 1 else 0x03
    send_audio(midi_out, [cmd, (20 - gain_db) * 2])
```

### Output Routing

```python
OUTPUT_CONFIG = {
    'hp_1_2_spk_1_2': 0,
    'hp_3_4_spk_1_2': 2,
    'hp_1_2_spk_3_4': 3,
}

def send_output_config(midi_out, config: int):
    value = 0 if config == 0 else config + 1
    send_audio(midi_out, [0x11, value])
```

---

## Color Palette

Pad and button colors are controlled via a 128-entry RGBW palette. Each color component is 7-bit encoded as two bytes (low 7 bits, high 7 bits).

| Command | Direction | Purpose |
|---|---|---|
| `0x03` | host -> device | Write palette entry |
| `0x04` | host -> device | Read palette entry (request) |
| `0x05` | host -> device | Re-apply palette after changes |

Write format (`0x03`):

```python
def write_palette_entry(midi_out, index: int, r: int, g: int, b: int, w: int = 0):
    # r, g, b, w: 0..255 each, encoded as 7-bit pairs
    def split(v): return v % 128, v // 128
    rl, rh = split(r)
    gl, gh = split(g)
    bl, bh = split(b)
    wl, wh = split(w)
    send_sysex(midi_out, [0x03, index, rl, rh, gl, gh, bl, bh, wl, wh])

def reapply_palette(midi_out):
    send_sysex(midi_out, [0x05])
```

This is shared with Push 2. Full documentation in the [Ableton Push 2 interface spec](https://github.com/Ableton/push-interface/blob/main/doc/AbletonPush2MIDIDisplayInterface.asc).

---

## Unknown Commands

```python
UNKNOWN = {
    0x38: 'Unknown',
    0x3A: 'Unknown',
    0x3E: 'Unknown',
}
```

---

The MPE and audio interface sections are based on [DrivenByMoss](https://github.com/git-moss/DrivenByMoss) by Jürgen Moßgraber, cross-referenced against captured SysEx data.

