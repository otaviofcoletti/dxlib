from __future__ import annotations

from enum import Enum


class SecurityType(Enum):
    equity = "equity"
    option = "option"
    future = "future"
    forex = "forex"
    crypto = "crypto"
    cash = "cash"


class Security:
    def __init__(self,
                 ticker: str,
                 security_type: str | SecurityType = SecurityType.equity,
                 source=None,
                 ):
        self.ticker = ticker
        self.source = source
        self.security_type = security_type if isinstance(security_type, SecurityType) else SecurityType(security_type)

    def __repr__(self):
        return f"{self.ticker} {self.security_type}"

    def __str__(self):
        return self.ticker

    def to_dict(self):
        return {
            "ticker": self.ticker,
            "security_type": self.security_type
        }

    def serialized(self):
        s = {
            "ticker": str(self.ticker),
            "security_type": self.security_type.value,
        }

        if self.source:
            s["source"] = str(self.source)

        return s

    @staticmethod
    def serialize(security):
        return security.serialized()


class SecurityManager:
    def __init__(self):
        self._securities: dict[str, Security] = {}
        self._cash = Security("cash", SecurityType.cash)

    def __iadd__(self, other: dict[str, Security]):
        self._securities.update(other)
        return self

    @property
    def cash(self):
        return self._cash

    @property
    def securities(self):
        return self._securities

    def __add__(self, other: dict[str | Security] | list[Security | str] | Security):
        if isinstance(other, dict):
            self._securities.update(other)
        elif isinstance(other, Security):
            self.add(other)
        elif isinstance(other, list):
            for security in other:
                self.add(security)

    def add(self, other: dict[str | Security] | list | Security | str):
        if isinstance(other, dict):
            self._securities.update(other)
        elif isinstance(other, str):
            self.securities[other] = Security(other)
        elif isinstance(other, list):
            for security in other:
                self.add(security)
        elif other.ticker not in self.securities:
            self.securities[other.ticker] = other

    def get(self, securities: list[str] | str = None) -> dict[str, Security]:
        if securities is None:
            return self.securities
        if isinstance(securities, str):
            return {securities: self.securities.get(securities, None)}

        filtered_securities = {}
        for security in securities:
            filtered_securities[security] = self.securities.get(security, None)
        return filtered_securities

    def to_dict(self):
        return {
            "securities": {k: v.to_dict() for k, v in self.securities.items()},
            "cash": self.cash.to_dict(),
        }

    def serialized(self):
        return {
            "securities": {k: v.serialized() for k, v in self.securities.items()},
            "cash": self.cash.serialized(),
        }
