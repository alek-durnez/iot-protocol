import socket
import struct
import time
import os
import csv

# CONFIGURATION
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 5005
LOG_FILE = "iot_gateway_log.csv"

# PROTOCOL
# Header: Seq (4B), Flags (1B), Budget (1B) -> 6 Bytes
HEADER_FORMAT = "!IBB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FLAG_ACK = 0x02


def start_gateway():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))

    print(f"IoT Gateway listening on port {LISTEN_PORT}")
    print(f"Log file: {LOG_FILE}")

    # Initialize CSV if missing
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as f:
            csv.writer(f).writerow(["Timestamp", "IP", "Seq", "Battery", "Payload_Size", "Data"])

    while True:
        try:
            data, addr = sock.recvfrom(1024)

            if len(data) < HEADER_SIZE:
                continue

            # 1. Unpack Header
            header = data[:HEADER_SIZE]
            payload = data[HEADER_SIZE:]
            seq, flags, budget = struct.unpack(HEADER_FORMAT, header)

            # 2. Process Data (Simplified for Demo)
            # In production, you would decrypt 'payload' here using the key.
            # For now, we assume raw binary or hex for visibility.

            # If payload is just bytes of integers (from your Sender.py logic)
            # We can try to unpack them if we know it's not encrypted for this specific test
            readings = list(payload)

            print(f"[{time.strftime('%H:%M:%S')}] RX from {addr[0]} | Seq:{seq} | Bat:{budget}% | Bytes:{len(payload)}")

            # 3. Save to Disk
            with open(LOG_FILE, 'a', newline='') as f:
                csv.writer(f).writerow([time.time(), addr[0], seq, budget, len(payload), readings])

            # 4. Send ACK (Optional, but good for protocol completeness)
            # Ack packet: Seq (4), Flag (ACK), Budget (0), No Payload
            ack_header = struct.pack(HEADER_FORMAT, seq, FLAG_ACK, 0)
            sock.sendto(ack_header, addr)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    start_gateway()