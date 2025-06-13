import os
import uuid
import hashlib
from Crypto.Cipher import AES

class FileService:
    @staticmethod
    def encrypt_file(session_key_hex: str, filepath: str) -> bytes:
        key = bytes.fromhex(session_key_hex)
        nonce = os.urandom(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        with open(filepath, 'rb') as f:
            data = f.read()
        ciphertext, tag = cipher.encrypt_and_digest(data)

        return nonce + tag + ciphertext

    @staticmethod
    def decrypt_file(session_key_hex: str, encrypted_data: bytes, out_path: str):
        key = bytes.fromhex(session_key_hex)
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'wb') as f:
            f.write(data)