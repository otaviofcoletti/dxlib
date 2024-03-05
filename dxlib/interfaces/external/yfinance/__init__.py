import asyncio
import threading
from typing import Any, Coroutine

from .yfinance_api import YFinanceAPI


class YFinanceMarketWS(YFinanceAPI):
    def __init__(self):
        super().__init__()

    async def get_data(self, tickers):
        while True:
            yield self.quote(tickers)
            await asyncio.sleep(60)

    # since no actual websocket exists for api, simulate a websocket by querying every 1 minute
    def listen(self, tickers, callback, threaded=False) -> Coroutine[Any, Any, None] | threading.Thread:
        # use self.get_data, call callback with data
        async def run():
            async for data in self.get_data(tickers):
                callback(data)

        # if threaded, create and return thread
        # else, return coroutine
        if threaded:
            # create thread and run await
            t = threading.Thread(target=lambda: asyncio.run(run()))
            return t
        else:
            return run()
