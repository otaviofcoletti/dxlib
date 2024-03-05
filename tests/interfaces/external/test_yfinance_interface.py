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

        self.assertEqual(len(quotes), 10)
        self.assertEqual(set(quotes.df.index.names), {"date", "security"})

    def test_async_quotes(self):
        today = dx.Date.today()
        last_week = dx.Date.prevdays(6)
        quotes = self.api.quote(["AAPL", "MSFT"], last_week, today, async_=True)

        self.assertEqual(len(quotes), 10)
        self.assertEqual(set(quotes.df.index.names), {"date", "security"})


if __name__ == '__main__':
    unittest.main()
