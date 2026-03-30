# push3-protocol-docs

Reverse-engineered protocol documentation for the Ableton Push 3. Ableton publishes no official API - this covers the USB display protocol, MIDI mapping, pad sensitivity curves, SysEx commands, MPE, and audio interface configuration.

---

## Docs

- [Quickstart](docs/quickstart.md) - open ports, enter User Mode, light a pad, log presses
- [Display Protocol](docs/display-protocol.md) - USB framebuffer, encryption, image prep, sending frames
- [Button Mapping](docs/buttons.md) - all 70+ buttons with CC values
- [Encoder Mapping](docs/encoders.md) - 10 encoders, touch detection, rotation values, touch strip
- [SysEx Protocol](docs/sysex.md) - pad sensitivity curves, MPE, touch strip modes, audio interface

## Tools

Research and testing scripts in [tools/](tools/). Requires `pyusb`, `pillow`, `mido`, `python-rtmidi`.

- `display_test.py` - push an image to the display
- `text_renderer.py` - generate display frames with text
- `midi_monitor.py` - log incoming MIDI in real time
- `midi_test.py` - test LED output and SysEx

See [tools/README.md](tools/README.md) for setup and usage.

Cheers.

---

Push 2 information references [DrivenByMoss](https://github.com/git-moss/DrivenByMoss) and Ableton's official Push 2 documentation.
