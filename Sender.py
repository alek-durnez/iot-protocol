import socket
import time
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet


class EnergyProtocolSender:
    def __init__(self, target_ip=LISTEN_IP, target_port=LISTEN_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = (target_ip, target_port)
        self.seq = 0
        self.current_battery = 100.0
        self.buffer = []

    def get_strategy(self):
        """Returns (Threshold, Description) based on battery."""
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
            self.flush()
        else:
            print(f"[TX Hold] Buffering... ({len(self.buffer)}/{threshold}) [{mode}]")

    def flush(self):
        if not self.buffer: return

        # Prepare Payload
        payload_str = DELIMITER.join(self.buffer)

        # Prepare Header Info
        is_aggregated = 1 if len(self.buffer) > 1 else 0
        budget_byte = int(self.current_battery)  # Simplified for demo

        # Pack and Send
        packet = Packet.pack(self.seq, is_aggregated, budget_byte, payload_str)
        self.sock.sendto(packet, self.target)

        print(f"--> [TX SENT] Seq:{self.seq} | Size:{len(packet)}B | Bat:{self.current_battery:.1f}%")

        # Reset State & Simulate Battery Drain
        self.seq += 1
        self.buffer = []
        self.current_battery -= 2.5  # Cost of turning on radio