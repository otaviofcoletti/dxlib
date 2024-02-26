import datetime
import os
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


class Date:
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


class Cache:
    def __init__(self, hash_func: callable = hash):
        self.directory = os.path.join(os.path.expanduser("~"), ".dxlib")
        self.hash_func = hash_func

    def _key(self, *args, **kwargs):
        # hash key
        return self.hash_func(args + tuple(kwargs.items()))

    def _path(self, path: str | tuple = None, key=None, *args, **kwargs):
        # path is subdirectory
        if path is not None:
            path = os.path.join(self.directory, *path)
        else:
            path = self.directory

        if key is None:
            key = self._key(*args, **kwargs)
        return os.path.join(path, str(key))

    def get(self, path: str | tuple = None, *args, **kwargs) -> str:
        with open(self._path(path, *args, **kwargs), "r") as f:
            return f.read()

    def set(self, data: str, path: str | tuple = None, *args, **kwargs) -> None:
        with open(self._path(path, *args, **kwargs), "w") as f:
            f.write(data)

    def exists(self, path: str | tuple = None, *args, **kwargs) -> bool:
        return os.path.exists(self._path(path, *args, **kwargs))
