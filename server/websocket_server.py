from .http_server import HttpServer
from . import websocket as ws, http


class WebSocketServer(HttpServer):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)
        self.routes.append(self._handle_handshake)

    @http.HttpRoute(route='/chat')
    def _handle_handshake(self, conn, message, data):
        client_key = ws.get_key(message.split())

        if not client_key:
            return self._close_connection(conn)

        response = ws.build_handshake_response(client_key)
        conn.sendall(response)

    _encode_message = lambda _, message: ws.encode_message(message)

    def _decode_data(self, data: bytes):
        if data[0] == ws.Codes.CLOSE:
            raise Exception("Fechar conexão")
        if data[0] == ws.Codes.MESSAGE:
            return ws.decode_data(data)
        else:
            return super()._decode_data(data)

    def _handle_message(self, conn, message, data):
        print("-" * 50)
        print(message)
        print("-" * 50)
