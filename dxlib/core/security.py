from enum import Enum
from operator import itemgetter


class SecurityType(Enum):
    equity = "equity"
    option = "option"
    future = "future"
    forex = "forex"
    crypto = "crypto"
    cash = "cash"


class Security:
    def __init__(self,
                 symbol: str,
                 source=None,
                 security_type: str | SecurityType = SecurityType.equity):
        self.symbol = symbol
        self.source = source
        self.security_type = security_type


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SecurityManager(metaclass=SingletonMeta):
    def __init__(self):
        self._securities: dict[str, Security] = {SecurityType.cash.value: Security("cash")}

    def __iadd__(self, security_dict: dict[str, Security]):
        self.securities = security_dict
        return self

    @property
    def securities(self):
        return self._securities

    @securities.setter
    def securities(self, security_dict: dict[str, Security] | Security):
        if isinstance(security_dict, Security):
            security_dict = {security_dict.symbol: security_dict}
        if not isinstance(security_dict, dict):
            raise ValueError("security_dict must be a Security or a dictionary of securities")

        self._securities.update(security_dict)

    def add_securities(self, securities: list[Security | str] | Security):
        if isinstance(securities, Security):
            securities = [securities]

        for security in securities:
            if isinstance(security, str):
                security = Security(security)
            self.securities[security.symbol] = security

    def get_cash(self):
        return self.securities[SecurityType.cash.value]

    def get_securities(self, symbols: list = None) -> dict[str, Security]:
        if symbols:
            return {symbol: self.securities[symbol] for symbol in symbols if symbol in self.securities}
        return self.securities
