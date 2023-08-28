import logging

import numpy as np
import pandas as pd

from ..core import Portfolio, TradeType, Signal, History
from ..strategies import Strategy
from ..api import Endpoint
from . import StrategyManager


class SimulationManager(StrategyManager):
    def __init__(self,
                 strategy,
                 use_server=False,
                 use_websocket=False,
                 port=None,
                 logger: logging.Logger = None,
                 ):
        super().__init__(strategy, use_server, use_websocket, port, logger)

    @Endpoint.post("reset", "Resets the Simulation's state")
    def reset(self):
        self.portfolios = []
        self.signals = []
        self._history = History(pd.DataFrame())
        self.running = False
        self.thread = None

    @Endpoint.post("start_socket", "Starts the simulation's socket server")
    def start_socket(self):
        if self.websocket:
            pass


def main():
    symbols = ["AAPL", "GOOGL", "MSFT"]
    history = np.array(
        [
            [150.0, 2500.0, 300.0],
            [152.0, 2550.0, 305.0],
            [151.5, 2510.0, 302.0],
            [155.0, 2555.0, 308.0],
            [157.0, 2540.0, 306.0],
        ]
    )

    history = pd.DataFrame(history, columns=symbols)

    starting_cash = 1e6
    portfolio = Portfolio()
    portfolio.add_cash(starting_cash)

    class BuyOnCondition(Strategy):
        def __init__(self):
            super().__init__()
            self.signal_history = []

        def execute(self, idx, row: pd.Series, history: History) -> pd.Series:
            row_signal = pd.Series(index=row.index)
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
    simulation.execute()

    print(portfolio.historical_returns())
    print("Profit:", str(portfolio.current_value - starting_cash))


# Example usage:
if __name__ == "__main__":
    main()
