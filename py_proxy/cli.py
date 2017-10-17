import asyncio
import uvloop
import click
from .server import Proxy


@click.command()
@click.option('--port', default=8080, help='TCP port to serve')
def serve(port):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    proxy = Proxy(port)
    print('Starting habrahabr proxy at http://127.0.0.1:{}/'.format(port))

    try:
        proxy.serve()
    except KeyboardInterrupt:
        pass
    finally:
        proxy.stop()


def main():
    serve()
