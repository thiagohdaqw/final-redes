import socket
import pathlib
from .server import Server
from . import http

class HttpServer(Server):
    routes: list[http.Route]

    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)
        self.routes = [self._route_send_file]

    _decode_data    = lambda _, data: http.decode_data(data)
    _encode_messages = lambda _, messages: http.encode_messages(messages)

    def _handle_writable(self, output: socket.socket):
        ...

    def _intercept_message(self, conn, message):
        ...
    
    def _handle_message(self, conn, message, data):
        ...

    def _manage_message(self, conn: socket.socket):
        data = conn.recv(10000)

        try:
            if data:
                return self._manage_data(conn, data)
        except Exception as ex:
            print("[EXCEPTION]:", ex)
        self._close_connection(conn)

    def _manage_data(self, conn: socket.socket, data: bytes):
        message = self._decode_data(data)

        if len(message.strip()) == 0:
            return

        if self._intercept_message(conn, message):
            return

        for route in reversed(self.routes):
            if route(conn=conn, message=message, data=data):
                return
        self._handle_message(conn, message, data)

    @http.HttpRoute(http.Methods.GET)
    def _route_send_file(self, conn, message, data):
        _, filename, *_ = message.split()
        filename = "index.html" if filename == "/" else filename[1:]
        pages_path = pathlib.Path("./pages")
        file = pages_path / filename

        if file.exists() and file.is_file():
            status = b"200 OK"
        else:
            status = b"404 Not Found"
            file = pages_path / "notfound.html"

        conn.sendall(b"HTTP/1.1 " + status + b"\nConnection: Closed\n\n")
        conn.sendall(file.read_bytes())
        self._close_connection(conn)
