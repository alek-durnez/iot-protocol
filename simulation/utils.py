import struct
import random
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Configuration
LISTEN_IP = "127.0.0.1"
LISTEN_PORT = 5005

# Protocol Constants
# Header: Seq (4 bytes) + Flags (1 byte) + Budget (1 byte) = 6 Bytes
HEADER_FORMAT = "!IBB"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FLAG_AGGREGATED = 0x01
FLAG_ACK = 0x02

# --- SECURITY MODULE ---
# In a real device, this key is burned into the chip.
# We use a hardcoded 32-byte key (AES-256) for this PoC.
MASTER_KEY = b'\x01\x02\x03\x04\x05\x06\x07\x08' * 4


def encrypt_payload(plaintext_bytes):
    """
    Encrypts data using AES-GCM.
    Returns: [Nonce (12B)] + [Ciphertext + AuthTag]
    """
    # 1. Generate unique Nonce (Number used once)
    nonce = os.urandom(12)

    # 2. Encrypt
    aesgcm = AESGCM(MASTER_KEY)
    # associated_data=None means only authenticate the payload, not the header (for simplicity)
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, associated_data=None)

    # 3. Pack: must send the Nonce so the receiver can decrypt
    return nonce + ciphertext


def decrypt_payload(encrypted_data):
    """
    Decrypts data. Returns None if tampering is detected.
    """
    if len(encrypted_data) < 12:
        return None  # Too short to contain nonce

    # 1. Extract Nonce
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    # 2. Decrypt & Verify
    aesgcm = AESGCM(MASTER_KEY)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
        return plaintext
    except Exception:
        # Decryption failed (Wrong key OR Data tampered)
        return None


class Packet:
    @staticmethod
    def pack(seq, flags, budget, payload):
        # Allow passing pre-encrypted bytes or raw bytes
        if isinstance(payload, str):
            payload = payload.encode('utf-8')

        header = struct.pack(HEADER_FORMAT, seq, flags, budget)
        return header + payload

    @staticmethod
    def unpack(data):
        if len(data) < HEADER_SIZE:
            return None, None, None, None

        header = data[:HEADER_SIZE]
        payload_bytes = data[HEADER_SIZE:]

        seq, flags, budget = struct.unpack(HEADER_FORMAT, header)
        return seq, flags, budget, payload_bytes


def simulate_network_loss(probability=0.2):
    return random.random() < probability