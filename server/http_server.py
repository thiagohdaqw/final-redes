import socket
import pathlib
from .server import Server
from .logger import logger


class HttpServer(Server):
    def __init__(self, ip, port, max_connections):
        super().__init__(ip, port, max_connections)

    def _handle_message(self, sock: socket.socket, message: str):
        ...

    def _handle_writable(self, sock: socket.socket):
        ...

    def _manage_message(self, conn: socket.socket):
        data = conn.recv(1024)

        try:
            if data:
                message = data.decode("utf-8")
                if len(message.strip()) == 0:
                    return

                command = message.split()[0]
                if command == "GET":
                    logger(conn, "Requisitando pagina", data)
                    self._handle_http_get(conn, message)
                else:
                    self._handle_message(conn, message)
                return
        except Exception:
            logger(conn, "Desconectando...")
        self._close_connection(conn)

    def _handle_http_get(self, conn, msg):
        method, filename, *headers = msg.split()
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
