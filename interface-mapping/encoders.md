# Push 3 Encoder & Knob Mapping Reference

Complete mapping of all rotary encoders and knobs on the Push 3, including touch detection and directional control values.

## Main Parameter Encoders (8 encoders)

Eight touch-sensitive endless rotary encoders located above the main display, used for parameter control.

### Encoder Touch Detection

Each encoder sends a touch detection message when physically touched:

```python
ENCODER_TOUCH = {
    'ENCODER_1': {'cc': 0, 'velocity': 127},   # Touch detected
    'ENCODER_2': {'cc': 1, 'velocity': 127},
    'ENCODER_3': {'cc': 2, 'velocity': 127},
    'ENCODER_4': {'cc': 3, 'velocity': 127},
    'ENCODER_5': {'cc': 4, 'velocity': 127},
    'ENCODER_6': {'cc': 5, 'velocity': 127},
    'ENCODER_7': {'cc': 6, 'velocity': 127},
    'ENCODER_8': {'cc': 7, 'velocity': 127}
}
```

### Encoder Rotation Values

Each encoder sends rotation data with direction-specific velocities:

| Encoder | Touch CC | Rotation CC | Left Turn | Right Turn |
|---------|----------|-------------|-----------|------------|
| **1** | 0 | 71 | Velocity 127 | Velocity 1 |
| **2** | 1 | 72 | Velocity 127 | Velocity 1 |
| **3** | 2 | 73 | Velocity 127 | Velocity 1 |
| **4** | 3 | 74 | Velocity 127 | Velocity 1 |
| **5** | 4 | 75 | Velocity 127 | Velocity 1 |
| **6** | 5 | 76 | Velocity 127 | Velocity 1 |
| **7** | 6 | 77 | Velocity 127 | Velocity 1 |
| **8** | 7 | 78 | Velocity 127 | Velocity 1 |

### Usage Examples

```python
# Example: Encoder 1 touched
# MIDI: Control Change, Channel 1, CC 0, Velocity 127

# Example: Encoder 1 turned left (counter-clockwise)
# MIDI: Control Change, Channel 1, CC 71, Velocity 127

# Example: Encoder 1 turned right (clockwise)  
# MIDI: Control Change, Channel 1, CC 71, Velocity 1
```

## Volume Encoder

Dedicated volume control encoder located on the left side of the device.

| Function | CC Value | Left Turn | Right Turn | Touch |
|----------|----------|-----------|------------|-------|
| **Volume** | 79 | Velocity 127 | Velocity 1 | CC 8, Vel 127 |


### Encoder Press

| Function         | CC Value | Pressed | Released |
|------------------|---------|---------|----------|
| **Encoder Press**| 111     | 0       | 127      |

```python
VOLUME_ENCODER = {
    'touch': {'cc': 8, 'velocity': 127},
    'rotation': {'cc': 79, 'left': 127, 'right': 1}
}
```

## Swing & Tempo Encoder

Combined swing and tempo control encoder with dual functionality.

| Function | CC Value | Left Turn | Right Turn | Touch |
|----------|----------|-----------|------------|-------|
| **Swing/Tempo** | 14 | Velocity 127 | Velocity 1 | CC 10, Vel 127 |

```python
SWING_TEMPO_ENCODER = {
    'touch': {'cc': 10, 'velocity': 127},
    'rotation': {'cc': 14, 'left': 127, 'right': 1}
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

Vertical touch-sensitive strip on the left side for pitch bend and modulation.

| Function | CC Value | Notes |
|----------|----------|-------|
| **Touch Detection** | 12 | Velocity 127 when touched |
| **Position Up** | *TBD* | Under investigation |
| **Position Down** | *TBD* | Under investigation |

```python
TOUCH_STRIP = {
    'touch': {'cc': 12, 'velocity': 127},
    'position_up': 'TBD',      # Needs further analysis
    'position_down': 'TBD'     # Needs further analysis
}
```

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
