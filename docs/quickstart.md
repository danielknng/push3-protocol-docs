# Push 3 + Python Quickstart

Get a two-way connection between Python and the Push 3: open ports, enter User Mode, light a pad, log pad presses.

---

## Requirements

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install mido python-rtmidi
```

Close Ableton Live before testing - it will grab the ports.

---

## How Push 3 MIDI works

Push 3 is a standard MIDI device. It sends `note_on`/`note_off` when you press pads and CC messages for buttons and encoders. It receives MIDI to light LEDs.

Two port directions:
- Push -> Python: pad presses arrive on `midi_in`
- Python -> Push: LED commands go out on `midi_out`

Use the **User** port, not the Live port. The Live port is reserved for Ableton Live.

Without **User Mode**, pad lighting and incoming messages behave inconsistently. Enable it first, every time.

---

## Constants

```python
MANUFACTURER_ID   = [0x00, 0x21, 0x1D]  # Ableton
DEVICE_ID         = [0x01, 0x01]         # Push 3 family/model
CMD_SET_USER_MODE = 0x0A
USER_MODE_ENABLE  = 0x01

TEST_PAD_NOTE = 36   # bottom-left pad
TEST_VELOCITY = 100  # controls brightness/color in User Mode
```

---

## 1. Open ports

```python
import mido

def find_push3_ports():
    ins  = mido.get_input_names()
    outs = mido.get_output_names()

    user_in  = next((n for n in ins  if 'User' in n), None)
    user_out = next((n for n in outs if 'User' in n), None)

    # fall back to any Push 3 port if User port not found
    push_in  = user_in  or next((n for n in ins  if 'Ableton Push 3' in n), None)
    push_out = user_out or next((n for n in outs if 'Ableton Push 3' in n), None)

    if not push_in or not push_out:
        raise RuntimeError('Push 3 MIDI ports not found. Check USB.')
    return push_in, push_out

in_name, out_name = find_push3_ports()
midi_in  = mido.open_input(in_name)
midi_out = mido.open_output(out_name)
```

---

## 2. Enter User Mode

SysEx wire message: `F0 00 21 1D 01 01 0A 01 F7`

| Bytes | Meaning |
|---|---|
| `F0` | SysEx start |
| `00 21 1D` | Ableton manufacturer ID |
| `01 01` | Push 3 family/model |
| `0A` | Set User Mode |
| `01` | Enable |
| `F7` | SysEx end |

```python
import time

def enter_user_mode(midi_out):
    payload = MANUFACTURER_ID + DEVICE_ID + [CMD_SET_USER_MODE, USER_MODE_ENABLE]
    midi_out.send(mido.Message('sysex', data=payload))
    time.sleep(0.1)

enter_user_mode(midi_out)
```

Optional: send a universal device inquiry first (`F0 7E 7F 06 01 F7`) to confirm the ports are working. Push 3 will reply with its identity.

---

## 3. Light a pad

```python
midi_out.send(mido.Message('note_on',  note=TEST_PAD_NOTE, velocity=TEST_VELOCITY, channel=0))
midi_out.send(mido.Message('note_off', note=TEST_PAD_NOTE, velocity=0,             channel=0))
```

If nothing lights up: confirm you are on User ports and that `enter_user_mode()` ran first.

---

## 4. Log pad presses

```python
def listen(midi_in):
    print('Listening... Ctrl+C to stop.')
    try:
        while True:
            for msg in midi_in.iter_pending():
                if msg.type in ('note_on', 'note_off'):
                    i   = msg.note - 36
                    row = (i // 8) + 1  # 1 = bottom
                    col = (i % 8)  + 1  # 1 = left
                    print(f'Row {row} Col {col} ({msg.note}) {msg.type} vel={msg.velocity}')
            time.sleep(0.002)
    except KeyboardInterrupt:
        print('Stopped.')

listen(midi_in)
```

Note numbers run left-to-right, bottom-to-top. Bottom-left is 36, top-right is 99.

---

## Troubleshooting

<details>
<summary>Push 2 compatibility</summary>

Push 2 and Push 3 share the same manufacturer ID (`00 21 1D`), device family (`01 01`), SysEx format, pad note numbers, and encoder CC values. Most MIDI code written for Push 2 works on Push 3 unchanged.

</details>

- Pad doesn't light: wrong port, or User Mode not set.
- No pad presses: input port not open, or DAW is blocking it.
- Wrong color: velocity controls color in User Mode. Try values 20, 60, 100.

