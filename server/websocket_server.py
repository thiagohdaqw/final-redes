import socket
import sys
from typing import TextIO
from .http_server import HttpServer
from . import websocket as ws


class WebSocketServer(HttpServer):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)
        self.inputs.append(sys.stdin)

    def _handle_http_get(self, conn, filename, headers):
        if filename == "/chat":
            self._handle_handshake(conn, headers)
        else:
            super()._handle_http_get(conn, filename, headers)

    def _handle_handshake(self, conn, headers):
        client_key = ws.get_key(headers)

        if not client_key:
            return self._close_connection(conn)

        response = ws.build_handshake_response(client_key)
        conn.sendall(response)

    def _decode_data(self, data: bytes):
        if data[0] == ws.Codes.MESSAGE:
            return ws.decode_data(data)
        else:
            print("\n", data, "\n")
            return super()._decode_data(data)

    def _handle_message(self, sock, message: str, data: bytes):
        print("-" * 50)
        print(message)
        print("-" * 50)

    def _manage_textio(self, input: TextIO):
        byte_max = 255
        msg = input.readline()[:byte_max].encode("utf-8")

        int_to_bytes = lambda i, l=1: i.to_bytes(l, 'big')
        length = int_to_bytes(len(msg))
        op = int_to_bytes(ws.Codes.MESSAGE)
        response = op + length + msg

        for client in self.clients:
            client.sendall(response)
