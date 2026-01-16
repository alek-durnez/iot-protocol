import socket
import struct
import time
import threading
import random

from EnergyProtocolReceiver import EnergyProtocolReceiver
from EnergyProtocolSender import EnergyProtocolSender

# --- CONFIGURATIE ---
LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 5005
TARGET_IP = "127.0.0.1"
TARGET_PORT = 5005

# Header formaat: !I B B (Big-endian, Unsigned Int (Seq), U-Char (Flags), U-Char (Budget))
# Totale header grootte: 4 + 1 + 1 = 6 bytes overhead
HEADER_FORMAT = "!I B B"

def run_demo():
    # Start de receiver in een aparte thread zodat we in dezelfde terminal kunnen zenden
    receiver = EnergyProtocolReceiver()
    rx_thread = threading.Thread(target=receiver.start)
    rx_thread.daemon = True
    rx_thread.start()

    time.sleep(1)  # Even wachten tot receiver klaar is

    # Start de sender
    sender = EnergyProtocolSender(TARGET_IP, TARGET_PORT)

    # Simuleer een reeks sensorwaarden
    print("\n--- START EXPERIMENT ---\n")
    for i in range(10):
        # Simuleer data (bv. temperatuur)
        dummy_data = f"Temp:{20 + i}C"
        sender.send_reading(dummy_data)

        # Simuleer variabele interval (sleep)
        time.sleep(0.5)

    print("\n--- EINDE DEMO ---")


if __name__ == "__main__":
    run_demo()