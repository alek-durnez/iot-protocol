import threading
import time

from Receiver import EnergyProtocolReceiver
from Sender import EnergyProtocolSender


def run_simulation():
    # 1. Start Receiver in Background
    rx = EnergyProtocolReceiver()
    rx_thread = threading.Thread(target=rx.start)
    rx_thread.daemon = True
    rx_thread.start()

    time.sleep(1)  # Wait for server start

    # 2. Start Sender
    tx = EnergyProtocolSender()

    print("\n=== EXPERIMENT START: 3 PHASES ===\n")

    # PHASE 1: HIGH BATTERY (90%) -> Should send immediately
    tx.current_battery = 90
    for i in range(3):
        tx.send_data(f"T:{20 + i}")
        time.sleep(0.3)

    print("\n--- DRAINING BATTERY TO 60% (Aggregation Mode) ---")

    # PHASE 2: MEDIUM BATTERY (60%) -> Should buffer 5 items
    tx.current_battery = 60
    for i in range(7):
        tx.send_data(f"T:{30 + i}")
        time.sleep(0.1)

    print("\n--- DRAINING BATTERY TO 15% (Survival Mode) ---")

    # PHASE 3: CRITICAL BATTERY (15%) -> Should buffer 10 items
    tx.current_battery = 15
    for i in range(12):
        tx.send_data(f"T:{40 + i}")
        time.sleep(0.1)

    print("\n=== EXPERIMENT COMPLETE ===")


if __name__ == "__main__":
    run_simulation()