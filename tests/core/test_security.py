import unittest


import dxlib as dx


class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.security = dx.Security("AAPL")

    def test_security(self):
        self.assertEqual(self.security.ticker, "AAPL")

    def test_security_type(self):
        self.assertEqual(self.security.security_type, dx.SecurityType.equity)


class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.security_manager = dx.SecurityManager()
        self.security = dx.Security("AAPL")

    def test_security_manager(self):
        self.assertEqual(len(self.security_manager), 0)

    def test_security_manager_add(self):
        self.security_manager.add(self.security)
        self.assertEqual(len(self.security_manager), 1)

    def test_cash(self):
        self.assertEqual(self.security_manager.cash.ticker, "cash")
        self.assertEqual(self.security_manager.cash.security_type, dx.SecurityType.cash)

    def test_get(self):
        self.security_manager.add(self.security)
        self.assertEqual(self.security_manager.get("AAPL").ticker, "AAPL")

    def test_add_tickers(self):
        tickers = ["AAPL", "MSFT", "GOOG"]
        self.security_manager.add_list(tickers)
        self.assertEqual(self.security_manager.get("AAPL").ticker, "AAPL")

    def test_add_existing(self):
        self.security_manager.add(self.security)

        with self.assertRaises(ValueError):
            self.security_manager.add(self.security)

    def test_get_non_existing(self):
        with self.assertRaises(KeyError):
            security = self.security_manager["AAPL"]

    def test_get_secure_non_existing(self):
        security = self.security_manager.get("AAPL")
        self.assertIsNone(security)

    def test_convert_ticker(self):
        tickers = ["AAPL", "MSFT", "GOOG"]
        self.security_manager.add(tickers[0])

        securities = self.security_manager.get_list(tickers)
        self.assertEqual(securities[0].ticker, "AAPL")

    def test_convert_security(self):
        securities = [dx.Security("AAPL"), dx.Security("MSFT"), dx.Security("GOOG")]
        self.security_manager.add(securities[0])

        different_securities = [
            dx.Security("AAPL"),
            dx.Security("MSFT"),
            dx.Security("GOOG"),
        ]

        securities = self.security_manager.get_list(different_securities)
        self.assertEqual(securities[0].ticker, "AAPL")

    def test_add_intersection(self):
        securities_1 = [dx.Security("AAPL"), dx.Security("MSFT"), dx.Security("GOOG")]
        securities_2 = [dx.Security("AAPL"), dx.Security("TSLA"), dx.Security("GOOG")]

        self.security_manager.add_list(securities_1)
        self.security_manager.add_list(securities_2)

        self.assertEqual(len(self.security_manager), 4)


if __name__ == "__main__":
    unittest.main()
