# Push 3 + Python - A Beginner's Quickstart

This guide walks you through:

1. Finding and opening the correct MIDI ports
2. Switching the Push 3 into **User Mode** (required)
3. Lighting **one pad**
4. Printing pad presses in the console

The goal: get a working two-way connection between Python and the Push 3 with minimal code.

---

## 1) Foreword

The Ableton Push 3 is a MIDI device:

* It sends MIDI messages when you press pads, turn knobs, or push buttons.
* It receives MIDI messages to light pads and update LEDs.
* Pads communicate using `note_on` (press) and `note_off` (release).

We will:

* Ignore buttons and encoders for now - pads only.
* Use the **User** port, not the Live port, so Ableton Live does not interfere.
* Enter **User Mode** first so the Push 3 behaves correctly for custom control.
  Without User Mode, pad lighting and messages may be inconsistent.

---

## 2) Requirements: Python 3 and virtual environment

Make sure you have Python 3 installed.
We will create a virtual environment to keep dependencies clean.

```bash
# Create and activate a clean environment (macOS/Linux)
python3 -m venv .venv
. .venv/bin/activate

# Windows PowerShell
# python -m venv .venv
# .venv\Scripts\Activate.ps1

# Install MIDI dependencies
pip install mido python-rtmidi
```

Tip: Close Ableton Live before testing to avoid port conflicts.

---

## 3) Constants at the top - and why they matter

At the very top of your Python script, define the following constants.
They give readable names to important numbers we will use later.

```python
# --- SysEx (System Exclusive) identifiers ---
# These bytes identify Ableton and the Push 3 when sending vendor-specific commands.

MANUFACTURER_ID = [0x00, 0x21, 0x1D]  # Ableton manufacturer ID
DEVICE_ID       = [0x01, 0x01]        # Push 3 family/model ID

# --- Command to enter User Mode ---
CMD_SET_USER_MODE = 0x0A  # "Set User Mode" command byte
USER_MODE_ENABLE  = 0x01  # Enable User Mode

# --- Test pad we will light up ---
# The bottom-left pad of the 8x8 grid is MIDI note 36.
TEST_PAD_NOTE  = 36
TEST_VELOCITY  = 100  # also controls brightness/color in User Mode
```

Why hex (0x)? MIDI docs use hex because messages are bytes. `0x0A` equals decimal 10. Python treats both as integers.

---

## 4) Open the MIDI ports (and understand the direction)

The Push 3 has two directions:

* Push -> Python: sends data like pad presses to `midi_in`
* Python -> Push: sends commands to light pads to `midi_out`

That means:

* `midi_out` in your Python script sends data to the Push, so on the Push side this is received through its MIDI IN port.
* `midi_in` in your Python script reads data from the Push, so on the Push side this comes from its MIDI OUT port.

```python
import mido

def find_push3_ports():
    ins  = mido.get_input_names()
    outs = mido.get_output_names()

    # Prefer the dedicated "User" port for custom control
    user_in  = next((n for n in ins  if "User" in n), None)
    user_out = next((n for n in outs if "User" in n), None)

    # Fallback to any "Ableton Push 3" port if no "User" found
    push_in  = user_in  or next((n for n in ins  if "Ableton Push 3" in n), None)
    push_out = user_out or next((n for n in outs if "Ableton Push 3" in n), None)

    if not push_in or not push_out:
        raise RuntimeError("Push 3 MIDI ports not found. Check USB connection.")
    return push_in, push_out

# Open ports
in_name, out_name = find_push3_ports()
midi_in  = mido.open_input(in_name)    # Push -> Python (reads pad presses)
midi_out = mido.open_output(out_name)  # Python -> Push (lights pads, write)

print(f"Connected:\n  APP IN <- {in_name}\n  APP OUT -> {out_name}")
```

---

## 5) Handshake: Inquiry (optional) + Enter User Mode (required)

Before doing anything else, run a handshake:

1. Optional device inquiry:
   `F0 7E 7F 06 01 F7`
   A standard MIDI command to ask, "Who are you?"
   Push 3 will reply with its identity, which you can print.
   This is a universal "Identity Request" defined by the MIDI spec.
   It is not Ableton-specific and any MIDI device should understand it.
   If the Push 3 replies, it proves your ports are set up correctly.

