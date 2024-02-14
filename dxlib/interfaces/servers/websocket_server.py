import asyncio
import threading

import websockets
from websockets.exceptions import ConnectionClosedError

from .server import Server, ServerStatus
from dxlib.interfaces.servers.handlers import WebsocketHandler


class WebsocketServer(Server):
    def __init__(self, handler: WebsocketHandler, port=None, logger=None):
        super().__init__(logger)
        self.handler = handler
        self.port = port if port else 8765

        self._thread = None
        self._server = None
        self._running = threading.Event()
        self._stop_event = asyncio.Event()

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
    async def send_message_async(cls, websocket, message):
        if websocket.open:
            await websocket.send(message)

    def send_message(self, websocket, message):
        asyncio.create_task(self.send_message_async(websocket, message))

    async def _serve(self):
        self._server = await websockets.serve(
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
        self._thread = threading.Thread(
            target=asyncio.run, args=(self._serve(),)
        )
        self._thread.start()
        self.logger.info("Websocket started. Press Ctrl+C to stop...")
        return ServerStatus.STARTED

    def stop(self):
        if not self._running.is_set():
            return ServerStatus.STOPPED

        self.logger.info("Stopping Websocket server")
        self._running.clear()

        if self._server is not None and self._server.is_serving():
            self._server.close()
            self._server = None

        if self._thread is not None and self._thread.is_alive():
            self._thread.join()
            self._thread = None

        self.logger.info("Websocket stopped")
        return ServerStatus.STOPPED

    @property
    def alive(self):
        return self._running.is_set() and self._server is not None and self._server.is_serving()
