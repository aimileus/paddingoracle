import os
from secrets import token_bytes

from paddingoracle.aes import pad, encrypt


def read_key():
    try:
        hex_key = os.environ["MC_PADDING_KEY"]

        k = bytes.fromhex(hex_key)
        print(f"Using configured key:", k.hex())

        assert len(k) == 16

    except KeyError:
        k = token_bytes(16)
        print(f"Using random key", k.hex())

    message = os.environ.get("MC_PADDING_MESSAGE", None)
    if message:
        padded = pad(message.encode())
        print("Padded message:", padded.hex())
        print("Encrypted message:", encrypt(k, padded).hex())

    return k
