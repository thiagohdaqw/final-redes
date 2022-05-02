import socket
import select
import sys
from typing import TextIO

class Client():
    server: socket.socket
    ip: str
    port: int
    channel: str
    input_list: list[socket.socket | TextIO]
    running: bool
    
    def __init__(self, ip, port, channel):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((ip, port))
        self.channel = channel
        self.input_list = [sys.stdin, self.server]
        self.running = False

    def start(self):
        join_channel = bytes(f'IN {self.channel}', 'utf-8')
        self.server.send(join_channel)
        self.running = True
        self._run()

    def _run(self):
        while self.running:
            inputs, outputs, exceptions = select.select(self.input_list,[],[])

            for sock in inputs:
                self._handle_input(sock)

    
    def _handle_input(self, socks):
        if socks == self.server:
            message = socks.recv(2048)
            if message:
                print (f'Received: {message}')
            else:
                print("Server disconnect")
                socks.close()
                self.input_list.remove(socks)
                self.running = False
        else:
            message = bytes(input(), 'utf-8')
            self.server.send(message)
            print(f'Sent: {message}', flush=True)