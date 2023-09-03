import json
import threading
import time

import websocket

from dxlib import no_logger, History


class FeedManager:
    def __init__(self, subscription, host="localhost", port=6000, secure=False, retry=False, logger=None):
        self._ws_url = f"ws{'s' if secure else ''}://{host}:{port}"
        self.subscription = subscription
        self.retry = retry

        self._ws = None
        self.thread = None
        self._running = threading.Event()
        self.logger = no_logger(__name__) if logger is None else logger
        self.current_retries = 0
        self.max_retries = 5 if retry else 1
        self.retry_interval = 1

    @property
    def timeout(self):
        return self.current_retries >= self.max_retries

    def _connect(self):
        self._ws = websocket.WebSocketApp(self._ws_url,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close,
                                          on_open=self.on_open)

    def _serve(self):
        if self._running.is_set():
            self.current_retries = 0
            max_retries = (self.max_retries if self.retry else 1)

            while self.current_retries < max_retries:
                time.sleep(self.retry_interval * self.current_retries)
                try:
                    self._connect()
                    self._ws.run_forever()

                    if not self.is_socket_alive():
                        raise ConnectionError("Socket could not connect")
                    return

                except KeyboardInterrupt:
                    return
                except Exception as e:
                    self.logger.warning(f"Connection attempt {self.current_retries + 1}/{max_retries} failed: {e}")
                    self.current_retries += 1

            if self.timeout:
                self._running.clear()
                self.logger.exception("{}, giving up on connection".format("Max retries reached" if max_retries > 1 else "No retry rule"))
                return

    def start(self):
        self.logger.info(f"Connecting to websocket on {self._ws_url}")
        if self.thread is None:
            self._running.set()
            self.thread = threading.Thread(target=self._serve)
            self.thread.start()

    def stop(self):
        if self._ws:
            self._ws.close()
        self._ws = None
        self._running.clear()

        if self.thread:
            self.thread.join()
        self.thread = None

    def restart(self):
        self.stop()
        self.start()

    def send_message(self, message):
        self._ws.send(message)

    def send_snapshot(self, data=None):
        try:
            if data is None:
                data = History(next(self.subscription)).to_dict()
        except StopIteration:
            self.logger.warning("Subscription has ended")
            return None
        message = {"snapshot": data}
        self.send_message(json.dumps(message))
        self.logger.info(f"Sent snapshot: {message}")
        return message

    def on_message(self, ws, message):
        print("Received Message:", message)

    def on_error(self, ws, error):
        print("Error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.warning(f"Websocket closed with status code {close_status_code}: {close_msg}")

    def on_open(self, ws):
        self.current_retries = 0
        self.logger.info("Connected to websocket. Press Ctrl+C to stop...")
        pass

    def is_alive(self):
        return self._running.is_set()

    def is_socket_alive(self):
        return self._ws and self._ws.sock and self._ws.sock.connected
