import socket
import select
from abc import ABC, abstractclassmethod
from .logger import logger


class Server(ABC):
    server: socket.socket
    ip: str
    port: int
    max_connections: int
    inputs: list[socket.socket]
    outputs: list[socket.socket]
    clients: list[socket.socket]

    def __init__(self, ip, port, max_connections):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.ip = ip
        self.port = port
        self.max_connections = max_connections
        self.inputs = [self.server]
        self.outputs = []
        self.clients = []

    def start(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        self.server.listen(self.max_connections)
        self._run()

    def close(self):
        print("Fechando conexões")
        for client in self.clients:
            client.close()
        self.server.close()

    def _run(self):
        print("Aguardando em ", (self.ip, self.port))

        while self.inputs:
            readable, writable, exceptional = select.select(
                self.inputs, self.outputs, []
            )

            for r in readable:
                self._handle_readable(r)

            for w in writable:
                self._handle_writable(w)

            for e in exceptional:
                self._handle_exceptions(e)

    @abstractclassmethod
    def _manage_message(self, sock: socket.socket):
        ...

    @abstractclassmethod
    def _handle_writable(self, sock: socket.socket):
        ...

    def _handle_readable(self, sock: socket.socket):
        if sock is self.server:
            self._manage_connection(sock)
        else:
            self._manage_message(sock)

    def _handle_exceptions(self, exceptions: socket.socket):
        self.inputs.remove(exceptions)
        if exceptions in self.outputs:
            self.outputs.remove(exceptions)
        exceptions.close()

    def _manage_connection(self, s):
        connection, _ = s.accept()
        connection.setblocking(0)

        self.inputs.append(connection)
        self.clients.append(connection)

        logger(s, "Nova conexão")

    def _close_connection(self, conn):
        if conn in self.outputs:
            self.outputs.remove(conn)

        self.inputs.remove(conn)
        self.clients.remove(conn)

        conn.close()