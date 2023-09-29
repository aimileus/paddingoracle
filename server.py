import os
import socket
import traceback
from secrets import token_bytes
from typing import Callable

from aes import valid_cipher, encrypt, pad, BLOCK_LENGTH


def answer(oracle: Callable[[bytes], bool], conn: socket.socket):
    while True:
        if not (raw_length := conn.recv(1)):
            return

        num_blocks = raw_length[0]

        if num_blocks == 0:
            return

        c = conn.recv(num_blocks * BLOCK_LENGTH + 1)

        if c[-1] != 0:
            raise ValueError("Message does not end with 0")

        if oracle(c[:-1]):
            conn.send(b"1\x00")
        else:
            conn.send(b"0\x00")


def main():
    k = read_key()

    def oracle(c: bytes) -> bool:
        return valid_cipher(k, c)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ip = "0.0.0.0"
    port = 8080

    soc.bind((ip, port))
    print(f"Listening on {ip}:{port}")
    soc.listen()

    while True:
        conn, (addr, port) = soc.accept()
        print(f"Opened connection from {addr}")

        # noinspection PyBroadException
        try:
            answer(oracle, conn)
        except Exception:
            traceback.print_exc()
        finally:
            conn.close()


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
        print("Encrypted message:", encrypt(k, padded).hex())

    return k


if __name__ == "__main__":
    main()
