from abc import ABC

import pandas as pd

from ..interface import Interface
from ..utils import Cache
from ...core import Schema, SchemaLevel, History


class ExternalInterface(Interface, ABC):

    def __init__(self, url: str):
        super().__init__(url)
        self.cache = Cache()


class MarketInterface(ExternalInterface, ABC):

    def __init__(self):
        super().__init__()

    @classmethod
    def to_history(cls, df: pd.DataFrame, levels: list = None, fields: list = None, security_manager=None) -> History:
        schema = Schema(
            levels=[SchemaLevel.SECURITY, SchemaLevel.DATE] if levels is None else levels,
            fields=list(df.columns) if fields is None else fields,
            security_manager=security_manager
        )

        return History.from_df(df, schema)

    def get_trades(self, ticker):
        raise NotImplementedError

    def quote_tickers(
            self,
            tickers: list | str,
            start: pd.Timestamp | str,
            end: pd.Timestamp | str,
            timeframe="1d",
            cache=False,
    ) -> History:
        raise NotImplementedError


class OrderInterface(ExternalInterface, ABC):

    def __init__(self):
        super().__init__()

    def execute(self, order):
        raise NotImplementedError


class PortfolioInterface(ExternalInterface, ABC):
    def __init__(self):
        super().__init__()

    def get(self, identifier=None):
        raise NotImplementedError

    def add(self, order, market):
        raise NotImplementedError

    def set(self, portfolio):
        raise NotImplementedError
