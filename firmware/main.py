import network
import socket
import time
import struct
import random


WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

SERVER_IP = "reqres.in"  # Placeholder. Replace with your IP
SERVER_PORT = 5005

HEADER_FORMAT = "!IBB"
FLAG_AGGREGATED = 0x01


class VirtualFirmware:
    def __init__(self):
        self.seq = 0
        self.buffer = []
        self.mock_battery = 100  # Start at 100%

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connect_wifi()

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print("Connecting to Wokwi Virtual WiFi...", end="")
        wlan.connect(WIFI_SSID, WIFI_PASS)

        while not wlan.isconnected():
            print(".", end="")
            time.sleep(0.1)

        print("\n Connected! Virtual IP:", wlan.ifconfig()[0])

    def get_battery_level(self):
        # Simulate battery draining by 2% every reading
        self.mock_battery = max(0, self.mock_battery - 2)
        return self.mock_battery

    def get_strategy(self, bat):
        if bat > 70:
            return 1, "REAL-TIME"
        elif bat > 30:
            return 5, "BALANCED"
        else:
            return 10, "SURVIVAL"

    def flush(self):
        if not self.buffer: return

        payload_format = f"{len(self.buffer)}B"
        payload_bytes = struct.pack(payload_format, *self.buffer)

        flags = FLAG_AGGREGATED if len(self.buffer) > 1 else 0
        header_bytes = struct.pack(HEADER_FORMAT, self.seq, flags, self.mock_battery)

        packet = header_bytes + payload_bytes

        print(f"🚀 TX: Packet #{self.seq} | {len(packet)} bytes -> {SERVER_IP}:{SERVER_PORT}")
        try:
            # Wokwi GUEST network will route this out to the internet
            self.sock.sendto(packet, socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1])
        except OSError as e:
            print(f" Network Error: {e}")

        self.seq += 1
        self.buffer = []

    def run(self):
        print("=== VIRTUAL FIRMWARE STARTED ===")
        while True:
            reading = random.randint(20, 30)
            self.buffer.append(reading)

            bat_level = self.get_battery_level()
            threshold, mode = self.get_strategy(bat_level)

            print(f"[Loop] Bat: {bat_level}% | Mode: {mode} | Buffer: {len(self.buffer)}/{threshold}")

            if len(self.buffer) >= threshold:
                self.flush()

            # Time flows faster in our simulation so you don't have to wait all day
            time.sleep(0.5)


if __name__ == "__main__":
    device = VirtualFirmware()
    device.run()