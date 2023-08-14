from abc import ABC

import pandas
import pandas as pd

from .. import History


class Strategy(ABC):
    def __init__(self):
        pass

    def fit(self, history: History):
        pass

    def execute(self, idx, row: pd.Series, history: History) -> pandas.Series:  # expected element type: Signal
        pass
