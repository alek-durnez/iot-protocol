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


class EnergyProtocolReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((LISTEN_IP, LISTEN_PORT))
        self.running = True

    def start(self):
        print(f"[Receiver] Luistert op {LISTEN_IP}:{LISTEN_PORT}...")
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            self.parse_packet(data, addr)

    def parse_packet(self, data, addr):
        # Header uitpakken (eerste 6 bytes)
        try:
            header = data[:6]
            payload = data[6:]

            seq, flags, budget = struct.unpack(HEADER_FORMAT, header)

            # logs
            print(
                f"[Receiver] Packet ontvangen | Seq: {seq} | Budget-Hint: {budget}/255 | Payload: {len(payload)} bytes")

            # Simulatie: Als budget laag is (bv < 20), log een waarschuwing
            if budget < 20:
                print(f"   >>> WAARSCHUWING: Afzender {addr} heeft kritiek laag energiebudget!")

        except Exception as e:
            print(f"[Receiver] Fout bij parsen: {e}")