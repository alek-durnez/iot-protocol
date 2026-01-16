import socket
import threading
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet


class EnergyProtocolReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((LISTEN_IP, LISTEN_PORT))
        self.running = True

    def start(self):
        print(f"[Receiver] Online at {LISTEN_IP}:{LISTEN_PORT}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self.process_packet(data, addr)
            except Exception as e:
                print(f"[Receiver] Error: {e}")

    def process_packet(self, data, addr):
        seq, flags, budget, payload = Packet.unpack(data)

        if seq is None:
            return  # Corrupt packet

        readings = payload.split(DELIMITER)

        # --- Visualization of Data Arriving ---
        print(f"[RX] Seq:{seq} | Bat:{budget}% | Items:{len(readings)} | Src:{addr}")

        if budget < 30:
            print(f"    └──CRITICAL ENERGY MODE DETECTED")

        for r in readings:
            if r: print(f"        └── Data: {r}")

    def stop(self):
        self.running = False
        self.sock.close()