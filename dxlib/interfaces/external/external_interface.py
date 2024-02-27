from abc import ABC

import pandas as pd

from ..utils import Cache
from ...core import StandardSchema, StandardLevel, History


class ExternalInterface(ABC):

    def __init__(self):
        self.cache = Cache()

    @classmethod
    def to_history(cls, df: pd.DataFrame, levels: list = None, fields: list = None, security_manager=None) -> History:
        schema = StandardSchema(
            levels=[StandardLevel.SECURITY, StandardLevel.DATE] if levels is None else levels,
            fields=list(df.columns) if fields is None else fields,
            security_manager=security_manager
        )

        return History.from_df(df, schema)


class ExternalHTTPInterface(ExternalInterface):
    pass


class ExternalWSInterface(ExternalInterface):
    pass
