import asyncio
import threading
import time
import os
import struct  # Added for binary sizing

# Import our contenders
from Sender import SmartSender
from Receiver import EnergyProtocolReceiver
import coap_competitor

# --- ENERGY MODEL ---
E_WAKEUP = 15.0
E_BYTE = 0.1


def calculate_energy(n_packets, total_bytes):
    return (n_packets * E_WAKEUP) + (total_bytes * E_BYTE)


def run_my_protocol_experiment(n_readings):
    print(f"\n[MY PROTOCOL] Starting Smart Sender ({n_readings} readings)...")

    sender = SmartSender()
    sender.battery.current = 50.0

    packets_sent = 0
    bytes_sent = 0

    # 2. Simulation Loop
    for i in range(n_readings):
        # BINARY UPDATE: Append Integer, not String
        sender.buffer.append(20 + i)

        thresh, mode, retries = sender.get_strategy()

        if len(sender.buffer) >= thresh:
            # BINARY UPDATE: Calculate Binary Size
            # Header (6) + 1 byte per reading
            pkg_size = 6 + len(sender.buffer)

            sender.flush(mode, retries)
            packets_sent += 1
            bytes_sent += pkg_size

        time.sleep(0.05)

        # Flush any remaining
    if sender.buffer:
        # Calculate size for remainder
        pkg_size = 6 + len(sender.buffer)

        sender.flush("FINAL", 1)
        packets_sent += 1
        bytes_sent += pkg_size

    return packets_sent, bytes_sent


async def main():
    n_readings = 50

    print("=" * 50)
    print("   IOT PROTOCOL BATTLE: BINARY vs STANDARD (CoAP)")
    print("=" * 50)

    # --- ROUND 1: YOUR PROTOCOL ---
    my_rx = EnergyProtocolReceiver()
    t = threading.Thread(target=my_rx.start)
    t.daemon = True
    t.start()

    my_pkts, my_bytes = run_my_protocol_experiment(n_readings)
    my_energy = calculate_energy(my_pkts, my_bytes)

    my_rx.stop()

    # --- ROUND 2: STANDARD COAP ---
    coap_bytes, _ = await coap_competitor.run_coap_standard_device(n_readings)
    coap_pkts = n_readings
    coap_energy = calculate_energy(coap_pkts, coap_bytes)

    # --- FINAL RESULTS ---
    print("\n\n" + "=" * 40)
    print("      HEAD-TO-HEAD RESULTS")
    print("=" * 40)
    print(f"SCENARIO: Sending {n_readings} sensor readings.\n")

    print(f"CANDIDATE 1: Standard CoAP (Text/JSON)")
    print(f"  - Packets: {coap_pkts}")
    print(f"  - Bytes:   {coap_bytes}")
    print(f"  - ENERGY:  {coap_energy:.1f} mJ")

    print(f"\nCANDIDATE 2: Smart Protocol (Binary Packed)")
    print(f"  - Packets: {my_pkts}")
    print(f"  - Bytes:   {my_bytes}")
    print(f"  - ENERGY:  {my_energy:.1f} mJ")

    if coap_energy > 0:
        savings = ((coap_energy - my_energy) / coap_energy) * 100
        print(f"\n>>> EFFICIENCY GAIN: {savings:.1f}% <<<")
    print("=" * 40)


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())