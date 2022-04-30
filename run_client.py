import click
from client import Client

@click.command()
@click.option('--ip', '-i', default='127.0.0.1', help='Ip address of the server')
@click.option('--port', '-p', default=7777, help='Port of the server')
@click.option('--channel', '-c', default='Geral', help='Channel to connect')
def main(ip, port, channel):
    try:
        client = Client(ip, port, channel)
        client.start()
    except KeyboardInterrupt:
        client.close()
        
if __name__ == '__main__':
    main()
