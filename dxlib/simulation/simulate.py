import logging
from abc import ABC

import numpy as np
import pandas

from .. import Portfolio, TradeType, Signal, History, info_logger
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
        row_signal = pandas.Series(index=range(len(row)))
        if 0 < idx < 3:
            signal = Signal(TradeType.BUY, 2, row[0])
            row_signal[0] = signal
        elif idx > 2:
            signal = Signal(TradeType.SELL, 6, row[0])
            row_signal[0] = signal
        row_signal[pandas.isna(row_signal)] = Signal(TradeType.WAIT)

        self.signal_history.append(row_signal)
        return row_signal


class SimulationManager:
    def __init__(self,
                 portfolio: Portfolio,
                 strategy: Strategy,
                 history: History | pandas.DataFrame,
                 logger: logging.Logger = None):
        self.portfolio = portfolio
        self.strategy = strategy

        if isinstance(history, pandas.DataFrame):
            self.history = History(history)

        if logger is None:
            self.logger = no_logger(__name__)
        else:
            self.logger = logger

    @classmethod
    def train_test_split(cls, features, labels, percentage):
        size = int(len(features) * percentage)

        train = {"x": features[:size], "y": labels[:size].flatten()}
        test = {"x": features[size:], "y": labels[size:].flatten()}

        return train, test

    def generate_signals(self):
        signal_history = []
        for idx, row in self.history:
            signal = self.strategy.execute(row, idx, self.history[:idx])
            signal_history.append(signal)
        signals = pandas.DataFrame(signal_history)
        signals.columns = self.history.df.columns
        return signals

    def execute(self, signals: pandas.DataFrame = None):
        if signals is None:
            signals = self.generate_signals()

        for idx, row in signals.iterrows():
            if self.portfolio.history is not None:
                self.portfolio.history.add_row(self.history.df.iloc[idx])
            else:
                self.portfolio.set_history(self.history.df.iloc[:1])

            for symbol, signal in row.items():
                try:
                    self.portfolio.trade(str(symbol), signal)
                    self.logger.info(f"Executed {signal} for {symbol}")
                except ValueError as e:
                    self.logger.info(f"Skipping {signal} for {symbol}")
        return self.portfolio.calculate_returns()


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
    strategy = BuyOnCondition()
    portfolio.add_cash(10000)

    simulation = SimulationManager(portfolio, strategy, price_data, info_logger())
    returns = simulation.execute()
    print(returns)
    print(portfolio.current_value)


# Example usage:
if __name__ == "__main__":
    main()
