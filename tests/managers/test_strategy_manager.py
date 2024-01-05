import time
import unittest

import pandas as pd

from dxlib import History, Strategy, StrategyManager
from dxlib.core.components.inventory import Inventory
from dxlib.servers import WebsocketServer


class TestStrategyManager(unittest.TestCase):
    class SimpleStrategy(Strategy):
        def __init__(self):
            super().__init__()

        def execute(self, idx, position: Inventory, history: History) -> pd.DataFrame:
            return pd.DataFrame()

    def test_execute(self):
        strategy = self.SimpleStrategy()
        sm = StrategyManager(strategy, comms=[WebsocketServer(port=6000)])

        sm.start()

        try:
            while sm.alive():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            sm.stop()


if __name__ == "__main__":
    unittest.main()
