import socket
from .websocket_server import WebSocketServer
from .channel import Channels, MessageType

class ChannelServer(WebSocketServer):
    channels: Channels

    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)
        self.channels = Channels(self.send_message, self.outputs)

    def _handle_writable(self, output: socket.socket):
        self.channels.send_channel_message(output)

    def _handle_message(self, conn: socket.socket, message: str, data: bytes):
        self.channels.manage_commands(conn, message)

    def _intercept_message(self, conn, message):
        webcam_data = "data:image/jpeg;"
        if message.startswith(webcam_data):
            print("recebi webcam")
            self.channels.manage_data(conn, message, MessageType.WEBCAM)
            return True
        return False

    def _close_connection(self, conn):
        self.channels.exit_channel(conn)
        super()._close_connection(conn)
