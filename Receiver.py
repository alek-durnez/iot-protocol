import socket
import struct
from utils import LISTEN_IP, LISTEN_PORT, Packet, FLAG_ACK


class EnergyProtocolReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((LISTEN_IP, LISTEN_PORT))
        self.running = True
        self.last_seq_received = -1

    def start(self):
        print(f"[Receiver] Online at {LISTEN_IP}:{LISTEN_PORT}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self.process_packet(data, addr)
            except OSError:
                break
            except Exception as e:
                print(f"[Receiver] Error: {e}")

    def process_packet(self, data, addr):
        seq, flags, budget, payload_bytes = Packet.unpack(data)
        if seq is None: return
        if flags & FLAG_ACK: return

        if seq == self.last_seq_received:
            self.send_ack(seq, budget, addr)
            return

        self.last_seq_received = seq

        # --- BINARY UNPACKING ---
        # Convert bytes back to list of integers
        count = len(payload_bytes)
        if count > 0:
            readings = struct.unpack(f"{count}B", payload_bytes)
        else:
            readings = []

        print(f"[RX] Seq:{seq} | Bat:{budget}% | Payload: {readings} ({count} bytes)")

        self.send_ack(seq, budget, addr)

    def send_ack(self, seq, budget, addr):
        # ACKs have empty payload
        ack_packet = Packet.pack(seq, FLAG_ACK, budget, b"")
        self.sock.sendto(ack_packet, addr)

    def stop(self):
        self.running = False
        self.sock.close()