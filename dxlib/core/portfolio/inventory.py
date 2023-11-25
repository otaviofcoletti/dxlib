from __future__ import annotations

from collections import Counter
from functools import lru_cache
from typing import Dict

from ..security import Security


class Inventory:
    def __init__(self, securities: Dict[Security, float | int] | None = None, source=None):
        self.source = source
        self._securities: Dict[Security, float | int] = securities if securities else {}

    def __iadd__(self, other: Inventory):
        self._securities = dict(Counter(self._securities) + Counter(other._securities))
        return self

    def __add__(self, other: Inventory):
        return Inventory(dict(Counter(self._securities) + Counter(other._securities)))

    @classmethod
    def from_dict(cls, data: dict[Security, float | int]):
        return cls(data)

    def add(self, security: Security, quantity: float | int):
        if security in self._securities:
            self._securities[security] += quantity
        else:
            self._securities[security] = quantity

    def remove(self, security: Security, quantity: float | int):
        if security in self._securities:
            self._securities[security] -= quantity
        else:
            self._securities[security] = -quantity

    @property
    def quantities(self):
        return self._securities

    @lru_cache(maxsize=128)
    def security_value(self, security: Security, prices: dict[str, float | int] | float | int):
        return self._securities[security] * prices.get(security.ticker, 0) if isinstance(prices, dict) \
            else self._securities[security] * prices

    @lru_cache(maxsize=4)
    def value(self, prices: dict[str, float] | None = None):
        if prices is None:
            prices = {}
        return sum([self.security_value(security, prices) for security in self._securities])

    @property
    @lru_cache(maxsize=4)
    def weights(self):
        total = sum(self._securities.values())
        return {security: quantity / total for security, quantity in self._securities.items()}

    @lru_cache(maxsize=4)
    def financial_weights(self, prices: dict[str, float] | None = None):
        value = self.value(prices)
        return {security: (self.security_value(security, prices) / value) for security in self._securities}

    def add_transaction(self, transaction):
        self.add(transaction.security, transaction.quantity)
