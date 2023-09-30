import asyncio
from typing import Callable

from paddingoracle.aes import valid_cipher, BLOCK_LENGTH
from paddingoracle.common import read_key


async def handle_oracle(oracle: Callable[[bytes], bool], reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr, _port = writer.get_extra_info('peername')
    print("Opened connection from", addr)

    while True:
        raw_length = await reader.read(1)
        if not raw_length:
            break

        num_blocks = raw_length[0]

        if num_blocks == 0:
            break

        try:
            c = await reader.readexactly(num_blocks * BLOCK_LENGTH + 1)
        except asyncio.IncompleteReadError:
            raise ValueError(f"{addr}: invalid number of blocks: {num_blocks}")

        if c[-1] != 0:
            raise ValueError(f"{addr}: message does not end with 0")

        if oracle(c[:-1]):
            ans = b"1\x00"
        else:
            ans = b"0\x00"

        writer.write(ans)
        await writer.drain()

    print("Closing connection from", addr)


async def main():
    k = read_key()

    async def cb(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        def oracle(c: bytes) -> bool:
            return valid_cipher(k, c)

        await handle_oracle(oracle, reader, writer)

    ip = "0.0.0.0"
    port = 8080

    print(f"Listening on {ip}:{port}")

    async with await asyncio.start_server(cb, ip, port) as s:
        await s.serve_forever()


def wrapper():
    asyncio.run(main())


if __name__ == "__main__":
    wrapper()
