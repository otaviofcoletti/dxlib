import datetime
import os

import requests

from enum import Enum


class RequestType(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


def request(func):
    def wrapper(self, *args, **kwargs):
        self.num_calls += 1
        return func(self, *args, **kwargs)

    return wrapper


class DataApi:
    def __init__(self, base_url=None, api_key=None, api_secret=None, api_version='v1'):
        self.base_url = base_url
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.api_version = api_version

        self.num_calls = 0

    def form_url(self, endpoint_uri):
        return f'{self.base_url}/{self.api_version}/{endpoint_uri}'

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
            return [datetime.datetime.strptime(single_date, '%Y-%m-%d') if isinstance(single_date, str) else single_date
                    for single_date in date]
        elif isinstance(date, str):
            return datetime.datetime.strptime(date, '%Y-%m-%d')
        else:
            raise TypeError('Date must be a list or str')

    @classmethod
    def date_to_str(cls, date):
        if isinstance(date, list) or isinstance(date, tuple):
            return [single_date.strftime('%Y-%m-%d') if isinstance(single_date, datetime.date) else single_date
                    for single_date in date]
        elif isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
            return date.strftime('%Y-%m-%d')
        else:
            raise TypeError('Date must be list or datetime.datetime')

    @classmethod
    def format_tickers(cls, tickers):
        if isinstance(tickers, str):
            tickers = [tickers]
        return tickers

    def cache_filename(self, tickers, start, end, timeframe, api_name=None, folder="cache", ext="csv"):
        if not os.path.exists(folder):
            print("Creating cache folder")
            os.mkdir(folder)
        tickers = "_".join(sorted(self.format_tickers(tickers)))
        start, end = self.date_to_str(self.default_date_interval(start, end))

        filename = f'{folder}/{tickers}_{start}_{end}_{timeframe}{"_" + api_name if api_name else ""}.cache.{ext}'

        return filename

    @request
    def get(self, url, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.get(
            url,
            headers=headers
        )

        return response.json()

    @request
    def post(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.post(
            url,
            headers=headers,
            data=data
        )

        return response.json()

    @request
    def put(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.put(
            url,
            headers=headers,
            data=data
        )

        return response.json()

    @request
    def delete(self, url, data=None, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'APCA-API-KEY-ID': self.__api_key,
            'APCA-API-SECRET-KEY': self.__api_secret
        })

        response = requests.delete(
            url,
            headers=headers,
            data=data
        )

        return response.json()


class Stream(DataApi):
    def __init__(self, api_key, api_secret, base_url, api_version='v1'):
        super().__init__(api_key, api_secret, base_url, api_version)

    def test(self):
        self.base_url = 'https://jsonplaceholder.typicode.com/posts/1'
        self.get_stream()

    def get_stream(self):
        s = requests.Session()

        with s.get(self.base_url, headers=None, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    print(line)
