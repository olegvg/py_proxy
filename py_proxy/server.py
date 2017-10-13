import re
import asyncio
import uvloop
from aiohttp import web, TCPConnector, request
import multidict
from lxml import html


class Proxy:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.client_connector = None
        self.request_funcs = {}

    def ensure_connector(self):
        if self.client_connector is None or self.client_connector.closed:
            self.client_connector = TCPConnector(loop=self.loop)

    def serve(self):
        self.loop.run_until_complete(self.proxy_server())

    def stop(self):
        self.loop.close()

    async def proxy_handler(self, req):
        self.ensure_connector()

        url = req.url.with_host('habrahabr.ru').with_port(None).with_scheme('https')
        req.headers.pop('Accept-Encoding', None)
        req.headers.pop('Connection', None)
        req.headers.pop('Host', None)
        async with request(
            method=req.method,
            url=url,
            headers=req.headers,
            cookies=req.cookies,
            connector=self.client_connector
        ) as resp:
            content = await resp.read()

            proxy_headers = multidict.CIMultiDict(resp.headers)
            proxy_headers.pop('Transfer-Encoding', None)
            proxy_headers.pop('Content-Encoding', None)
            proxy_headers.pop('Connection', None)

            proxy_resp = web.StreamResponse(headers=proxy_headers, status=resp.status)

            for v in resp.cookies.items():
                proxy_resp.set_cookie(*v)
            proxy_resp.content_type = resp.content_type

            if resp.content_type == 'text/html':
                proxy_resp.charset = resp.charset
                content = content.decode(resp.charset if resp.charset else 'UTF-8')

                content = self.alter_content(content)

                content = content.encode(resp.charset if resp.charset else 'UTF-8')

            await proxy_resp.prepare(req)
            proxy_resp.write(content)
            await proxy_resp.drain()
            return proxy_resp

    @staticmethod
    def alter_content(content):
        content = re.sub(r'https://habrahabr\.ru/', 'http://127.0.0.1:8080/', content, flags=re.S)

        tree = html.fromstring(content)

        match_conditon = r'(^|\s)(\w{6})($|\s)'
        subst = r'\1\2™\3'
        for element in tree.getiterator():
            if element.tag in ('script', 'style'):
                continue

            if isinstance(element.text, str):
                element.text = re.sub(match_conditon, subst, element.text)
            if isinstance(element.tail, str):
                element.tail = re.sub(match_conditon, subst, element.tail)

        content = html.tostring(tree, encoding='unicode')

        return content

    async def proxy_server(self):
        server = web.Server(self.proxy_handler)
        async_server = await self.loop.create_server(server, "127.0.0.1", 8080)
        await async_server.wait_closed()


if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    proxy = Proxy()

    try:
        proxy.serve()
    except KeyboardInterrupt:
        pass
    finally:
        proxy.stop()
