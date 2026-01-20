import struct
import random

# Configuration
LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 5005
DELIMITER = "|"  # Unused in binary mode, but kept for legacy safety

# Protocol Constants
HEADER_FORMAT = "!IBB"  # (Seq: 4 bytes, Flags: 1, Budget: 1) = 6 Bytes Total
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FLAG_AGGREGATED = 0x01
FLAG_ACK = 0x02


class Packet:
    @staticmethod
    def pack(seq, flags, budget, payload):
        """
        Packs header + payload. 
        Auto-detects if payload is binary or string.
        """
        if isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        else:
            payload_bytes = payload  # Assume it's already bytes (Binary Mode)

        header = struct.pack(HEADER_FORMAT, seq, flags, budget)
        return header + payload_bytes

    @staticmethod
    def unpack(data):
        if len(data) < HEADER_SIZE:
            return None, None, None, None

        header = data[:HEADER_SIZE]
        payload_bytes = data[HEADER_SIZE:]  # Keep as raw bytes!

        seq, flags, budget = struct.unpack(HEADER_FORMAT, header)
        return seq, flags, budget, payload_bytes


def simulate_network_loss(probability=0.2):
    return random.random() < probability