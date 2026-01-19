import socket
import time
import os
import csv
import random
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet, FLAG_ACK, FLAG_AGGREGATED, simulate_network_loss
from battery import Battery

LOG_FILE = "results/smart_sender_log.csv"
# Ensure results directory exists
os.makedirs("results", exist_ok=True)


class SmartSender:
    def __init__(self, target_ip=LISTEN_IP, target_port=LISTEN_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = (target_ip, target_port)
        self.seq = 0
        self.buffer = []

        # PHYSICS ENGINE
        self.battery = Battery(initial_capacity=100.0, drain_idle=0.1, drain_tx=3.0)

        self.sock.settimeout(1.0)  # Base timeout

        with open(LOG_FILE, mode='w', newline='') as f:
            csv.writer(f).writerow(["Timestamp", "Seq", "Battery", "Mode", "Event"])

    def get_strategy(self):
        bat = self.battery.update_idle()

        # Strategy Table
        if bat > 70:
            return 1, "REAL-TIME", 3
        elif bat > 30:
            return 5, "BALANCED", 1
        else:
            return 10, "SURVIVAL", 0

    def run(self):
        print(f"=== SMART SENDER STARTED (Bat: {self.battery.current}%) ===")
        while not self.battery.is_dead:
            # 1. Simulate Sensor Reading
            reading = f"TEMP:{random.randint(20, 30)}"
            self.buffer.append(reading)

            # 2. Decide Strategy
            threshold, mode, max_retries = self.get_strategy()
            print(f"[Sensor] Buffer: {len(self.buffer)}/{threshold} | Bat: {self.battery.current:.2f}% | Mode: {mode}")

            # 3. Flush if threshold met
            if len(self.buffer) >= threshold:
                self.flush(mode, max_retries)

            # 4. Wait
            time.sleep(1.0)
            self.battery.update_idle()
        print("\n=== BATTERY DEAD. SYSTEM SHUTDOWN. ===")

    def flush(self, mode, max_retries):
        if not self.buffer: return

        payload_str = DELIMITER.join(self.buffer)
        is_aggregated = FLAG_AGGREGATED if len(self.buffer) > 1 else 0
        budget_byte = int(self.battery.current)

        packet = Packet.pack(self.seq, is_aggregated, budget_byte, payload_str)

        attempts = 0
        success = False
        current_timeout = 0.5

        while attempts <= max_retries:
            if self.battery.is_dead: break

            try:
                self.sock.settimeout(current_timeout)

                if simulate_network_loss():
                    print(f"    [CHAOS] Packet #{self.seq} dropped.")
                    self.battery.consume_tx(retries=0)
                else:
                    self.sock.sendto(packet, self.target)
                    self.battery.consume_tx(retries=0)

                # Wait for ACK
                ack_data, _ = self.sock.recvfrom(128)
                ack_seq, flags, _, _ = Packet.unpack(ack_data)

                if (flags & FLAG_ACK) and (ack_seq == self.seq):
                    success = True
                    break

            except socket.timeout:
                attempts += 1
                if attempts <= max_retries:
                    print(f"    !!! TIMEOUT. Retrying...")
                    current_timeout *= 2  # Exponential Backoff

        with open(LOG_FILE, mode='a', newline='') as f:
            status = "SENT" if success else "DROP"
            csv.writer(f).writerow([time.time(), self.seq, self.battery.current, mode, status])

        self.seq += 1
        self.buffer = []