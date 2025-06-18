import json
import hashlib
from local_storage import Session, Device
from crypto_service import CryptoService

ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def b58encode(b: bytes) -> str:
    # Convert to integer
    n = int.from_bytes(b, 'big')
    # Encode to Base58
    res = ''
    while n > 0:
        n, r = divmod(n, 58)
        res = ALPHABET[r] + res
    # Preserve leading zero bytes
    pad = 0
    for c in b:
        if c == 0:
            pad += 1
        else:
            break
    return ALPHABET[0] * pad + res

def b58decode(s: str) -> bytes:
    n = 0
    for char in s:
        n = n * 58 + ALPHABET.index(char)
    # Convert back to bytes
    h = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    # Restore leading zeros
    pad = len(s) - len(s.lstrip(ALPHABET[0]))
    return b'\x00' * pad + h

class CodeService:
    @staticmethod
    def generate_code(username: str, public_ip: str, port: int) -> str:
        # Fetch our public key
        session = Session()
        device = session.query(Device).first()
        session.close()
        pubkey = device.public_key

        payload = {
            'username':   username,
            'ip':         public_ip,
            'port':       port,
            'public_key': pubkey
        }
        raw = json.dumps(payload, separators=(',',':')).encode()
        return b58encode(raw)

    @staticmethod
    def decode_code(code: str) -> dict:
        raw = b58decode(code)
        return json.loads(raw.decode())
