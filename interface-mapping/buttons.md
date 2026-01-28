# Push 3 Button Mapping Reference

Complete mapping of all Push 3 buttons with their corresponding MIDI CC values, organized by functional groups.

## Performance Pads (64 pads, 8×8 grid)

The main performance surface consists of 64 velocity-sensitive pads arranged in an 8×8 grid. Notes are mapped chromatically from bottom-left to top-right.

```python
# Pad Layout (MIDI Note Numbers)
PADS = {
    'ROW_1': [36, 37, 38, 39, 40, 41, 42, 43],  # Bottom row
    'ROW_2': [44, 45, 46, 47, 48, 49, 50, 51],
    'ROW_3': [52, 53, 54, 55, 56, 57, 58, 59],
    'ROW_4': [60, 61, 62, 63, 64, 65, 66, 67],  # Middle C row
    'ROW_5': [68, 69, 70, 71, 72, 73, 74, 75],
    'ROW_6': [76, 77, 78, 79, 80, 81, 82, 83],
    'ROW_7': [84, 85, 86, 87, 88, 89, 90, 91],
    'ROW_8': [92, 93, 94, 95, 96, 97, 98, 99]   # Top row
}
```

## Transport Controls

Essential playback and recording controls located on the left side of the device.

| Button | CC Value | Function |
|--------|----------|----------|
| **Play** | 85 | Start/stop playback |
| **Record** | 86 | Record arm/start recording |
| **Stop** | 29 | Stop playback |
| **Capture** | 65 | Capture MIDI/audio |

## Production Controls

Core production tools for sequencing and editing.

| Button | CC Value | Function |
|--------|----------|----------|
| **New** | 92 | Create new clip/pattern |
| **Automate** | 89 | Toggle automation recording |
| **Fixed Length** | 90 | Set fixed loop length |
| **Quantize** | 116 | Quantize recorded material |
| **Duplicate** | 88 | Duplicate current selection |
| **Delete** | 118 | Delete selection |
| **Double Loop** | 117 | Double current loop length |
| **Convert** | 35 | Convert audio to MIDI |

## Musical Controls

Tools for controlling musical parameters and timing.

| Button | CC Value | Function |
|--------|----------|----------|
| **Repeat** | 56 | Note repeat function |
| **Accent** | 57 | Accent velocity |
| **Scale** | 58 | Scale mode |
| **Layout** | 31 | Pad layout selection |
| **Note** | 50 | Note mode |
| **Session** | 51 | Session view mode |

## Timing & Metronome

Tempo and timing controls.

| Button | CC Value | Function |
|--------|----------|----------|
| **Metronome** | 9 | Toggle metronome |
| **Tap Tempo** | 3 | Tap tempo input |

## System Controls

File management and system functions.

| Button | CC Value | Function |
|--------|----------|----------|
| **Save** | 82 | Save current project |
| **Undo** | 119 | Undo last action |
| **Sets** | 80 | Project/set management |
| **Setup** | 30 | Device setup menu |
| **Learn** | 81 | MIDI learn mode |
| **User Mode** | 59 | User-defined mode |

## Track Controls

Individual track and channel controls.

| Button | CC Value | Function |
|--------|----------|----------|
| **Mute** | 60 | Mute current track |
| **Solo** | 61 | Solo current track |
| **Lock** | 83 | Lock track from changes |

## Display Controls

Buttons surrounding the main display for menu navigation.

### Upper Display Buttons (8 buttons)
| Position | CC Value | Typical Function |
|----------|----------|-----------------|
| **1** | 102 | Display menu option 1 |
| **2** | 103 | Display menu option 2 |
| **3** | 104 | Display menu option 3 |
| **4** | 105 | Display menu option 4 |
| **5** | 106 | Display menu option 5 |
| **6** | 107 | Display menu option 6 |
| **7** | 108 | Display menu option 7 |
| **8** | 109 | Display menu option 8 |

### Lower Display Buttons (8 buttons)
| Position | CC Value | Typical Function |
|----------|----------|-----------------|
| **1** | 20 | Parameter control 1 |
| **2** | 21 | Parameter control 2 |
| **3** | 22 | Parameter control 3 |
| **4** | 23 | Parameter control 4 |
| **5** | 24 | Parameter control 5 |
| **6** | 25 | Parameter control 6 |
| **7** | 26 | Parameter control 7 |
| **8** | 27 | Parameter control 8 |

## Mode Selection

Main mode buttons on the right side.

| Button | CC Value | Function |
|--------|----------|----------|
| **Device** | 110 | Device control mode |
| **Mix** | 112 | Mixer mode |
| **Clip** | 113 | Clip detail mode |
| **Session** | 34 | Session overview |

## Utility Controls

Additional control functions.

| Button | CC Value | Function |
|--------|----------|----------|
| **Add** | 32 | Add track/device |
| **Swap** | 33 | Swap track order |
| **Master Track** | 28 | Select master track |

## Navigation Controls

Transport and navigation controls.

| Button | CC Value | Function |
|--------|----------|----------|
| **Shift** | 49 | Modifier key |
| **Select** | 48 | Selection mode |
| **Octave Down** | 54 | Lower octave |
| **Octave Up** | 55 | Raise octave |
| **Page Left** | 62 | Navigate left |
| **Page Right** | 63 | Navigate right |

## Session Navigation D-Pad

5-way directional control for session navigation.

| Direction | CC Value | Function |
|-----------|----------|----------|
| **Up** | 46 | Navigate up |
| **Down** | 47 | Navigate down |
| **Left** | 44 | Navigate left |
| **Right** | 45 | Navigate right |
| **Center** | 91 | Select/enter |

## Scene & Repeat Controls

Performance and scene launch controls on the right edge.

| Button | CC Value | Function |
|--------|----------|----------|
| **1/32t** | 43 | 32nd note triplet repeat |
| **1/32** | 42 | 32nd note repeat |
| **1/16t** | 41 | 16th note triplet repeat |
| **1/16** | 40 | 16th note repeat |
| **1/8t** | 39 | 8th note triplet repeat |
| **1/8** | 38 | 8th note repeat |
| **1/4t** | 37 | Quarter note triplet repeat |
| **1/4** | 36 | Quarter note repeat |

## Notes

- All CC values are sent on MIDI channel 1 unless otherwise specified
- Button state: Velocity 127 = pressed, Velocity 0 = released
- Some buttons may have different functions depending on current mode
- LED feedback available for most buttons via MIDI commands
- Touch-sensitive controls send additional touch detection messages
