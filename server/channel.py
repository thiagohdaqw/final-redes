import socket
import queue
from dataclasses import dataclass, field
from typing import Callable, NamedTuple


class Command(NamedTuple):
    value: str
    params: str
    help: str

    def __eq__(self, other):
        return self.value == other

    def __str__(self):
        return f'{self.value} {self.params}'.strip()

class Commands:
    CREATE   = Command('/CREATE', '<NomeCanal> <CapacidadeDeUsuarios> <NomeUsuario>', 'Create Channel')
    JOIN     = Command('/JOIN', '<NomeCanal> <NomeUsuario>', 'Join Channel')
    OUT      = Command('/OUT', '', 'Exit Channel')
    CHANNELS = Command('/CHANNELS', '', 'List available channels')
    LIST     = Command('/LIST', '', 'List user in channel')
    HELP     = Command('/HELP', '', 'Show all commands description')


@dataclass
class User:
    username: str
    connection: socket.socket
    channel: str
    messages: queue.Queue = field(default_factory=queue.Queue)

@dataclass
class Channel:
    capacity: int
    users : list[User] = field(default_factory=list)


@dataclass
class Channels:
    send_message: Callable[[socket.socket, str], None]
    outputs: list[socket.socket]
    channels: dict[str, Channel] = field(default_factory=dict)
    users: dict[socket.socket, User] = field(default_factory=dict)

    def manage_commands(self, conn: socket.socket, message: str):
        command = message.split()[0].upper()

        if command == Commands.CREATE:
            return self.create_channel(conn, message)
        elif command == Commands.JOIN:
            return self.join_channel(conn, message)
        elif command == Commands.HELP:
            return self.explain_commands(conn)
        elif command == Commands.CHANNELS:
            return self.list_channels(conn)

        if not self.is_user_in_channel(conn):
            return self.send_server_message(conn, f"[ERRO] - E necessario entrar em uma sala para utilizar o camando {command}\n")

        if command == Commands.LIST:
            self.list_users(conn)
        elif command == Commands.OUT:
            self.exit_channel(conn)
        else:
            self.enqueue_message(conn, message)
            
    def create_channel(self, conn, message):
        if len(message.split()) != 4:
            return self.send_server_message(conn, f"[ERRO] - Formato invalido, tente {Commands.CREATE}\n")

        _, channel_name, capacity, username = message.split()
        channel_name = channel_name.lower()
        try:
            capacity = int(capacity)
        except Exception:
            return self.send_server_message(conn, "[ERRO] - Formato invalido, capacidade de usuario deve ser um numero inteiro.\n")
        
        if channel_name not in self.channels:
            new_channel = Channel(capacity)
            self.channels[channel_name] = new_channel
        else:
            return self.send_server_message(conn, "[ERRO] - Esse canal ja existe.\n")
        
        self.exit_channel(conn)
        
        user = User(username, conn, channel_name)
        
        self.users[conn] = user
        self.channels[channel_name].users.append(user)

        self.enqueue_message(conn, "Entrou na sala.\n")

    def join_channel(self, conn, message):
        if len(message.split()) != 3:
            return self.send_server_message(conn, f"[ERRO] - Formato invalido, tente {Commands.JOIN}\n")

        _, channel_name, username = message.split()
        channel_name = channel_name.lower()

        if channel_name not in self.channels:
            return self.send_server_message(conn, f"[ERRO] - Essa sala não existe, crie uma com o comando {Commands.Create}\n")
        
        channel_typed = self.channels[channel_name]

        if(len(channel_typed.users) == channel_typed.capacity):
            return self.send_server_message(conn, f"[ERRO] - O canal \"{channel_name}\" esta cheio no momento. Entre em outro canal ou tente novamente mais tarde.\n")

        if conn in self.users and self.users[conn].channel == channel_name:
            return self.send_server_message(conn, "[ERRO] - Voce ja esta no canal informado.\n")
        
        if self.is_username_repeated(username, channel_typed.users):
            return self.send_server_message(conn, "[ERRO] - Esse nome ja existe nessa sala, tente novamente com outro.\n")
        
        self.exit_channel(conn)
        
        user = User(username, conn, channel_name)
        
        self.users[conn] = user
        channel_typed.users.append(user)

        self.enqueue_message(conn, "Entrou na sala.\n")
        
    def exit_channel(self, conn):
        if not self.is_user_in_channel(conn):
            return

        user = self.users[conn]
        user.messages.put("Saiu da sala\n")
        self.send_channel_message(conn)
        if len(self.channels[user.channel].users) > 1:
            self.channels[user.channel].users.remove(user)
        else:
            del self.channels[user.channel]
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
            
            for user in filter(lambda c: c.connection != conn, self.channels[user.channel].users):
                self.send_message(user.connection, next_msg)
        except queue.Empty:
            self.outputs.remove(conn)
    
    def explain_commands(self, conn):
        formatter = lambda c: f'{c} - {c.help}' 
        commands = (getattr(Commands, name) for name in dir(Commands) if not name.startswith('_'))
        commands_help = "\n".join(formatter(c) for c in commands) + "\n"

        self.send_server_message(conn, commands_help)

    def list_users(self, conn):
        channel = self.users[conn].channel
        
        msg = f"LISTA DE USUARIOS NO CANAL {channel} ({len(self.channels[channel].users)}/{self.channels[channel].capacity}):\n"
        msg += "".join(f"- {user.username}\n" for user in self.channels[channel].users)
        self.send_server_message(conn, msg)

    def list_channels(self, conn):
        msg = f"LISTA DE CANAIS DISPONIVEIS ({len(self.channels)}):\n" if len(self.channels) > 0 else "NAO HA CANAIS DISPONIVEIS.\n"
        msg += "".join(f"- {channel}\n" for channel in self.channels)
        self.send_server_message(conn, msg)

    def send_server_message(self, conn, text):
        message = "---------------------------------------\n"
        message += text
        message += "---------------------------------------\n"
        message = message
        self.send_message(conn, message)

    def is_user_in_channel(self, conn):
        return conn in self.users
    
    def is_username_repeated(self, username, users):
        for user in users:
            if user.username == username:
                return True
        return False
