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


class EnergyProtocolSender:
    def __init__(self, target_ip, target_port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = (target_ip, target_port)
        self.seq = 0

        # Research parameters
        self.current_battery = 100.0  # Percentage
        self.energy_cost_per_tx = 0.5  # Willekeurige unit per zending

    def send_reading(self, sensor_data):
        # 1. Energie Check
        if self.current_battery <= 0:
            print("[Sender] Batterij leeg. Stopt zenden.")
            return

        # 2. Header aanmaken
        # Map batterij 0-100% naar 0-255 byte
        budget_byte = int((self.current_battery / 100) * 255)
        flags = 0x00  # Voor nu geen speciale flags

        header = struct.pack(HEADER_FORMAT, self.seq, flags, budget_byte)
        packet = header + sensor_data.encode('utf-8')

        # 3. Verzenden
        self.sock.sendto(packet, self.target)
        print(f"[Sender] Verstuurd Seq: {self.seq} | Batterij: {self.current_battery:.1f}%")

        # 4. Update State
        self.seq += 1
        self.current_battery -= self.energy_cost_per_tx


def run_demo():
    # Start de receiver in een aparte thread zodat we in dezelfde terminal kunnen zenden
    receiver = EnergyProtocolReceiver()
    rx_thread = threading.Thread(target=receiver.start)
    rx_thread.daemon = True
    rx_thread.start()

    time.sleep(1)  # Even wachten tot receiver klaar is

    # Start de sender
    sender = EnergyProtocolSender(TARGET_IP, TARGET_PORT)

    # Simuleer een reeks sensorwaarden
    print("\n--- START EXPERIMENT ---\n")
    for i in range(10):
        # Simuleer data (bv. temperatuur)
        dummy_data = f"Temp:{20 + i}C"
        sender.send_reading(dummy_data)

        # Simuleer variabele interval (sleep)
        time.sleep(0.5)

    print("\n--- EINDE DEMO ---")


if __name__ == "__main__":
    run_demo()