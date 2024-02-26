from .api import *
from ..external_interface import ExternalHTTPInterface


class HTTPInterface(ExternalHTTPInterface):
    pass


class YFinance:
    def __init__(self):
        self.http_interface = HTTPInterface()