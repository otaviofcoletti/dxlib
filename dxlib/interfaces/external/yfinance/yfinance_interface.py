from datetime import datetime
from typing import List

from .yfinance_api import YFinanceAPI
from ...internal.internal_interface import InternalInterface
from ...servers.endpoint import Endpoint, Method


class YFinanceInterface(InternalInterface):
    def __init__(self, api: YFinanceAPI = None, interface_url: str = None, headers: dict = None):
        super().__init__(interface_url, headers)
        self.api = api or YFinanceAPI()

    @Endpoint.http(Method.POST, "/quote", "Get quote data for a list of securities")
    def quote(self, tickers: List[str], start: datetime | str = None, end: datetime | str = None):
        quotes = self.api.quote(tickers, start, end)

        response = {
            "status": "success",
            "data": quotes.to_dict(serializable=True),
        }

        return response
