import logging
from abc import ABC

import numpy
import pandas

from .. import Portfolio, TradeType, Signal, History, info_logger
from .. import no_logger


class Strategy(ABC):
    def __init__(self):
        pass

    def execute(self, row, idx, history) -> list[Signal]:
        pass


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
                    if signal.trade_type != TradeType.WAIT:
                        self.portfolio.trade(str(symbol), signal)
                        self.logger.info(f"Executed {signal} for {symbol}")
                except ValueError:
                    pass
                    # self.logger.info(f"Skipping {signal} for {symbol}")
        return self.portfolio.historical_quantity


def main():
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    history = numpy.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])

    history = pandas.DataFrame(history, columns=symbols)

    starting_cash = 1e6
    portfolio = Portfolio()
    portfolio.add_cash(starting_cash)

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

    strategy = BuyOnCondition()
    simulation = SimulationManager(portfolio, strategy, history, info_logger())

    historical_quantity = simulation.execute()
    portfolio.print_transaction_history()
    print(portfolio.historical_returns(historical_quantity))
    print("Profit:", str(portfolio.current_value - starting_cash))


# Example usage:
if __name__ == "__main__":
    main()
