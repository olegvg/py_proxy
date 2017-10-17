import unittest
from functools import partial
from py_proxy import server


class TestAlterContent(unittest.TestCase):
    alter_content = partial(server.Proxy.alter_content,
                            url_subst='http://127.0.0.1:8080',
                            tag_subst='™')

    def test_alter_empty_content(self):
        self.assertEqual(
            self.alter_content("<html></html>"), "<html></html>")

    def test_alter_triggering_content(self):
        self.assertEqual(
            self.alter_content("<html><div>Privet</div></html>"),
            "<html><body><div>Privet™</div></body></html>")

    def test_html_entities(self):
        self.assertEqual(
            self.alter_content("<strong>+1</strong>"), "<strong>+1</strong>"
        )

    def test_broader_tag_escaping(self):
        self.assertEqual(
            self.alter_content("<strong>Erlang/OTP</strong>"), "<strong>Erlang™/OTP</strong>"
        )
