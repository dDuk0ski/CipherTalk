import uuid
from crypto_service import CryptoService
from local_storage import LocalStorage


class FriendService:
    @staticmethod
    def add_friend(username: str, ip: str, port: int, peer_pubkey_hex: str):
        our_priv_hex = LocalStorage.load_private_key()
        our_priv = CryptoService.deserialize_private(our_priv_hex)
        peer_pub = CryptoService.deserialize_public(peer_pubkey_hex)

        shared_key = our_priv.exchange(peer_pub)
        shared_key_hex = shared_key.hex()

        contact_id = str(uuid.uuid4())
        LocalStorage.save_contact(contact_id, username, ip, port, peer_pubkey_hex, shared_key_hex)
        return contact_id