import time
import unittest

from dxlib.servers.handlers.interface_manager import InterfaceManager
from dxlib.interfaces.sandbox import SandboxMarket
from dxlib.servers import HttpServer, WebsocketServer


class TestInterfaceManager(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_market_manager(self):
        market = SandboxMarket()
        mm = InterfaceManager(
            market, comms=[HttpServer(port=8001), WebsocketServer(port=5001)]
        )

        mm.start()
        time.sleep(1)
        mm.stop()


if __name__ == "__main__":
    unittest.main()
