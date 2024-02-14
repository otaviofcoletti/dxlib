import unittest

import dxlib as dx


class TestOrders(unittest.TestCase):
    def setUp(self):
        self.security = dx.Security("AAPL")
        self.order_data = dx.OrderDetails(
            security=self.security,
            price=100,
            quantity=100,
            side=dx.Side.BUY,
            order_type=dx.OrderType.MARKET,
        )

    def test_order_details(self):
        self.assertEqual(self.order_data.security, self.security)
        self.assertEqual(self.order_data.price, 100)
        self.assertEqual(self.order_data.quantity, 100)
        self.assertEqual(self.order_data.side, dx.Side.BUY)
        self.assertEqual(self.order_data.order_type, dx.OrderType.MARKET)

        self.assertEqual(self.order_data.__repr__(), "BUY: AAPL 100 @ 100")

    def test_order_from_data(self):
        order = dx.Order(self.order_data)

        self.assertEqual(order.data, self.order_data)

        self.assertEqual(order.__repr__(), "BUY: AAPL 100 @ 100 -> [0 transactions]")

    def test_order_from_data_with_transactions(self):
        order = dx.Order(
            self.order_data, transactions=[dx.Transaction(self.security, 100, 100)]
        )

        self.assertEqual(order.data, self.order_data)

        self.assertEqual(order.__repr__(), "BUY: AAPL 100 @ 100 -> [1 transactions]")

    def test_order_details_json(self):
        self.assertEqual(
            self.order_data.to_json(),
            {
                "security": self.security.to_json(),
                "price": 100,
                "quantity": 100,
                "side": dx.Side.BUY.to_json(),
                "order_type": dx.OrderType.MARKET.to_json(),
            },
        )

    def test_order_json(self):
        self.assertEqual(
            dx.Order(self.order_data).to_json(),
            {
                "data": {
                    "security": self.security,
                    "price": 100,
                    "quantity": 100,
                    "side": dx.Side.BUY,
                    "order_type": dx.OrderType.MARKET,
                },
                "transactions": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
