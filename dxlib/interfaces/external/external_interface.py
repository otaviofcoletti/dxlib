from abc import ABC

from ..utils import Cache


class ExternalInterface(ABC):
    pass


class ExternalHTTPInterface(ExternalInterface):
    def __init__(self):
        self.cache = Cache()

