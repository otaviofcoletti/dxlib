from __future__ import annotations

import asyncio

import websockets

from ...core import Strategy
from ..servers.endpoint import Endpoint, Method, get_endpoints
from .internal_interface import InternalInterface


class StrategyHTTPInterface(InternalInterface):
    def __init__(self, strategy, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.strategy: Strategy = strategy

    @Endpoint.http(Method.POST, "/execute", "Executes a single observation and returns the result")
    async def execute(self, observation: any, position, history):
        return self.strategy.execute(observation, position, history)

    @property
    def endpoints(self):
        return get_endpoints(self)


class StrategyWebsocketInterface(InternalInterface):
    def __init__(self, strategy: Strategy):
        super().__init__()
        self.strategy = strategy

        self.websocket_queue = asyncio.Queue()
        self.send_lock = asyncio.Lock()

    @Endpoint.websocket("/execute", "Gets the currently registered portfolios")
    async def execute(self, websocket: websockets.WebSocketServerProtocol):
        while True:
            message = await self.websocket_queue.get()
            async with self.send_lock:
                await websocket.send(message)

    async def handle(self, websocket: websockets.WebSocketServerProtocol, endpoint: str, message: str):
        pass

    def connect(self, websocket: websockets.WebSocketServerProtocol, endpoint: str):
        pass
