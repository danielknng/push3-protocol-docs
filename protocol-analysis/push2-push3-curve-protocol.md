This document explains how Push 2 and Push 3 handle pad sensitivity curves.  
It covers **message formats**, **curve generation**, and **working code** for both devices.

The general information in this document is based on the GitHub project **[DrivenByMoss](https://github.com/git-moss/DrivenByMoss)**.

---

## 1. Overview

Both devices use a **128-entry lookup table (LUT)** to convert **pad pressure** into **MIDI velocity**.

Each LUT entry is a single 7-bit value (0..127).

| Term           | Meaning                                       |
| -------------- | --------------------------------------------- |
| LUT length     | 128 values                                    |
| Value range    | 0..127 (7-bit)                                |
| Monotonic rule | Values must never go down                     |
| Plateau rule   | Once a value hits 127, all following stay 127 |

---

## 2. Push 2 vs Push 3

| Aspect         | Push 2                               | Push 3                                     |
| -------------- | ------------------------------------ | ------------------------------------------ |
| Sending method | 0x20 per-entry (8 chunks of 16)      | 0x43 single bulk message (all 128 at once) |
| Extra message  | 0x1B with thresholds + cpmin + cpmax | None                                       |
| Curve building | LUT + separate calibration           | LUT only                                   |
| Complexity     | Higher                               | Lower                                      |

---

## 3. Why Push 2 Needs Thresholds

Push 2 needs **two calibration values** for its pads:

| Name  | Purpose                                                  |
| ----- | -------------------------------------------------------- |
| cpmin | Minimum force that counts as a pad press                 |
| cpmax | Force at which the pad is fully saturated (velocity 127) |

If these are missing:

* cpmin too low → pads trigger too easily.
* cpmax too high → full velocity is unreachable.

Push 3 **does not need these values**, because:

* Its LUT already defines the start point (**Threshold**) and end point (**Range**) directly.
* No extra messages required.

---

## 4. SysEx Message Formats

### 4.1 Push 2 - Curve (0x20)

Sends the LUT in 8 messages, each carrying 16 values.

```
F0 00 21 1D
01 01 20
<start_index>          ; 0, 16, 32, ... 112
<16 values>            ; each 0-127
F7
```

---

### 4.2 Push 2 - Calibration (0x1B)

One message with four numbers:

* th0 = 33 (fixed)
* th1 = 31 (fixed)
* cpmin
* cpmax

Each is split into two bytes:

* L = value & 0x7F  (low 7 bits)
* H = (value >> 7) & 0x1F (high 5 bits)

```
F0 00 21 1D
01 01 1B
<th0_L> <th0_H>
<th1_L> <th1_H>
<cpmin_L> <cpmin_H>
<cpmax_L> <cpmax_H>
F7
```

---

### 4.3 Push 3 - Bulk Curve (0x43)

One single message containing all 128 curve values.

```
F0 00 21 1D
01 01 43
<128 values>          ; 7-bit, monotonic, plateau at 127
F7
```

---

## 5. Push 3 Parameters

| Parameter | Range    | Meaning                                                           |
| --------- | -------- | ----------------------------------------------------------------- |
| Threshold | 0..100   | Pads below this are always velocity 1                             |
| Drive     | -50..+50 | Skews the curve: negative = softer start, positive = harder start |
| Compand   | -50..+50 | Adds a soft or hard transition (S-shape)                          |
| Range     | 0..100   | Pads above this are always velocity 127                           |

Mapping:

* Threshold → 0..16 leading 1s.
* Range → 0..103 trailing 127s.
* Drive → b = clamp(0.5 + Drive/100, 0.01..0.99)
* Compand → g = clamp(0.5 + Compand/100, 0.01..0.99)

---

## 6. Building the Push 3 Curve

### 6.1 Helper Functions

```python
import math

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
```

---

### 6.2 Calculate Threshold and Range Counts

```python
def threshold_count(threshold):
    # 0..100 -> 0..16
    return round(clamp(threshold, 0, 100) * 16 / 100)

def range_count(range_):
    # 0..100 -> 0..103
    return round(clamp(range_, 0, 100) * 103 / 100)
```

---

### 6.3 Build the Full LUT

```python
def build_curve_push3(threshold, drive, compand, range_):
    Nt = threshold_count(threshold)  # leading 1s
    Nr = range_count(range_)         # trailing 127s

    # safety
    Nt = min(Nt, 127)
    Nr = min(Nr, 127 - Nt)

    numCurveValues = max(2, 128 - Nt - Nr + 2)

    b = clamp(0.5 + drive / 100, 0.01, 0.99)
    g = clamp(0.5 + compand / 100, 0.01, 0.99)

    curve = [0] * 128

    # 1) Threshold region
    for i in range(Nt):
        curve[i] = 1

    # 2) Dynamic region
    for i in range(numCurveValues):
        x = i / (numCurveValues - 1)
        y = gain(x, g)     # Compand first
        y = bias(y, b)     # Drive second
        v = int(round(1 + y * 126))
        curve[max(0, Nt + i - 1)] = min(127, max(1, v))

    # 3) Range region
    for i in range(128 - Nr, 128):
        curve[i] = 127

    # 4) Make sure curve never decreases
    for i in range(1, 128):
        if curve[i] < curve[i-1]:
            curve[i] = curve[i-1]

    return curve
```

---

## 7. Sending to Push 3

### 7.1 Build the SysEx message

```python
def to_sysex_push3(curve):
    # F0 00 21 1D 01 01 43 <128 bytes> F7
    return [0xF0,0x00,0x21,0x1D,0x01,0x01,0x43,*curve,0xF7]
```

---

### 7.2 Example Usage

```python
import mido

curve = build_curve_push3(threshold=5, drive=10, compand=-10, range_=30)
frame = to_sysex_push3(curve)

with mido.open_output("Ableton Push 3") as out:
    out.send(mido.Message("sysex", data=frame[1:-1]))  # mido strips F0/F7
```

---

## 8. Push 2 Code

### 8.1 Build Curve Chunks

```python
def push2_curve_chunks(curve):
    frames = []
    for start in range(0, 128, 16):
        payload = [0x20, start, *curve[start:start+16]]
        frames.append([0xF0,0x00,0x21,0x1D,0x01,0x01,*payload,0xF7])
    return frames
```

---

### 8.2 Build Calibration Message

```python
def split_14bit(v):
    return v & 0x7F, (v >> 7) & 0x1F

def push2_threshold_cp(th0, th1, cpmin, cpmax):
    data = [0x1B]
    for val in (th0, th1, cpmin, cpmax):
        L, H = split_14bit(val)
        data += [L, H]
    return [0xF0,0x00,0x21,0x1D,0x01,0x01,*data,0xF7]
```

---

### 8.3 Send Everything to Push 2

```python
with mido.open_output("Ableton Push 2") as out:
    cpmin = 1650
    cpmax = 2050

    frames = push2_curve_chunks(curve)
    cfg = push2_threshold_cp(33, 31, cpmin, cpmax)

    for f in frames:
        out.send(mido.Message("sysex", data=f[1:-1]))
    out.send(mido.Message("sysex", data=cfg[1:-1]))
```

---

## 9. Validation

```python
def validate(curve):
    assert len(curve) == 128
    assert all(0 <= v <= 127 for v in curve)
    for i in range(1, 128):
        assert curve[i] >= curve[i-1]
    idx = next((i for i,v in enumerate(curve) if v == 127), None)
    if idx is not None:
        assert all(v == 127 for v in curve[idx:])
```

---

## 10. Final Summary

| Task               | Push 2                             | Push 3                    |
| ------------------ | ---------------------------------- | ------------------------- |
| LUT sending        | 8 messages, 16 values each         | 1 message, all 128 values |
| Calibration needed | Yes, cpmin/cpmax via extra message | No, built into LUT        |
| Complexity         | Higher                             | Lower                     |

* **Push 2:** Two-step process -> calibration first, then curve data.
* **Push 3:** One-step process -> one LUT with everything included.
