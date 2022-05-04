import socket
import select
import pathlib
from server.logger import logger
from server.channel import Channels

class Server:
    server: socket.socket
    ip: str
    port: int
    max_connections: int
    inputs: list[socket.socket]
    outputs: list[socket.socket]
    clients: list[socket.socket]
    channels: Channels

    def __init__(self, ip, port, max_connections):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.ip = ip
        self.port = port
        self.max_connections = max_connections
        self.inputs = [ self.server ]
        self.outputs = []
        self.clients = []
        self.channels = Channels(self.server, self.outputs)

    def start(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.ip, self.port))
        self.server.listen(self.max_connections)
        self._run()
        self.close()

    def close(self):
        print("Fechando conexões")
        for client in self.clients:
            client.close()
        self.server.close()

    def _run(self):
        print("Aguardando em ", (self.ip, self.port))
        
        while self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, [])
            
            for r in readable:
                self._handle_input(r)

            for w in writable:
                self.channels.send_channel_message(w)

            for e in exceptional:
                self._handle_exceptions(e)

    def _handle_input(self, input):
        if input is self.server:
            self._manage_connection(input)
        else:
            self._manage_message(input)

    def _handle_exceptions(self, s):
        self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        s.close()

    def _manage_connection(self, s):
        connection, _ = s.accept()
        connection.setblocking(0)
        
        self.inputs.append(connection)
        self.clients.append(connection)

        logger(s, "Nova conexão")

    def _manage_message(self, conn):
        data = conn.recv(1024)

        try:
            if data:
                message = data.decode('utf-8')
                if len(message.strip()) == 0:
                    return

                command = message.split()[0]
                if command == "GET":
                    logger(conn, "Requisitando pagina", data)
                    self._handle_http_get(conn, message)
                else:
                    self.channels.manage_commands(conn, command, data)
                return
        except Exception:
            logger(conn, "Desconectando...")
        self._close_connection(conn)

    def _handle_http_get(self, conn, msg):
        method, filename, *headers = msg.split()
        filename = "index.html" if filename == '/' else filename[1:]
        pages_path = pathlib.Path("./pages")
        file = pages_path / filename

        if file.exists():
            status = b'200 OK'
        else:
            status = b'404 Not Found'
            file = pages_path / 'notfound.html'

        conn.sendall(b'HTTP/1.1 ' + status + b'\nConnection: Closed\n\n')
        conn.sendall(file.read_bytes())
        self._close_connection(conn)

    def _close_connection(self, conn):
        if conn in self.outputs:
            self.outputs.remove(conn)
        
        self.channels.exit_channel(conn)

        self.inputs.remove(conn)
        self.clients.remove(conn)

        conn.close()
