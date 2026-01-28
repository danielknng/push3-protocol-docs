# Documentation Overview

### Protocol Analysis

#### - Quickstart:

* **[Push 3 + Python - A Beginner's Quickstart](protocol-analysis/push3-python-quickstart.md)** - A quick guide to interact with the Push 3 for the first time.
* **[Push 2 vs Push 3 Protocol Comparison](protocol-analysis/push2-push3-protocol.md)** - Detailed compatibility analysis highlighting differences and nuances between both devices.

#### - More in-depth:

* **[Push 3 USB Display Protocol](protocol-analysis/push3-display-protocol.md)** - Full documentation of the USB framebuffer implementation specific to the Push 3.
* **[Push 2 vs Push 3 Pad Sensitivity Curve Protocol](protocol-analysis/push2-push3-curve-protocol.md)** - Explanation of how pad sensitivity curves are generated and how they differ between Push 2 and Push 3.

### Interface Mapping

* **[Button Mapping](interface-mapping/buttons.md)** - All 70+ buttons with CC values.
* **[Encoder Mapping](interface-mapping/encoders.md)** - 10 encoders with touch detection.

### Research Tools

* **[Research Tools](tools)** - Hardware testing and analysis scripts

  * `display_test.py` - USB display testing with included test image
  * `text_renderer.py` - Dynamic parameter display generation
  * `midi_monitor.py` - Real-time MIDI message monitoring and analysis
  * `midi_test.py` - LED control and MIDI functionality testing
