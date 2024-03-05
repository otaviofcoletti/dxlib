import time
import unittest

import dxlib as dx


class TestYFinanceApi(unittest.TestCase):
    def setUp(self) -> None:
        self.api = dx.interfaces.YFinanceAPI()

    def test_version(self):
        self.assertEqual(self.api.version, "1.0")

    def test_quotes(self):
        today = dx.Date.today()
        last_week = dx.Date.prevdays(6)
        quotes = self.api.quote(["AAPL", "MSFT"], last_week, today)

        self.assertEqual(len(quotes), 2)
        self.assertEqual(set(quotes.df.index.names), {"date", "security"})

    def test_historical(self):
        today = dx.Date.today()
        last_week = dx.Date.prevdays(6)
        history = self.api.historical(["AAPL", "MSFT"], last_week, today)

        self.assertEqual(set(history.df.index.names), {"date", "security"})


class TestYFinanceInterface(unittest.TestCase):
    server = None
    websocket = None
    interface = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = dx.servers.HTTPServer()
        cls.websocket = dx.servers.WebsocketServer()
        cls.interface = dx.interfaces.MarketInterface(dx.YFinanceAPI(), interface_url=cls.server.url)
        cls.server.add_interface(cls.interface)
        cls.websocket.add_interface(cls.interface)

        cls.server.start()
        while not cls.server.alive:
            time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()
        while cls.server.alive:
            time.sleep(0.1)

    def test_quote(self):
        today = dx.Date.today()
        last_week = dx.Date.prevdays(6)
        args = {
            "tickers": ["AAPL", "MSFT"],
            "start": last_week.strftime("%Y-%m-%d"),
            "end": today.strftime("%Y-%m-%d"),
        }
        quotes = self.interface.request(self.interface.quote, json=args)
        data = quotes["data"]
        quotes = dx.History.from_dict(serialized=True, **data)

        self.assertEqual(len(quotes), 2)
        self.assertEqual(set(quotes.df.index.names), {"date", "security"})


if __name__ == '__main__':
    unittest.main()
