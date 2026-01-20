import socket
import time
import os
import csv
import random
import struct
from utils import LISTEN_IP, LISTEN_PORT, Packet, FLAG_ACK, FLAG_AGGREGATED, simulate_network_loss, encrypt_payload
from battery import Battery

LOG_FILE = "results/smart_sender_log.csv"
os.makedirs("results", exist_ok=True)


class SmartSender:
    def __init__(self, target_ip=LISTEN_IP, target_port=LISTEN_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = (target_ip, target_port)
        self.seq = 0
        self.buffer = []  # Stores Integers

        # PHYSICS ENGINE
        self.battery = Battery(initial_capacity=100.0, drain_idle=0.1, drain_tx=3.0)
        self.sock.settimeout(1.0)

        with open(LOG_FILE, mode='w', newline='') as f:
            csv.writer(f).writerow(["Timestamp", "Seq", "Battery", "Mode", "Event"])

    def get_strategy(self):
        bat = self.battery.update_idle()
        if bat > 70:
            return 1, "REAL-TIME", 3
        elif bat > 30:
            return 5, "BALANCED", 1
        else:
            return 10, "SURVIVAL", 0

    def run(self):
        print(f"=== SECURE SENDER STARTED (Bat: {self.battery.current}%) ===")
        while not self.battery.is_dead:
            # 1. Simulate Sensor Reading (Binary)
            reading = random.randint(20, 30)
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

        # Binary packing
        # Convert list of ints to bytes (e.g. [22, 23] -> b'\x16\x17')
        pack_format = f"{len(self.buffer)}B"
        raw_payload = struct.pack(pack_format, *self.buffer)

        # Encryption (AES-GCM)
        secure_payload = encrypt_payload(raw_payload)

        is_aggregated = FLAG_AGGREGATED if len(self.buffer) > 1 else 0
        budget_byte = int(self.battery.current)

        # Create Packet
        packet = Packet.pack(self.seq, is_aggregated, budget_byte, secure_payload)

        attempts = 0
        success = False
        current_timeout = 0.5

        while attempts <= max_retries:
            if self.battery.is_dead: break

            try:
                self.sock.settimeout(current_timeout)

                if simulate_network_loss():
                    print(f"    [CHAOS] Packet #{self.seq} dropped.")
                    self.battery.consume_tx(retries=attempts)
                else:
                    self.sock.sendto(packet, self.target)
                    self.battery.consume_tx(retries=attempts)

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
                    current_timeout *= 2

        with open(LOG_FILE, mode='a', newline='') as f:
            status = "SENT" if success else "DROP"
            csv.writer(f).writerow([time.time(), self.seq, self.battery.current, mode, status])

        self.seq += 1
        self.buffer = []