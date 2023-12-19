from dxlib import History

from ...interfaces import MarketInterface, PortfolioInterface, OrderInterface


class AlphaVantageMarket(MarketInterface):
    def __init__(self):
        super().__init__()

    @property
    def history(self) -> History:
        return History()
