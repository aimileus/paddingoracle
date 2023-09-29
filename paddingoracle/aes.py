from secrets import token_bytes

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BLOCK_LENGTH = 16


def cbc(key: bytes, iv: bytes) -> Cipher:
    return Cipher(algorithms.AES(key), modes.CBC(iv))


def decrypt(k: bytes, c: bytes):
    iv = c[:BLOCK_LENGTH]
    b1 = c[BLOCK_LENGTH:]

    cipher: Cipher = cbc(k, iv)
    decryptor = cipher.decryptor()

    plain = decryptor.update(b1) + decryptor.finalize()

    assert len(plain) == len(c) - BLOCK_LENGTH

    return plain


def encrypt(k: bytes, m: bytes):
    iv = token_bytes(BLOCK_LENGTH)

    cipher = cbc(k, iv)
    encryptor = cipher.encryptor()
    return iv + encryptor.update(m) + encryptor.finalize()


def pad(m: bytes):
    padder = padding.PKCS7(BLOCK_LENGTH * 8).padder()
    return padder.update(m) + padder.finalize()


def valid_cipher(k: bytes, c: bytes) -> bool:
    m = decrypt(k, c)
    return valid_padding(m)


def valid_padding(m: bytes) -> bool:
    unpadder = padding.PKCS7(BLOCK_LENGTH * 8).unpadder()

    try:
        _unpadded = unpadder.update(m) + unpadder.finalize()
    except ValueError:
        return False
    else:
        return True
