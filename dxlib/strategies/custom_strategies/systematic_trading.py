import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from ..strategy import Strategy
from ...core import History


class SystematicRandomForest(Strategy):
    def __init__(self):
        super().__init__()
        self.model = None

    def train(self, historical_data):
        pass

        self.model = RandomForestClassifier()

    def execute(self, idx: pd.Index, position: pd.Series, history: History) -> pd.Series:
        y_pred = self.model.predict()
        print(y_pred)
        return pd.Series()
