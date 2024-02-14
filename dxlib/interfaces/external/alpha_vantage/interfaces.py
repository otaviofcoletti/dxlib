from dxlib import History

from dxlib.interfaces.external.external_interfaces import MarketInterface


class AlphaVantageMarket(MarketInterface):
    def __init__(self):
        super().__init__()

    @property
    def history(self) -> History:
        return History()
