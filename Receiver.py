import socket
from utils import LISTEN_IP, LISTEN_PORT, DELIMITER, Packet, FLAG_ACK


class EnergyProtocolReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allow reusing address to prevent "Address already in use" errors during quick restarts
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
                break  # Socket closed
            except Exception as e:
                print(f"[Receiver] Error: {e}")

    def process_packet(self, data, addr):
        seq, flags, budget, payload = Packet.unpack(data)
        if seq is None: return
        if flags & FLAG_ACK: return

        # Duplicate Detection
        if seq == self.last_seq_received:
            # print(f"[RX] Duplicate Packet #{seq} detected. Resending ACK.")
            self.send_ack(seq, budget, addr)
            return

        self.last_seq_received = seq
        # readings = payload.split(DELIMITER)
        # print(f"[RX] Seq:{seq} | Bat:{budget}% | Items:{len(readings)}")

        self.send_ack(seq, budget, addr)

    def send_ack(self, seq, budget, addr):
        ack_packet = Packet.pack(seq, FLAG_ACK, budget, "")
        self.sock.sendto(ack_packet, addr)

    def stop(self):
        self.running = False
        self.sock.close()