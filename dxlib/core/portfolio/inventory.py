from __future__ import annotations

from functools import lru_cache
from typing import Dict, Union

from ..security import Security


class Inventory(dict[Security, Union[float, int]]):
    def __init__(self, securities: Dict[Security, float | int] | None = None):
        super().__init__()
        self._securities: Dict[Security, float | int] = securities if securities else {}

    def __len__(self):
        return len(self._securities)

    def __getitem__(self, item: Security):
        return self._securities[item]

    def get(self, item: Security, default: float | int = None):
        return self._securities.get(item, default)

    def __iter__(self):
        return iter(self._securities.keys())

    def __iadd__(self, other: Inventory):
        self._securities = (self + other)._securities
        return self

    def __add__(self, other: Inventory):
        return Inventory({key: self.get(key, 0) + other.get(key, 0) for key in set(self) | set(other)})

    def increase(self, security: Security, quantity: float | int):
        if security in self._securities:
            self._securities[security] += quantity
        else:
            self._securities[security] = quantity

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
