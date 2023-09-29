# Padding Oracle

This repository implements a [padding oracle](https://en.wikipedia.org/wiki/Padding_oracle_attack) server. A client can
send the server a ciphertext. The server will then verify the validity of the PKCS#7 padding of AES encrypted
ciphertexts.

## Installation

Install the `paddingoracle` command using

```shell
pip install .
```

To run using Docker, build the Dockerfile using

```shell
docker build -t paddingoracle .
```

And then run the container using

```shell
docker run paddingoracle
```

Environment variables can be passed like

```shell
docker run -e MC_PADDING_KEY=69abbb5a5b0a8f7740717105a25f9698 paddingoracle
```

## Configuration

Environment variables:

- `MC_PADDING_KEY`: By default the server generates a random key. If this variable is set, then it is interpreted as
  the hexadecimal value of the key.
- `MC_PADDING_MESSAGE`: If this environment variable is set, then the CBC encryption of this message is printed on
  startup.

## Usage

A client can open a TCP connection to the server. The server can receive messages of the following byte format

```
<num_blocks> || IV || <block_2> || .. || <block_n> || 0x00
```

The number of blocks is a single byte, whose numeric value indicates the number of blocks (including the IV). When the
number of blocks is 0, then the server closes the connection. If the message format is invalid, then the server also
closes the connection. When the message format is valid, the server will decrypt the message, and verify the padding.
If the padding is valid, the server sends the ASCII code for `1` (0x31) back. If the padding is invalid, then the
server sends the ASCII code for `0` (0x30). As long as all the messages are valid, the client can reuse the connection
to the server.