from abc import ABC, abstractmethod

import pandas as pd

from .. import History


class Strategy(ABC):
    def __init__(self):
        pass

    def fit(self, history: History):
        pass

    @abstractmethod
    def execute(
        self, idx, position: pd.Series, history: History
    ) -> pd.Series:  # expected element type: Signal
        pass
