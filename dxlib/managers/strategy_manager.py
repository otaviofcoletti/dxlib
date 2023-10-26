from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import threading
from collections import Counter
from typing import AsyncGenerator, Generator

import numpy as np
import pandas as pd

from .generic_manager import GenericManager, GenericMessageHandler
from ..api import Endpoint
from ..core import Portfolio, History, Signal, TradeType, no_logger
from ..strategies import Strategy


class StrategyManager(GenericManager):
    def __init__(self,
                 strategy,
                 server_port=None,
                 websocket_port=None,
                 logger: logging.Logger = None,
                 ):
        super().__init__(server_port, websocket_port, logger)
        self.strategy: Strategy = strategy

        self.portfolios: dict[str, Portfolio] = {}
        self.histories: list[History] = []

        self._history = History(pd.DataFrame())

        self.running = False
        self.thread = None

        self.message_handler = StrategyMessageHandler(self)
        self.logger = no_logger(__name__) if logger is None else logger

    @Endpoint.get("portfolios", "Gets the currently registered portfolios")
    def get_portfolios(self, identifier=None):
        if identifier:
            return self.portfolios[identifier]

        return {identifier: portfolio.to_dict() for identifier, portfolio in self.portfolios.items()}

    @Endpoint.get("portfolios", "Gets the currently registered portfolios")
    def get_portfolio_values(self, identifier: str):
        values = pd.DataFrame(np.zeros_like(self._history.df),
                              index=self._history.df.index,
                              columns=self._history.df.columns)

        for transaction in self.portfolios[identifier].transaction_history:
            if transaction.security in self._history.securities:
                values[transaction.security][transaction.timestamp] = transaction.price * transaction.quantity

        return values.cumsum()

    @Endpoint.post("portfolios", "Registers a portfolio with the strategy manager")
    def register_portfolio(self, portfolio: Portfolio | dict, identifier: str = None):
        if isinstance(portfolio, dict):
            portfolio = Portfolio(**portfolio)

        if identifier in self.portfolios:
            raise ValueError(f"Portfolio {portfolio} already registered")
        if identifier is None:
            identifier = hashlib.sha256(str(portfolio).encode()).hexdigest()

        self.logger.info(f"Registering portfolio {portfolio}")
        self.portfolios[identifier] = portfolio

    @property
    @Endpoint.get("history", "Gets the currently history for the simulation")
    def history(self):
        return self._history

    @history.setter
    @Endpoint.post("history", "Sets the history for the simulation")
    def history(self, value: History | pd.DataFrame | np.ndarray | dict):
        self._history = value

    @property
    def position(self) -> dict[Security, int]:
        return dict(sum((Counter(
            {security: portfolio.position[security] for security in portfolio.position.keys()}
        ) for portfolio in self.portfolios.values()), Counter()))

    @Endpoint.get("position", "Gets the current position for the simulation")
    def get_position(self):
        return  {security.symbol: quantity for security, quantity in self.position.items()}

    def execute(self, bar=None):
        if bar:
            idx, _ = bar
        elif self.history:
            idx = self.history.df.index[-1]
        else:
            raise ValueError("No history or bar provided")

        try:
            signals = self.strategy.execute(idx,
                                            pd.Series(self.position, dtype=np.float64),
                                            self.history)
        except:
            self.logger.warning("Error executing strategy", exc_info=True)
            return   pd.Series(Signal(TradeType.WAIT), index=self.history.securities.values())

        for security in signals.keys():
            for portfolio in self.portfolios.values():
                if isinstance(portfolio, Portfolio):
                    try:
                        portfolio.trade(security, signals[security], idx)
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
            generated_signals = self.execute(bars)
        self.running = False
        return generated_signals

    def _consume(self, subscription: Generator):
        for bars in subscription:
            self._history += bars
            generated_signals = self.execute(bars)
        self.running = False
        return generated_signals

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


class StrategyMessageHandler(GenericMessageHandler):
    def __init__(self, manager: StrategyManager):
        super().__init__()
        self.manager = manager
        self.registered_portfolios: dict = {}
        self.registered_histories: dict = {}

    def _register_portfolio(self, portfolio: dict = None):
        try:
            portfolio = Portfolio(**portfolio)
            self.manager.register(portfolio)
        except TypeError:
            raise json.dumps("Message does not contain a valid portfolio")

    def _register_history(self, history: dict | History = None):
        try:
            history = History(**history if history else pd.DataFrame()) if (
                        isinstance(history, dict) or history is None) else history
            self.manager.history = history
        except TypeError:
            raise json.dumps("Message does not contain a valid history")

    def _register_snapshot(self, snapshot: dict) -> History:
        try:
            history = History.from_dict(snapshot)
            if self.manager.history is None or self.manager.history.df.empty:
                self._register_history(history)
            self.manager.run(history)
        except TypeError:
            raise json.dumps("Message does not contain a valid snapshot")

    def send_signals(self, signals: pd.Series | dict[Security, Signal]):
        for security in signals.keys():
            for portfolio in self.registered_portfolios:
                if security in portfolio.position.keys():
                    self.manager.websocket_server.send_message(
                        signals[security].to_json(),
                        self.manager.websocket_server.message_subjects.signal(security)
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
            response = str(self.process(websocket, message))
            self.manager.websocket_server.send_message(websocket, response)
        except (ValueError, TypeError) as e:
            self.manager.logger.warning(e)
            self.manager.websocket_server.send_message(websocket, str(e))

    def disconnect(self, websocket, endpoint):
        pass


if __name__ == "__main__":
    from .. import info_logger, Security
    from ..strategies import RsiStrategy

    my_logger = info_logger(__name__)

    my_strategy = RsiStrategy()
    my_portfolio = Portfolio().add_cash(1e4)

    strategy_manager = StrategyManager(my_strategy, server_port=5000, websocket_port=6000, logger=my_logger)
    strategy_manager.start()
    strategy_manager.register(my_portfolio)

    try:
        while True:
            with strategy_manager.websocket_server.exceptions as exceptions:
                if exceptions:
                    raise exceptions[0]
    except ConnectionError:
        my_logger.warning("Exception occurred", exc_info=True)
    except KeyboardInterrupt:
        my_logger.info("User interrupted program")
    finally:
        strategy_manager.stop()
