import socket
import queue

Channel = str

class Channels:
    server: socket.socket
    channels: dict[Channel, list[socket.socket]]
    connections: dict[socket.socket, Channel]
    message_queues: dict[socket.socket, queue.Queue]
    outputs: list[socket.socket]

    def __init__(self, server, outputs):
        self.server = server
        self.outputs = outputs
        self.message_queues = {}
        self.connections = {}
        self.channels = {}

    def join_channel(self, conn, channel):
        if channel not in self.channels:
            self.channels[channel] = []

        self.exit_channel(conn)

        self.channels[channel].append(conn)
        self.connections[conn] = channel
        self.message_queues[conn] = queue.Queue()

    def exit_channel(self, conn):
        if conn in self.message_queues:
            del self.message_queues[conn]

        if conn in self.connections:
            current_channel = self.connections[conn]
            self.channels[current_channel].remove(conn)
            del self.connections[conn]

    def enqueue_mensage(self, conn, data):
        self.message_queues[conn].put(data)
        if conn not in self.outputs:
            self.outputs.append(conn)

    def send_mensage(self, conn):
        try:
            next_msg = self.message_queues[conn].get_nowait()

            current_channel = self.connections[conn]

            for client in filter(lambda c: c != conn, self.channels[current_channel]):
                client.sendall(next_msg)
        except queue.Empty:
            print("Ola")
            self.outputs.remove(conn)