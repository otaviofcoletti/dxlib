from __future__ import annotations

from ..core.history import History
from ..core.security import SecurityManager


class Market:
    def __init__(self, identifier: str | None = None):
        self.security_manager = SecurityManager()
        self.identifier = identifier or hash(self)
        self.history = History(self.security_manager)

    def get_securities(self, ticker: str = None):
        return self.security_manager.get(ticker)

    @property
    def time(self):
        return self.history.time()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.identifier})"

