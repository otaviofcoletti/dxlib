from __future__ import annotations

from functools import lru_cache
from typing import Dict, Union

from ..security import Security


class Inventory(dict[Security, Union[float, int]]):
    def __init__(self, securities: Dict[Security, float | int] | None = None):
        super().__init__()
        self._securities: Dict[Security, float | int] = securities if securities else {}

    def __dict__(self):
        return {
            "securities": {security.__dict__(): quantity for security, quantity in self._securities.items()}
        }

    def __len__(self):
        return len(self._securities)

    def __getitem__(self, item: Security):
        return self._securities[item]

    def __iter__(self):
        return iter(self._securities.keys())

    def __add__(self, other: Inventory):
        return Inventory({key: self.get(key, 0) + other.get(key, 0) for key in set(self) | set(other)})

    def __iadd__(self, other: Inventory):
        self._securities = (self + other)._securities
        return self

    def get(self, item: Security, default: float | int = None):
        return self._securities.get(item, default)

    def add(self, security: Security, quantity: float | int):
        if security in self._securities:
            self._securities[security] += quantity
        else:
            self._securities[security] = quantity

    @property
    def quantities(self):
        return self._securities

    def _value(self, security: Security, prices: dict[Security, float]):
        return self._securities.get(security, 0) * prices.get(security, 0)

    @lru_cache(maxsize=128)
    def value(self, prices: Dict[Security, float]):
        return sum([self._value(security, prices) for security in self._securities])

    @property
    @lru_cache(maxsize=4)
    def weights(self):
        total = sum(self._securities.values())
        return {security: quantity / total for security, quantity in self._securities.items()}

    @lru_cache(maxsize=4)
    def financial_weights(self, prices: dict[Security, float]):
        value = self.value(prices)
        return {security: (self._value(security, prices) / value) for security in self._securities}
