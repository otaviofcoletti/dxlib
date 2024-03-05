import asyncio
import time
import unittest

import websocket

import dxlib as dx


class TestWebsocket(unittest.TestCase):
    server = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = dx.servers.WebsocketServer(logger=dx.InfoLogger())
        cls.server.start()

        while not cls.server.alive:
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        while cls.server.alive:
            time.sleep(0.1)
        cls.server.stop()

    def test_start(self):
        if not self.server.alive:
            self.server.start()
        while not self.server.alive:
            time.sleep(0.1)
        self.assertTrue(self.server.alive)

    def test_stop(self):
        self.server.stop()
        while self.server.alive:
            time.sleep(0.1)
        self.assertFalse(self.server.alive)

        self.server.start()
        while not self.server.alive:
            time.sleep(0.1)

    def test_message(self):
        ws = websocket.WebSocket()
        ws.connect(f"ws://localhost:{self.server.port}/")
        self.assertTrue(ws.connected)
        ws.send("test")
        ws.close()

    def test_listen(self):
        @dx.Endpoint.websocket("/test")
        async def test():
            for i in range(10):
                yield {"test": i}
                await asyncio.sleep(0.1)
        self.server.listen(test)
        ws = websocket.WebSocket()
        ws.connect(f"ws://localhost:{self.server.port}/test")
        self.assertTrue(ws.connected)
        # Might not receive all messages, so ws.recv() == {"test": i} is not guaranteed for i ~>= 5
        for i in range(5):
            self.assertIn("test", ws.recv())
        ws.close()

    def tearDown(self):
        self.server.stop()


if __name__ == '__main__':
    unittest.main()
