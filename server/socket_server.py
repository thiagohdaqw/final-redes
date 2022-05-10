import socket
from .http_server import HttpServer
from .channel import Channels

class SocketServer(HttpServer):
    channels: Channels

    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)
        self.channels = Channels(self.server, self.outputs)

    def _handle_writable(self, sock: socket.socket):
        self.channels.manage_commands(sock)

    def _handle_message(self, conn: socket.socket, message: str):
        self.channels.manage_commands(conn, message)

    def _close_connection(self, conn):
        self.channels.exit_channel(conn)
        super()._close_connection(conn)
