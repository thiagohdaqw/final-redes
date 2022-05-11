import base64
import hashlib
import socket
from typing import Optional
from .http_server import HttpServer


class Codes:
    MESSAGE = 0x81
    PING = 0x9
    PONG = 0xA


class WebSocketServer(HttpServer):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)

    def _handle_http_get(self, conn, filename, headers):
        if filename == "/chat":
            self._handle_handshake(conn, headers)
        else:
            super()._handle_http_get(conn, filename, headers)

    def _handle_handshake(self, conn, headers):
        client_key = get_key(headers)

        if not client_key:
            return self._close_connection(conn)

        response = build_handshake_response(client_key)
        conn.sendall(response)

    def _decode_data(self, data: bytes):
        if data[0] == Codes.MESSAGE:
            return decode_data(data)
        else:
            print("\n", data, "\n")
            return super()._decode_data(data)

    def _handle_message(self, sock, message: str, data: bytes):
        print("-" * 50)
        print(message)
        print("-" * 50)


def get_key(headers) -> Optional[str]:
    try:
        key_index = headers.index("Sec-WebSocket-Key:") + 1
        return headers[key_index]
    except ValueError:
        return None


def get_security_key(client_key: str) -> bytes:
    client_key_guid = client_key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    sha1_key = hashlib.sha1(client_key_guid.encode("utf-8")).digest()
    b64_key = base64.b64encode(sha1_key)
    return b64_key


def build_handshake_response(client_key: str) -> bytes:
    security_key = get_security_key(client_key)
    
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
