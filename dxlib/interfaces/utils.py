import os
from enum import Enum
from hashlib import md5


class RequestType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


def md5hash(value: str):
    return md5(value.encode()).hexdigest()


class Cache:
    def __init__(self, hash_func: callable = None):
        self.directory = os.path.join(os.path.expanduser("~"), ".dxlib")
        self.hash_func = hash_func or md5hash

    def _key(self, *args, **kwargs):
        # hash key
        return self.hash_func(str(args + tuple(kwargs.items())))

    def filename(self, *args, **kwargs):
        return str(self._key(*args, **kwargs)) + ".cache.json"

    def get_path(self, filename, path: str | tuple = None):
        if path is not None:
            if isinstance(path, str):
                path = (path,)
            path = os.path.join(self.directory, *path)
        else:
            path = self.directory
        return os.path.join(path, filename)

    def get(self, filename, path: str | tuple = None) -> str:
        with open(self.get_path(filename, path), "r") as f:
            return f.read()

    def set(self, data: str, filename, path: str | tuple = None):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        with open(self.get_path(filename, path), "w") as f:
            f.write(data)

    def exists(self, filename, path: str | tuple = None) -> bool:
        return os.path.exists(self.get_path(filename, path))
