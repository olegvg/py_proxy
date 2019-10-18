import unittest
from functools import partial
from py_proxy import server


class TestAlterContent(unittest.TestCase):
    proxy = server.Proxy(listen_host='127.0.0.1', listen_port=8080, subst_host='127.0.0.1', subst_port=8080)

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
