import socket
import select
import sys

class Client():
    server: socket.socket
    ip: str
    port: int
    channel: str
    
    def __init__(self, ip, port, channel) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((ip, port))
        self.channel = channel
        pass

    def start(self):
        join_channel = bytes(f'IN {self.channel}', 'utf-8')
        self.server.send(join_channel)
        self._run()

    def _run(self):
        while True:
            sockets_list = [sys.stdin, self.server]
        
            """ There are two possible input situations. Either the
            user wants to give manual input to send to other people,
            or the server is sending a message to be printed on the
            screen. Select returns from sockets_list, the stream that
            is reader for input. So for example, if the server wants
            to send a message, then the if condition will hold true
            below.If the user wants to send a message, the else
            condition will evaluate as true"""
            inputs, outputs, exceptions = select.select(sockets_list,[],[])
        
            for sock in inputs:
                self._handle_input(sock)

    
    def _handle_input(self, socks):
        if socks == self.server:
            message = socks.recv(2048)
            print (f'Received: {str(message)}')
        else:
            message = bytes(input(), 'utf-8')
            self.server.send(message)
            print(f'Sent: {str(message)}', end='\n', flush=True)