from __future__ import annotations

import asyncio
import concurrent.futures
from typing import AsyncGenerator, Generator

import numpy as np
import pandas as pd
import websockets

from ..core import Portfolio, History, Strategy, LoggerMixin, Inventory
from ..servers import WebsocketServer
from ..servers.endpoint import Endpoint
from .manager import Manager


class StrategyEndpointHandler(Manager):
    def __init__(self, strategy, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.strategy: Strategy = strategy
        self.portfolios: dict[str, Portfolio] = {}
        self.executors: set[Executor] = set()

        for comm in kwargs.get("comms", []):
            if isinstance(comm, WebsocketServer) and comm.handler is None:
                comm.handler = StrategyMessageHandler(self, comm)

    @Endpoint.get("portfolios", "Gets the currently registered portfolios")
    def get_portfolios(self, identifier=None):
        if identifier:
            return self.portfolios[identifier]

        return {
            identifier: portfolio.to_dict()
            for identifier, portfolio in self.portfolios.items()
        }

    @Endpoint.get("portfolios", "Gets the currently registered portfolios")
    def get_values(self, identifier: str, prices: dict[str, float] | None = None):
        if identifier and identifier in self.portfolios:
            return self.portfolios[identifier].value(prices)
        elif identifier:
            raise ValueError(f"Portfolio {identifier} not registered")

        return {
            identifier: portfolio.value(prices)
            for identifier, portfolio in self.portfolios.items()
        }

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

    def run(
        self,
        obj: History | Generator | AsyncGenerator | pd.DataFrame | np.ndarray | dict,
        threaded=False,
        executor: Executor = None,
        position: Inventory = None,
    ) -> History | Generator | AsyncGenerator | concurrent.futures.Future | None:
        if position is None:
            position = self.position

        if executor is None:
            executor = Executor(self.strategy, position)
            self.executors.add(executor)

        return executor.run(obj, threaded)


class StrategyMessageHandler:
    def __init__(
        self, manager: StrategyManager, websocket_server: WebsocketServer = None
    ):
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
