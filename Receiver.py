import socket
import threading
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet, FLAG_ACK, FLAG_AGGREGATED


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

        if seq is None: return

        # Is dit een ACK? (Zou niet moeten, want wij zijn de server, maar voor de zekerheid)
        if flags & FLAG_ACK:
            return

        # 1. Verwerk de Data
        readings = payload.split(DELIMITER)
        print(f"[RX] Seq:{seq} | Bat:{budget}% | Items:{len(readings)}")

        # 2. STUUR ACK TERUG
        # We sturen een leeg pakketje terug met de FLAG_ACK aan en hetzelfde Seq nummer.
        ack_packet = Packet.pack(seq, FLAG_ACK, budget, "")
        self.sock.sendto(ack_packet, addr)
        print(f"    -> Sent ACK for #{seq}") 
    def stop(self):
        self.running = False
        self.sock.close()