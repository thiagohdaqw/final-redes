import click
from server.socket_server import SocketServer
from server.websocket_server import WebSocketServer

SERVER_FACTORY = {
    'SOCKET': SocketServer,
    'WEBSOCKET': WebSocketServer
}
SERVER_FACTORY_KEYS = list(SERVER_FACTORY.keys())


@click.command()
@click.option('--ip', '-i', default='127.0.0.1', help='Ip address of the server', show_default=True)
@click.option('--port', '-p', default=7777, help='Port of the server', show_default=True)
@click.option('--max', '-m', default=10, help='Max connections of the server', show_default=True)
@click.option('--type', '-t', default=SERVER_FACTORY_KEYS[0], type=click.Choice(SERVER_FACTORY_KEYS, case_sensitive=False), help='Type of the server' ,show_default=True)
def main(ip, port, max, type):
    server = SERVER_FACTORY[type](ip, port, max)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("Finalizando...")
    finally:
        server.close()

if __name__ == '__main__':
    main()
