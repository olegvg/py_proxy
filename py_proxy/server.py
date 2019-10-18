import re
import asyncio
from http.cookies import SimpleCookie
import html as shtml

from aiohttp import web, TCPConnector, request
import multidict
from lxml import html as lhtml


class Proxy:
    tag_subst = '™'

    loop = asyncio.get_event_loop()
    client_connector = None
    request_funcs = {}

    def __init__(self, listen_host: str, listen_port: int, subst_host: str, subst_port: int):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.url_subst = f'http://{subst_host}:{subst_port}/'

    def serve(self):
        self.loop.run_until_complete(self.proxy_server())

    async def proxy_handler(self, req: web.BaseRequest) -> web.StreamResponse:

        url = req.url.\
            with_host('habr.com')\
            .with_port(None)\
            .with_scheme('https')

        req_headers = multidict.CIMultiDict(req.headers)

        req_headers.pop('Accept-Encoding', None)
        req_headers['Connection'] = 'close'
        req_headers.pop('Host', None)
        if req_headers.get('Referer', None):
            req_headers['Referer'] = req_headers['Referer'].replace(self.url_subst, 'https://habr.com/')

        async with request(
            method=req.method,
            url=url,
            headers=req_headers,
            cookies=SimpleCookie(req.cookies),
            connector=self.client_connector
        ) as resp:
            content = await resp.read()

            resp_headers = multidict.CIMultiDict(resp.headers)
            resp_headers.pop('Transfer-Encoding', None)
            resp_headers.pop('Content-Encoding', None)
            resp_headers['Connection'] = 'close'

            proxy_resp = web.StreamResponse(headers=resp_headers, status=resp.status)

            valid_cookie_attrs = ['expires', 'path', 'domain', 'max-age', 'secure', 'version', 'httponly', 'samesite']
            for name, cookie in resp.cookies.items():
                attrs = {k.replace('-', '_'): v for k, v in cookie.items() if k in valid_cookie_attrs}
                proxy_resp.set_cookie(name, cookie.value, **attrs)
            proxy_resp.content_type = resp.content_type

            if resp.content_type == 'text/html':
                proxy_resp.charset = resp.charset
                content = content.decode(resp.charset if resp.charset else 'UTF-8')

                content = self.alter_content(content)

                content = content.encode(resp.charset if resp.charset else 'UTF-8')

            await proxy_resp.prepare(req)
            await proxy_resp.write(content)
            return proxy_resp

    def alter_content(self, content: str):
        content = re.sub(
            r'https://habr\.com/',
            self.url_subst,
            content,
            flags=re.S)

        tree = lhtml.fromstring(content)

        match_conditon = r'(^|\s|\W)(\w{6})($|\s|\W)'
        subst = rf'\1\2{self.tag_subst}\3'
        for element in tree.getiterator():
            if element.tag in ('script', 'style'):
                continue

            if isinstance(element.text, str):
                element.text = re.sub(match_conditon, subst, element.text)
                element.text = shtml.unescape(element.text)
            if isinstance(element.tail, str):
                element.tail = re.sub(match_conditon, subst, element.tail)
                element.tail = shtml.unescape(element.tail)

        content = lhtml.tostring(tree, encoding='unicode')

        return content

    async def proxy_server(self):
        server = web.Server(self.proxy_handler)
        async_server = await self.loop.create_server(server, self.listen_host, self.listen_port)
        await async_server.wait_closed()
