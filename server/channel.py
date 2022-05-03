import socket
import queue
from dataclasses import dataclass

Channel = str

ChannelCommands = {
    "--IN": "<NomeCanal> <NomeUsuario> - Join Channel",
    "--OUT": "- Exit Channel",
    "--LIST": "- List user in channel",
    "--HELP": "- Show all commands description"
}

@dataclass
class User:
    username: str
    connection: socket.socket
    channel: Channel
    messages: queue.Queue

class Channels:
    server: socket.socket
    channels: dict[Channel, list[User]]
    users: dict[socket.socket, User]
    outputs: list[socket.socket]

    def __init__(self, server, outputs):
        self.server = server
        self.outputs = outputs
        self.message_queues = {}
        self.users = {}
        self.channels = {}

    def manage_commands(self, conn: socket.socket, command: str, data: bytearray):
        message = data.decode("utf-8")
        command = command.upper()

        if command == "--IN":
            self.join_channel(conn, message)
            return
        elif command == "--HELP":
            self.explain_commands(conn)
            return

        if not self.is_user_in_channel(conn):
            self.send_message(conn, f"E necessario entrar em uma sala para utilizar o camando {command}\n")
            return

        if command == "--LIST":
            self.list_users(conn)
        elif command == "--OUT":
            self.exit_channel(conn)
        else:
            self.enqueue_message(conn, message)

    def join_channel(self, conn, message):
        if len(message.split()) != 3:
            self.send_message(conn, "Formato invalido, tente --IN <NomeCanal> <NomeUsuario>\n")
            return

        _, channel, username = message.split()
        channel = channel.lower()

        if channel not in self.channels:
            self.channels[channel] = []

        self.exit_channel(conn)

        user = User(username, conn, channel, queue.Queue())
        
        self.users[conn] = user
        self.channels[channel].append(user)

        self.enqueue_message(conn, "Entrou na sala.\n")

    def exit_channel(self, conn):
        if not self.is_user_in_channel(conn):
            return

        user = self.users[conn]
        user.messages.put("Saiu da sala\n")
        self.send_channel_message(conn)

        self.channels[user.channel].remove(user)
        del self.users[conn]

    def enqueue_message(self, conn, message):
        user = self.users[conn]
        user.messages.put(message)
        if conn not in self.outputs:
            self.outputs.append(conn)

    def send_channel_message(self, conn):
        try:
            user = self.users[conn]
            next_msg = f"[{user.username}]: {user.messages.get_nowait()}"
            
            for user in filter(lambda c: c.connection != conn, self.channels[user.channel]):
                self.send_message(user.connection, next_msg)
        except queue.Empty:
            self.outputs.remove(conn)
    
    def explain_commands(self, conn):
        self.send_message(conn, "\n".join(f"{command} {message}" for command, message in ChannelCommands.items()) + "\n")

    def list_users(self, conn):
        channel = self.users[conn].channel
        msg = "---------------------------------------\n"
        msg += f"LISTA DE USUARIOS NO CANAL {channel}:\n"
        for user in self.channels[channel]:
            msg += f"- {user.username}\n"
        msg += "---------------------------------------\n"
        self.send_message(conn, msg)

    def send_message(self, conn, message):
        if type(message) == str:
            message = message.encode("utf-8")
        conn.sendall(message)

    def is_user_in_channel(self, conn):
        return conn in self.users