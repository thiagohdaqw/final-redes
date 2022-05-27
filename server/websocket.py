import base64
import hashlib
from typing import Optional

# 5.2.  Base Framing Protocol - https://datatracker.ietf.org/doc/html/rfc6455#section-5.2
PAYLOAD_MAX_LENGTH = 126 # in bytes

class Codes:
    MESSAGE    = 0b10000001
    CLOSE   = 0b10001000
    PING    = 0b10001001
    PONG    = 0x10001010


def get_key(headers) -> Optional[str]:
    try:
        key_index = headers.index("Sec-WebSocket-Key:") + 1
        return headers[key_index]
    except ValueError:
        return None


def generate_security_key(client_key: str) -> bytes:
    client_key_guid = client_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    sha1_key = hashlib.sha1(client_key_guid.encode("utf-8")).digest()
    b64_key = base64.b64encode(sha1_key)
    return b64_key


def build_handshake_response(client_key: str) -> bytes:
    security_key = generate_security_key(client_key)

    response = b"HTTP/1.1 101 Switching Protocols\n"
    response += b"Upgrade: websocket\n"
    response += b"Connection: Upgrade\n"
    response += b"Sec-WebSocket-Accept: " + security_key + b"\n\n"
    return response


def decode_data(data: bytes) -> str:
    # https://datatracker.ietf.org/doc/html/rfc6455#section-5.2
    payload_length = data[1] & 0b1111111 # 127

    if payload_length < PAYLOAD_MAX_LENGTH:
        mask = data[2:6]
        payload = data[6:]
    elif payload_length == PAYLOAD_MAX_LENGTH:
        breakpoint()
        mask = data[4:8]
        payload = data[8:]
    else:
        raise NotImplemented("Data greater than 2**17-1 were not implemented")

    return "".join(decode_bytes(payload, mask))


def decode_bytes(payload, mask):
    for index, value in enumerate(payload):
        decoded = value ^ mask[index % 4]
        yield chr(decoded)

def encode_message(message: str) -> bytes:
    msg_bytes = message.encode('utf-8')
    msg_length = len(msg_bytes)

    op = int_to_bytes(Codes.MESSAGE)

    if msg_length <= PAYLOAD_MAX_LENGTH:
        return op + int_to_bytes(msg_length) + msg_bytes
    else:
        len1, len2 = int_to_bytes(msg_length, 2)
        return op + int_to_bytes(PAYLOAD_MAX_LENGTH) + int_to_bytes(len1) + int_to_bytes(len2) + msg_bytes

def int_to_bytes(integer, length = 1):
    return integer.to_bytes(length, 'big')