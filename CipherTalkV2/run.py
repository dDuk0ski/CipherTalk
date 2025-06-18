import os
import json
import socket
import threading
import time
import uuid

from crypto_service   import CryptoService
from keystore         import KeyStore
from local_storage    import LocalStorage, Session, Contact
from friend_service   import FriendService
from message_service  import MessageService
from file_service     import FileService
from code_service     import CodeService
from ServerService    import ServerService
from group_service    import GroupService
import log_service

LISTEN_PORT = 9000

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def ensure_device():
    path = os.path.expanduser("~/.cipher_talk/keys/device_private.key")
    if not os.path.exists(path):
        priv, pub = CryptoService.generate_keypair()
        KeyStore.seal("device_private", CryptoService.serialize_private(priv))
        LocalStorage.save_device(str(uuid.uuid4()), CryptoService.serialize_public(pub))
        print(f"[Device] New identity created: {CryptoService.serialize_public(pub)}")
    else:
        print("[Device] Identity already initialized.")

def status_pinger():
    """Ping contacts every 30s to update .online flag."""
    while True:
        sess = Session()
        for c in sess.query(Contact).all():
            try:
                req = json.dumps({"type":"status_request"}).encode()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(2)
                    s.connect((c.ip, c.port))
                    s.sendall(req)
                    resp = s.recv(4096)
                    msg  = json.loads(resp.decode())
                    c.online = (msg.get("type")=="status_response")
            except:
                c.online = False
        sess.close()
        time.sleep(30)

def show_friends():
    sess = Session()
    rows = sess.query(Contact).order_by(Contact.username).all()
    sess.close()
    print("\nYour Friends:")
    for c in rows:
        icon = "🟢" if getattr(c, "online", False) else "⚪"
        print(f"  {icon} {c.username} @ {c.ip}:{c.port}")
    print()
    return rows

def chat_with(friend_username, local_username):
    contact = MessageService.get_contact_by_username(friend_username)
    print(f"\n💬 Chat with {friend_username}")
    print("  • Type your message and press Enter")
    print("  • To send a file: `/send_file /full/path/to/file.ext`")
    print("  • To exit chat: `/exit`\n")

    # load and display history
    skey = bytes.fromhex(contact.session_key)
    for ts, snd, txt in log_service.load_private_history(friend_username, skey):
        print(f"[{ts}][{snd}] {txt}")

    while True:
        line = input(f"{friend_username}> ").strip()
        if not line:
            continue
        if line.lower() in ("/exit", "exit"):
            break

        # FILE SEND
        if line.startswith("/send_file "):
            path = line[len("/send_file "):].strip()
            if not os.path.isfile(path):
                print(f"❌ File not found: {path}")
                continue
            enc = FileService.encrypt_file(contact.session_key, path)
            pkt = {
                "type":     "file_chunk",
                "from":     local_username,
                "to":       friend_username,
                "filename": os.path.basename(path),
                "body":     enc.hex()
            }
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", LISTEN_PORT))
                s.sendall(json.dumps(pkt).encode())
            log_service.log_private_message(friend_username, local_username, enc.hex())
            print(f"✅ Sent file: {os.path.basename(path)}")
            continue

        # TEXT MESSAGE
        ct = MessageService.encrypt(contact.session_key, line)
        pkt = {
            "type":"chat_msg",
            "from": local_username,
            "to":   friend_username,
            "body": ct.hex()
        }
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", LISTEN_PORT))
            s.sendall(json.dumps(pkt).encode())
        log_service.log_private_message(friend_username, local_username, ct.hex())

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    ensure_device()
    local_username = input("🔑 Enter your nickname: ").strip()

    # start server relay & status pinger
    server = ServerService(host="0.0.0.0", port=LISTEN_PORT, local_username=local_username)
    server.start()
    threading.Thread(target=status_pinger, daemon=True).start()
    print(f"[ServerService] Listening on port {LISTEN_PORT}")

    # menu loop
    while True:
        print("""
=== Main Menu ===
1) Generate ID code
2) Add friend
3) Friend list
4) Chats
5) Create group chat
6) Server panel
7) Setup
8) Exit
""")
        choice = input("Select [1–8]: ").strip()

        if choice == "1":
            ip = input("Enter your public IP: ").strip()
            code = CodeService.generate_code(local_username, ip, LISTEN_PORT)
            print(f"\nYour ID code:\n{code}\n")

        elif choice == "2":
            code = input("Paste friend’s ID code: ").strip()
            try:
                info = CodeService.decode_code(code)
                FriendService.add_friend(
                    info['username'], info['ip'], int(info['port']), info['public_key']
                )
                print(f"\n✅ Added: {info['username']}\n")
            except Exception as e:
                print(f"\n❌ Invalid code: {e}\n")

        elif choice == "3":
            show_friends()

        elif choice == "4":
            show_friends()
            friend = input("Enter friend username (blank to cancel): ").strip()
            if friend:
                chat_with(friend, local_username)

        elif choice == "5":
            show_friends()
            raw = input("Enter friend usernames to include (comma‐separated): ").strip()
            members = [u.strip() for u in raw.split(",") if u.strip()]
            if not members:
                print("\n❌ No members selected.\n")
            else:
                group_name = "_".join(members)
                gid = GroupService.create_group(
                    group_name, local_username, members,
                    server.host, server.port
                )
                print(f"\n✅ Group '{group_name}' created as ID {gid}\n")

        elif choice == "6":
            s = server.get_stats()
            print(f"\nServer Panel:\n  Sessions: {s['sessions']}\n  In: {s['packets_in']}  Out: {s['packets_out']}\n")

        elif choice == "7":
            print("""
Quick Setup Guide:
1. Find your public IP (e.g. https://ifconfig.me).
2. Forward TCP port 9000 → your PC’s 9000.
3. Allow TCP 9000 through firewall.
4. Run: python run.py, enter your nickname.
5. Share ID code or use Add friend.
""")

        elif choice == "8":
            print("\nGoodbye!")
            break

        else:
            print("\n❓ Invalid choice. Pick 1–8.\n")

    server.stop()

if __name__ == "__main__":
    main()
