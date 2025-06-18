import pytest
from crypto_service import CryptoService
from nacl.public import PrivateKey, PublicKey

def test_generate_keypair_types():
    priv, pub = CryptoService.generate_keypair()
    assert isinstance(priv, PrivateKey)
    assert isinstance(pub, PublicKey)

@pytest.mark.parametrize("text", ["hello", "1234", ""])
def test_serialize_deserialize_roundtrip(text):
    # generate a fresh keypair, serialize/deserialize, and ensure round-trip
    priv, pub = CryptoService.generate_keypair()
    priv_hex = CryptoService.serialize_private(priv)
    pub_hex  = CryptoService.serialize_public(pub)

    # re-deserialize
    priv2 = CryptoService.deserialize_private(priv_hex)
    pub2  = CryptoService.deserialize_public(pub_hex)

    # serializing again yields the same hex
    assert CryptoService.serialize_private(priv2) == priv_hex
    assert CryptoService.serialize_public(pub2)  == pub_hex

def test_invalid_deserialize_public():
    with pytest.raises(Exception):
        # not a valid hex ⇒ should raise
        CryptoService.deserialize_public("deadbeef")

def test_invalid_deserialize_private():
    with pytest.raises(Exception):
        CryptoService.deserialize_private("00ff00ff")
