import os
import socket
import traceback
from secrets import token_bytes
from threading import Thread
from typing import Callable

from paddingoracle.aes import valid_cipher, encrypt, pad, BLOCK_LENGTH


def send_answer(conn: socket, oracle: Callable[[bytes], bool]):
    while True:
        raw_length = conn.recv(1)
        if not raw_length:
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


def answer(k: bytes, conn: socket.socket):
    def oracle(c: bytes) -> bool:
        return valid_cipher(k, c)

    try:
        send_answer(conn, oracle)
    finally:
        conn.close()


def main():
    k = read_key()

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
        t = Thread(target=answer, args=(k, conn))
        t.start()


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
