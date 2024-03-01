from datetime import datetime
from typing import List

from .internal_interface import InternalInterface
from ..servers.endpoint import Endpoint, Method
from ... import History


class MarketInterface(InternalInterface):
    def __init__(self, market_api=None, interface_url: str = None, headers: dict = None):
        super().__init__(interface_url, headers)
        if market_api is None and interface_url is None:
            raise ValueError("Executor or URL must be provided")
        self.market_api = market_api

    @Endpoint.http(Method.POST,
                   "/quote",
                   "Get quote data for a list of securities",
                   output=lambda response: History.from_dict(serialized=True, **response["data"]))
    def quote(self, tickers: List[str], start: datetime | str = None, end: datetime | str = None):
        if self.market_api is None:
            raise ValueError("No market API provided")
        quotes = self.market_api.quote(tickers, start, end)

        response = {
            "status": "success",
            "data": quotes.to_dict(serializable=True),
        }

        return response

    @Endpoint.http(Method.POST,
                   "/historical",
                   "Get historical data for a list of securities",
                   output=lambda response: History.from_dict(serialized=True, **response["data"]))
    def historical(self, tickers: List[str], start: datetime | str, end: datetime | str):
        if self.market_api is None:
            raise ValueError("No market API provided")
        history = self.market_api.historical(tickers, start, end)

        response = {
            "status": "success",
            "data": history.to_dict(serializable=True),
        }

        return response
