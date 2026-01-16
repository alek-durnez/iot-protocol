```markdown
# Energy-Aware Transport Protocol (Research PoC)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Status](https://img.shields.io/badge/Status-Research_Prototype-orange)

## Abstract
This project implements a Proof-of-Concept (PoC) for a novel **Energy-Efficient Transport Protocol** designed for battery-constrained IoT devices.

Standard protocols like UDP and CoAP impose significant overhead ("Header Tax") and inefficient radio duty cycles on small sensor payloads. This research proposes a **context-aware transport layer** that dynamically aggregates packets and adapts transmission behavior based on the device's remaining energy budget.

## Research Goals
1.  **Reduce Protocol Overhead:** Minimize the ratio of header bytes to payload bytes via packet aggregation.
2.  **Optimize Radio Duty Cycle:** Reduce energy-expensive radio state transitions (Sleep <-> Wake) by buffering data.
3.  **Extend Network Lifetime:** Introduce "Graceful Degradation" where nodes sacrifice latency for longevity when the battery is critical.

## Protocol Specification

The protocol operates over UDP but implements a custom lightweight header to facilitate energy awareness.

### Header Structure (6 Bytes)
Unlike standard TCP (20+ bytes), this header is stripped down to the bare minimum required for sequenced, state-aware delivery.

```text
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        Sequence Number (32)                   |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |   Flags (8)   |   Budget (8)  |      Payload (Variable) ...
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

```

* **Sequence Number (4 bytes):** Used for ordering and detecting packet loss.
* **Flags (1 byte):** Indicates compression status or aggregation type.
* **Budget (1 byte):** A value from `0-255` representing the device's energy status (mapped from 0-100% battery). The receiver uses this to log network health.

## Getting Started

### Prerequisites

* Python 3.8+
* Standard libraries only (`socket`, `struct`, `threading`) for the core protocol.
* *(Optional)* `matplotlib` for plotting results.

### Installation

Clone the repository:

```bash
git clone [https://github.com/yourusername/energy-proto-research.git](https://github.com/yourusername/energy-proto-research.git)
cd energy-proto-research

```

### Running the Demo

The main script runs both the Sender and Receiver locally for demonstration purposes.

```bash
python energy_proto.py

```

You will see output indicating packet transmission, the mapped energy budget, and the receiver parsing the custom header.

## Methodology & Metrics

To evaluate the efficacy of this protocol, we compare it against a standard UDP baseline using the following metrics:

1. **Goodput Ratio:** Payload Bytes / Total Bytes Transmitted
2. **Energy Estimate (E_est):** Calculated using a simplified radio model:



*Where aggregation reduces N_tx (transmission events).*
3. **Packet Delivery Ratio (PDR):** Percentage of successfully received packets under simulated lossy conditions.

## Project Structure

```text
.
├── energy_proto.py    # Main PoC implementation (Sender & Receiver classes)
├── results/           # CSV logs generated during experiments (ignored by git)
├── README.md          # Project documentation
└── .gitignore         # Git configuration

```

## Future Work

* Implement adaptive aggregation window (buffer time) based on the `Budget` byte.
* Add a chaotic network simulator (packet loss/delay) to test robustness.
* Compare results against CoAP/MQTT-SN.
