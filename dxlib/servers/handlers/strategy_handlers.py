from __future__ import annotations

import asyncio
import concurrent.futures
from typing import AsyncGenerator, Generator

import websockets

from ...core import Strategy
from ..endpoint import Endpoint, Method
from ..handler import HTTPHandler, WebsocketHandler


class StrategyHTTPHandler(HTTPHandler):
    def __init__(self, strategy, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.strategy: Strategy = strategy

    @Endpoint.http(Method.GET, "/execute", "Gets the currently registered portfolios")
    async def execute(self, observation: any, position, history):
        return self.strategy.execute(observation, position, history)


class StrategyWebsocketHandler(WebsocketHandler):
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

