import os
import json
import socket
import threading
import uuid

from crypto_service import CryptoService
from keystore import KeyStore
from local_storage import LocalStorage, Session, Device, Contact
from friend_service import FriendService
from message_service import MessageService
from file_service import FileService

LISTEN_PORT = 9000
MEDIA_DIR = os.path.expanduser("~/cipher_talk/media")
os.makedirs(MEDIA_DIR, exist_ok=True)

def get_own_pubkey():
    session = Session()
    device = session.query(Device).first()
    session.close()
    return device.public_key

def ensure_device():
    key_path = os.path.expanduser("~/.cipher_talk/keys/device_private.key")
    if not os.path.exists(key_path):
        priv, pub = CryptoService.generate_keypair()
        priv_hex = CryptoService.serialize_private(priv)
        pub_hex = CryptoService.serialize_public(pub)
        KeyStore.seal("device_private", priv_hex)
        LocalStorage.save_device(str(uuid.uuid4()), pub_hex)
        print(f"[Device] New identity created: {pub_hex}")
    else:
        print("[Device] Identity already initialized.")

def start_listener(local_username):
    def handler(conn, addr):
        try:
            data = conn.recv(8192)
            msg = json.loads(data.decode())

            if msg.get("type") == "handshake":
                peer_username = msg["username"]
                peer_pubkey  = msg["public_key"]
                print(f"[Handshake] from {peer_username}@{addr[0]}")
                FriendService.add_friend(peer_username, addr[0], LISTEN_PORT, peer_pubkey)

                # Respond with our handshake
                resp = json.dumps({
                    "type":       "handshake",
                    "username":   local_username,
                    "public_key": get_own_pubkey()
                }).encode()
                conn.sendall(resp)

            elif msg.get("type") == "message":
                for contact in Session().query(Contact).all():
                    try:
                        pt = MessageService.decrypt(contact.session_key, bytes.fromhex(msg["body"]))
                        print(f"\n[{contact.username}] {pt}")
                        break
                    except:
                        continue

            elif msg.get("type") == "file":
                for contact in Session().query(Contact).all():
                    try:
                        data = bytes.fromhex(msg["body"])
                        out_file = os.path.join(MEDIA_DIR,
                            f"{contact.username}_{uuid.uuid4().hex[:8]}")
                        FileService.decrypt_file(contact.session_key, data, out_file)
                        print(f"\n[{contact.username}] 📁 File saved: {out_file}")
                        break
                    except:
                        continue

        except Exception as e:
            print(f"[Listener error] {e}")
        finally:
            conn.close()

    def listen():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", LISTEN_PORT))
            s.listen()
            print(f"[Listener] waiting on port {LISTEN_PORT} …")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handler, args=(conn, addr), daemon=True).start()

    threading.Thread(target=listen, daemon=True).start()

def perform_handshake(peer_ip, local_username):
    handshake = json.dumps({
        "type":       "handshake",
        "username":   local_username,
        "public_key": get_own_pubkey()
    }).encode()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_ip, LISTEN_PORT))
            s.sendall(handshake)
            resp = s.recv(8192)
            msg = json.loads(resp.decode())
            if msg.get("type") == "handshake":
                peer_username = msg["username"]
                peer_pubkey   = msg["public_key"]
                FriendService.add_friend(peer_username, peer_ip, LISTEN_PORT, peer_pubkey)
                print(f"[Handshake] Completed with {peer_username}")
                return peer_username
    except Exception as e:
        print(f"[Handshake error] {e}")

    return None

def chat_loop(peer_username):
    print("💬 Chat now (type 'exit' to quit)")
    while True:
        text = input("You: ")
        if text.strip().lower() in ("exit", "quit"):
            break

        contact   = MessageService.get_contact_by_username(peer_username)
        ciphertext = MessageService.encrypt(contact.session_key, text)

        payload = json.dumps({
            "type": "message",
            "body": ciphertext.hex()
        }).encode()

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((contact.ip, contact.port))
                s.sendall(payload)
        except Exception as e:
            print(f"[Send error] {e}")

def main():
    ensure_device()
    local_username = input("🔑 Enter your username: ").strip()
    start_listener(local_username)
    peer_ip = input("🔌 Enter peer IP to connect: ").strip()
    peer_username = perform_handshake(peer_ip, local_username)
    if peer_username:
        chat_loop(peer_username)

if __name__ == "__main__":
    main()