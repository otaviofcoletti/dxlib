from abc import ABC, abstractmethod

import pandas as pd

from ..core import History
from ..core.portfolio.inventory import Inventory


class Strategy(ABC):
    def __init__(self, identifier: str = None):
        self.identifier = identifier

    def fit(self, history: History):
        pass

    @abstractmethod
    def execute(
        self, idx, position: Inventory, history: History
    ) -> pd.Series:  # expected element type: Signal
        pass