2. Required Set User Mode command:
   Tells the Push 3 to switch into custom control mode.
   Without this, your pad lights and incoming messages may not work correctly.

### The actual wire message to enable User Mode

`F0 00 21 1D 01 01 0A 01 F7`

| Bytes    | Meaning                 |
| -------- | ----------------------- |
| F0       | SysEx start             |
| 00 21 1D | Ableton manufacturer ID |
| 01 01    | Push 3 family/model ID  |
| 0A       | Command: Set User Mode  |
| 01       | Data: Enable            |
| F7       | SysEx end               |

### Code

```python
import time

def device_handshake(midi_in, midi_out):
    # 1) Optional: Universal Device Inquiry "Who are you?"
    midi_out.send(mido.Message('sysex', data=[0x7E, 0x7F, 0x06, 0x01]))
    time.sleep(0.3)  # short wait for response

    for msg in midi_in.iter_pending():
        if msg.type == 'sysex':
            print("Device inquiry response:", list(msg.data))

    # 2) Required: Set User Mode
    payload = MANUFACTURER_ID + DEVICE_ID + [CMD_SET_USER_MODE, USER_MODE_ENABLE]
    midi_out.send(mido.Message('sysex', data=payload))
    print("Push 3: User Mode enabled.")

# Run immediately after opening ports
device_handshake(midi_in, midi_out)
```

---

## 6) Light up a single pad

The bottom-left pad (note 36) is perfect for a test.

```python
# Turn the pad on
midi_out.send(mido.Message('note_on',  note=TEST_PAD_NOTE, velocity=TEST_VELOCITY, channel=0))

# Turn the pad off
midi_out.send(mido.Message('note_off', note=TEST_PAD_NOTE, velocity=0, channel=0))
```

If it does not light:

* Confirm you are on User ports (step 4).
* Confirm you ran `device_handshake()` first (step 5).

---

## 7) Log pad presses to the console

Once in User Mode, pads send `note_on` when pressed and `note_off` when released.

```python
import time

def listen_for_pads(midi_in):
    print("Listening for pad presses... Ctrl+C to stop.")
    try:
        while True:
            for msg in midi_in.iter_pending():
                if msg.type == "note_on":
                    print(f"PAD {msg.note} ON  vel={msg.velocity}")
                elif msg.type == "note_off":
                    print(f"PAD {msg.note} OFF vel={msg.velocity}")
            time.sleep(0.002)  # keep CPU usage low
    except KeyboardInterrupt:
        print("Stopped.")

listen_for_pads(midi_in)
```

Tip: If you want the grid position, note numbers increase left -> right, bottom -> top.
For note 36 as bottom-left:

```python
i = msg.note - 36
row = (i // 8) + 1  # 1 = bottom, 8 = top
col = (i % 8)  + 1  # 1 = left, 8 = right
print(f"Row {row}, Col {col}")
```

Integrated:

```python
def listen_for_pads(midi_in):
    print("Listening for pad presses... Ctrl+C to stop.")
    try:
        while True:
            for msg in midi_in.iter_pending():
                if msg.type in ("note_on", "note_off"):
                    i = msg.note - 36
                    row = (i // 8) + 1
                    col = (i % 8)  + 1
                    print(f"PAD Row {row} Col {col} ({msg.note}) {msg.type.upper()} vel={msg.velocity}")
            time.sleep(0.002)
    except KeyboardInterrupt:
        print("Stopped.")

listen_for_pads(midi_in)
```

---

## Troubleshooting

**Pad doesn't light:**

* Make sure you are on User ports (`print(mido.get_output_names())`).
* Confirm `device_handshake()` was run before trying to light pads.

**No messages when pressing pads:**

* Confirm the input port is opened correctly.
* Make sure no DAW (like Ableton Live) is blocking the port.

**Pad lights wrong color:**

* In User Mode, velocity controls brightness/color.
* Try different velocities like 20, 60, 100.

---

## Recap

1. Open both User MIDI ports (input and output).
2. Run `device_handshake()` -> sets User Mode.
3. Use `note_on`/`note_off` to light pads.
4. Listen on `midi_in` to log pad presses.

With these steps, you now have a two-way link:

* Python -> Push: Light pads and control LEDs.
* Push -> Python: Log pad presses in your script.