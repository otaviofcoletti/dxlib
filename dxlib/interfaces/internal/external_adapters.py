import asyncio
from datetime import datetime
from typing import List, AsyncGenerator

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
    def quote(self, tickers: List[str], start: datetime | str = None, end: datetime | str = None) -> dict:
        if self.market_api is None:
            raise ValueError("No market API provided")
        quotes = self.market_api.quote(tickers, start, end)

        response = {
            "status": "success",
            "data": quotes.to_dict(serializable=True),
        }

        return response

    @Endpoint.websocket("/quote",
                        "Stream quotes for a list of securities",
                        )
    def quote_stream(self,
                     websocket: any,
                     ) -> AsyncGenerator:
        async def quote_stream():
            async for quote in self.market_api.quote_stream():
                yield quote.to_dict(serializable=True)
                # async sleep 1 minute
                await asyncio.sleep(60)

        return quote_stream()

    @Endpoint.http(Method.POST,
                   "/historical",
                   "Get historical data for a list of securities",
                   output=lambda response: History.from_dict(serialized=True, **response["data"]))
    def historical(self, tickers: List[str], start: datetime | str, end: datetime | str) -> dict:
        if self.market_api is None:
            raise ValueError("No market API provided")
        history = self.market_api.historical(tickers, start, end)

        response = {
            "status": "success",
            "data": history.to_dict(serializable=True),
        }

        return response
