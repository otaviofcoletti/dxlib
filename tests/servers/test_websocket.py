import unittest

import dxlib as dx


class TestWebsocket(unittest.TestCase):
    def setUp(self):
        handler = dx.servers.WebsocketHandler()
        self.server = dx.servers.WebsocketServer(handler, logger=dx.InfoLogger())

    def test_start(self):
        self.server.start()
        self.assertTrue(self.server.alive)

    def test_stop(self):
        self.server.start()
        self.server.stop()
        self.assertFalse(self.server.alive)

    def tearDown(self):
        self.server.stop()


if __name__ == '__main__':
    unittest.main()
