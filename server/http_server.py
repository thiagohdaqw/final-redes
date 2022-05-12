import socket
import pathlib
from typing import TextIO
from .server import Server
from .logger import logger

class Methods:
    GET = "GET"
    POST = "POST"


class HttpServer(Server):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)

    def _handle_message(self, sock: socket.socket, message: str, data: bytes):
        ...

    def _handle_writable(self, output: socket.socket):
        ...

    def _manage_message(self, conn: socket.socket):
        data = conn.recv(2048)

        try:
            if data:
                return self._manage_data(conn, data)
        except Exception:
            ...
        self._close_connection(conn)

    def _manage_data(self, conn: socket.socket, data: bytes):
        message = self._decode_data(data)

        if len(message.strip()) == 0:
            return

        command = message.split()[0]
        if command == Methods.GET:
            logger(conn, "Requisição GET", data)
            method, filename, *headers = message.split()
            self._handle_http_get(conn, filename, headers)
        else:
            self._handle_message(conn, message, data)

    def _decode_data(self, data: bytes):
        return data.decode("utf-8")

    def _handle_http_get(self, conn, filename, headers):
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
