import unittest
from datetime import datetime

import dxlib as dx


class TestInventoryHistory(unittest.TestCase):
    def setUp(self):
        self.security_manager = dx.SecurityManager.from_list(["AAPL", "MSFT"])
        self.schema = dx.StandardSchema(
            levels=dx.StandardLevel.levels(),
            security_manager=self.security_manager
        )

        self.quantity_scheme = self.schema + dx.StandardSchema(fields=["quantity"])
        self.value_scheme = self.schema + dx.StandardSchema(fields=["value"])

        aapl = self.security_manager.get("AAPL")
        msft = self.security_manager.get("MSFT")

        self.sample_orders = {
            datetime(2021, 1, 1): [
                dx.OrderData(security=aapl, price=100, quantity=10, side=dx.Side.BUY),
                dx.OrderData(security=msft, price=200, quantity=20, side=dx.Side.BUY),
            ],
            datetime(2021, 1, 2): [
                dx.OrderData(security=aapl, price=110, quantity=10, side=dx.Side.SELL),
                dx.OrderData(security=msft, price=210, quantity=20, side=dx.Side.SELL),
            ]
        }

        self.inventories = {
            date: dx.Inventory.from_order_data(orders)
            for date, orders in self.sample_orders.items()
        }

    def test_init(self):
        history = dx.InventoryHistory(self.schema)
        self.assertEqual(history.schema, self.schema)
        self.assertEqual(history.df.empty, True)

    def test_from_inventories(self):
        orders = dx.InventoryHistory.from_inventories(
            self.inventories,
            self.quantity_scheme
        )

        self.assertEqual(orders.df.shape, (4, 1))
        self.assertEqual(orders.df.index.names, ["date", "security"])
        self.assertEqual(orders.df.columns, ["quantity"])

        aapl = self.security_manager.get("AAPL")

        self.assertEqual(orders.df.index[0], (datetime(2021, 1, 1, 0, 0), aapl))

        self.assertEqual(orders.df.loc[(datetime(2021, 1, 1, 0, 0), aapl), "quantity"], 10)


if __name__ == '__main__':
    unittest.main()
