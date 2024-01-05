import unittest

import pandas as pd

import dxlib as dx
from dxlib.interfaces.external.alpaca_markets import (
    AlpacaAPI,
    AlpacaMarket,
    AlpacaOrder,
    AlpacaPortfolio,
)

import config


class SimpleStrategy(dx.Strategy):
    def __init__(self):
        super().__init__()

    def execute(self, idx, position: dx.Inventory, history: dx.History) -> pd.DataFrame:
        # Signal is dataframe:
        # index: Security
        # columns: OrderData
        # For simple strategy buy 1 of each security if price is below 10
        # and sell 1 of each security if price is above 10

        prices = history.get(fields=["close"], dates=[idx]).df
        prices.index = prices.index.droplevel("date")

        signals = pd.DataFrame(columns=["signal"], index=[])

        for security in prices.index:
            price = prices.loc[security, "close"]
            if price < 10:
                order = dx.OrderData(security, price, 1, dx.Side.BUY, "market")
                signals = pd.concat(
                    [
                        signals,
                        pd.DataFrame([order], columns=["signal"], index=[security]),
                    ]
                )

            elif price > 10:
                order = dx.OrderData(security, price, 1, dx.Side.SELL, "market")
                signals = pd.concat(
                    [
                        signals,
                        pd.DataFrame([order], columns=["signal"], index=[security]),
                    ]
                )

        signals.index.name = "security"

        signals["date"] = idx
        signals = signals.set_index(["date"], append=True)
        signals.reorder_levels(["date", "security"])

        return signals


class TestSTrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = SimpleStrategy()
        self.sm = dx.StrategyManager(self.strategy)

        self.portfolio = dx.Portfolio()

        self.api = AlpacaAPI(config.API_KEY, config.API_SECRET)

        self.market_interface = AlpacaMarket(self.api)
        self.order_interface = AlpacaOrder(self.api)
        self.portfolio_interface = AlpacaPortfolio(self.api)

    def test_execute(self):
        self.sm.start()

        stream = self.api.stream_api.connect()

        try:
            obj = self.api.market_api.get_historical_bars(
                "AAPL", start="2020-01-01", end="2021-01-01", timeframe="1D"
            )
            signals = self.sm.run(obj)

            signal = (
                signals.get(dates=[signals.date(0)]).df.iloc[-1].to_dict().get("signal")
            )
            self.order_interface.send(signal)

        except KeyboardInterrupt:
            pass
        finally:
            self.sm.stop()


if __name__ == "__main__":
    unittest.main()
