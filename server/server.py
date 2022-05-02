import socket
import select
import queue
import pathlib
from message import Message
from channel import Channels



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
        while self.inputs:
            print('\nEsperando próximo evento')
            
            readable, writable, exceptional = select.select(self.inputs, self.outputs, [])
            
            for r in readable:
                self._handle_input(r)

            for w in writable:
                self.channels.send_mensage(w)

            for r in exceptional:
                self._handle_exceptions(r)

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
        if data:
            msg = data.decode('utf-8')
            if msg.startswith(Message.JOIN_CHANNEL):
                channel = msg[len(Message.JOIN_CHANNEL):].strip()
                self.channels.join_channel(conn, channel)
                logger(conn, "Entrando na sala", channel)
            elif msg.startswith(Message.HTTP_GET):
                logger(conn, "Requisitando pagina", msg)
                self._handle_http_get(conn, msg)
            else:
                self.channels.enqueue_mensage(conn, data)
        else:
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

def logger(conn, *msg):
    print(f"[{conn}]: ", msg)