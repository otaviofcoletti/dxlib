from __future__ import annotations

from enum import Enum
from typing import List, Dict, Union


class SecurityType(Enum):
    equity = "equity"
    option = "option"
    future = "future"
    forex = "forex"
    crypto = "crypto"
    cash = "cash"

    def __str__(self):
        return self.value

    def to_dict(self) -> dict:
        return {
            "value": self.value
        }

    @classmethod
    def from_dict(cls, **kwargs) -> SecurityType:
        return cls(kwargs["value"].lower())


class Security:
    def __init__(
        self,
        ticker: str,
        security_type: SecurityType | str = SecurityType.equity,
    ):
        self.ticker = ticker
        self.security_type = (
            security_type
            if isinstance(security_type, SecurityType)
            else SecurityType(security_type)
        )

    def __repr__(self):
        return f"Security({self.ticker}, {self.security_type.__repr__()})"

    def __str__(self):
        return f"{self.ticker} ({self.security_type})"

    def __lt__(self, other):
        return self.ticker < other.ticker

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "security_type": self.security_type.to_dict()
        }

    @classmethod
    def from_dict(cls, **kwargs) -> Security:
        return cls(
            ticker=kwargs["ticker"],
            security_type=SecurityType.from_dict(
                **kwargs.get("security_type")
            )
        )


class SecurityManager(dict[str, Security]):
    def __init__(
        self, securities: Dict[str, Security] = None, cash: Security | str | None = None
    ):
        super().__init__()
        self._securities: Dict[str, Security] = securities if securities else {}
        self._cash = Security("cash", SecurityType.cash) if cash is None else cash

    @classmethod
    def convert(cls, security: Security | str):
        if isinstance(security, Security):
            return security
        elif isinstance(security, str):
            return Security(security)
        else:
            raise ValueError(f"Invalid security type {type(security)}")

    def __repr__(self):
        return f"SecurityManager({len(self._securities)})"

    def __len__(self):
        return len(self._securities)

    def __getitem__(self, item: str):
        return self._securities[item]

    def __contains__(self, item: str | Security):
        return item in self._securities or (
            isinstance(item, Security) and item.ticker in self._securities
        )

    def __iter__(self):
        return iter(self._securities.keys())

    def items(self):
        return self._securities.items()

    def values(self):
        return self._securities.values()

    def keys(self):
        return self._securities.keys()

    def __add__(self, other: SecurityManager):
        if not isinstance(other, SecurityManager):
            raise ValueError(f"Invalid security manager type {type(other)}")
        return SecurityManager(
            securities={**self._securities, **other._securities}, cash=self._cash
        )

    def __iadd__(self, other: SecurityManager | Security | str):
        if isinstance(other, SecurityManager):
            self._securities.update(other._securities)
        elif isinstance(other, Security) or isinstance(other, str):
            self.add(other)
        else:
            raise ValueError(f"Invalid security manager type {type(other)}")
        return self

    @property
    def cash(self):
        return self._cash

    def get(self, item: Security | str, default: Security | str | None = None):
        if isinstance(item, Security):
            return self._securities.get(item.ticker, default)
        elif isinstance(item, str):
            return self._securities.get(item, default)
        else:
            raise ValueError(f"Invalid type {type(item)} for item")

    def map(self, items: List[Security | str]):
        return [self.get(item) for item in items]

    def add(self, security: Security | str):
        if isinstance(security, Security):
            if security.ticker in self._securities:
                return self._securities[security.ticker]
            self._securities[security.ticker] = security
            return security
        elif isinstance(security, str):
            if security in self._securities:
                return self._securities[security]
            self._securities[security] = Security(security)
            return self._securities[security]
        else:
            raise ValueError(f"Invalid security type {type(security)}")

    def extend(self, securities: Union[List[Security | str], SecurityManager]):
        if isinstance(securities, SecurityManager):
            securities = securities.values()
        for security in securities:
            self.add(security) if security not in self else None

    def to_dict(self, serializable: bool = False) -> dict:
        return {
            "securities": {key: security.to_dict() for key, security in self._securities.items()},
            "cash": self._cash.to_dict(),
        }

    @classmethod
    def from_dict(cls, **kwargs) -> SecurityManager:
        return cls(
            securities={
                key: Security.from_dict(**value)
                for key, value in kwargs.get("securities").items()
            },
            cash=Security.from_dict(**kwargs.get("cash"))
        )

    @classmethod
    def from_list(
        cls, securities: List[Security] | List[str], cash: Security | str | None = None
    ):
        securities = [cls.convert(security) for security in securities]

        return SecurityManager(
            {security.ticker: security for security in securities}, cash=cash
        )
