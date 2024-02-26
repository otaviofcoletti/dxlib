from __future__ import annotations

import datetime
import os

import requests


class YFinanceAPI:
    def __init__(self, base_url="https://query1.finance.yahoo.com/v8/finance/chart/"):
        self.base_url = base_url
        self.session = requests.Session()

        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.3"
        )

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
            "Time": [datetime.datetime.fromtimestamp(ts) for ts in trades],
            "Open": prices["open"],
            "High": prices["high"],
            "Low": prices["low"],
            "Close": prices["close"],
            "Volume": prices["volume"],
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

    def quote_tickers(
            self,
            tickers,
            start: str | datetime.date = None,
            end: str | datetime.date = None,
            timeframe="1d",
            cache=True,
    ):
        tickers = self.format_tickers(tickers)
        start, end = self.str_to_date(self.default_date_interval(start, end))

        tickers_cache = self.tickers_cache(start, end, timeframe, "yfinance_bars")
        if os.path.exists(tickers_cache) and cache:
            return pd.read_csv(
                tickers_cache, header=[0, 1], index_col=0, parse_dates=True
            )

        historical_bars = self._query_historical_bars(tickers, timeframe, start, end)
        concatenated_data = []
        for ticker, data in historical_bars.items():
            df = pd.DataFrame(data)
            df.set_index("Time", inplace=True)
            df.columns = pd.MultiIndex.from_product(
                [[ticker], df.columns], names=["Ticker", "Field"]
            )
            concatenated_data.append(df)

        historical_bars = (
            pd.concat(concatenated_data, axis=1).swaplevel(axis=1).sort_index(axis=1)
        )

        if cache:
            historical_bars.to_csv(tickers_cache)

        return historical_bars

    def _quote_tickers(
            self, tickers, timeframe, start: datetime.datetime, end: datetime.datetime
    ):
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
