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
from qr_service import QRService

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

def connect_via_qr_code(local_username):
    """Connect to a peer using QR code or text code"""
    print("\n📱 QR Code Connection Options:")
    print("1. Enter connection code manually")
    print("2. Scan QR code (manual process)")
    print("3. Go back")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        print("\n📝 Enter the connection code:")
        connection_code = input("Paste the connection code here: ").strip()
        
        # Parse the connection data
        connection_data = QRService.parse_connection_data(connection_code)
        if connection_data:
            peer_username = connection_data["username"]
            peer_ip = connection_data["ip"]
            peer_port = connection_data["port"]
            peer_pubkey = connection_data["public_key"]
            
            print(f"\n🔗 Attempting to connect to {peer_username} at {peer_ip}:{peer_port}")
            
            # Perform handshake
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_ip, peer_port))
                    
                    # Send handshake
                    handshake = json.dumps({
                        "type": "handshake",
                        "username": local_username,
                        "public_key": get_own_pubkey()
                    }).encode()
                    s.sendall(handshake)
                    
                    # Receive response
                    resp = s.recv(8192)
                    msg = json.loads(resp.decode())
                    
                    if msg.get("type") == "handshake":
                        FriendService.add_friend(peer_username, peer_ip, peer_port, peer_pubkey)
                        print(f"✅ Successfully connected to {peer_username}")
                        return peer_username
                    else:
                        print("❌ Invalid handshake response")
                        return None
                        
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return None
        else:
            print("❌ Invalid connection code")
            return None
    
    elif choice == "2":
        print("\n📷 QR Code Scanning:")
        print("1. Open the QR code image on another device")
        print("2. Use a QR code scanner app to read it")
        print("3. Copy the scanned text and use option 1")
        input("Press Enter when ready...")
        return connect_via_qr_code(local_username)  # Recursive call
    
    elif choice == "3":
        return None
    
    else:
        print("❌ Invalid choice")
        return connect_via_qr_code(local_username)  # Recursive call

def main():
    ensure_device()
    local_username = input("🔑 Enter your username: ").strip()
    
    # Generate and display connection information
    print(f"\n🔄 Generating connection information for {local_username}...")
    QRService.generate_and_save_connection_info(local_username, get_own_pubkey(), LISTEN_PORT)
    
    start_listener(local_username)
    
    print("\n🔌 Connection Options:")
    print("1. Connect via IP address")
    print("2. Connect via QR code/text code")
    
    choice = input("Choose connection method (1-2): ").strip()
    
    if choice == "1":
        # Original IP-based connection
        peer_ip = input("🔌 Enter peer IP to connect: ").strip()
        peer_username = perform_handshake(peer_ip, local_username)
    elif choice == "2":
        # QR code based connection
        peer_username = connect_via_qr_code(local_username)
    else:
        print("❌ Invalid choice, using IP connection")
        peer_ip = input("🔌 Enter peer IP to connect: ").strip()
        peer_username = perform_handshake(peer_ip, local_username)
    
    if peer_username:
        chat_loop(peer_username)

if __name__ == "__main__":
    main()