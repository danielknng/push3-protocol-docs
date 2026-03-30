# Push 3 Encoder & Knob Mapping

---

## Rotation Value Encoding

All encoders use 7-bit two's complement for relative movement:

- Right (clockwise): values 1-63 - higher = faster turn
- Left (counter-clockwise): values 64-127 - lower = faster turn (127 = slowest left)

One full 360° turn sends approximately 210 steps, except the Swing/Tempo encoder which is detented at 18 steps per turn.

```python
def decode_encoder(value: int) -> float:
    # Returns relative change: positive = right, negative = left
    if value <= 63:
        return value        # right turn
    else:
        return value - 128  # left turn (two's complement)
```

---

## Main Parameter Encoders

Eight touch-sensitive encoders above the display. Touch is sent as `note_on` on channel 0.

| Encoder | Rotation CC | Touch CC |
|---|---|---|
| 1 | 71 | 0 |
| 2 | 72 | 1 |
| 3 | 73 | 2 |
| 4 | 74 | 3 |
| 5 | 75 | 4 |
| 6 | 76 | 5 |
| 7 | 77 | 6 |
| 8 | 78 | 7 |

```python
ENCODERS = {
    i + 1: {'rotation_cc': 71 + i, 'touch_cc': i}
    for i in range(8)
}
```

## Small Knob 1 - Tempo / Swing

Controls tempo by default. Press to toggle between Tempo and Swing mode.

```python
SMALL_KNOB_1 = {
    'rotation': {'cc': 14},   # left: 127, right: 1
    'touch':    {'cc': 10, 'velocity': 127},
    'press':    {'cc': 15},   # toggles Tempo <-> Swing mode
}
```

Note: CC 15 is shared between this press and Small Knob 2 rotation - see below.

---

## Small Knob 2 - Play Position (Push 3 only)

Controls the play cursor position. Press to switch to loop start control.

```python
SMALL_KNOB_2 = {
    'rotation': {'cc': 15},   # left: 127, right: 1 - shared with Small Knob 1 press
    'touch':    {'cc': 9, 'velocity': 127},
}
```

---

## Knob 9 - Master Volume

Rightmost encoder, controls master volume. On Push 3, pressing Browse (CC 111) toggles between master volume and cue mix volume.

```python
KNOB_9 = {
    'rotation': {'cc': 79},   # left: 127, right: 1
    'touch':    {'cc': 8, 'velocity': 127},
}
```

## Jog Wheel (Navigation Control)

Large navigation wheel on the right side with multiple interaction modes.

### Scroll Function
Continuous rotation for menu navigation and parameter scrolling:

| Direction | CC Value | Velocity |
|-----------|----------|----------|
| **Left** | 70 | 127 |
| **Right** | 70 | 1 |

### Nudge Function  
Discrete steps for precise positioning:

| Direction | CC Value |
|-----------|----------|
| **Left** | 93 |
| **Right** | 95 |

### Press Function
Center press for selection/enter:

| Action | CC Value |
|--------|----------|
| **Press (Enter)** | 94 |

### Touch Detection
Touch sensing for the jog wheel surface:

| Action | CC Value | Velocity |
|--------|----------|----------|
| **Touch** | 11 | 127 |

```python
JOG_WHEEL = {
    'scroll': {'cc': 70, 'left': 127, 'right': 1},
    'nudge_left': {'cc': 93},
    'nudge_right': {'cc': 95},
    'press': {'cc': 94},
    'touch': {'cc': 11, 'velocity': 127}
}
```

## Touch Strip

Vertical touch-sensitive strip on the left side. Touch detection arrives as CC 12, position as a standard pitchbend message on channel 0.

```python
TOUCH_STRIP = {
    'touch': {'cc': 12, 'velocity': 127},
    'position': 'pitchbend channel 0',  # standard MIDI pitchbend, 0..16383
}
```

For mode configuration (pitchbend, volume, pan, discrete) and SysEx details, see [push3-extensions.md](push3-extensions.md#touch-strip).

## Encoder Behavior Patterns

### Touch-First Interaction
Most encoders follow this pattern:
1. Touch detected (Touch CC sent with velocity 127)
2. Rotation begins (Rotation CC sent with direction-specific velocity)
3. Touch released (no specific message, inferred from lack of rotation)

### Velocity Direction Encoding
- **Left/Counter-clockwise**: Velocity 127
- **Right/Clockwise**: Velocity 1
- This binary encoding allows simple direction detection

### Continuous vs. Discrete
- **Parameter Encoders**: Continuous rotation, relative values
- **Jog Wheel**: Both continuous (scroll) and discrete (nudge) modes
- **Volume/Tempo**: Continuous rotation with wide range

## Technical Notes

### MIDI Implementation
- All encoders send CC messages on MIDI Channel 1
- Touch detection always uses velocity 127
- No release messages for touch events
- Rotation speed affects message frequency, not velocity values

### Debouncing
- Hardware implements natural debouncing
- No software debouncing required for normal use
- High-speed rotation may require rate limiting

### Encoder Resolution
- Each encoder detent typically sends 1-2 MIDI messages
- Resolution is hardware-dependent and consistent
- Fine control possible with slow movements

## Usage Recommendations

### Parameter Control
```python
# Typical parameter control implementation
if cc_number in range(71, 79):  # Encoders 1-8
    encoder_num = cc_number - 70
    if velocity == 127:
        parameter_decrease(encoder_num)
    elif velocity == 1:
        parameter_increase(encoder_num)
```

### Touch-Sensitive Features
```python
# Enable touch-sensitive parameter changes
if cc_number in range(0, 8):  # Touch detection
    encoder_touched[cc_number] = True
    enable_fine_mode(cc_number)
```
