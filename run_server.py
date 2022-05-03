import click
from server.server import Server

@click.command()
@click.option('--ip', '-i', default='127.0.0.1', help='Ip address of the server')
@click.option('--port', '-p', default=7777, help='Port of the server')
@click.option('--max', '-m', default=10, help='Max connections of the server')
def main(ip, port, max):
    try:
        server = Server(ip, port, max)
        server.start()
    except KeyboardInterrupt:
        server.close()
        
if __name__ == '__main__':
    main()
