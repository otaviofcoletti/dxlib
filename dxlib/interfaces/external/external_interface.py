from abc import ABC
from datetime import datetime
from typing import List

import pandas as pd

from ..utils import Cache
from ...core import Schema, SchemaLevel, History


class ExternalInterface(ABC):

    def __init__(self):
        self.cache = Cache()


class MarketApi(ExternalInterface):
    @classmethod
    def to_history(cls, df: pd.DataFrame, levels: list = None, fields: list = None, security_manager=None) -> History:
        schema = Schema(
            levels=[SchemaLevel.SECURITY, SchemaLevel.DATE] if levels is None else levels,
            fields=list(df.columns) if fields is None else fields,
            security_manager=security_manager
        )

        return History.from_df(df, schema)

    def historical(
            self,
            tickers: List[str] | str,
            start: datetime | str,
            end: datetime | str,
            timeframe="1d",
            cache=False,
    ) -> History:
        raise NotImplementedError

    def quote(
            self,
            tickers: List[str] | str,
            start: datetime | str = None,
            end: datetime | str = None,
            interval="1m",
            cache=False,
    ) -> History:
        raise NotImplementedError


class OrderInterface(ExternalInterface, ABC):
    def execute(self, order):
        raise NotImplementedError


class PortfolioInterface(ExternalInterface, ABC):
    def get(self, identifier=None):
        raise NotImplementedError

    def add(self, order, market):
        raise NotImplementedError

    def set(self, portfolio):
        raise NotImplementedError
