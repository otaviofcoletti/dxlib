import asyncio
import json
import logging
import threading

from typing import AsyncGenerator, Generator
from collections import Counter
import pandas as pd

from ..api import Endpoint
from ..core import Portfolio, History
from ..strategies import Strategy
from .generic_manager import GenericManager


class StrategyManager(GenericManager):
    def __init__(self,
                 strategy,
                 use_server=False,
                 use_websocket=False,
                 port=None,
                 logger: logging.Logger = None,
                 ):
        super().__init__(use_server, use_websocket, port, logger)
        self.strategy: Strategy = strategy

        self.portfolios: list[Portfolio] = []
        self.signals = []
        self._history = History(pd.DataFrame())

        self.running = False
        self.thread = None

        self.message_handler = MessageHandler(self)

    def register(self, portfolio):
        self.logger.info(f"Registering portfolio {portfolio}")
        self.portfolios.append(portfolio)

    @property
    @Endpoint.get("history", "Gets the currently history for the simulation")
    def history(self):
        return self._history

    def execute(self):
        position = dict(sum(*[Counter(portfolio.position) for portfolio in self.portfolios]))
        signals = self.strategy.execute(self.history.df.index[-1], pd.Series(position), self.history)

        for security in signals:
            self.websocket.send_messages(f"Trade {security} {signals[security]}")

            for portfolio in self.portfolios:
                portfolio.trade(security, signals[security])

        return signals

    async def _async_consume(self, subscription: AsyncGenerator | Generator):
        async for bars in subscription:
            if not self.running:
                break
            self._history += bars
            generated_signals = self.execute()
            self.signals.append(generated_signals)
        self.running = False
        return self.signals

    def _consume(self, subscription: Generator):
        for bars in subscription:
            self._history += bars
            generated_signals = self.execute()
            self.signals.append(generated_signals)
        self.running = False
        return self.signals

    def stop(self):
        if self.running:
            self.running = False
        if self.thread:
            self.thread.join()
        self.stop_servers()

    def run(self, subscription: AsyncGenerator | Generator, threaded=False):
        if threaded:
            if isinstance(subscription, Generator):
                self.thread = threading.Thread(target=self._consume, args=(subscription,))
            else:
                self.thread = threading.Thread(target=asyncio.run, args=(self._async_consume(subscription),))
            self.thread.start()
            self.running = True
        else:
            if isinstance(subscription, Generator):
                self._consume(subscription)
            else:
                asyncio.run(self._async_consume(subscription))
        return self.signals

    def start_socket(self):
        self.websocket.on_message = self.message_handler.handle
        if self.websocket is not None:
            self.websocket.start()


class MessageHandler:
    def __init__(self, manager: StrategyManager):
        self.manager = manager

    @classmethod
    def format(cls, message):
        message = json.loads(message)

        portfolio = message.get("portfolio", None)

        if portfolio is not None:
            try:
                portfolio = Portfolio(**portfolio)
                return portfolio
            except TypeError:
                raise TypeError("Message does not contain a valid portfolio")
        else:
            raise ValueError("Message does not contain a portfolio")

    def handle(self, message):
        try:
            portfolio = self.format(message)
            self.manager.register(portfolio)
            self.manager.websocket.send_message(list(self.manager.websocket.message_subjects.keys())[0],
                                                "Registered portfolio {portfolio}")
        except (ValueError, TypeError) as e:
            self.manager.logger.warning(e)


if __name__ == "__main__":
    from .. import info_logger

    class MyStrategy(Strategy):
        def execute(self, idx, history, position):
            return {}

    strategy = MyStrategy()
    logger = info_logger(__name__)
    strategy_manager = StrategyManager(strategy, use_websocket=True, logger=logger)
    strategy_manager.start_socket()
    try:
        while strategy_manager.websocket.is_alive():
            with strategy_manager.websocket.exceptions as exceptions:
                if exceptions:
                    logger.exception(exceptions)
                    raise exceptions
            input("Press enter to continue")
            strategy_manager.run(*list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        strategy_manager.stop()
