import logging
from abc import ABC

import numpy as np
import pandas

from ..core import Portfolio, TradeType, Signal
from .. import no_logger
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score


class Strategy(ABC):
    def __init__(self):
        pass

    def execute(self, row, idx, history) -> Signal:
        pass


class BuyOnCondition(Strategy):
    def __init__(self):
        super().__init__()
        self.signal_history = []

    def execute(self, row, idx, history):
        if 0 < idx < 4:
            signal = Signal(TradeType.BUY, 2, row[0])
            self.signal_history.append(signal)
        elif idx > 5:
            signal = Signal(TradeType.SELL, 59, row[1])
            self.signal_history.append(signal)
        else:
            signal = Signal(TradeType.WAIT)
        return signal


class Simulation:
    def __init__(self, portfolio: Portfolio, strategy: Strategy, logger: logging.Logger = None):
        self.portfolio = portfolio
        self.strategy = strategy

        if logger is None:
            self.logger = no_logger(__name__)
        else:
            self.logger = logger

    @classmethod
    def momentum(cls, security, T):
        momentum_T = security.copy()
        momentum_T[0:T] = 0

        for i in range(T, len(momentum_T.values)):
            momentum_T.iloc[i] = security.iloc[i] / security.iloc[i - T]

        return momentum_T

    @classmethod
    def price_size(cls, security, T):
        pcs = security / security.rolling(T).sum()

        return pcs.fillna(method='bfill')

    @classmethod
    def vol_rolling(cls, security, T):
        vol = security.pct_change().rolling(T).std(ddof=0)

        return vol.fillna(method='bfill')

    @classmethod
    def train_test_split(cls, features, labels, percentage):
        size = int(len(features) * percentage)

        train = {"x": features[:size], "y": labels[:size].flatten()}
        test = {"x": features[size:], "y": labels[size:].flatten()}

        return train, test

    @classmethod
    def simulate_trade_allocation(cls, title, y_pred, basis, symbol, symbol2):
        y_pred_portfolio = np.array([1 - y_pred, y_pred]).T
        basis['BUY-PRED'] = np.argmin(y_pred_portfolio, axis=1)
        basis['SELL-PRED'] = np.argmax(y_pred_portfolio, axis=1)

        basis['BUY-PRED'] = basis['BUY-PRED'].shift(1).fillna(1)
        basis['SELL-PRED'] = basis['SELL-PRED'].shift(1).fillna(0)

        basis['PRED-PERCENTAGE'] = basis[symbol].to_numpy().flatten() * basis['BUY-PRED'].to_numpy() + basis[
            symbol2].to_numpy().flatten() * basis['SELL-PRED'].to_numpy()
        basis['PRED-CHANGES'] = (1 + basis['PRED-PERCENTAGE'].fillna(0).to_numpy()).cumprod()

        print(title)
        return basis["PRED-CHANGES"], \
            (basis["PRED-CHANGES"].iloc[-1] - basis["PRED-CHANGES"].iloc[0]) / basis["PRED-CHANGES"].iloc[0]

    def run(self):
        signal_history = []
        for idx, row in self.portfolio.history.df.iterrows():
            signal = self.strategy.execute(row, idx, self.portfolio.history)
            signal_history.append(signal)

            self.logger.info(f"Executing {signal}")
        return signal_history


def main():
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    price_data = np.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])

    price_data = pandas.DataFrame(price_data, columns=symbols)

    portfolio = Portfolio()
    portfolio.set_history(price_data)
    portfolio.add_cash(10000)
    strategy = BuyOnCondition()

    simulation = Simulation(portfolio, strategy)
    signal_history = simulation.run()

    returns = portfolio.calculate_returns(signal_history)
    print(returns)


# Example usage:
if __name__ == "__main__":
    main()
