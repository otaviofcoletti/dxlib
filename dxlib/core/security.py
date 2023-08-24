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
                 symbol: str,
                 security_type: str | SecurityType = SecurityType.equity,
                 source=None,
                 ):
        self.symbol = symbol
        self.source = source
        self.security_type = security_type

    def __repr__(self):
        return f"{self.__class__.__name__}({self.symbol}, {self.security_type})"

    def __str__(self):
        return f"{self.symbol}"

    def to_json(self):
        return {
            "symbol": self.symbol,
            "security_type": self.security_type.value,
            "source": self.source if self.source else None,
        }


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SecurityManager(metaclass=SingletonMeta):
    def __init__(self):
        self._securities: dict[str, Security] = {}
        self._cash = Security("cash", SecurityType.cash)

    def __iadd__(self, security_dict: dict[str, Security]):
        self.securities = security_dict
        return self

    @property
    def cash(self):
        return self._cash

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
            if security.symbol not in self.securities:
                self.securities[security.symbol] = security

    def get_securities(self, securities: list[str, Security] = None) -> dict[str, Security]:
        if securities:
            filtered_securities = {}
            for security in securities:
                if isinstance(security, str):
                    filtered_securities[security] = self.securities[security]
                elif isinstance(security, Security):
                    filtered_securities[security.symbol] = self.securities[security.symbol]
            return filtered_securities
        return self.securities
