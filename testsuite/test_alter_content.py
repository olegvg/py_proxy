import unittest

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, make_mocked_request
from aiohttp import web
import aresponses

from py_proxy.server import Proxy


class TestAlterContent(unittest.TestCase):
    proxy = Proxy(listen_host='127.0.0.1', listen_port=8080, subst_host='127.0.0.1', subst_port=8080)

    def test_alter_empty_content(self):
        self.assertEqual(
            self.proxy.alter_content("<html></html>"), "<html></html>")

    def test_alter_triggering_content(self):
        self.assertEqual(
            self.proxy.alter_content("<html><div>Privet</div></html>"),
            "<html><body><div>Privet™</div></body></html>")

    def test_html_entities(self):
        self.assertEqual(
            self.proxy.alter_content("<strong>+1</strong>"), "<strong>+1</strong>"
        )

    def test_broader_tag_escaping(self):
        self.assertEqual(
            self.proxy.alter_content("<strong>Erlang/OTP</strong>"),
            "<strong>Erlang™/OTP</strong>"
        )


class TestProxyHandler(AioHTTPTestCase):
    async def get_application(self):
        app = web.Application()
        return app

    @unittest_run_loop
    async def test_passthrough(self):
        requested_html = '<h1>Hello, world</h1>'
        processed_html = requested_html

        proxy = Proxy(listen_host='127.0.0.1', listen_port=8081, subst_host='127.0.0.1', subst_port=8081)

        async with aresponses.ResponsesMockServer(loop=self.loop) as aresp:
            aresp.add('habr.com', '/', 'GET', aresp.Response(text=requested_html, content_type='text/html'))
            req = make_mocked_request('GET', '/')
            resp = await proxy.proxy_handler(req)

        self.assertEqual(200, resp.status)
        self.assertEqual(processed_html, resp.text)

    @unittest_run_loop
    async def test_modify(self):
        requested_html = '<h1>Helloo, world</h1>'
        processed_html = '<h1>Helloo™, world</h1>'

        proxy = Proxy(listen_host='127.0.0.1', listen_port=8081, subst_host='127.0.0.1', subst_port=8081)

        async with aresponses.ResponsesMockServer(loop=self.loop) as aresp:
            aresp.add('habr.com', '/', 'GET', aresp.Response(text=requested_html, content_type='text/html'))
            req = make_mocked_request('GET', '/')
            resp = await proxy.proxy_handler(req)

        self.assertEqual(200, resp.status)
        self.assertEqual(processed_html, resp.text)

    @unittest_run_loop
    async def test_script_unmodified(self):
        requested_html = '<script>Helloo, world</script>'
        processed_html = '<html><head><script>Helloo, world</script></head></html>'

        proxy = Proxy(listen_host='127.0.0.1', listen_port=8081, subst_host='127.0.0.1', subst_port=8081)

        async with aresponses.ResponsesMockServer(loop=self.loop) as aresp:
            aresp.add('habr.com', '/', 'GET', aresp.Response(text=requested_html, content_type='text/html'))
            req = make_mocked_request('GET', '/')
            resp = await proxy.proxy_handler(req)

        self.assertEqual(200, resp.status)
        self.assertEqual(processed_html, resp.text)

    @unittest_run_loop
    async def test_mixed(self):
        requested_html = '<script>Helloo, world</script><h1>Hello, worldd</h1>'
        processed_html = '<html><head><script>Helloo, world</script></head><body><h1>Hello, worldd™</h1></body></html>'

        proxy = Proxy(listen_host='127.0.0.1', listen_port=8081, subst_host='127.0.0.1', subst_port=8081)

        async with aresponses.ResponsesMockServer(loop=self.loop) as aresp:
            aresp.add('habr.com', '/', 'GET', aresp.Response(text=requested_html, content_type='text/html'))
            req = make_mocked_request('GET', '/')
            resp = await proxy.proxy_handler(req)

        self.assertEqual(200, resp.status)
        self.assertEqual(processed_html, resp.text)
