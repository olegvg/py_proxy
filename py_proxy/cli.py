import asyncio
import uvloop
import click
from .server import Proxy


@click.command()
@click.option('--listen-host', default='127.0.0.1', help='Host to serve')
@click.option('--listen-port', default=8080, help='TCP port to serve')
@click.option('--subst-host', default='127.0.0.1', help='Host to substitute links in HTML content')
@click.option('--subst-port', default=8080, help='TCP port to substitute links in HTML content')
def serve(listen_host, listen_port, subst_host, subst_port):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    proxy = Proxy(listen_host=listen_host, listen_port=listen_port, subst_host=subst_host, subst_port=subst_port)
    print(f'Starting habr.com proxy at http://{listen_host}:{listen_port}/')

    try:
        proxy.serve()
    except KeyboardInterrupt:
        pass
    finally:
        proxy.stop()


def main():
    serve()
