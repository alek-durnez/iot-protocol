import socket
import time
import os
import csv
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet

# Ensure results directory exists
os.makedirs("results", exist_ok=True)
LOG_FILE = "results/experiment_log.csv"


class EnergyProtocolSender:
    def __init__(self, target_ip=LISTEN_IP, target_port=LISTEN_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = (target_ip, target_port)
        self.seq = 0
        self.current_battery = 100.0
        self.buffer = []

        # Initialize CSV Header
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Seq", "Battery", "Bytes_Sent", "Items_In_Packet", "Mode"])

    def get_strategy(self):
        if self.current_battery > 70:
            return 1, "REAL-TIME"
        elif self.current_battery > 30:
            return 5, "BALANCED"
        else:
            return 10, "SURVIVAL"

    def send_data(self, reading):
        self.buffer.append(reading)
        threshold, mode = self.get_strategy()

        if len(self.buffer) >= threshold:
            self.flush(mode)
        else:
            print(f"[TX Hold] Buffering... ({len(self.buffer)}/{threshold})")

    def flush(self, mode):
        if not self.buffer: return

        payload_str = DELIMITER.join(self.buffer)
        is_aggregated = 1 if len(self.buffer) > 1 else 0
        budget_byte = int(self.current_battery)

        packet = Packet.pack(self.seq, is_aggregated, budget_byte, payload_str)
        self.sock.sendto(packet, self.target)

        # --- LOGGING DATA ---
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            # Log: Time, Seq, Battery, Total Size, Aggregation Count, Mode Name
            writer.writerow([time.time(), self.seq, self.current_battery, len(packet), len(self.buffer), mode])

        print(f"--> [TX SENT] Seq:{self.seq} | Size:{len(packet)}B | Mode:{mode}")

        self.seq += 1
        self.buffer = []
        self.current_battery -= 2.0