import socket
from .server import Server


class WebSocketServer(Server):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)

    def _manage_message(self, sock: socket.socket):
        ...

    def _handle_writable(self, sock: socket.socket):
        ...
