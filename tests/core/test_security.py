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


if __name__ == "__main__":
    unittest.main()
