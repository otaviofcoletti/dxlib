class Security:
    def __init__(self, symbol: str, source=None):
        self.symbol = symbol
        self.source = source


class SecurityManager:
    securities: dict[str, Security] = {"cash": Security("cash")}

    @classmethod
    def add_security(cls, security: Security | str):
        if isinstance(security, str):
            security = Security(security)

        if security.symbol in cls.securities:
            return

        cls.securities[security.symbol] = security

    @classmethod
    def add_securities(cls, securities: list[Security | str]):
        for security in securities:
            cls.add_security(security)

    @classmethod
    def get_security(cls, symbol):
        return cls.securities[symbol]

    @classmethod
    def get_cash(cls):
        return cls.securities["cash"]

    @classmethod
    def get_securities(cls):
        return cls.securities.values()
