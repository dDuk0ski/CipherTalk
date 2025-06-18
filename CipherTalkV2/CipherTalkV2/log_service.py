import os
from datetime import datetime
from message_service import MessageService
from group_service import GroupService

LOG_DIR     = os.path.expanduser("~/.cipher_talk/logs")
PRIVATE_DIR = os.path.join(LOG_DIR, "private")
GROUP_DIR   = os.path.join(LOG_DIR, "groups")
os.makedirs(PRIVATE_DIR, exist_ok=True)
os.makedirs(GROUP_DIR, exist_ok=True)

def log_private_message(peer_username: str, sender: str, ciphertext_hex: str):
    path = os.path.join(PRIVATE_DIR, f"{peer_username}.log")
    with open(path, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}|{sender}|{ciphertext_hex}\n")

def load_private_history(peer_username: str, session_key: bytes):
    path = os.path.join(PRIVATE_DIR, f"{peer_username}.log")
    if not os.path.exists(path):
        return []
    msgs = []
    with open(path, "r") as f:
        for line in f:
            ts, sender, hexct = line.strip().split("|", 2)
            pt = MessageService.decrypt(session_key, bytes.fromhex(hexct))
            msgs.append((ts, sender, pt))
    return msgs

def log_group_message(group_id: str, sender: str, ciphertext_hex: str):
    path = os.path.join(GROUP_DIR, f"{group_id}.log")
    with open(path, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()}|{sender}|{ciphertext_hex}\n")

def load_group_history(group_id: str, group_key: bytes):
    path = os.path.join(GROUP_DIR, f"{group_id}.log")
    if not os.path.exists(path):
        return []
    msgs = []
    with open(path, "r") as f:
        for line in f:
            ts, sender, hexct = line.strip().split("|", 2)
            pt = GroupService.decrypt_group(group_key, bytes.fromhex(hexct))
            msgs.append((ts, sender, pt))
    return msgs
