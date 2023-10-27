from __future__ import annotations

from .transaction import TransactionType


class TradeSignal:
    def __init__(
            self, transaction_type: TransactionType | str, quantity: int = 1, price: float = None
    ):
        if isinstance(transaction_type, str):
            transaction_type = TransactionType[transaction_type.upper()]
        self.trade_type = transaction_type
        self.quantity = quantity
        self.price = price

    def to_json(self):
        return {
            "trade_type": self.trade_type.name,
            "quantity": self.quantity,
            "price": self.price if self.price else "mkt",
        }

    def __str__(self):
        if self.trade_type != TransactionType.WAIT:
            return f"{self.trade_type.name}: {self.quantity} @ {self.price if self.price else 'mkt'}"
        else:
            return f"{self.trade_type.name}"
