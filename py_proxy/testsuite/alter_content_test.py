import unittest
from py_proxy import server


class TestAlterContent(unittest.TestCase):
    def test_alter_empty_content(self):
        self.assertEqual(
            server.Proxy.alter_content("<html></html>"), "<html></html>")

    def test_alter_triggering_content(self):
        self.assertEqual(
            server.Proxy.alter_content("<html><div>Privet</div></html>"),
            "<html><body><div>Privet™</div></body></html>")
