import socket
import struct
import time
import threading
import random

# --- CONFIGURATIE ---
LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 5005
TARGET_IP = "127.0.0.1"
TARGET_PORT = 5005

# Header formaat: !I B B (Big-endian, Unsigned Int (Seq), U-Char (Flags), U-Char (Budget))
# Totale header grootte: 4 + 1 + 1 = 6 bytes overhead
HEADER_FORMAT = "!I B B"

class EnergyProtocolSender:
    def __init__(self, target_ip, target_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = (target_ip, target_port)
        self.seq = 0

        # Research parameters
        self.current_battery = 100.0  # Percentage
        self.energy_cost_per_tx = 0.5  # Willekeurige unit per zending

    def send_reading(self, sensor_data):
        # 1. Energie Check
        if self.current_battery <= 0:
            print("[Sender] Batterij leeg. Stopt zenden.")
            return

        # 2. Header aanmaken
        # Map batterij 0-100% naar 0-255 byte
        budget_byte = int((self.current_battery / 100) * 255)
        flags = 0x00  # Voor nu geen speciale flags

        header = struct.pack(HEADER_FORMAT, self.seq, flags, budget_byte)
        packet = header + sensor_data.encode('utf-8')

        # 3. Verzenden
        self.sock.sendto(packet, self.target)
        print(f"[Sender] Verstuurd Seq: {self.seq} | Batterij: {self.current_battery:.1f}%")

        # 4. Update State
        self.seq += 1
        self.current_battery -= self.energy_cost_per_tx