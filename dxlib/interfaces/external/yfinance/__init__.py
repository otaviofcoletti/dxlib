from .yfinance_api import YFinanceAPI
from ..external_interface import ExternalWSInterface, ExternalHTTPInterface


class MarketHTTPInterface(ExternalHTTPInterface, YFinanceAPI):
    pass


class MarketWSInterface(ExternalWSInterface, YFinanceAPI):
    pass
