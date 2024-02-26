from __future__ import annotations

import datetime
import json
import os
from datetime import datetime
from enum import Enum

import pandas as pd
import websocket

from dxlib.interfaces.utils import SnapshotApi


class AlpacaMarketAPI(SnapshotApi):
    def __init__(self, api_key=None, api_secret=None):
        super().__init__("https://data.alpaca.markets", api_key, api_secret, "v2")
        self.headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}

    class Endpoints(Enum):
        stocks = "stocks"
        screener = "screener"
        exchanges = "exchanges"
        symbols = "symbols"
        bars = "bars"

    def get_trades(self, ticker):
        url = self.form_url(
            f"{self.Endpoints.stocks.value}/trades/latest?symbols={ticker}"
        )
        response = self.get(url)
        return response

    @staticmethod
    def format_trade_data(trade):
        formatted_data = {
            "Time": trade["t"],
            "Exchange": trade["x"],
            "Price": trade["p"],
            "Size": trade["s"],
            "Conditions": ", ".join(trade["c"]),
            "ID": trade["i"],
            "Tape": trade["z"],
        }
        return formatted_data

    def get_historical_trades(
        self, tickers, start: datetime.date = None, end: datetime.date = None
    ):
        if isinstance(tickers, str):
            tickers = [tickers]
        start, end = self.date_to_str(self.default_date_interval(start, end))

        ticker_str = ",".join(tickers)
        url = self.form_url(
            f"{self.Endpoints.stocks.value}/trades?symbols={ticker_str}&start={start}&end={end}"
        )
        response = self.get(url)

        formatted_data = []

        for ticker, trades in response["trades"].items():
            for trade in trades:
                formatted_trade = {
                    "Ticker": ticker,
                    "Time": trade["t"],
                    "Exchange": trade["x"],
                    "Price": trade["p"],
                    "Size": trade["s"],
                    "Conditions": ", ".join(trade["c"]),
                    "ID": trade["i"],
                    "Tape": trade["z"],
                }
                formatted_data.append(formatted_trade)

        return formatted_data

    @staticmethod
    def conversion(timeframe, x):
        return (
            datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").date()
            if timeframe == "1D"
            else datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
        )

    def _query_historical_bars(self, tickers, timeframe, start, end, page_token=None):
        ticker_str = ",".join(tickers)
        url = self.form_url(
            f"{self.Endpoints.stocks.value}/bars?symbols="
            f"{ticker_str}&start={start}&end={end}&adjustment=all&timeframe={timeframe}"
        )

        if page_token:
            url += f"&page_token={page_token}"

        response = self.get(url)
        formatted_data = []
        for ticker, bars in response["bars"].items():
            for bar in bars:
                formatted_bar = {
                    "security": ticker,
                    "date": self.conversion(timeframe, bar["t"]),
                    "open": bar["o"],
                    "high": bar["h"],
                    "low": bar["l"],
                    "close": bar["c"],
                    "volume": bar["v"],
                    "num_trades": bar["n"],
                    "vwap": bar["vw"],
                }
                formatted_data.append(formatted_bar)

        # Dataframe is a multindex instead, with columns = Open, High, Low, Close, Volume, NumTrades, VWAP
        dataframe = pd.DataFrame(formatted_data)

        if dataframe.empty:
            return dataframe
        formatted_df = dataframe.set_index(["date", "security"])

        # If response incomplete, recursive call to get next page
        next_page_token = response.get("next_page_token")
        if next_page_token:
            next_query = self._query_historical_bars(
                tickers, timeframe, start, end, page_token=next_page_token
            )
            formatted_df = pd.concat([formatted_df, next_query])

        return formatted_df

    def get_historical_bars(
        self,
        tickers,
        start: datetime.date | str = None,
        end: datetime.date | str = None,
        timeframe="1D",
        cache=True,
    ):
        tickers = self.format_tickers(tickers)
        start, end = self.date_to_str(self.default_date_interval(start, end))

        tickers_cache = self.tickers_cache(start, end, timeframe, "alpaca_market_bars")

        if os.path.exists(tickers_cache) and cache:
            df = pd.read_csv(tickers_cache, index_col=[0, 1], parse_dates=True)
            if timeframe == "1D":
                # Map first level of index to date instead of datetime
                # Leave second level as ticker
                df.index = df.index.set_levels(
                    df.index.levels[0].map(lambda x: x.date()), level=0
                )
            return df

        historical_bars = self._query_historical_bars(tickers, timeframe, start, end)

        if cache:
            historical_bars.to_csv(tickers_cache)

        return historical_bars

    def _get_tickers(self, n=10, filter_="volume"):
        # https://data.alpaca.markets/v1beta1/screener/stocks/most-actives?by=volume&top=100
        url = self.form_url(
            f"{self.Endpoints.screener.value}/{self.Endpoints.stocks.value}/most-actives?by={filter_}&top={n}",
            "v1beta1",
        )
        response = self.get(url)
        return response

    def get_tickers(self, filter_="volume", n=10, cache=True) -> pd.DataFrame:
        tickers_cache = f"cache/alpaca_markets_tickers_{n}_{filter_}" + ".cache.csv"

        if os.path.exists(tickers_cache) and cache:
            return pd.read_csv(tickers_cache, index_col=0)

        response = self._get_tickers(n, filter_)
        tickers = pd.DataFrame(response["most_actives"]).rename(
            columns={"symbol": "ticker"}
        )

        if cache:
            tickers.to_csv(tickers_cache)

        return tickers


class AlpacaStreamAPI:
    def __init__(self, api_key=None, api_secret=None, feed="iex"):
        self.api_key = api_key
        self.api_secret = api_secret

        self.headers = {"APCA-API-KEY-ID": api_key, "APCA-API-SECRET-KEY": api_secret}

        self.url = f"wss://stream.data.alpaca.markets/v2/{feed}"
        self.ws = None

    def on_open(self):
        msg = json.loads(self.ws.recv())
        print(msg)
        # send {"action": "auth", "key": "{KEY_ID}", "secret": "{SECRET}"}
        msg = json.loads(self.ws.recv())
        print(msg)
        # test {"action":"subscribe","trades":["AAPL"],"quotes":["AMD","CLDR"],"bars":["*"]}
        self.ws.send(
            json.dumps(
                {
                    "action": "subscribe",
                    "trades": ["AAPL"],
                    "quotes": ["AMD", "CLDR"],
                    "bars": ["*"],
                }
            )
        )
        # listen for messages
        for i in range(10):
            msg = json.loads(self.ws.recv())
            print(msg)

        self.ws.close()

    def connect(self):
        # Send a request to the server to establish a connection
        self.ws = websocket.create_connection(self.url, header=self.headers)
        self.on_open()

    def on_error(self, error):
        print(error)
