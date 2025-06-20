from Crypto.Cipher import AES
import os
from local_storage import Session, Contact

class MessageService:
    @staticmethod
    def encrypt(session_key_hex: str, plaintext: str) -> bytes:
        key = bytes.fromhex(session_key_hex)
        nonce = os.urandom(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return nonce + tag + ciphertext

    @staticmethod
    def decrypt(session_key_hex: str, data: bytes) -> str:
        key = bytes.fromhex(session_key_hex)
        nonce = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        try:
            return plaintext.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            return plaintext

    @staticmethod
    def get_contact_by_username(username: str):
        session = Session()
        contact = session.query(Contact).filter_by(username=username).first()
        session.close()
        return contact