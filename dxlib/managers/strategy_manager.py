from __future__ import annotations

import asyncio
import concurrent.futures
import threading
from typing import AsyncGenerator, Generator

import numpy as np
import pandas as pd
import websockets

from ..core import Portfolio, History
from ..core.portfolio.inventory import Inventory
from ..servers import WebsocketServer
from ..servers.endpoint import Endpoint
from ..strategies import Strategy
from .manager import Manager, MessageHandler


class StrategyManager(Manager):
    def __init__(self,
                 strategy,
                 *args,
                 **kwargs
                 ):
        super().__init__(
            *args,
            **kwargs)

        self.strategy: Strategy = strategy
        self.portfolios: dict[str, Portfolio] = {}
        self.executors: set[Executor] = set()

        for comm in kwargs.get('comms', []):
            if isinstance(comm, WebsocketServer) and comm.handler is None:
                comm.handler = StrategyMessageHandler(self, comm)

    @Endpoint.get("portfolios", "Gets the currently registered portfolios")
    def get_portfolios(self, identifier=None):
        if identifier:
            return self.portfolios[identifier]

        return {identifier: portfolio.to_dict() for identifier, portfolio in self.portfolios.items()}

    @Endpoint.get("portfolios", "Gets the currently registered portfolios")
    def get_values(self, identifier: str, prices: dict[str, float] | None = None):
        if identifier and identifier in self.portfolios:
            return self.portfolios[identifier].value(prices)
        elif identifier:
            raise ValueError(f"Portfolio {identifier} not registered")

        return {identifier: portfolio.value(prices) for identifier, portfolio in self.portfolios.items()}

    @Endpoint.post("portfolios", "Registers a portfolio with the strategy manager")
    def register_portfolio(self, portfolio: Portfolio | dict, identifier: str = None):
        if isinstance(portfolio, dict):
            portfolio = Portfolio(**portfolio)

        if identifier in self.portfolios:
            raise ValueError(f"Portfolio {portfolio} already registered")
        if identifier is None:
            identifier = hash(portfolio)

        self.logger.info(f"Registering portfolio {portfolio}")
        self.portfolios[identifier] = portfolio

    @property
    def position(self) -> Inventory:
        portfolio = Portfolio()
        for identifier in self.portfolios:
            portfolio += self.portfolios[identifier]

        return portfolio.accumulate()

    def run(self,
            obj: History | Generator | AsyncGenerator | pd.DataFrame | np.ndarray | dict,
            threaded=False,
            executor: Executor = None,
            position: Inventory = None) -> History | Generator | AsyncGenerator | concurrent.futures.Future | None:
        if position is None:
            position = self.position

        if executor is None:
            executor = Executor(self.strategy, position)
            self.executors.add(executor)

        return executor.run(obj, threaded)


class Executor:
    def __init__(self, strategy: Strategy, position: Inventory = None):
        self.strategy = strategy
        self._position = position
        self._history = None

        self._running = threading.Event()

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, value: History | pd.DataFrame | np.ndarray | dict):
        self._history = self.format(value)

    def run(self,
            obj: History | Generator | AsyncGenerator | pd.DataFrame | np.ndarray | dict,
            threaded=False) -> History | Generator | AsyncGenerator | concurrent.futures.Future | None:
        obj = self.format(obj) if isinstance(obj, (pd.DataFrame, np.ndarray, dict)) else obj
        if obj is None:
            return

        if not self._history:
            self._history = History()

        self._running.set()
        if threaded:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._consume, obj)
                return future
        else:
            return self._consume(obj)

    def stop(self):
        self._running.clear()

    def _consume(self, obj: History | Generator | AsyncGenerator) -> History | Generator | AsyncGenerator | None:
        if isinstance(obj, History):
            return self._consume_sync(obj)
        elif isinstance(obj, Generator):
            return self._consume_subscription(obj)
        elif isinstance(obj, AsyncGenerator):
            return self._consume_async_subscription(obj)
        else:
            raise TypeError(f"Object {obj} is not a valid type")

    @staticmethod
    def format(obj: History | pd.DataFrame | np.ndarray | dict):
        if isinstance(obj, dict):
            obj = History.from_dict(obj)
        elif isinstance(obj, (pd.DataFrame, np.ndarray)):
            obj = History(obj)

        return obj

    def _consume_sync(self, obj: History) -> History | None:
        signals_history = History()
        dates = obj.get_level('date')

        try:
            for date in sorted(dates):
                if not self._running.is_set():
                    return signals_history
                bars = obj.get(dates=[date])
                self._history += bars

                signals = self.strategy.execute(date, self._position, self._history)

                signals_history += signals
        finally:
            self._running.clear()
            return signals_history

    def _consume_subscription(self, obj: Generator):
        try:
            for bar in obj:
                if not self._running.is_set():
                    break
                bar_df = self._transform_bar(bar)
                self._history += bar_df
                signals = self._process_bar(bar_df)
                yield signals
        finally:
            self._running.clear()

    async def _consume_async_subscription(self, obj: AsyncGenerator):
        try:
            async for bar in obj:
                if not self._running.is_set():
                    break
                bar_df = self._transform_bar(bar)
                self._history += bar_df
                signals = self._process_bar(bar_df)
                yield signals
        finally:
            self._running.clear()

    def _transform_bar(self, bar):
        bar_df = pd.DataFrame.from_dict(bar, orient='index')
        bar_df.index = pd.MultiIndex.from_tuples(
            [(bar_df.index.name, list(self._history.security_manager.get(security).values())[0]) for security in
             bar_df.index])

        return bar_df

    def _process_bar(self, bar_df):
        date = bar_df.index.get_level_values('date').unique().tolist()[0]
        date_idx = self._history.get_level('date').sorted().index(date)

        signals = self.strategy.execute(date_idx, self._position, self._history)
        signals_df = pd.DataFrame(signals, columns=['signal'])

        return signals_df


class StrategyMessageHandler(MessageHandler):
    def __init__(self, manager: StrategyManager, websocket_server: WebsocketServer = None):
        super().__init__()
        self.manager = manager
        self.websocket_server = websocket_server
        self.websocket_queue = asyncio.Queue()

        self.send_lock = asyncio.Lock()

    async def run_async_generator(self, websocket):
        async_generator = self._message_generator()
        asyncio.ensure_future(self._send_to_async_generator(websocket, async_generator))

        response = self.manager.run(async_generator)

        if isinstance(response, AsyncGenerator):
            async with self.send_lock:
                await response.asend(None)

    async def _send_to_async_generator(self, websocket, async_generator):
        try:
            while True:
                message = await self.websocket_queue.get()
                async with self.send_lock:
                    print(message)
                    await async_generator.asend(message)
        except websockets.ConnectionClosed:
            pass

    async def _message_generator(self):
        while True:
            try:
                message = await asyncio.wait_for(self.websocket_queue.get(), timeout=1)
                yield message
            except asyncio.TimeoutError:
                pass

    async def handle(self, websocket, endpoint, message):
        if endpoint == "/bar":
            await self.websocket_queue.put(message)

    def connect(self, websocket, endpoint):
        asyncio.ensure_future(self.run_async_generator(websocket))
