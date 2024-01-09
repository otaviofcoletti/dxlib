import asyncio
import threading

import websockets
from websockets.exceptions import ConnectionClosedError

from .server import Server, ServerStatus
from .handler import WebsocketHandler


class WebsocketServer(Server):
    def __init__(self, handler: WebsocketHandler, port=None, logger=None):
        super().__init__(handler, logger)
        self._websocket_thread = None
        self._websocket_server = None
        self._running = threading.Event()
        self._stop_event = asyncio.Event()

        self.port = port if port else 8765

    async def websocket_handler(self, websocket, endpoint):
        self.logger.info("New websocket connection")
        self.handler.connect(websocket, endpoint)

        try:
            async for message in websocket:
                if self.handler:
                    await self.handler.handle(websocket, endpoint, message)
        except ConnectionClosedError:
            self.logger.warning("Websocket connection closed")

        self.handler.disconnect(websocket, endpoint)

    @classmethod
    async def _send_message(cls, websocket, message):
        if websocket.open:
            await websocket.send(message)

    def send_message(self, websocket, message):
        asyncio.create_task(self._send_message(websocket, message))

    async def _serve(self):
        self._websocket_server = await websockets.serve(
            self.websocket_handler, "", self.port
        )
        try:
            while self._running.is_set():
                await asyncio.sleep(0.1)
        except (asyncio.CancelledError, KeyboardInterrupt) as e:
            self.exception_queue.put(e)

    def start(self):
        self.logger.info(f"Starting websocket on port {self.port}")
        self._running.set()
        self._websocket_thread = threading.Thread(
            target=asyncio.run, args=(self._serve(),)
        )
        self._websocket_thread.start()
        self.logger.info("Websocket started. Press Ctrl+C to stop...")
        return ServerStatus.STARTED

    def stop(self):
        self.logger.info("Stopping websocket")
        self._running.clear()

        if self._websocket_server:
            self._websocket_server.close()
            self._websocket_server = None

        if self._websocket_thread:
            self._websocket_thread.join()
            self._websocket_thread = None

        self.logger.info("Websocket stopped")
        return ServerStatus.STOPPED

    def alive(self):
        return self._running.is_set()
