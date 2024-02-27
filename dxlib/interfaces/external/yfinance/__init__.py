from .yfinance_api import YFinanceAPI
from ..external_interface import ExternalWSInterface, ExternalHTTPInterface


class YFinanceHTTPInterface(ExternalHTTPInterface, YFinanceAPI):
    pass


class YFinanceWSInterface(ExternalWSInterface, YFinanceAPI):
    pass
