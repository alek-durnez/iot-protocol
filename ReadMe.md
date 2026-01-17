# Energy-Aware Transport Protocol (Research PoC)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Status](https://img.shields.io/badge/Status-Research_Prototype-orange)

## Abstract

This project implements a Proof-of-Concept (PoC) for a novel **Energy-Efficient Transport Protocol** designed for battery-constrained IoT devices.

Standard protocols like UDP and CoAP impose significant overhead ("Header Tax") and provide no reliability guarantees, while TCP is too heavy for duty-cycled radios. This research proposes a **context-aware transport layer** that dynamically aggregates packets and adapts both transmission behavior and reliability guarantees (ARQ) based on the device's remaining energy budget.

## Research Goals

1.  **Reduce Protocol Overhead:** Minimize the ratio of header bytes to payload bytes via packet aggregation.
2.  **Optimize Radio Duty Cycle:** Reduce energy-expensive radio state transitions (Sleep to Wake) by buffering data.
3.  **Adaptive Reliability:** Implement an energy-aware Automatic Repeat Request (ARQ) mechanism that stops retrying when the battery is critical.
4.  **Extend Network Lifetime:** Introduce "Graceful Degradation" where nodes sacrifice latency and reliability for longevity.

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

* **Sequence Number (4 bytes):** Used for ordering and matching ACKs to requests.
* **Flags (1 byte):** Bitmask for protocol state.
* `0x01`: Aggregated Payload.
* `0x02`: ACK Packet.


* **Budget (1 byte):** A value from `0-255` representing the device's energy status (mapped from 0-100% battery).
* **Payload:** Contains one or multiple sensor readings separated by a delimiter.

## Adaptive Logic (The Core Innovation)

The core innovation of this protocol is the **Energy-Aware State Machine**. The sender monitors its own battery state and adjusts the aggregation threshold and reliability policy dynamically.

| Battery Level | Operational Mode | Aggregation Threshold | Reliability Policy | Energy Efficiency |
| --- | --- | --- | --- | --- |
| **> 70%** | Real-Time | 1 item (Immediate) | **High (3 Retries)** | Low |
| **30% - 70%** | Balanced | 5 items | **Medium (1 Retry)** | Medium |
| **< 30%** | Survival | 10 items | **None (0 Retries)** | Maximum |

*In "Survival Mode", the device deliberately sacrifices data freshness and reliability to minimize radio wake-up events.*

## Network Chaos Simulation

To validate the reliability logic, `utils.py` includes a **Packet Loss Simulator**.
By default, there is a **20% chance** that any transmitted packet is "dropped" (ignored) by the code to simulate a poor wireless environment. This forces the Sender to demonstrate its Retry/Timeout logic visible in the console logs.

## Getting Started

### Prerequisites

* Python 3.8+
* Standard libraries only (`socket`, `struct`, `threading`, `random`, `csv`).

### Installation

Clone the repository:

```bash
git clone [https://gitlab.com/Alekdurnez/iot-protocol.git](https://gitlab.com/Alekdurnez/iot-protocol.git)
cd iot-protocol

```

### Running the Simulation

The project is modularized. Run the `main.py` entry point to start the Receiver, Sender, and Battery Drain Simulation.

```bash
python main.py

```

The simulation will cycle through three phases (High, Medium, and Critical battery). You should observe:

* `[TX SUCCESS]`: Packet arrived and was acknowledged.
* `!!! Timeout ... Retrying`: The Network Simulator dropped a packet, and the sender is fighting to deliver it.
* `[TX FAILED]`: The sender gave up on a packet because the battery was too low to justify another retry.

## Project Structure

* **main.py:** The experiment orchestrator. Starts the sender and receiver threads and simulates battery drain.
* **sender.py:** Implements the Adaptive Logic, Buffering, and Stop-and-Wait ARQ with Backoff.
* **receiver.py:** Listens for packets and immediately responds with ACKs.
* **utils.py:** Shared constants, Packet class, and **Network Loss Simulator**.
* **results/:** Directory for generated CSV logs (ignored by git).

## Methodology & Metrics

To evaluate the efficacy of this protocol, the system logs every event to `results/experiment_log.csv`. Future experiments will compare it against a standard UDP baseline using:

1. **Network Efficiency:** (Useful Payload Bytes) / (Total Bytes on Wire including Retries).
2. **Energy Estimate:** Calculated based on the number of TX events (First attempts + Retries).
3. **Reliability Cost:** The energy "penalty" paid to guarantee delivery in high-battery modes.
