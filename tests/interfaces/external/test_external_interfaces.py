import unittest

import dxlib as dx


class TestOrderInterface(unittest.TestCase):
    def setUp(self):
        self.order_interface = dx.OrderInterface()

    def test_execute_order(self):
        order_data = dx.OrderData(
            security=dx.Security("AAPL"),
            price=100,
            quantity=10,
            side=dx.Side.BUY,
            order_type=dx.OrderType.MARKET
        )
        order = self.order_interface.execute_order(order_data)
        self.assertIsInstance(order, dx.Order)

    def test_execute_orders(self):
        order_data = dx.OrderData(
            security=dx.Security("AAPL"),
            price=100,
            quantity=10,
            side=dx.Side.BUY,
            order_type=dx.OrderType.MARKET
        )
        orders = self.order_interface.execute_orders([order_data])
        self.assertIsInstance(orders, list)
        self.assertIsInstance(orders[0], dx.Order)

    def test_map_signals(self):
        signals = {
            dx.Security("AAPL"): dx.Signal(
                price=100,
                quantity=10,
                side=dx.Side.BUY
            )
        }
        orders = dx.OrderInterface.map_signals(signals)
        self.assertIsInstance(orders, list)
        self.assertIsInstance(orders[0], dx.OrderData)

    def test_execute_signals(self):
        signals = {
            dx.Security("AAPL"): dx.Signal(
                price=100,
                quantity=10,
                side=dx.Side.BUY
            )
        }
        orders_data = dx.OrderInterface.map_signals(signals)

        orders = self.order_interface.execute_orders(orders_data)
        self.assertIsInstance(orders, list)
        self.assertIsInstance(orders[0], dx.Order)

    def test_map_history(self):
        schema = dx.Schema(
            levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
            fields=["signal"],
            security_manager=dx.SecurityManager.from_list([dx.Security("AAPL")])
        )

        data = {
            ("2021-01-01", "AAPL"): {"signal": dx.Signal(dx.Side.BUY, 100, 10)},
            ("2021-01-02", "AAPL"): {"signal": dx.Signal(dx.Side.SELL, 110, 10)}
        }

        history = dx.History(data, schema)
        order_data = self.order_interface.map_history(history)  # History[OrderData]
        self.assertIsInstance(order_data, dx.History)

    def test_execute_history(self):
        schema = dx.Schema(
            levels=[dx.SchemaLevel.DATE, dx.SchemaLevel.SECURITY],
            fields=["signal"],
            security_manager=dx.SecurityManager.from_list([dx.Security("AAPL")])
        )

        data = {
            ("2021-01-01", "AAPL"): {"signal": dx.Signal(dx.Side.BUY, 100, 10)},
            ("2021-01-02", "AAPL"): {"signal": dx.Signal(dx.Side.SELL, 110, 10)}
        }

        history = dx.History(data, schema)
        orders = self.order_interface.execute_history(history)
        self.assertIsInstance(orders, dx.History)
        self.assertIsInstance(orders.df.iloc[0, 0], dx.Order)


if __name__ == '__main__':
    unittest.main()
