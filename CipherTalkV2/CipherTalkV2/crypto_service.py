import os
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import HexEncoder

class CryptoService:
    @staticmethod
    def generate_keypair():
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        return private_key, public_key

    @staticmethod
    def serialize_private(priv: PrivateKey) -> str:
        return priv.encode(encoder=HexEncoder).decode()

    @staticmethod
    def serialize_public(pub: PublicKey) -> str:
        return pub.encode(encoder=HexEncoder).decode()

    @staticmethod
    def deserialize_private(hex_str: str) -> PrivateKey:
        return PrivateKey(hex_str, encoder=HexEncoder)

    @staticmethod
    def deserialize_public(hex_str: str) -> PublicKey:
        return PublicKey(hex_str, encoder=HexEncoder)
