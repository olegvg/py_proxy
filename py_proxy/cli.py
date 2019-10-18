import asyncio
import logging

import uvloop
import click
from .server import Proxy

uvloop.install()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--listen-host', default='127.0.0.1', help='Host to serve')
@click.option('--listen-port', default=8080, help='TCP port to serve')
@click.option('--subst-host', default='127.0.0.1', help='Host to substitute links in HTML content')
@click.option('--subst-port', default=8080, help='TCP port to substitute links in HTML content')
def serve(listen_host, listen_port, subst_host, subst_port):
    logger.info(f'Starting habr.com proxy at http://{listen_host}:{listen_port}/')
    proxy = Proxy(listen_host=listen_host, listen_port=listen_port, subst_host=subst_host, subst_port=subst_port)

    try:
        proxy.serve()
    except KeyboardInterrupt:
        logger.info(f'Got KeyboardInterrupt and shutting down...')
    finally:
        proxy.stop()

        loop = asyncio.get_event_loop()
        tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=loop), return_exceptions=False)
        tasks.cancel()
        loop.run_until_complete(tasks)
        loop.stop()
        loop.close()
        logger.info('Shutdown done gracefully')


def main():
    serve()
