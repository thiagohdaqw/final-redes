import socket
import select
import sys
from typing import TextIO

class Client():
    server: socket.socket
    ip: str
    port: int
    input_list: list[socket.socket | TextIO]
    running: bool
    
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((ip, port))
        self.input_list = [sys.stdin, self.server]
        self.running = False

    def start(self):
        print("Conexao concluida. Digite --HELP para ajuda.\n")
        self.running = True
        self._run()

    def close(self):
        self.server.close()

    def _run(self):
        while self.running:
            inputs, _, _ = select.select(self.input_list,[],[])

            for sock in inputs:
                self._handle_input(sock)

    def _handle_input(self, socks):
        if socks == self.server:
            message = socks.recv(2048)
            try:
                if message:
                    print(message.decode("utf-8"), end='')
                    return
            except Exception:
                ...
            self._exit_server()
        else:
            message = bytes(input(), 'utf-8')
            self.server.send(message)

    def _exit_server(self):
        print("Saindo do servidor...")
        self.input_list.remove(self.server)
        self.server.close()
        self.running = False
