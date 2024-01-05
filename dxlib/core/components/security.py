from __future__ import annotations

from enum import Enum
from typing import List


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
    def __init__(self, cash: Security | str | None = None, securities: List[Security] = None):
        super().__init__()
        self._cash = Security("cash", SecurityType.cash) if cash is None else cash
        self._securities: dict[str, Security] = securities if securities else {}

    @classmethod
    def from_list(
        cls, securities: List[Security | str], cash: Security | str | None = None
    ):
        security_manager = SecurityManager(cash)
        for security in securities:
            security_manager.add(security)
        return security_manager

    def __repr__(self):
        return f"SecurityManager({len(self._securities)})"

    @property
    def cash(self):
        return self._cash

    def __len__(self):
        return len(self._securities)

    def __getitem__(self, item: str):
        return self._securities[item]

    def get(self, item: str, default: Security | None = None):
        return self._securities.get(item, default)

    def __contains__(self, item: str):
        return item in self._securities

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

    def add(self, security: Security | List[Security] | str):
        if isinstance(security, Security):
            self.add_security(security)
        elif isinstance(security, list):
            self.add_securities(security)
        elif isinstance(security, str):
            self.add_ticker(security)
        else:
            raise ValueError(f"Invalid security type {type(security)}")

    def add_security(self, security: Security):
        if security.ticker in self._securities:
            raise ValueError(f"Security {security} already exists in manager")
        self._securities[security.ticker] = security

    def add_securities(self, securities: List[Security]):
        for security in securities:
            self.add_security(security)

    def add_ticker(self, ticker: str):
        self.add_security(Security(ticker))
