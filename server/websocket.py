import base64
import hashlib
from typing import Optional


class Codes:
    MESSAGE = 0x81
    PING = 0x9
    PONG = 0xA


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
    mask = data[2:6]
    payload = data[6:]

    return "".join(decode_bytes(payload, mask))


def decode_bytes(payload, mask):
    for index, value in enumerate(payload):
        decoded = value ^ mask[index % 4]
        yield chr(decoded)
