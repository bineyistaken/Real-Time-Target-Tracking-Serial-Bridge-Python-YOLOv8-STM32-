---

# Real-Time Visual Target Tracking & Serial Bridge (Python to STM32)

A real-time optical target tracking interface and telemetry bridge designed to compute frame-relative target deviations and stream framed serial packets to an **STM32** microcontroller over UART.

This module serves as the primary vision-to-actuation link for closed-loop gimbal stabilization, optical tracking, and autonomous UAV mission payloads.

---

## Overview

The pipeline captures frames via OpenCV, computes relative Cartesian errors (ΔX, ΔY) between the optical center and the target coordinate, frames the payload using start/stop delimiters, and transmits the vector downstream to an embedded target at 115200 baud. The interface also supports bidirectional logging to capture response telemetry streamed back from the STM32.

### Key Capabilities

* **Packet Framing Protocol:** Delimited payload format (`<X,Y>\n`) preventing buffer desynchronization on the microcontroller UART parser.
* **Full-Duplex Serial Verification:** Concurrent transmission of error vectors and reception of microcontroller ACK/status strings.
* **Closed-Loop Error Calculation:** Continuous tracking of signed pixel displacement relative to the frame center (W/2, H/2).
* **Interactive HIL Calibration:** Real-time mouse callback interrupts to reposition the target for hardware-in-the-loop latency testing.

---

## System Architecture

```
[ Camera Stream (640x480) ]
             │
             ▼
[ Frame Center (X:320, Y:240) ] ──► [ Compute Delta: (dx, dy) ]
                                                  │
                                                  ▼
                                      [ Frame Packet: <dx,dy>\n ]
                                                  │
                                       (UART @ 115200 Baud)
                                                  ▼
                                      [ STM32 Microcontroller ]
                                                  │
                                        (Actuation / Servos)

```

---

## Packet Structure

Telemetry is formatted as plain ASCII with explicit start and termination markers to enable robust hardware UART interrupt (IDLE / RXNE) handling on embedded targets:

| Field | Marker / Sample | Function |
| --- | --- | --- |
| **Start Byte** | `<` | Frame synchronization marker |
| **Payload** | `-120,45` | Comma-separated signed pixel error (ΔX, ΔY) |
| **Stop Byte** | `>` | End of numeric coordinate sequence |
| **Terminator** | `\n` | Buffer flush and newline trigger |

*Example Frame:* `<-85,42>\n` denotes an object located 85 pixels to the left and 42 pixels below the optical center.

---

## Getting Started

### Prerequisites

Install the required Python dependencies:

```
pip install opencv-python pyserial

```

### Hardware Connection

1. Connect the host machine to the STM32 board via USB-UART bridge or VCP.
2. Cross the communication lines:
* **Host TX** -> **STM32 RX**
* **Host RX** <- **STM32 TX**
* **GND** <-> **GND**


3. Configure the STM32 UART peripheral for **115200 Baud, 8 Data Bits, 1 Stop Bit, No Parity**.

### Execution

Run the tracking bridge script:

```
python target_tracker_bridge.py

```

* **Left Click:** Place tracking crosshairs at any coordinate on the video stream.
* **Q:** Terminate video capture, close the serial handle, and release resources.
