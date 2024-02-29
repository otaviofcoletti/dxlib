import asyncio
import threading

from .yfinance_api import YFinanceAPI
from ..external_interface import ExternalWSInterface, ExternalHTTPInterface


class MarketHTTPInterface(ExternalHTTPInterface, YFinanceAPI):
    pass


class MarketWSInterface(ExternalWSInterface, YFinanceAPI):
    def __init__(self):
        super().__init__()

    async def get_data(self, tickers):
        while True:
            yield self.quote(tickers)
            await asyncio.sleep(60)

    # since no actual websocket exists for api, simulate a websocket by querying every 1 minute
    def listen(self, tickers, callback, threaded=False) -> threading.Thread | asyncio.Task:
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
class MarketWSInterface(ExternalWSInterface, YFinanceAPI):
    pass
