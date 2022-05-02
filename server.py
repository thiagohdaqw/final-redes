import socket
import select
import queue
import pathlib
from message import Message


class Server:
    server: socket.socket
    ip: str
    port: int
    max_connections: int
    inputs: list[socket.socket]
    outputs: list[socket.socket]
    clients: list[socket.socket]
    message_queues: dict[socket.socket, queue.Queue]

    connection_channel: dict[socket.socket, str]
    channel_connections: dict[str, list[socket.socket]]

    def __init__(self, ip, port, max_connections):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        self.ip = ip
        self.port = port
        self.max_connections = max_connections
        self.inputs = [ self.server ]
        self.outputs = []
        self.clients = []
        self.message_queues = {}
        self.connection_channel = {}
        self.channel_connections = {}

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

            for rr in readable:
                self._handle_input(rr)

            for r in writable:
                self._handle_output(r)

            for r in exceptional:
                self._handle_exceptions(r)

    def _handle_input(self, input):
        if input is self.server:
            self._manage_connection(input)
        else:
            self._manage_message(input)

    def _handle_output(self, s):
        try:
            next_msg = self.message_queues[s].get_nowait()
            channel = self.connection_channel[s]
            for client in filter(lambda conn: conn != s,self.channel_connections[channel]):
                client.sendall(next_msg)
        except queue.Empty:
            self.outputs.remove(s)

    def _handle_exceptions(self, s):
        self.inputs.remove(s)
        if s in self.outputs:
            self.outputs.remove(s)
        s.close()

        del self.message_queues[s]

    def _manage_connection(self, s):
        connection, _ = s.accept()
        connection.setblocking(0)
        
        self.inputs.append(connection)
        self.clients.append(connection)
        self.message_queues[connection] = queue.Queue()

        logger(s, "Nova conexão")

    def _manage_message(self, s):
        data = s.recv(1024)
        if data:
            msg = data.decode('utf-8')
            if msg.startswith(Message.JOIN_CHANNEL):
                channel = msg[len(Message.JOIN_CHANNEL):].strip()
                logger(s, "Entrando na sala", channel)
                self._add_channel(channel, s)
            elif msg.startswith(Message.HTTP_GET):
                    logger(s, "Requisitando pagina index.html", msg)
                    self._handle_http_get(s, msg)
            else:
                logger(s, "Enviando mensagem:", msg)
                self._add_mensage(data, s)
        else:
            self._close_connection(s)

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
    
    def _add_channel(self, channel, conn):
        if channel not in self.channel_connections:
            self.channel_connections[channel] = []

        self.channel_connections[channel].append(conn)
        self.connection_channel[conn] = channel

    def _add_mensage(self, data, conn):
        self.message_queues[conn].put(data)
        if conn not in self.outputs:
            self.outputs.append(conn)

    def _close_connection(self, conn):
        if conn in self.outputs:
            self.outputs.remove(conn)
        
        if conn in self.channel_connections:
            channel = self.connection_channel[conn]
            self.channel_connections[channel].remove(conn)
            del self.connection_channel[conn]

        self.inputs.remove(conn)
        self.clients.remove(conn)
        del self.message_queues[conn]

        conn.close()

def logger(conn, *msg):
    print(f"[{conn}]: ", msg)