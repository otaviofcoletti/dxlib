from __future__ import annotations

import asyncio
import json
import logging
import threading
from collections import Counter
from typing import AsyncGenerator, Generator

import numpy as np
import pandas as pd

from .generic_manager import GenericManager
from ..api import Endpoint
from ..core import Portfolio, History, Signal
from ..strategies import Strategy


class StrategyManager(GenericManager):
    def __init__(self,
                 strategy,
                 use_server=False,
                 use_websocket=False,
                 server_port=None,
                 websocket_port=None,
                 logger: logging.Logger = None,
                 ):
        super().__init__(use_server, use_websocket, server_port, websocket_port, logger)
        self.strategy: Strategy = strategy

        self.portfolios: list[Portfolio] = []
        self.histories: list[History] = []

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

    @history.setter
    @Endpoint.post("history", "Sets the history for the simulation")
    def history(self, value):
        self._history = value

    def execute(self):
        position = dict(sum((Counter(portfolio.position) for portfolio in self.portfolios), Counter()))
        signals = self.strategy.execute(self.history.df.index[-1], pd.Series(position), self.history)

        for security in signals.keys():
            for portfolio in self.portfolios:
                if isinstance(portfolio, Portfolio):
                    try:
                        portfolio.trade(security, signals[security])
                    except ValueError as e:
                        self.logger.warning(e)
                else:
                    self.message_handler.send_signals(signals)

        return signals

    async def _async_consume(self, subscription: AsyncGenerator):
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
        super().stop()

    def run(self, subscription: History | AsyncGenerator | Generator | pd.DataFrame | np.ndarray, threaded=False):
        if isinstance(subscription, pd.DataFrame):
            subscription = subscription.iterrows()
        elif isinstance(subscription, History):
            subscription = subscription.df.iterrows()
        if threaded:
            if isinstance(subscription, AsyncGenerator):
                self.thread = threading.Thread(target=asyncio.run, args=(self._async_consume(subscription),))
            else:
                self.thread = threading.Thread(target=self._consume, args=(subscription,))
            self.thread.start()
            self.running = True
        else:
            if isinstance(subscription, AsyncGenerator):
                asyncio.run(self._async_consume(subscription))
            else:
                self._consume(subscription)
        return self.signals


class MessageHandler:
    def __init__(self, manager: StrategyManager):
        self.manager = manager
        self.registered_portfolios: dict = {}
        self.registered_histories: dict = {}

    def _register_portfolio(self, portfolio=None):
        try:
            portfolio = Portfolio(**portfolio)
            self.manager.register(portfolio)
            return portfolio
        except TypeError:
            raise TypeError("Message does not contain a valid portfolio")

    def _register_history(self, history=None):
        try:
            history = History(**history if history else pd.DataFrame())
            self.manager.history = history
            return history
        except TypeError:
            raise TypeError("Message does not contain a valid portfolio")

    def _register_snapshot(self, snapshot) -> History:
        try:
            if self.manager.history is None or self.manager.history.df.empty:
                return self._register_history(snapshot)
            self.manager.run(History(**snapshot))
            return self.manager.history
        except TypeError:
            raise TypeError("Message does not contain a valid portfolio")

    def send_signals(self, signals: pd.Series | dict[Security, Signal]):
        for security in signals.keys():
            for portfolio in self.registered_portfolios:
                if security in portfolio.position.keys():
                    self.manager.websocket.send_message(
                        signals[security].to_json(),
                        self.manager.websocket.message_subjects.signal(security)
                    )

    def process(self, websocket, message):
        portfolio = message.get("portfolio", None)
        history = message.get("history", None)
        snapshot = message.get("snapshot", None)

        if portfolio is not None:
            portfolio = self._register_portfolio(portfolio)
            self.registered_portfolios[websocket] = portfolio
            return f"Portfolio registered"
        if history is not None:
            history = self._register_history(history)
            self.registered_histories[websocket] = history
            return "History registered"
        if snapshot is not None:
            updated_history = self._register_snapshot(snapshot)
            self.registered_histories[websocket] = updated_history
            return f"Snapshot registered: {self.manager.history.to_json()}"

        raise ValueError("Message does not contain any valid information")

    def connect(self, websocket, endpoint):
        if endpoint == "portfolio":
            self.registered_portfolios[websocket] = self._register_portfolio()
            return f"Portfolio connected"
        elif endpoint == "history":
            self.registered_histories[websocket] = self._register_history()
            return "History connected"

    def handle(self, websocket, message):
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            raise TypeError("Message is not valid JSON")

        try:
            response = self.process(websocket, message)
            self.manager.websocket.send_message(websocket, response)
        except (ValueError, TypeError) as e:
            self.manager.logger.warning(e)
            self.manager.websocket.send_message(websocket, e)

    def disconnect(self, websocket, endpoint):
        pass


if __name__ == "__main__":
    from .. import info_logger, Security, api
    from ..strategies import RsiStrategy

    historical_bars = api.YFinanceAPI().get_historical_bars(["AAPL", "MSFT"])
    my_logger = info_logger(__name__)

    my_strategy = RsiStrategy()
    my_portfolio = Portfolio().add_cash(1e4)

    strategy_manager = StrategyManager(my_strategy, use_server=True, use_websocket=True, logger=my_logger)
    strategy_manager.start()
    strategy_manager.register(my_portfolio)

    try:
        # strategy_manager.run(historical_bars)
        while True:
            with strategy_manager.server.exceptions as exceptions:
                if exceptions:
                    raise exceptions[0]
    except ConnectionError:
        my_logger.warning("Exception occurred", exc_info=True)
    except KeyboardInterrupt:
        my_logger.info("User interrupted program")
    finally:
        strategy_manager.stop()
