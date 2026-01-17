import socket
import time
import os
import csv
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet, FLAG_ACK, FLAG_AGGREGATED

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

        # NIEUW: Wacht maximaal 1.0s op een ACK
        self.sock.settimeout(1.0)

        # Initialize CSV Header
        with open(LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Seq", "Battery", "Bytes_Sent", "Items_In_Packet", "Mode", "Retries"])

    def get_strategy(self):
        """
        Geeft terug: (Threshold, Mode, MaxRetries)
        Research Logic: Rijke batterij mag vaker proberen (betrouwbaarheid).
        Arme batterij spaart energie en probeert het maar 1x of 0x (survival).
        """
        if self.current_battery > 70:
            return 1, "REAL-TIME", 3  # Hoge betrouwbaarheid (3 retries)
        elif self.current_battery > 30:
            return 5, "BALANCED", 1  # Balans (1 retry)
        else:
            return 10, "SURVIVAL", 0  # Puur overleven (Geen retries)

    def send_data(self, reading):
        self.buffer.append(reading)
        threshold, mode, max_retries = self.get_strategy()

        if len(self.buffer) >= threshold:
            self.flush(mode, max_retries)
        else:
            print(f"[TX Hold] Buffering... ({len(self.buffer)}/{threshold})")

    def flush(self, mode, max_retries):
        if not self.buffer: return

        # 1. Packet voorbereiden
        payload_str = DELIMITER.join(self.buffer)
        is_aggregated = FLAG_AGGREGATED if len(self.buffer) > 1 else 0
        budget_byte = int(self.current_battery) if self.current_battery > 0 else 0

        packet = Packet.pack(self.seq, is_aggregated, budget_byte, payload_str)

        attempts = 0
        success = False
        total_bytes_sent_on_wire = 0  # Telt bytes van alle pogingen op

        # 2. Retransmission Loop
        while attempts <= max_retries:
            try:
                # Verstuur (Poging X)
                self.sock.sendto(packet, self.target)
                total_bytes_sent_on_wire += len(packet)
                self.current_battery -= 2.0  # TX kost energie

                # Wacht op ACK
                ack_data, _ = self.sock.recvfrom(128)
                ack_seq, flags, _, _ = Packet.unpack(ack_data)

                # Check of het een geldige ACK is voor óns sequence nummer
                if (flags & FLAG_ACK) and (ack_seq == self.seq):
                    success = True
                    break 

            except socket.timeout:
                attempts += 1
                if attempts <= max_retries:
                    print(f"    !!! Timeout Seq:{self.seq}. Retrying ({attempts}/{max_retries})...")
                    self.current_battery -= 0.5  # Wachten/Retry setup kost beetje energie

        # 3. Logging & Output
        status = "SUCCESS" if success else "FAILED"
        print(f"--> [TX {status}] Seq:{self.seq} | Mode:{mode} | Retries:{attempts} | Bat:{self.current_battery:.1f}%")

        # Log naar CSV
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(),
                self.seq,
                self.current_battery,
                total_bytes_sent_on_wire, 
                len(self.buffer),
                mode,
                attempts
            ])

        # 4. Opruimen
        self.seq += 1
        self.buffer = []