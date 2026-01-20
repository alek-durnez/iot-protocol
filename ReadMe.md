# Secure & Energy-Aware Transport Protocol

## Abstract

This project implements a Proof-of-Concept (PoC) for a **Secure, Energy-Efficient Transport Protocol** designed for battery-constrained IoT devices.

Standard protocols like UDP provide no security or reliability, while TCP/TLS is often too heavy (handshake overhead) for duty-cycled radios. This research proposes a **context-aware transport layer** that combines:

1. **Smart Aggregation:** Dynamically buffering packets based on battery life.
2. **Binary Packing:** Reducing payload size using `struct` packing instead of JSON/Text.
3. **Lightweight Security:** Implementing **AES-GCM** (Authenticated Encryption) to ensure confidentiality and integrity without a full TLS handshake.

## Research Goals

1. **Reduce Protocol Overhead:** Minimize the ratio of header bytes to payload bytes via packet aggregation and binary compression.
2. **Ensure Data Integrity:** Prevent spoofing and tampering using Authenticated Encryption (AEAD).
3. **Optimize Radio Duty Cycle:** Reduce energy-expensive radio state transitions (Sleep to Wake) by buffering data.
4. **Adaptive Reliability:** Implement an energy-aware Automatic Repeat Request (ARQ) mechanism that stops retrying when the battery is critical.

## Protocol Specification

The protocol operates over UDP but implements a custom binary header and an encrypted payload structure.

### Packet Structure

Total Packet Size = `Header (6B)` + `Nonce (12B)` + `Ciphertext (Variable)` + `Auth Tag (16B)`

```text
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        Sequence Number (32)                   |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |   Flags (8)   |   Budget (8)  |          Nonce (96) ...
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 ... Nonce (cont)                |      Encrypted Payload ...
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

```

* **Header (Cleartext):**
* **Sequence Number (4 bytes):** Used for ordering and matching ACKs.
* **Flags (1 byte):** `0x01` (Aggregated), `0x02` (ACK).
* **Budget (1 byte):** Device battery status (0-100%).


* **Security Layer:**
* **Nonce (12 bytes):** Random value generated per packet to prevent Replay Attacks.
* **Encrypted Payload:** The sensor data, packed in binary and encrypted with AES-256.



## Security Architecture

Security is often ignored in lightweight protocols. This project implements **AES-GCM (Galois/Counter Mode)**, a modern Authenticated Encryption standard.

| Feature | Implementation | Benefit |
| --- | --- | --- |
| **Confidentiality** | AES-256 | An attacker capturing packets cannot read the sensor data. |
| **Integrity** | GCM Auth Tag | Any tampering with the ciphertext causes the Receiver to drop the packet immediately. |
| **Anti-Replay** | Unique Nonce | Capturing a valid packet and sending it again later will fail decryption/logic checks. |

## Adaptive Logic (The Core Innovation)

The sender monitors its own battery state and adjusts the aggregation threshold and reliability policy dynamically.

| Battery Level | Operational Mode | Aggregation Threshold | Reliability Policy |
| --- | --- | --- | --- |
| **> 70%** | Real-Time | 1 item (Immediate) | **High (3 Retries)** |
| **30% - 70%** | Balanced | 5 items | **Medium (1 Retry)** |
| **< 30%** | Survival | 10 items | **None (0 Retries)** |

*In "Survival Mode", the device deliberately sacrifices data freshness to minimize radio wake-up events.*

## Getting Started

### Prerequisites

* Python 3.10+
* `cryptography` (For AES-GCM)
* `aiocoap` (For competitor benchmark)

```bash
pip install cryptography aiocoap matplotlib

```

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/energy-aware-transport.git
cd energy-aware-transport

```

### Running the Benchmark

The project is configured as a Head-to-Head benchmark. Run `main.py` to start the comparison between the **Secure Smart Protocol** and **Standard CoAP**.

```bash
python main.py

```

## Methodology & Results

The benchmark compares:

1. **Standard CoAP:** Sending JSON/Text data (high overhead).
2. **Smart Protocol:** Sending Binary Encrypted data (low overhead + security).

**Result:** Even with the added overhead of Encryption (Nonce + Tag), the Smart Protocol achieves **~80% energy savings** compared to standard CoAP due to aggressive packet aggregation and binary packing.

## Project Structure

* **`main.py`**: The experiment orchestrator.
* **`sender.py`**: Implements Adaptive Logic, Binary Packing, and Encryption.
* **`receiver.py`**: Validates Integrity, Decrypts, and Unpacks data.
* **`utils.py`**: Shared constants, Packet definitions, and Crypto wrappers.
* **`coap_competitor.py`**: The baseline implementation.
* **`results/`**: Directory for generated logs.