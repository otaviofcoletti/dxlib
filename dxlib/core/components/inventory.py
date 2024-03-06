from __future__ import annotations

from functools import lru_cache
from typing import Dict, Union, List

from ..trading import Order
from .security import Security, SecurityManager


class Inventory(dict[Security, Union[float, int]]):
    def __init__(self, securities: Dict[Security, Union[float, int]] | None = None):
        super().__init__()
        self._securities: Dict[Security, Union[float, int]] = securities if securities else {}

    @property
    def securities(self):
        return self._securities

    def __repr__(self):
        securities = {str(security): quantity for security, quantity in self._securities.items()}
        return f"Inventory({securities})"

    def __len__(self):
        return len(self._securities)

    def __getitem__(self, item: Security):
        return self._securities[item]

    def __iter__(self):
        return iter(self._securities.keys())

    def __add__(self, other: Inventory):
        return Inventory(
            {
                key: self.get(key, 0) + other.get(key, 0)
                for key in set(self) | set(other)
            }
        )

    def __iadd__(self, other: Inventory):
        self._securities = (self + other)._securities
        return self

    def __eq__(self, other: Inventory):
        return all([
            self.get(security) == other.get(security) for security in set(self) | set(other)
        ])

    def items(self):
        return self._securities.items()

    def values(self):
        return self._securities.values()

    def keys(self):
        return self._securities.keys()

    def get(self, item: Security, default: float | int = None):
        return self._securities.get(item, default)

    def add_signals(self, signals: dict[Security, float | int]):
        for security, quantity in signals.items():
            self.add(security, quantity)

    def add(self, security: Security, quantity: float | int):
        if security in self._securities:
            self._securities[security] += quantity
        else:
            self._securities[security] = quantity

    @property
    def quantities(self):
        return sum(self._securities.values())

    def _value(self, security: Security, values: dict[Security, float]):
        return self._securities.get(security, 0) * values.get(security, 0)

    def value(self, values: Dict[Security, float]):
        return sum([self._value(security, values) for security in self._securities])

    @property
    @lru_cache(maxsize=4)
    def weights(self):
        total = sum(self._securities.values())
        return {
            security: quantity / total
            for security, quantity in self._securities.items()
        }

    @lru_cache(maxsize=4)
    def financial_weights(self, prices: dict[Security, float]):
        value = self.value(prices)
        return {
            security: (self._value(security, prices) / value)
            for security in self._securities
        }

    @classmethod
    def serialize(cls, obj: any):
        if isinstance(obj, (int, float, str)):
            return obj
        elif isinstance(obj, dict):
            return tuple((cls.serialize(k), cls.serialize(v)) for k, v in obj.items())
        elif isinstance(obj, Security):
            return cls.serialize(obj.to_dict())
        elif isinstance(obj, tuple):
            return tuple(map(cls.serialize, obj))
        return obj

    @classmethod
    def deserialize(cls, obj: any):
        if isinstance(obj, (int, float, str)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return {cls.deserialize(k): cls.deserialize(v) for k, v in obj}
        return obj

    def to_dict(self, serializable=False):
        to_key = str if serializable else lambda x: x
        return {
            "securities": {
                to_key(self.serialize(security)): quantity
                for security, quantity in self._securities.items()
            }
        }

    @classmethod
    def from_dict(cls, serialized=False, **kwargs) -> Inventory:
        to_key = eval if serialized else lambda x: x
        return cls(
            securities={
                Security.from_dict(**cls.deserialize(to_key(key))): value
                for key, value in kwargs.get("securities").items()
            }
        )

    def map_securities(self, security_manager: SecurityManager):
        self._securities = {
            security_manager.get(security, security): quantity
            for security, quantity in self._securities.items()
        }

        return self

    @classmethod
    def from_orders(cls, orders: List[Order]):
        return cls(
            securities={
                order.data.security: (order.data.quantity or 0) * order.data.side.value
                for order in orders
            }
        )
