import logging

import numpy as np
import pandas
import pandas as pd

from .. import Portfolio, TradeType, Signal, History, GenericManager
from ..strategies import Strategy
from ..api import endpoint


class SimulationManager(GenericManager):
    def __init__(self,
                 portfolio: Portfolio,
                 strategy: Strategy,
                 history: History | pd.DataFrame,
                 use_server=False,
                 port=None,
                 logger: logging.Logger = None):
        super().__init__(use_server, port, logger)
        self.portfolio = portfolio
        self.strategy = strategy
        self._history: History | None = None
        self._current_step: int = 0

        self.history = history

    @property
    def finished(self):
        return self._current_step >= len(self.history.df)

    @property
    def current_step(self):
        return self._current_step

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, history: History | pd.DataFrame | np.ndarray):
        self.portfolio.security_manager.add_securities(history.columns)

        if isinstance(history, pd.DataFrame):
            history = History(history)
        elif isinstance(history, np.ndarray):
            history = History(pd.DataFrame(history))

        if self.portfolio.history is None:
            self.portfolio.history = History(pandas.DataFrame(columns=history.df.columns))

        self._history = history

    @classmethod
    def train_test_split(cls, features, labels, percentage):
        size = int(len(features) * percentage)

        train = {"x": features[:size], "y": labels[:size].flatten()}
        test = {"x": features[size:], "y": labels[size:].flatten()}

        return train, test

    @endpoint("execute", "Calls the execute method within a simulation manager instance")
    def execute(self, steps: int = None):
        signal_history = []
        if self.history is None:
            raise ValueError("SimulationManager has no history to expand on.")

        if steps is None:
            steps = len(self.history.df) - self._current_step

        for idx, row in self.history.df.iloc[self._current_step:self._current_step + steps].iterrows():
            index = pd.Index(pd.Series(idx))
            self.portfolio.history.add_row(row, index=index)
            self._current_step += 1

            signals = self.strategy.execute(idx, row, self.portfolio.history)

            for symbol, signal in signals.items():
                try:
                    if signal.trade_type != TradeType.WAIT:
                        signal_history.append(signal)
                        self.portfolio.trade(str(symbol), signal)
                        self.logger.info(f"Executed {signal} for {symbol}")
                except ValueError as e:
                    self.logger.warning(f"{e}")

        return signal_history


def main():
    import numpy as np

    symbols = ['AAPL', 'GOOGL', 'MSFT']
    history = np.array([
        [150.0, 2500.0, 300.0],
        [152.0, 2550.0, 305.0],
        [151.5, 2510.0, 302.0],
        [155.0, 2555.0, 308.0],
        [157.0, 2540.0, 306.0],
    ])

    history = pd.DataFrame(history, columns=symbols)

    starting_cash = 1e6
    portfolio = Portfolio()
    portfolio.add_cash(starting_cash)

    class BuyOnCondition(Strategy):
        def __init__(self):
            super().__init__()
            self.signal_history = []

        def execute(self, row, idx, history):
            row_signal = pd.Series(index=range(len(row)))
            if 0 < idx < 3:
                signal = Signal(TradeType.BUY, 2, row[0])
                row_signal[0] = signal
            elif idx > 2:
                signal = Signal(TradeType.SELL, 6, row[0])
                row_signal[0] = signal
            row_signal[pd.isna(row_signal)] = Signal(TradeType.WAIT)

            self.signal_history.append(row_signal)
            return row_signal

    strategy = BuyOnCondition()

    from .. import info_logger
    simulation = SimulationManager(portfolio, strategy, history, logger=info_logger())

    historical_quantity = simulation.execute()
    print(portfolio.historical_returns(historical_quantity))
    print("Profit:", str(portfolio.current_value - starting_cash))


# Example usage:
if __name__ == "__main__":
    main()
