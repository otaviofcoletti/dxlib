import numpy
import pandas
from enum import Enum

from .history import History
from .security import Security
from .logger import no_logger


class TradeType(Enum):
    BUY = 1
    WAIT = 0
    SELL = -1


class Transaction:
    transaction_cost = 1e-2

    def __init__(self,
                 attributed_security: Security = None,
                 quantity=None,
                 price=None,
                 trade_type=TradeType.BUY,
                 timestamp=None):
        self.attributed_histories = {}
        self._price = None
        self._cost = None

        self.attributed_security = attributed_security
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.trade_type.name}: {self.attributed_security.symbol} {self.quantity} @ {self.price}"

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price
        if self.quantity and self._price and self.trade_type:
            self._cost = -(self._price * self.quantity) * self.trade_type.value - self.transaction_cost

    @property
    def cost(self):
        return self._cost


class Signal:
    def __init__(self, trade_type: TradeType, quantity: int = None, price: float = None):
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price

    def __str__(self):
        if self.trade_type != TradeType.WAIT:
            return f"Signal({self.trade_type}, {self.quantity}, {self.price})"
        else:
            return f"Signal({self.trade_type})"


class Portfolio:
    def __init__(self, name: str = None, logger=None):
        self._name: str = name
        self._transaction_history: list[Transaction] = []
        self._total_value = 0
        self.cash = 0

        if logger is None:
            self.logger = no_logger(__name__)
        else:
            self.logger = logger

        self.current_assets: dict[Security, float] = {}
        self._history: History | None = None

    @property
    def total_value(self):
        return self._total_value + self.cash

    @property
    def transaction_history(self):
        return self._transaction_history

    @property
    def history(self):
        return self._history

    @property
    def name(self):
        return self._name if self._name else self.__class__.__name__

    def print_transaction_history(self):
        print("Transaction cost (per trade):", Transaction.transaction_cost)
        for idx, transaction in enumerate(self._transaction_history):
            print(transaction.timestamp if transaction.timestamp else idx, transaction)

    def add_cash(self, cash: float):
        self.cash += cash

    def set_history(self, history: History | pandas.DataFrame | numpy.ndarray):
        if isinstance(history, pandas.DataFrame):
            history = History(history)
        elif isinstance(history, numpy.ndarray):
            history = History(pandas.DataFrame(history))
        self.logger.info("History set for: " + self.name)
        self._history = history

    def record_transaction(self, transaction: Transaction):
        self._transaction_history.append(transaction)
        if transaction.attributed_security and transaction.cost:
            self._total_value += transaction.cost
            self._update_current_assets(transaction)

    def _update_current_assets(self, transaction: Transaction):
        if transaction.attributed_security in self.current_assets:
            self.current_assets[transaction.attributed_security] += transaction.quantity
        else:
            self.current_assets[transaction.attributed_security] = transaction.quantity

    def execute_signal(self, signal: Signal):
        pass
        # self.trade(signal.trade_type, signal.quantity, signal.price)

    def trade(self,
              security: Security | str,
              quantity: int,
              price: int = None,
              trade_type: TradeType = TradeType.BUY,
              timestamp=None):
        if isinstance(security, str):
            security = Security(security)

        if trade_type == TradeType.BUY:
            if self._history is not None and price is None:
                price = self._history.df[security.symbol].iloc[-1]

            transaction = Transaction(security, quantity, price, trade_type, timestamp)
            transaction.quantity = quantity
            if price:
                transaction.price = price

            if self._history is not None and transaction.timestamp is not None:
                self.logger.info(f"Associating transaction: {transaction}")
                # self._associate_transaction_with_history(transaction)

            if transaction.cost > self.total_value:
                raise ValueError("Not enough cash to execute the order.")

            self.record_transaction(transaction)

    def _associate_transaction_with_history(self, transaction: Transaction):
        for history_symbol, history_df in self._history.df.items():
            if transaction.attributed_security.symbol == history_symbol:
                closest_index = history_df.index.get_loc(transaction.timestamp, method='nearest')
                transaction.attributed_histories[history_symbol] = closest_index
                break

    def calculate_returns(self, signals=None):
        total_value = self.history.df
        returns = total_value.pct_change()
        return returns
    #
    # def calculate_max_drawdown(self):
    #     total_value = self.get_portfolio_value(self.portfolio[self.symbols])
    #     cumulative_returns = (1 + total_value.pct_change()).cumprod()
    #     peak = cumulative_returns.expanding(min_periods=1).max()
    #     drawdown = (cumulative_returns - peak) / peak
    #     max_drawdown = drawdown.min()
    #     return max_drawdown

    # def print_portfolio_summary(self):
    #     print("\nPortfolio Summary:")
    #     print(self.portfolio)
    #     print("\nTransaction History:")
    #     df = pd.DataFrame(self.transaction_history)
    #     print(df)


def main():
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    price_data = numpy.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])
    price_data = pandas.DataFrame(price_data, columns=symbols)

    portfolio = Portfolio()
    portfolio.add_cash(1000)

    portfolio.set_history(price_data)
    portfolio.trade("AAPL", 1)
    portfolio.trade("AAPL", 1)
    portfolio.print_transaction_history()
    print(portfolio.total_value)


# Example usage:
if __name__ == "__main__":
    main()
