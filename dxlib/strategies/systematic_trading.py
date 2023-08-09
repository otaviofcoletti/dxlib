from sklearn.ensemble import RandomForestClassifier

from ..simulation import Strategy
from ..core import Signal, TradeType


class SystematicRandomForest(Strategy):
    def __init__(self):
        super().__init__()
        self.model = None

    def train(self, historical_data):
        pass

        self.model = RandomForestClassifier()

    def execute(self, row, idx, history):
        y_pred = self.model.predict()
        print(y_pred)
