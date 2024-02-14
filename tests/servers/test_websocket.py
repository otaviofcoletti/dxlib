import time
import unittest
import websocket

import dxlib as dx


class TestWebsocket(unittest.TestCase):
    def setUp(self):
        handler = dx.servers.WebsocketHandler()
        self.server = dx.servers.WebsocketServer(handler, logger=dx.InfoLogger())

    def test_start(self):
        self.server.start()
        while not self.server.alive:
            time.sleep(0.1)
        self.assertTrue(self.server.alive)

    def test_stop(self):
        self.server.start()
        self.server.stop()
        self.assertFalse(self.server.alive)

    def test_connect(self):
        self.server.start()
        time.sleep(2)
        ws = websocket.WebSocket()
        ws.connect(f"ws://localhost:{self.server.port}/")
        self.assertTrue(ws.connected)
        ws.close()

    class CustomHandler(dx.servers.WebsocketHandler):
        def __init__(self, server: dx.servers.WebsocketServer):
            super().__init__()
            self.server = server

        async def handle(self, websocket, endpoint, message):
            await self.server.send_message_async(websocket, message)

    def test_send_message(self):
        handler = self.CustomHandler(self.server)
        self.server.handler = handler
        self.server.start()

        while not self.server.alive:
            time.sleep(0.1)
        ws = websocket.WebSocket()
        ws.connect(f"ws://localhost:{self.server.port}/")
        self.assertTrue(ws.connected)
        ws.send("Hello")
        self.assertEqual(ws.recv(), "Hello")
        ws.close()

    def tearDown(self):
        self.server.stop()


if __name__ == '__main__':
    unittest.main()
