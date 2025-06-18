import os
import pytest
from message_service import MessageService

# Use a fixed 32-byte key for repeatable tests
FIXED_KEY = bytes(range(32)).hex()

@pytest.mark.parametrize("plaintext", ["", "a", "The quick brown fox"])
def test_encrypt_decrypt_roundtrip(plaintext):
    enc = MessageService.encrypt(FIXED_KEY, plaintext)
    # encrypted data is longer than plaintext
    assert isinstance(enc, bytes)
    assert len(enc) > len(plaintext)

    dec = MessageService.decrypt(FIXED_KEY, enc)
    assert dec == plaintext

def test_decrypt_tampered():
    enc = MessageService.encrypt(FIXED_KEY, "secure")
    # flip a byte
    tampered = bytearray(enc)
    tampered[len(tampered)//2] ^= 0xFF
    with pytest.raises(Exception):
        MessageService.decrypt(FIXED_KEY, bytes(tampered))

def test_encrypt_varies_nonce():
    e1 = MessageService.encrypt(FIXED_KEY, "hello")
    e2 = MessageService.encrypt(FIXED_KEY, "hello")
    # different nonces ⇒ ciphertext should differ
    assert e1 != e2
