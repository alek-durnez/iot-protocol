import struct

# Configuration
LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 5005
HEADER_FORMAT = "!I B B"  # Seq (4), Flags (1), Budget (1)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
DELIMITER = "|"


class Packet:
    """Helper class to handle binary packing/unpacking."""

    @staticmethod
    def pack(seq, flags, budget, payload_str):
        payload_bytes = payload_str.encode('utf-8')
        header = struct.pack(HEADER_FORMAT, seq, flags, budget)
        return header + payload_bytes

    @staticmethod
    def unpack(data):
        if len(data) < HEADER_SIZE:
            return None, None, None, None

        header = data[:HEADER_SIZE]
        payload_bytes = data[HEADER_SIZE:]

        seq, flags, budget = struct.unpack(HEADER_FORMAT, header)
        payload_str = payload_bytes.decode('utf-8')
        return seq, flags, budget, payload_str