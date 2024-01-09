from __future__ import annotations

from enum import Enum
from typing import List, Dict


class SecurityType(Enum):
    equity = "equity"
    option = "option"
    future = "future"
    forex = "forex"
    crypto = "crypto"
    cash = "cash"

    def __str__(self):
        return self.name

    def __dict__(self):
        return self.value


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

    def __dict__(self):
        return {
            "ticker": self.ticker,
            "security_type": self.security_type.__dict__(),
        }


class SecurityManager(dict[str, Security]):
    def __init__(
            self, securities: Dict[str, Security] = None, cash: Security | str | None = None
    ):
        super().__init__()
        self._securities: Dict[str, Security] = securities if securities else {}
        self._cash = Security("cash", SecurityType.cash) if cash is None else cash

    @classmethod
    def from_list(cls, securities: List[Security] | List[str], cash: Security | str | None = None):
        securities = [cls.convert(security) for security in securities]

        return SecurityManager({
            security.ticker: security for security in securities
        }, cash=cash)

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

    def __dict__(self):
        return {
            "securities": [s.__dict__() for s in self._securities.values()],
            "cash": self._cash.__dict__(),
        }

    def __add__(self, other: SecurityManager):
        if not isinstance(other, SecurityManager):
            raise ValueError(f"Invalid security manager type {type(other)}")
        return SecurityManager.from_list(list(self) + list(other), cash=self.cash)

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
                raise ValueError(f"Security {security} already exists in manager")
            self._securities[security.ticker] = security
        elif isinstance(security, str):
            self._securities[security] = Security(security)
        else:
            raise ValueError(f"Invalid security type {type(security)}")

    def add_list(self, securities: List[Security | str]):
        for security in securities:
            self.add(security) if security not in self else None
