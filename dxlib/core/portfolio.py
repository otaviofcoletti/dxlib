from __future__ import annotations

import json
from enum import Enum

import numpy as np
import pandas as pd

from .history import History
from .logger import no_logger
from .security import Security, SecurityManager, SecurityType


class TradeType(Enum):
    BUY = 1
    WAIT = 0
    SELL = -1

    def __eq__(self, other):
        if isinstance(other, TradeType):
            return self.value == other.value
        return False


class Transaction:
    _cost = 1e-2

    def __init__(
            self,
            security: Security = None,
            quantity=None,
            price=None,
            trade_type=TradeType.BUY,
            timestamp=None,
    ):
        self.attributed_histories = {}
        self._price = None
        self._quantity = None
        self._value = None

        self.security = security
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.trade_type.name}: {self.security.symbol} {self.quantity} @ {self.price}"

    def to_dict(self):
        return {
            "security": self.security.symbol,
            "trade_type": self.trade_type.name,
            "quantity": float(self.quantity),
            "price": float(self.price),
            "timestamp": self.timestamp,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price
        if self._quantity and self._price and self.trade_type:
            self._value = (self._price * self._quantity) * self.trade_type.value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity
        if self._quantity and self._price and self.trade_type:
            self._value = (self._price * self._quantity) * self.trade_type.value

    @property
    def value(self):
        return self._value

    @property
    def cost(self):
        return self._cost

    def get_time(self, history: History | None):
        if history is not None:
            return self.attributed_histories[history]
        else:
            return 0


class Signal:
    def __init__(
            self, trade_type: TradeType | str, quantity: int = 1, price: float = None
    ):
        if isinstance(trade_type, str):
            trade_type = TradeType[trade_type.upper()]
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price

    def to_json(self):
        return {
            "trade_type": self.trade_type.name,
            "quantity": self.quantity,
            "price": self.price if self.price else "mkt",
        }

    def __str__(self):
        if self.trade_type != TradeType.WAIT:
            return f"{self.trade_type.name}: {self.quantity} @ {self.price if self.price else 'mkt'}"
        else:
            return f"{self.trade_type.name}"


class Portfolio:
    def __init__(self, history=None, name: str = None, position=None, logger=None):
        self._name: str = name
        self._transaction_history: list[Transaction] = []
        self._history: History | None = None

        self._historical_quantity = None
        self._current_assets: dict[Security, float] = {}
        self._current_assets_value: dict[Security, float] = {}
        self._current_assets_weights: dict[Security, float] = {}
        self._is_assets_value_updated = True
        self._is_assets_weights_updated = None
        self.current_cash = 0

        self.security_manager = SecurityManager()
        self.logger = logger if logger else no_logger(__name__)

        if history is not None:
            self.history = history
        if position is not None:
            self.position = position

    def to_dict(self):
        return {
            "name": str(self.name),
            "current_cash": float(self.current_cash),
            "current_assets": {
                security.symbol: float(quantity)
                for security, quantity in self._current_assets.items()
            },
            "transaction_history": [
                transaction.to_dict() for transaction in self.transaction_history
                if transaction.security.security_type != SecurityType.cash
            ],
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @property
    def position(self):
        return self._current_assets

    @position.setter
    def position(self, position: dict[Security | str, float]):
        for security, quantity in position.items():
            if security == self.security_manager.cash or security == "cash":
                if quantity > self.current_cash:
                    self.add_cash(quantity - self.current_cash)
                elif quantity < self.current_cash:
                    self._use_cash(self.current_cash - quantity)
                continue
            security = self.security_manager.add_security(security)
            self._current_assets[security] = quantity

    @property
    def transaction_history(self) -> list[Transaction]:
        return self._transaction_history

    @property
    def history(self):
        return self._history

    @property
    def name(self):
        return self._name if self._name else self.__class__.__name__

    def _update_assets_value(self):
        current_value = self.history.last()
        self._current_assets_value = {
            security: self._current_assets[security] * current_value[security]
            for security in self._current_assets
        }

        self._is_assets_value_updated = True

    def print_transaction_history(self):
        for idx, transaction in enumerate(self._transaction_history):
            print(transaction.timestamp if transaction.timestamp else idx, transaction)
        print("Transaction cost (per trade):", Transaction.cost)

    def add_cash(self, amount: float, timestamp=-1):
        self.current_cash += amount
        cash = self.security_manager.cash
        self.record_transaction(
            Transaction(cash, amount, 1, timestamp=timestamp), is_asset=False
        )
        return self

    def _use_cash(self, amount: float, timestamp=-1):
        self.current_cash -= amount
        cash = self.security_manager.cash
        self.record_transaction(
            Transaction(cash, amount, 1, TradeType.SELL, timestamp=timestamp), is_asset=False
        )
        return self

    @history.setter
    def history(self, history: History | pd.DataFrame | np.ndarray | list):
        if isinstance(history, pd.DataFrame):
            history = History(history)
        elif isinstance(history, np.ndarray) or isinstance(history, list):
            history = History(pd.DataFrame(history))
        self.security_manager.add_securities(history.df.columns)

        self.logger.info("History set for: " + self.name)
        self._history = history

    def record_transaction(
            self, transaction: Transaction, is_asset=True, idx: int = -1
    ):
        self._transaction_history.append(transaction)
        if idx == -1:
            if self._history is not None:
                idx = max(0, min(len(self._history), len(self._history) + idx))
                transaction.attributed_histories[self._history] = idx
            if transaction.security and transaction.value and is_asset:
                self._update_current_assets(transaction)

        else:
            transaction.attributed_histories[self._history] = idx

        self._is_assets_weights_updated = False

    def _update_current_assets(self, transaction: Transaction):
        if transaction.security in self._current_assets:
            self._current_assets[transaction.security] += (
                    transaction.quantity * transaction.trade_type.value
            )
        else:
            self._current_assets[transaction.security] = transaction.quantity
        self._is_assets_value_updated = False

    def trade(self, security: Security | str, signal: Signal | str, timestamp=None):
        if signal.trade_type == TradeType.WAIT or signal.quantity == 0:
            return
        if isinstance(security, str):
            security = self.security_manager.securities[security]

        price = signal.price
        if self._history is not None and signal.price is None:
            price = self._history.df[security].iloc[-1]
        transaction = Transaction(
            security, signal.quantity, price, signal.trade_type, timestamp
        )

        if signal.trade_type == TradeType.BUY:
            if transaction.value + transaction.cost > self.current_cash:
                raise ValueError(
                    "Not enough cash to execute the order. "
                    "Trying to use {} but only have {}.".format(
                        transaction.value, self.current_cash
                    )
                )
            self._use_cash(transaction.value + transaction.cost, timestamp)

        elif signal.trade_type.SELL:
            if (
                    not self._current_assets
                    or not (security in self._current_assets)
                    or signal.quantity > self._current_assets[security]
            ):
                raise ValueError(
                    "Not enough of the security {} to sell. "
                    "Trying to sell {} but only have {}.".format(
                        security,
                        signal.quantity,
                        self._current_assets.get(security, 0),
                    )
                )
            self.add_cash(abs(transaction.value) - transaction.cost, timestamp)

        self.record_transaction(transaction)

    def _associate_transaction_with_history(self, transaction: Transaction):
        for security, history_df in self._history.df.items():
            if transaction.security == security:
                closest_index = history_df.index.get_loc(
                    transaction.timestamp, method="nearest"
                )
                transaction.attributed_histories[security] = closest_index
                break

    @property
    def historical_quantity(self):
        if self.history is None:
            return None
        self._historical_quantity = np.zeros_like(self.history.df)
        self._historical_quantity = pd.DataFrame(
            self._historical_quantity,
            index=self.history.df.index,
            columns=self.history.df.columns,
        )

        for transaction in self.transaction_history:
            if transaction.security not in self.history.securities:
                continue

            time_index = transaction.get_time(self.history)
            security_weights = self._historical_quantity[transaction.security]

            if transaction.trade_type == TradeType.BUY:
                security_weights.iloc[time_index:] += transaction.quantity
            elif transaction.trade_type == TradeType.SELL:
                security_weights.iloc[time_index:] -= transaction.quantity

        return self._historical_quantity

    def historical_returns(self, historical_quantity=None):
        if self.history is None:
            return None

        returns = self.history.df.pct_change()
        returns.iloc[0] = 0

        return returns * (
            self.historical_quantity
            if historical_quantity is None
            else historical_quantity
        )


def main():
    symbols: list[str] = ["AAPL", "GOOGL", "MSFT"]
    price_data = np.array(
        [
            [150.0, 2500.0, 300.0],
            [152.0, 2550.0, 305.0],
            [151.5, 2510.0, 302.0],
            [155.0, 2555.0, 308.0],
            [157.0, 2540.0, 306.0],
        ]
    )
    price_data = pd.DataFrame(price_data, columns=symbols)

    portfolio = Portfolio()
    portfolio.add_cash(1000, 0)

    portfolio.history = price_data

    portfolio.trade("AAPL", Signal(TradeType.BUY, 1))
    portfolio.trade("MSFT", Signal(TradeType.BUY, 2))
    portfolio.print_transaction_history()
    print(portfolio.current_cash)
    print(portfolio.historical_returns())


# Example usage:
if __name__ == "__main__":
    main()
