import os
import uuid
import json
from Crypto.Cipher import AES
from local_storage import Session, Contact, LocalStorage
from message_service import MessageService
from tcp_connection import TCPConnection

class GroupService:
    @staticmethod
    def generate_group_key() -> bytes:
        return os.urandom(32)

    @staticmethod
    def encrypt_group(group_key: bytes, plaintext: str) -> bytes:
        nonce  = os.urandom(12)
        cipher = AES.new(group_key, AES.MODE_GCM, nonce=nonce)
        ct, tag = cipher.encrypt_and_digest(plaintext.encode())
        return nonce + tag + ct

    @staticmethod
    def decrypt_group(group_key: bytes, data: bytes) -> str:
        nonce = data[:12]
        tag   = data[12:28]
        ct    = data[28:]
        cipher= AES.new(group_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ct, tag).decode()

    @staticmethod
    def encrypt_group_file(group_key: bytes, filepath: str) -> bytes:
        with open(filepath, 'rb') as f:
            data = f.read()
        nonce  = os.urandom(12)
        cipher = AES.new(group_key, AES.MODE_GCM, nonce=nonce)
        ct, tag = cipher.encrypt_and_digest(data)
        return nonce + tag + ct

    @staticmethod
    def create_group(name: str, owner_username: str, member_usernames: list, owner_ip: str, owner_port: int) -> str:
        # 1) Generate ID & key, save owner/group
        group_id        = str(uuid.uuid4())
        group_key_bytes = GroupService.generate_group_key()
        group_key_hex   = group_key_bytes.hex()
        LocalStorage.save_group(group_id, name, owner_username, group_key_hex)
        LocalStorage.save_group_member(str(uuid.uuid4()), group_id, owner_username, group_key_hex)

        # 2) Distribute key to members
        for u in member_usernames:
            session = Session()
            contact = session.query(Contact).filter_by(username=u).first()
            session.close()
            if not contact:
                continue
            # encrypt group_key under their session_key
            encrypted_key = MessageService.encrypt(contact.session_key, group_key_hex)
            packet = {
                "type":       "group_handshake",
                "from":       owner_username,
                "to":         u,
                "group_id":   group_id,
                "group_name": name,
                "body":       encrypted_key.hex()
            }
            TCPConnection.send(contact.ip, contact.port, json.dumps(packet).encode())
            LocalStorage.save_group_member(str(uuid.uuid4()), group_id, u, group_key_hex)

        return group_id

    @staticmethod
    def send_group_message(group_id: str, sender_username: str, text: str, host_ip: str, host_port: int):
        session = Session()
        grp = session.query(LocalStorage.Base.classes.groups).filter_by(group_id=group_id).first()
        session.close()
        if not grp:
            raise ValueError(f"No such group: {group_id}")
        group_key = bytes.fromhex(grp.group_key)
        enc       = GroupService.encrypt_group(group_key, text)
        packet    = {
            "type":     "group_msg",
            "from":     sender_username,
            "group_id": group_id,
            "body":     enc.hex()
        }
        TCPConnection.send(host_ip, host_port, json.dumps(packet).encode())
