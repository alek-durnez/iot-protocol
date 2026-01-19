import asyncio
import threading
import time
import os

# Import our contenders
from Sender import SmartSender
from Receiver import EnergyProtocolReceiver
import coap_competitor

# --- ENERGY MODEL (Research Based) ---
# We use standard values for ZigBee/WiFi IoT radios
E_WAKEUP = 15.0  # mJ (Energy to wake radio, PLL sync, preamble)
E_BYTE = 0.1  # mJ (Energy to transmit 1 byte)


def calculate_energy(n_packets, total_bytes):
    return (n_packets * E_WAKEUP) + (total_bytes * E_BYTE)


def run_my_protocol_experiment(n_readings):
    print(f"\n[MY PROTOCOL] Starting Smart Sender ({n_readings} readings)...")

    # 1. Setup
    sender = SmartSender()
    # We force the battery to 50% to trigger "Balanced Mode" (Aggregation)
    # This demonstrates the core feature of your protocol
    sender.battery.current = 50.0

    packets_sent = 0
    bytes_sent = 0

    # 2. Simulation Loop
    for i in range(n_readings):
        # Add data to buffer
        sender.buffer.append(f"TEMP:{20 + i}")

        # Ask logic: "Should I send?"
        thresh, mode, retries = sender.get_strategy()

        if len(sender.buffer) >= thresh:
            # FLUSH (Send Packet)
            payload = "|".join(sender.buffer)
            # Header (6) + Payload
            pkg_size = 6 + len(payload)

            sender.flush(mode, retries)
            packets_sent += 1
            bytes_sent += pkg_size

        time.sleep(0.05)  # Fast simulation

    # Flush any remaining data
    if sender.buffer:
        sender.flush("FINAL", 1)
        packets_sent += 1
        bytes_sent += 6 + len("|".join(sender.buffer))

    return packets_sent, bytes_sent


async def main():
    n_readings = 50

    print("=" * 50)
    print("   IOT PROTOCOL BATTLE: SMART vs STANDARD (CoAP)")
    print("=" * 50)

    # my protocol    
    my_rx = EnergyProtocolReceiver()
    t = threading.Thread(target=my_rx.start)
    t.daemon = True
    t.start()

    # Run sender
    my_pkts, my_bytes = run_my_protocol_experiment(n_readings)
    my_energy = calculate_energy(my_pkts, my_bytes)

    # Stop receiver
    my_rx.stop()

    # COAP
    coap_bytes, _ = await coap_competitor.run_coap_standard_device(n_readings)

    # CoAP sends 1 packet per reading 
    coap_pkts = n_readings
    coap_energy = calculate_energy(coap_pkts, coap_bytes)

    # Results
    print("\n\n" + "=" * 40)
    print("      HEAD-TO-HEAD RESULTS")
    print("=" * 40)
    print(f"SCENARIO: Sending {n_readings} sensor readings.\n")

    print(f"CANDIDATE 1: Standard CoAP (RFC 7252)")
    print(f"  - Packets: {coap_pkts}")
    print(f"  - Bytes:   {coap_bytes}")
    print(f"  - ENERGY:  {coap_energy:.1f} mJ")

    print(f"\nCANDIDATE 2: My Protocol (Smart Aggregation)")
    print(f"  - Packets: {my_pkts}")
    print(f"  - Bytes:   {my_bytes}")
    print(f"  - ENERGY:  {my_energy:.1f} mJ")

    if coap_energy > 0:
        savings = ((coap_energy - my_energy) / coap_energy) * 100
        print(f"\n>>> EFFICIENCY GAIN: {savings:.1f}% <<<")
    print("=" * 40)


if __name__ == "__main__":
    # Windows-specific fix for asyncio loops
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())