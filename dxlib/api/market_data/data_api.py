import datetime
import os

import requests

from enum import Enum


class RequestType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


def request(func):
    def wrapper(self, *args, **kwargs):
        self.num_calls += 1
        return func(self, *args, **kwargs)

    return wrapper


class DataApi:
    def __init__(self, base_url=None, api_key=None, api_secret=None, api_version="v1"):
        self.base_url = base_url
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.api_version = api_version
        self.headers = {}

    @classmethod
    def default_date_interval(cls, start=None, end=None):
        if start is None:
            start = datetime.datetime.today() - datetime.timedelta(days=365)
        if end is None:
            end = datetime.datetime.today() - datetime.timedelta(days=1)

        return start, end

    @classmethod
    def str_to_date(cls, date):
        if isinstance(date, list) or isinstance(date, tuple):
            return [
                datetime.datetime.strptime(single_date, "%Y-%m-%d")
                if isinstance(single_date, str)
                else single_date
                for single_date in date
            ]
        elif isinstance(date, str):
            return datetime.datetime.strptime(date, "%Y-%m-%d")
        else:
            raise TypeError("Date must be a list or str")

    @classmethod
    def date_to_str(cls, date):
        if isinstance(date, list) or isinstance(date, tuple):
            return [
                single_date.strftime("%Y-%m-%d")
                if isinstance(single_date, datetime.date)
                else single_date
                for single_date in date
            ]
        elif isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            return date.strftime("%Y-%m-%d")
        else:
            raise TypeError("Date must be list or datetime.datetime")

    @classmethod
    def format_tickers(cls, tickers):
        if isinstance(tickers, str):
            tickers = [tickers]
        return tickers

    def form_url(self, endpoint_uri, api_version=None):
        if api_version is None:
            api_version = self.api_version
        return f"{self.base_url}/{api_version}/{endpoint_uri}"


class SnapshotApi(DataApi):
    def __init__(self, base_url=None, api_key=None, api_secret=None, api_version="v1"):
        super().__init__(base_url, api_key, api_secret, api_version)

        self.num_calls = 0

    def tickers_cache(
        self, start, end, timeframe, api_name=None, folder="cache", ext="csv"
    ):
        if not os.path.exists(folder):
            print("Creating cache folder")
            os.mkdir(folder)
        start, end = self.date_to_str(self.default_date_interval(start, end))

        filename = f'{folder}/{start}_{end}_{timeframe}{"_" + api_name if api_name else ""}.cache.{ext}'

        return filename

    @classmethod
    def symbols_cache(cls, api_name=None, n=10, filter_="volume", folder="cache", ext="csv"):
        if not os.path.exists(folder):
            print("Creating cache folder")
            os.mkdir(folder)
        filename = f'{folder}/symbols_{n}_{filter_}_{"_" + api_name if api_name else ""}.cache.{ext}'

        return filename

    @request
    def get(self, url, headers=None):
        if headers is None:
            headers = {}

        response = requests.get(url, headers=headers | self.headers)

        return response.json()

    @request
    def post(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        response = requests.post(url, headers=headers | self.headers, data=data)

        return response.json()

    @request
    def put(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        response = requests.put(url, headers=headers | self.headers, data=data)

        return response.json()

    @request
    def delete(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        response = requests.delete(url, headers=headers | self.headers, data=data)

        return response.json()


class StreamApi(DataApi):
    def __init__(self, base_url, api_key=None, api_secret=None, api_version="v1"):
        super().__init__(base_url, api_key, api_secret, api_version)

    def get_stream(self):
        s = requests.Session()

        with s.get(self.base_url, headers=None, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    print(line)
