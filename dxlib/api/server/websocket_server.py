import asyncio
import threading

import websockets
from websockets.exceptions import ConnectionClosedError

from .server import Server, ServerStatus
from ...core import no_logger


class WebSocketServer(Server):
    def __init__(self, manager, port=None, logger=None):
        super().__init__(manager, logger)
        self._websocket_thread = None
        self._websocket_server = None
        self._running = threading.Event()
        self._stop_event = asyncio.Event()

        self.port = port if port else 8765
        self.manager = manager

        self.logger = logger if logger else no_logger(__name__)

    async def websocket_handler(self, websocket, endpoint):
        self.logger.info("New websocket connection")
        self.manager.message_handler.connect(websocket, endpoint)

        try:
            async for message in websocket:
                if self.manager.message_handler:
                    self.manager.message_handler.handle(websocket, message)
        except ConnectionClosedError:
            self.logger.warning("Websocket connection closed")

        self.manager.message_handler.disconnect(websocket, endpoint)

    @classmethod
    async def _send_message(cls, websocket, message):
        if websocket.open:
            await websocket.send(message)

    def send_message(self, websocket, message):
        asyncio.create_task(self._send_message(websocket, message))

    async def _serve(self):
        self._websocket_server = await websockets.serve(self.websocket_handler, "", self.port)
        try:
            while self._running.is_set():
                await asyncio.sleep(0.1)
        except (asyncio.CancelledError, KeyboardInterrupt) as e:
            self.exception_queue.put(e)

    def start(self):
        self.logger.info(f"Starting websocket on port {self.port}")
        self._running.set()
        self._websocket_thread = threading.Thread(target=asyncio.run, args=(self._serve(),))
        self._websocket_thread.start()
        self.logger.info("Websocket started. Press Ctrl+C to stop...")
        return ServerStatus.STARTED

    def stop(self):
        self.logger.info("Stopping websocket")
        if self._websocket_server is None:
            return ServerStatus.STOPPED
        self._running.clear()

        self._websocket_server.close()
        self._websocket_server = None

        self._websocket_thread.join()
        self._websocket_thread = None

        self.logger.info("Websocket stopped")
        return ServerStatus.STOPPED

    def is_alive(self):
        return self._running.is_set()


if __name__ == "__main__":
    websocket_server = WebSocketServer(None)
    websocket_server.start()
    try:
        input("Press any key to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        websocket_server.stop()
