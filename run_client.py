import click
from client.client import Client

@click.command()
@click.option('--ip', '-i', default='127.0.0.1', help='Ip address of the server')
@click.option('--port', '-p', default=7777, help='Port of the server')
def main(ip, port):
    try:
        client = Client(ip, port)
        client.start()
    except KeyboardInterrupt:
        client.close()
        
if __name__ == '__main__':
    main()
