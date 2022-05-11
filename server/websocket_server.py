from .http_server import HttpServer
from . import websocket as ws


class WebSocketServer(HttpServer):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)

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
