import time
import unittest

from dxlib.managers.interface_manager import InterfaceManager, InterfaceMessageHandler
from dxlib.interfaces.sandbox import SandboxMarket
from dxlib.servers import HttpServer


class TestInterfaceManager(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_market_manager(self):
        handler = InterfaceMessageHandler()
        market = SandboxMarket()
        mm = InterfaceManager(market, handler)
        mm.add_comm(HttpServer(handler, 8000))

        mm.start()
        time.sleep(10)
        mm.stop()


if __name__ == '__main__':
    unittest.main()
