from __future__ import annotations

import datetime
from typing import List

import pandas as pd
import requests

from ..external_interface import ExternalInterface
from .... import SecurityManager
from ....core import History


class YFinanceAPI(ExternalInterface):
    def __init__(self, base_url="https://query1.finance.yahoo.com/v8/finance/chart/"):
        super().__init__()
        self.base_url = base_url
        self.session = requests.Session()

        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )

    @property
    def version(self):
        return "1.0"

    @property
    def header(self):
        return {'User-Agent': self.user_agent,}

    @property
    def keepalive_header(self):
        return {'Connection': 'keep-alive',
                'Expires': '-1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                }

    @staticmethod
    def _crumbs():
        return None, None
        # website = requests.get(url, headers=header)
        # crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(bs(website.text, 'lxml')))[0]

        # return crumb, website.cookies

    @classmethod
    def format_response_data(cls, data):
        trades = data["chart"]["result"][0]["timestamp"]
        prices = data["chart"]["result"][0]["indicators"]["quote"][0]
        trade_data = {
            "date": [datetime.datetime.fromtimestamp(ts) for ts in trades],
            "open": prices["open"],
            "high": prices["high"],
            "low": prices["low"],
            "close": prices["close"],
            "volume": prices["volume"],
        }

        return trade_data

    def get_trades(self, ticker):
        url = f"{self.base_url}{ticker}?range=1d&interval=1m"
        response = requests.get(url)
        data = response.json()
        if "chart" in data:
            return self.format_response_data(data)
        else:
            return None

    def _quote_tickers(
            self, tickers, timeframe, start: datetime.datetime, end: datetime.datetime
    ) -> dict:
        formatted_data = {}

        for ticker in tickers:
            url = (
                f"{self.base_url}{ticker}?period1={int(start.timestamp())}&period2={int(end.timestamp())}"
                f"&interval={timeframe}"
            )
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers)

            data = response.json()

            if "chart" in data:
                formatted_data[ticker] = self.format_response_data(data)

        return formatted_data

    @classmethod
    def to_history(cls, df: pd.DataFrame, levels: list = None, _: list = None, __=None) -> History:
        df.index.name = "security"
        security_manager = SecurityManager.from_list(df.index.unique())
        history = super(YFinanceAPI, cls).to_history(df,
                                                     levels, ["open", "high", "low", "close", "volume"],
                                                     security_manager)
        history.df = history.df.swaplevel(1, 0)
        history.schema.levels.reverse()
        return history

    def quote_tickers(
            self,
            tickers: List[str] | str,
            start: datetime.datetime | str,
            end: datetime.datetime | str,
            timeframe="1d",
            cache=False,
    ) -> History:
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(start, str):
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
        if isinstance(end, str):
            end = datetime.datetime.strptime(end, "%Y-%m-%d")

        filename = self.cache.filename(*tickers, start, end, timeframe)

        if cache and self.cache.exists(filename):
            obj = self.cache.get(filename)
            # read unix as datetime
            df = pd.read_json(obj)
            return self.to_history(df)

        obj = self._quote_tickers(tickers, timeframe, start, end)
        df = pd.DataFrame.from_dict(obj, orient="index")

        if cache:
            self.cache.set(df.to_json(date_format="iso"), filename)

        return self.to_history(df)
