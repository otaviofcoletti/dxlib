from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .trade_signal import TradeSignal
from .transaction import Transaction, TransactionType
from ..history import History
from ..security import SecurityType, Security
from ... import SecurityManager, no_logger


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
            Transaction(cash, amount, 1, TransactionType.SELL, timestamp=timestamp), is_asset=False
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

    def trade(self, security: Security | str, signal: TradeSignal | str, timestamp=None):
        if signal.trade_type == TransactionType.WAIT or signal.quantity == 0:
            return
        if isinstance(security, str):
            security = self.security_manager.securities[security]

        price = signal.price
        if self._history is not None and signal.price is None:
            price = self._history.df[security].iloc[-1]
        transaction = Transaction(
            security, signal.quantity, price, signal.trade_type, timestamp
        )

        if signal.trade_type == TransactionType.BUY:
            if transaction.value + transaction.cost > self.current_cash:
                raise ValueError(
                    "Not enough cash to execute the order. "
                    "Trying to use {} but only have {}.".format(
                        transaction.value, self.current_cash
                    )
                )
            self._use_cash(abs(transaction.value * 1.03) + transaction.cost, timestamp)

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
            self.add_cash(abs(transaction.value * 0.97) - transaction.cost, timestamp)

        self.record_transaction(transaction)

    def _associate_transaction_with_history(self, transaction: Transaction):
        for security, history_df in self._history.df.items():
            if transaction.security == security:
                closest_index = history_df.index.get_loc(
                    transaction.timestamp, method="nearest"
                )
                transaction.attributed_histories[security] = closest_index
                break

    def historical_quantity(self, history: History | None = None):
        if history is None:
            history = self._history

        _historical_quantity = pd.DataFrame(
            0,
            index=history.df["Close"].index,
            columns=history.df["Close"].columns,
        )

        # Add cash column
        _historical_quantity[self.security_manager.cash] = 0

        for transaction in self.transaction_history:
            timestamp = transaction.timestamp
            if timestamp == -1:
                timestamp = history.df.index[0]

            # Set value to current timestamp date until end
            if transaction.trade_type == TransactionType.BUY:
                _historical_quantity.loc[timestamp:, transaction.security] += transaction.quantity
            elif transaction.trade_type == TransactionType.SELL:
                _historical_quantity.loc[timestamp:, transaction.security] -= transaction.quantity

        return _historical_quantity

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

    portfolio.trade("AAPL", TradeSignal(TransactionType.BUY, 1))
    portfolio.trade("MSFT", TradeSignal(TransactionType.BUY, 2))
    portfolio.print_transaction_history()
    print(portfolio.current_cash)
    print(portfolio.historical_returns())


# Example usage:
if __name__ == "__main__":
    main()
