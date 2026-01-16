```markdown
# Energy-Aware Transport Protocol (Research PoC)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Status](https://img.shields.io/badge/Status-Research_Prototype-orange)

## Abstract
This project implements a Proof-of-Concept (PoC) for a novel **Energy-Efficient Transport Protocol** designed for battery-constrained IoT devices.

Standard protocols like UDP and CoAP impose significant overhead ("Header Tax") and inefficient radio duty cycles on small sensor payloads. This research proposes a **context-aware transport layer** that dynamically aggregates packets and adapts transmission behavior based on the device's remaining energy budget.

## Research Goals
1.  **Reduce Protocol Overhead:** Minimize the ratio of header bytes to payload bytes via packet aggregation.
2.  **Optimize Radio Duty Cycle:** Reduce energy-expensive radio state transitions (Sleep to Wake) by buffering data.
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
* **Budget (1 byte):** A value from `0-255` representing the device's energy status (mapped from 0-100% battery).
* **Payload:** Contains one or multiple sensor readings separated by a delimiter.

## Adaptive Aggregation Logic

The core innovation of this protocol is the **Energy-Aware Aggregation Threshold**. The sender monitors its own battery state and adjusts the transmission strategy dynamically.

| Battery Level | Operational Mode | Aggregation Threshold | Latency | Energy Efficiency |
| --- | --- | --- | --- | --- |
| **> 70%** | Real-Time | 1 item (Immediate) | Low | Low |
| **30% - 70%** | Balanced | 5 items | Medium | Medium |
| **< 30%** | Survival | 10 items | High | Maximum |

*In "Survival Mode", the device deliberately sacrifices data freshness to minimize radio wake-up events, extending operational life.*

## Getting Started

### Prerequisites

* Python 3.8+
* Standard libraries only (`socket`, `struct`, `threading`).

### Installation

Clone the repository:

```bash
git clone [https://github.com/yourusername/energy-proto-research.git](https://github.com/yourusername/energy-proto-research.git)
cd energy-proto-research

```

### Running the Simulation

The project is modularized. Run the `main.py` entry point to start the Receiver and Sender threads automatically.

```bash
python main.py

```

The simulation will cycle through three phases (High, Medium, and Critical battery) to demonstrate the changing aggregation behavior in the console output.

## Project Structure

* **main.py:** The experiment orchestrator. Starts the sender and receiver threads and simulates battery drain.
* **sender.py:** Contains the `EnergyProtocolSender` class with the adaptive buffering logic.
* **receiver.py:** Contains the `EnergyProtocolReceiver` class for parsing packets and logging metrics.
* **utils.py:** Shared configuration, constants, and the `Packet` class for binary packing/unpacking.
* **results/:** Directory for generated CSV logs (ignored by git).

## Methodology & Metrics

To evaluate the efficacy of this protocol, future experiments will compare it against a standard UDP baseline using:

1. **Goodput Ratio:** Payload Bytes / Total Bytes Transmitted.
2. **Energy Estimate:** Calculated based on the number of TX events saved via aggregation.
3. **Packet Delivery Ratio:** Reliability under simulated network loss.
