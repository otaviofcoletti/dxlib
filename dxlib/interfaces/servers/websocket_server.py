import asyncio
import json
import threading

import websockets
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from dxlib.interfaces.servers.handlers import WebsocketHandler
from .endpoint import EndpointScheme
from .server import Server, ServerStatus


class WebsocketServer(Server):
    def __init__(self, handler: WebsocketHandler = None, host="localhost", port=None, logger=None):
        super().__init__(logger)
        self.handler = handler or WebsocketHandler()
        self.host = host
        self.port = port if port else self._get_free_port()

        self._thread = None
        self._server = None
        self._running = threading.Event()
        self.loop = asyncio.get_event_loop()
        self.futures = {}

    @property
    def base_url(self):
        return f"ws://{self.host}:{self.port}"

    def add_interface(self, interface):
        self.handler.add_interface(interface, endpoint_scheme=EndpointScheme.WEBSOCKET)

    def listen(self, func, *args, **kwargs):
        route_name = func.endpoint.route_name
        generator = func(*args, **kwargs)

        self.handler.set_endpoint(func.endpoint, func)

        async def _listen():
            async for message in generator:
                if not self._running.is_set():
                    break
                for websocket in self.handler.websockets.get(route_name, []):
                    await websocket.send(json.dumps(message))

        self.logger.info(f"Listening to {func.__name__}")

        future = asyncio.run_coroutine_threadsafe(_listen(), self.loop)
        self.futures[func.__name__] = future
        return future

    async def websocket_handler(self, websocket, endpoint):
        try:
            if endpoint == "/":
                self.logger.info("Websocket connection established")
            else:
                self.handler.on_connect(websocket, endpoint)
        except Exception as e:
            self.logger.error(f"Error while handling websocket connection: {e}")
            return

        try:
            async for message in websocket:
                try:
                    await self.handler.on_message(websocket, endpoint, message)
                except ValueError as e:
                    self.logger.error(f"Error while handling message: {e}")
                    await websocket.send(str(e))
        except ConnectionClosedOK:
            self.logger.info("Websocket connection closed")
        except ConnectionClosedError as e:
            self.logger.warning(f"Websocket connection closed with error: {e}")

        self.handler.on_disconnect(websocket, endpoint)

    @classmethod
    async def send_message_async(cls, websocket, message):
        if websocket.open:
            await websocket.send(message)

    def send_message(self, websocket, message):
        asyncio.create_task(self.send_message_async(websocket, message))

    async def _serve(self):
        self._server = await websockets.serve(
            self.websocket_handler, self.host, self.port
        )
        try:
            while self._running.is_set():
                await asyncio.sleep(0.1)
        except (asyncio.CancelledError, KeyboardInterrupt) as e:
            self.exception_queue.put(e)

    def start(self):
        self.logger.info(f"Websocket server starting on address {self.base_url}")
        self._running.set()
        self._thread = threading.Thread(
            target=self.loop.run_until_complete, args=(self._serve(),)
        )

        self._thread.start()
        self.logger.info("Websocket started. Press Ctrl+C to stop...")
        return ServerStatus.STARTED

    def stop(self):
        if not self._running.is_set():
            return ServerStatus.STOPPED

        self.logger.info("Stopping Websocket server")
        self._running.clear()

        self.handler.disconnect()

        for future in self.futures.values():
            future.cancel()

        if self._server is not None and self._server.is_serving():
            self._server.close()
            self._server = None
        if self._thread is not None and self._thread.is_alive():
            self._thread.join()
            self._thread = None
        self.loop.stop()

        self.logger.info("Websocket stopped")
        return ServerStatus.STOPPED

    @property
    def alive(self):
        return (self._running.is_set() and
                self._server is not None and
                self._server.is_serving() and
                self.loop.is_running()
                )

    @property
    def stopped(self):
        return not (
            self._running.is_set() or
            (self._server is not None and self._server.is_serving()) or
            self.loop.is_running()
        )
