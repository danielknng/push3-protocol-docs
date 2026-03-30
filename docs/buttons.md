# Push 3 Button Mapping

All buttons send CC messages on MIDI channel 0. Velocity 127 = pressed, velocity 0 = released.

---

## Performance Pads

64 velocity-sensitive pads in an 8x8 grid, mapped as MIDI notes. Bottom-left is note 36, top-right is 99.

```python
PADS = {
    'ROW_1': [36, 37, 38, 39, 40, 41, 42, 43],  # bottom row
    'ROW_2': [44, 45, 46, 47, 48, 49, 50, 51],
    'ROW_3': [52, 53, 54, 55, 56, 57, 58, 59],
    'ROW_4': [60, 61, 62, 63, 64, 65, 66, 67],  # middle C row
    'ROW_5': [68, 69, 70, 71, 72, 73, 74, 75],
    'ROW_6': [76, 77, 78, 79, 80, 81, 82, 83],
    'ROW_7': [84, 85, 86, 87, 88, 89, 90, 91],
    'ROW_8': [92, 93, 94, 95, 96, 97, 98, 99],  # top row
}
```

---

## Display Buttons

Two rows of 8 buttons around the main display.

### Upper Row (above display)

| Button | CC |
|---|---|
| 1 | 20 |
| 2 | 21 |
| 3 | 22 |
| 4 | 23 |
| 5 | 24 |
| 6 | 25 |
| 7 | 26 |
| 8 | 27 |

### Lower Row (below display)

| Button | CC |
|---|---|
| 1 | 102 |
| 2 | 103 |
| 3 | 104 |
| 4 | 105 |
| 5 | 106 |
| 6 | 107 |
| 7 | 108 |
| 8 | 109 |

---

## Transport

| Button | CC |
|---|---|
| Play | 85 |
| Record | 86 |
| New | 92 |
| Duplicate | 88 |
| Fixed Length | 90 |
| Automate | 89 |
| Double Loop | 117 |
| Quantize | 116 |
| Delete | 118 |
| Undo | 119 |
| Convert | 35 |
| Capture MIDI | 65 |

---

## Navigation

| Button | CC |
|---|---|
| Up | 46 |
| Down | 47 |
| Left | 44 |
| Right | 45 |
| Center | 91 |
| Shift | 49 |
| Select | 48 |
| Octave Down | 54 |
| Octave Up | 55 |
| Page Left | 62 |
| Page Right | 63 |

---

## Jogwheel

| Control | CC |
|---|---|
| Left (counter-clockwise) | 93 |
| Right (clockwise) | 95 |
| Press | 94 |

---

## Mode & View

| Button | CC |
|---|---|
| Note | 50 |
| Session | 51 |
| Device | 110 |
| Mix | 112 |
| Clip | 113 |
| Browse | 111 |
| Add Effect | 52 |
| Add Track | 53 |
| Layout | 31 |
| Scale | 58 |
| User Mode | 59 |

---

## Performance

| Button | CC |
|---|---|
| Repeat | 56 |
| Accent | 57 |
| Tap Tempo | 3 |
| Metronome | 9 |

---

## Mixer

| Button | CC |
|---|---|
| Master Track | 28 |
| Stop Clip | 29 |
| Mute | 60 |
| Solo | 61 |
| Volume | 114 |
| Pan/Send | 115 |

---

## System

| Button | CC |
|---|---|
| Setup | 30 |
| Save | 82 |
| Learn | 81 |
| Sets | 80 |
| Lock | 83 |
| Swap | 33 |
| Add | 32 |

---

## Scene / Note Repeat Buttons

These 8 buttons on the right edge have dual function depending on context:
- In Session view: Scene launch (Scene 1-8)
- In Note Repeat mode: Repeat rate selection

| Button | CC | Note Repeat Rate |
|---|---|---|
| Scene 1 / 1/4 | 36 | Quarter note |
| Scene 2 / 1/4t | 37 | Quarter note triplet |
| Scene 3 / 1/8 | 38 | 8th note |
| Scene 4 / 1/8t | 39 | 8th note triplet |
| Scene 5 / 1/16 | 40 | 16th note |
| Scene 6 / 1/16t | 41 | 16th note triplet |
| Scene 7 / 1/32 | 42 | 32nd note |
| Scene 8 / 1/32t | 43 | 32nd note triplet |

---

## Footswitches

External footswitch inputs. Send CC when connected and activated.

| Input | CC |
|---|---|
| Footswitch 1 | 64 |
| Footswitch 2 | 69 |
