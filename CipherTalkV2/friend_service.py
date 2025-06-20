import uuid
from cryptography.hazmat.primitives.asymmetric import x25519

from local_storage import LocalStorage


class FriendService:
    @staticmethod
    def add_friend(username: str, ip: str, port: int, peer_pubkey_hex: str):
        # Load our private key from storage
        our_priv_hex = LocalStorage.load_private_key()
        our_priv_bytes = bytes.fromhex(our_priv_hex)
        our_priv = x25519.X25519PrivateKey.from_private_bytes(our_priv_bytes)

        # Deserialize peer public key
        peer_pub_bytes = bytes.fromhex(peer_pubkey_hex)
        peer_pub = x25519.X25519PublicKey.from_public_bytes(peer_pub_bytes)

        # Perform key exchange
        shared_key = our_priv.exchange(peer_pub)
        shared_key_hex = shared_key.hex()

        # Save contact
        contact_id = str(uuid.uuid4())
        LocalStorage.save_contact(contact_id, username, ip, port, peer_pubkey_hex, shared_key_hex)
        return contact_id
