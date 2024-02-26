import unittest

import dxlib as dx


class TestYFinanceApi(unittest.TestCase):
    def setUp(self) -> None:
        self.api = dx.interfaces.YFinanceAPI()

    def test(self):
        print(self.api.api_version)

    def test2(self):
        today = dx.utils.get_today()
        bars = self.api.get_historical_bars(["BTC-USD"], end=today)
        print(bars)


if __name__ == '__main__':
    unittest.main()
