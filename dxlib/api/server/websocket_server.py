import asyncio
import threading

import websockets
from websockets.exceptions import ConnectionClosedError

from .server import Server
from ... import no_logger


class WebSocketServer(Server):
    def __init__(self, manager, port=None, logger=None):
        super().__init__(manager, logger)
        self.message_subjects = {}
        self._websocket_thread = None
        self._websocket_server = None
        self._started = threading.Event()
        self._stop_event = asyncio.Event()

        self.port = port if port else 8765
        self.manager = manager

        self.logger = logger if logger else no_logger(__name__)

        self.on_message = None

    async def websocket_handler(self, websocket, _):
        message_subject = []
        self.message_subjects[websocket] = message_subject
        self.logger.info("New websocket connection")
        try:
            async for message in websocket:
                if self.on_message:
                    self.on_message(message)
        except ConnectionClosedError:
            self.logger.warning("Websocket connection closed")

        del self.message_subjects[websocket]

    async def _send_message(self, websocket, message):
        await websocket.send(message)

    def send_messages(self, message):
        loop = asyncio.get_event_loop()
        tasks = [self.send_message(websocket, message) for websocket in self.message_subjects.keys()]
        loop.run_until_complete(asyncio.gather(*tasks))

    def send_message(self, websocket, message):
        asyncio.run_coroutine_threadsafe(self._send_message(websocket, message), loop=asyncio.get_event_loop()).result()

    async def _serve(self):
        self._websocket_server = await websockets.serve(self.websocket_handler, "localhost", self.port)

        try:
            while self._started.is_set():
                await asyncio.sleep(0.1)
        except (asyncio.CancelledError, KeyboardInterrupt) as e:
            self.exception_queue.put(e)

    def start(self):
        self.logger.info(f"Starting websocket server on port {self.port}")
        self._websocket_thread = threading.Thread(target=asyncio.run, args=(self._serve(),))
        self._websocket_thread.start()
        self._started.set()

    def stop(self):
        if self._websocket_server:
            self._started.clear()
            self._websocket_thread.join()

    def is_alive(self):
        return self._started.is_set()


if __name__ == "__main__":
    websocket_server = WebSocketServer(None)
    websocket_server.start()
    try:
        input("Press any key to exit...")
    except KeyboardInterrupt:
        pass
    finally:
        websocket_server.stop()
