import socket
import threading
import json
import logging
import os
import uuid

from local_storage import Session, Contact, LocalStorage, Group, GroupMember
from message_service import MessageService
from file_service import FileService
from group_service import GroupService
from tcp_connection import TCPConnection
import log_service  # NEW

MEDIA_DIR = os.path.expanduser("~/cipher_talk/media")
os.makedirs(MEDIA_DIR, exist_ok=True)

class ServerService:
    def __init__(self, host='0.0.0.0', port=9000, local_username=None):
        self.host           = host
        self.port           = port
        self.local_username = local_username
        self.running        = False
        self.server_socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lock           = threading.Lock()
        self.stats          = {'sessions': 0, 'packets_in': 0, 'packets_out': 0}
        logging.basicConfig(level=logging.DEBUG)

    def start(self):
        self.running = True
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.server_socket.close()

    def _accept_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                with self.lock:
                    self.stats['sessions'] += 1
                threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
            except OSError:
                break

    def _handle_client(self, sock, addr):
        try:
            data = sock.recv(16_384)
            if not data:
                return
            with self.lock:
                self.stats['packets_in'] += 1

            pkt   = json.loads(data.decode())
            ptype = pkt.get('type')

            # — STATUS PING —
            if ptype == 'status_request':
                resp = json.dumps({"type":"status_response","username":self.local_username}).encode()
                sock.sendall(resp)
                with self.lock:
                    self.stats['packets_out'] += 1
                return
            if ptype == 'status_response':
                return

            # — Handshake —
            if ptype == 'handshake':
                from friend_service import FriendService
                FriendService.add_friend(
                    pkt['username'], addr[0], pkt.get('port',self.port), pkt['public_key']
                )
                resp = {
                    "type":       "handshake",
                    "username":   self.local_username,
                    "public_key": MessageService.get_own_pubkey(),
                    "port":       self.port
                }
                sock.sendall(json.dumps(resp).encode())
                return

            # — Private chat relay & logging —
            if ptype == 'chat_msg':
                sender, recipient = pkt['from'], pkt['to']
                if recipient == self.local_username:
                    contact = Session().query(Contact).filter_by(username=sender).first()
                    pt = MessageService.decrypt(contact.session_key, bytes.fromhex(pkt['body']))
                    print(f"\n[{sender}] {pt}")
                    log_service.log_private_message(sender, sender, pkt['body'])
                else:
                    c = Session().query(Contact).filter_by(username=recipient).first()
                    if c:
                        TCPConnection.send(c.ip, c.port, data)
                        with self.lock:
                            self.stats['packets_out'] += 1
                return

            # — File relay —
            if ptype == 'file_chunk':
                sender, recipient = pkt['from'], pkt['to']
                fname = pkt.get('filename')
                if recipient == self.local_username:
                    contact = Session().query(Contact).filter_by(username=sender).first()
                    outp    = os.path.join(MEDIA_DIR, f"{sender}_{uuid.uuid4().hex[:8]}_{fname}")
                    FileService.decrypt_file(contact.session_key, bytes.fromhex(pkt['body']), outp)
                    print(f"\n[{sender}] 📁 File saved: {outp}")
                else:
                    c = Session().query(Contact).filter_by(username=recipient).first()
                    if c:
                        TCPConnection.send(c.ip, c.port, data)
                        with self.lock:
                            self.stats['packets_out'] += 1
                return

            # — Group handshake (key distribution) —
            if ptype == 'group_handshake':
                sender    = pkt['from']
                gid       = pkt['group_id']
                name      = pkt.get('group_name')
                enc_key   = bytes.fromhex(pkt['body'])
                contact   = Session().query(Contact).filter_by(username=sender).first()
                group_key = MessageService.decrypt(contact.session_key, enc_key)
                LocalStorage.save_group(gid, name, pkt.get('to'), group_key)
                LocalStorage.save_group_member(str(uuid.uuid4()), gid, self.local_username, group_key)
                print(f"[Group] Joined '{name}' ({gid})")
                return

            # — Group message relay & logging —
            if ptype == 'group_msg':
                sender, gid = pkt['from'], pkt['group_id']
                sess   = Session()
                grp    = sess.query(Group).filter_by(group_id=gid).first()
                members= sess.query(GroupMember).filter_by(group_id=gid).all()
                sess.close()

                # If I'm host, forward to everyone except sender
                if self.local_username == grp.owner:
                    for m in members:
                        if m.username != sender:
                            c = Session().query(Contact).filter_by(username=m.username).first()
                            if c:
                                TCPConnection.send(c.ip, c.port, data)
                                with self.lock:
                                    self.stats['packets_out'] += 1

                # Decrypt & print using nickname
                for m in members:
                    if m.username == self.local_username:
                        group_key = bytes.fromhex(grp.group_key)
                        txt       = GroupService.decrypt_group(group_key, bytes.fromhex(pkt['body']))
                        sender_nm = next((x.nickname for x in members if x.username==sender), sender)
                        print(f"\n[{grp.name}][{sender_nm}] {txt}")
                        log_service.log_group_message(gid, sender_nm, pkt['body'])
                return

            logging.debug(f"Unknown packet type '{ptype}' from {addr}")
        except Exception as e:
            logging.error(f"[ServerService error] {e}")
        finally:
            sock.close()
            with self.lock:
                self.stats['sessions'] -= 1

    def get_stats(self):
        with self.lock:
            return dict(self.stats)