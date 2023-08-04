import numpy
import pandas
from enum import Enum

from .history import History
from .security import Security, SecurityManager
from .logger import no_logger


class TradeType(Enum):
    BUY = 1
    WAIT = 0
    SELL = -1


class Transaction:
    _cost = 1e-2

    def __init__(self,
                 attributed_security: Security = None,
                 quantity=None,
                 price=None,
                 trade_type=TradeType.BUY,
                 timestamp=None):
        self.attributed_histories = {}
        self._price = None
        self._value = None

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
            self._value = (self._price * self.quantity) * self.trade_type.value

    @property
    def value(self):
        return self._value

    @classmethod
    def get_cost(cls):
        return cls._cost

    def get_time(self, history: History | None):
        if history is not None:
            return self.attributed_histories[history]
        else:
            return 0


class Signal:
    def __init__(self, trade_type: TradeType, quantity: int = None, price: float = None):
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price

    def __str__(self):
        if self.trade_type != TradeType.WAIT:
            return f"{self.trade_type.name}: {self.quantity} @ {self.price}"
        else:
            return f"{self.trade_type.name}"


class Portfolio:
    def __init__(self, name: str = None, logger=None):
        self._name: str = name
        self._transaction_history: list[Transaction] = []
        self._is_value_updated = True
        self._history: History | None = None

        self._current_assets: dict[Security, float] = {}
        self._current_assets_value = 0
        self.current_cash = 0

        self.security_manager = SecurityManager()

        if logger is None:
            self.logger = no_logger(__name__)
        else:
            self.logger = logger

    @property
    def current_value(self):
        self._update_assets_value()
        return self.current_cash + self.current_assets_value

    @property
    def current_assets_value(self):
        return self._current_assets_value

    @property
    def transaction_history(self):
        return self._transaction_history

    @property
    def history(self):
        return self._history

    @property
    def name(self):
        return self._name if self._name else self.__class__.__name__

    def _update_assets_value(self):
        current_value = self.history.last()
        self._current_assets_value = sum(
            [self._current_assets[security] * current_value[security.symbol] for security in self._current_assets]
        )

    def print_transaction_history(self):
        print("Transaction cost (per trade):", Transaction.get_cost())
        for idx, transaction in enumerate(self._transaction_history):
            print(transaction.timestamp if transaction.timestamp else idx, transaction)

    def add_cash(self, amount: float, idx=-1):
        self.current_cash += amount
        cash = self.security_manager.get_cash()
        self.record_transaction(Transaction(cash, amount, 1), is_asset=False, idx=idx)

    def _use_cash(self, amount: float, idx=-1):
        self.current_cash -= amount
        cash = self.security_manager.get_cash()
        self.record_transaction(Transaction(cash, amount, 1, TradeType.SELL), is_asset=False, idx=idx)

    def set_history(self, history: History | pandas.DataFrame | numpy.ndarray):
        self.security_manager.add_securities(history.columns)

        if isinstance(history, pandas.DataFrame):
            history = History(history)
        elif isinstance(history, numpy.ndarray):
            history = History(pandas.DataFrame(history))
        self.logger.info("History set for: " + self.name)
        self._history = history

    def record_transaction(self, transaction: Transaction, is_asset=True, idx: int = -1):
        self._transaction_history.append(transaction)
        if idx == -1:
            if self._history is not None:
                idx = max(0, min(len(self._history), len(self._history) + idx))
                transaction.attributed_histories[self._history] = idx
            if transaction.attributed_security and transaction.value and is_asset:
                self._update_current_assets(transaction)

        else:
            # TODO: update value and assets to reflect historical transaction
            transaction.attributed_histories[self._history] = idx

    def _update_current_assets(self, transaction: Transaction):
        if transaction.attributed_security in self._current_assets:
            self._current_assets[transaction.attributed_security] += transaction.quantity
        else:
            self._current_assets[transaction.attributed_security] = transaction.quantity
        self._current_assets_value += transaction.value

    def trade(self,
              security: Security | str,
              signal: Signal,

              timestamp=None):
        if signal.trade_type == TradeType.WAIT:
            return
        if isinstance(security, str):
            security = self.security_manager.get_security(security)

        price = signal.price
        if self._history is not None and signal.price is None:
            price = self._history.df[security.symbol].iloc[-1]

        transaction = Transaction(security, signal.quantity, price, signal.trade_type, timestamp)

        if signal.trade_type == TradeType.BUY:
            if transaction.value + transaction.get_cost() > self.current_cash:
                raise ValueError("Not enough cash to execute the order.")

        elif signal.trade_type.SELL:
            if signal.quantity > self._current_assets[security]:
                raise ValueError("Not enough of the security to sell.")

        self._use_cash(transaction.value + transaction.get_cost())
        self.record_transaction(transaction)

    def _associate_transaction_with_history(self, transaction: Transaction):
        for history_symbol, history_df in self._history.df.items():
            if transaction.attributed_security.symbol == history_symbol:
                closest_index = history_df.index.get_loc(transaction.timestamp, method='nearest')
                transaction.attributed_histories[history_symbol] = closest_index
                break

    def calculate_returns(self):
        if self.history is None:
            return None

        returns = self.history.df.pct_change()
        returns.iloc[0] = 0

        weights = numpy.zeros_like(returns)
        weights = pandas.DataFrame(weights, index=returns.index, columns=returns.columns)

        for transaction in self.transaction_history:
            if transaction.attributed_security.symbol not in weights:
                continue

            time_index = transaction.get_time(self.history)
            security_history = weights[transaction.attributed_security.symbol]

            if transaction.trade_type == TradeType.BUY:
                security_history.iloc[time_index:] += transaction.quantity
            elif transaction.trade_type == TradeType.SELL:
                security_history.iloc[time_index:] -= transaction.quantity

        return returns * weights


def main():
    symbols: list[str] = ['AAPL', 'GOOGL', 'MSFT']
    price_data = numpy.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])
    price_data = pandas.DataFrame(price_data, columns=symbols)

    portfolio = Portfolio()
    portfolio.add_cash(1000, 0)

    portfolio.set_history(price_data)

    portfolio.trade("AAPL", Signal(TradeType.BUY, 1))
    portfolio.trade("MSFT", Signal(TradeType.BUY, 2))
    portfolio.print_transaction_history()
    print(portfolio.current_cash)
    print(portfolio.current_assets_value)

    print(portfolio.calculate_returns())


# Example usage:
if __name__ == "__main__":
    main()
