from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import AsyncGenerator, Generator

import numpy as np
import pandas as pd
from websocket import WebSocket

from .generic_manager import GenericManager, GenericMessageHandler
from ..core import Portfolio, History, Security, Order, Inventory, Signal, SecurityManager, info_logger, no_logger
from ..servers import Endpoint
from ..strategies import Strategy


class StrategyManager(GenericManager):
    def __init__(self,
                 strategy,
                 security_manager=None,
                 server_port=None,
                 websocket_port=None,
                 logger: logging.Logger = None,
                 ):
        super().__init__(server_port, websocket_port, logger)
        self.strategy: Strategy = strategy

        self._portfolio = Portfolio()
        self.security_manager = SecurityManager() if security_manager is None else security_manager
        self._history = History(pd.DataFrame(), self.security_manager)

        self.running = False
        self.thread = None

        self.message_handler = StrategyMessageHandler(self)
        self.logger = no_logger(__name__) if logger is None else logger

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    @Endpoint.get("portfolio", "Gets the inventories managed by the strategy manager")
    def get_portfolio(self):
        return self.portfolio

    @Endpoint.post("portfolios", "Registers a portfolio with the strategy manager")
    def register_portfolio(self, portfolio: Portfolio = None):
        if portfolio is None:
            portfolio = Portfolio()
        if isinstance(portfolio, dict):
            portfolio = Portfolio(**portfolio)

        self.security_manager += {security.ticker: security
                                  for security in portfolio.inventory.keys() if security.ticker != "cash"}

        self.logger.info(f"Registering portfolio {portfolio}")
        self._portfolio += portfolio

    @property
    @Endpoint.get("history", "Gets the currently history for the simulation")
    def history(self):
        return self._history

    @history.setter
    @Endpoint.post("history", "Registers a history with the strategy manager")
    def history(self, value: History | pd.DataFrame | np.ndarray | dict):
        self._history = value

    @property
    def position(self) -> dict[Security, int]:
        return {security: self.portfolio.inventory[security] for security in self.portfolio.inventory.keys()}

    @Endpoint.get("position", "Gets the current aggregated position registered with the strategy manager")
    def get_position(self):
        return self.position

    def orders_from_signals(self, signals: pd.Series):
        # Signals are a series, where each index is a Security, and each value is a TradeSignal
        orders = {}
        for security, signal in signals.items():
            if signal is not None:
                security = security if isinstance(security, Security) else self.security_manager.securities[security]
                orders[security] = Order.from_signal(signal, security)
        return orders

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
        except Exception:
            self.logger.warning("Error executing strategy", exc_info=True)
            return pd.Series(pd.NA, index=self.security_manager.securities)

        if isinstance(self._portfolio, Portfolio):
            try:
                self._portfolio.add(self.orders_from_signals(signals))
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
            self.execute(bars)
        self.running = False

    def _consume(self, subscription: Generator):
        for bars in subscription:
            self._history += bars
            self.execute(bars)
        self.running = False

    def run(self, subscription: History | AsyncGenerator | Generator | pd.DataFrame | np.ndarray, threaded=False):
        if isinstance(subscription, pd.DataFrame):
            subscription = subscription.iterrows()
        elif isinstance(subscription, History):
            subscription = subscription.df.iterrows()
        if threaded:
            self.thread = threading.Thread(target=self._consume, args=(subscription,))
            self.thread.start()
        else:
            if isinstance(subscription, AsyncGenerator):
                asyncio.run(self._async_consume(subscription))
            else:
                self._consume(subscription)

    def stop(self):
        if self.running:
            self.running = False
        if self.thread:
            self.thread.join()
        super().stop()


class StrategyMessageHandler(GenericMessageHandler):
    def __init__(self, manager: StrategyManager):
        super().__init__()
        self.manager = manager
        self.connected_portfolios: dict[WebSocket, Portfolio] = {}
        self.connected_snapshots: list[WebSocket] = []

    def _register_portfolio(self, portfolio: dict = None):
        try:
            portfolio = Portfolio(**portfolio)
            self.manager.register_portfolio(portfolio)
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
            return history
        except TypeError:
            raise json.dumps("Message does not contain a valid snapshot")

    def send_signals(self, signals: pd.Series | dict[Security, Signal]):
        for security in signals.keys():
            for websocket, portfolio in self.connected_portfolios.items():
                if security in portfolio.inventory:
                    self.manager.websocket_server.send_message(
                        signals[security].to_json(),
                        self.manager.websocket_server.message_subjects.signal(security)
                    )

    def process(self, message):
        snapshot = message.get()

        if snapshot is not None:
            self._register_snapshot(snapshot)
            return f"Snapshot registered"

        raise ValueError("Message does not contain any valid information")

    def connect(self, websocket, endpoint):
        if endpoint == "portfolio":
            self.connected_portfolios[websocket] = self._register_portfolio()
            return f"Portfolio connected"
        elif endpoint == "snapshot":
            self.connected_snapshots.append(websocket)
            return "History connected"

    def handle(self, websocket, message):
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            raise TypeError("Message is not valid JSON")

        try:
            response = str(self.process(message))
            self.manager.websocket_server.send_message(websocket, response)
        except (ValueError, TypeError) as e:
            self.manager.logger.warning(e)
            self.manager.websocket_server.send_message(websocket, str(e))

    def disconnect(self, websocket, endpoint):
        pass


if __name__ == "__main__":
    from ..strategies import RsiStrategy

    my_logger = info_logger(__name__)

    my_strategy = RsiStrategy()

    strategy_manager = StrategyManager(my_strategy, server_port=5000, websocket_port=6000, logger=my_logger)
    strategy_manager.start()

    # Or my_portfolio = Portfolio(Inventory({strategy_manager.security_manager.cash: 100000})), logger=my_logger)
    my_portfolio = Portfolio(Inventory({Security("AAPL"): 100}), logger=my_logger)
    strategy_manager.register_portfolio(my_portfolio)

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
