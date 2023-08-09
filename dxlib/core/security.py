class Security:
    def __init__(self, symbol: str, source=None):
        self.symbol = symbol
        self.source = source


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SecurityManager(metaclass=SingletonMeta):
    def __init__(self):
        self.securities: dict[str, Security] = {"cash": Security("cash")}

    def add_security(self, security: Security | str):
        if isinstance(security, str):
            security = Security(security)

        if security.symbol in self.securities:
            return

        self.securities[security.symbol] = security

    def add_securities(self, securities: list[Security | str]):
        for security in securities:
            self.add_security(security)

    def get_security(self, symbol):
        return self.securities[symbol]

    def get_cash(self):
        return self.securities["cash"]

    def get_securities(self):
        return self.securities.values()
