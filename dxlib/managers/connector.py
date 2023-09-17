import asyncio
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import websockets


class Connector:
    def __init__(self, servers=None, http_port=4000):
        if servers is None:
            servers = {}
        self.http_port = http_port
        self.servers: dict[str, dict] = servers
        self.clients: dict[str, websockets.WebSocketClientProtocol] = {}
        self._running = threading.Event()
        self._httpd_server = None
        self._httpd_thread = None

    def add_server(self, name, uri):
        self.servers[name] = uri

    async def connect_server(self, server_name):
        server = self.servers.get(server_name)
        uri = server.get("uri") if isinstance(server, dict) else server
        data_type = server.get("data_type") if isinstance(server, dict) else None
        if uri:
            try:
                async with websockets.connect(uri) as websocket:
                    while self._running.is_set():
                        message = await websocket.recv()
                        print(f"{data_type} received: ", message)
                        await self.forward_to_clients(json.dumps({data_type: json.loads(message)}))

            except ConnectionRefusedError as e:
                print(f"Connection refused: {e}")

    async def forward_to_clients(self, message):
        for client in self.clients.values():
            if client.open:
                await client.send(message)

    async def ping_clients(self):
        while self._running.is_set():
            for name, client in self.clients.items():
                try:
                    if client.open:
                        await client.ping()
                    else:
                        self.remove_client(name)
                except Exception as e:
                    print(f"Error pinging client {name}: {e}")
            await asyncio.sleep(10)


    def add_client(self, client):
        uri = client.get("uri") if isinstance(client, dict) else client
        data_type = client.get("requesting") if isinstance(client, dict) else None
        name = client.get("name") if isinstance(client, dict) else client

        async def connect_client():
            async with websockets.connect(uri) as websocket:
                self.clients[name] = websocket
                while self._running.is_set():
                    try:
                        pass
                    except Exception as e:
                        print(f"Error receiving from {uri}: {e}")
                        break

        threading.Thread(target=asyncio.run, args=(connect_client(),)).start()

    def remove_client(self, websocket):
        self.clients.pop(websocket)

    def start(self):
        class ClientHandler(BaseHTTPRequestHandler):
            connector = self

            def do_GET(self):
                if self.path == "/":
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(str(self.connector.servers), "utf-8"))
                elif self.path.startswith("/?server="):
                    server = self.path.split("=")[1]
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(self.connector.servers.get(server, {}).get("uri", None), "utf-8"))
                else:
                    self.send_response(404)

            def do_POST(self):
                # Test if posting a client, specifically with data = {'uri': 'wss://...'}
                if self.path == "/":
                    try:
                        content_length = int(self.headers["Content-Length"])
                        post_data = self.rfile.read(content_length)
                        client_uri = json.loads(post_data)["uri"]

                        self.connector.add_client(client_uri)
                        self.send_response(200)
                        self.end_headers()
                    except RuntimeError as e:
                        print(e)
                        self.send_response(400)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()

        def run_httpd():
            server_address = ("localhost", self.http_port)
            self._httpd_server = HTTPServer(server_address, ClientHandler)
            self._httpd_server.serve_forever()

        self._running.set()
        self._httpd_thread = threading.Thread(target=run_httpd)
        self._httpd_thread.start()

        threading.Thread(target=asyncio.run, args=(self.ping_clients(),)).start()

        threads = []
        for server_name in self.servers.keys():
            thread = threading.Thread(target=asyncio.run, args=(self.connect_server(server_name),))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def stop(self):
        self._running.wait()
        self._running.clear()

        for client in self.clients.values():
            asyncio.run_coroutine_threadsafe(client.close(), asyncio.get_event_loop())

        self._httpd_server.shutdown()
        self._httpd_server = None
        self._httpd_thread.join()
        self._httpd_thread = None


if __name__ == "__main__":
    connector = Connector()
    connector.add_server("binance", "wss://stream.binance.com:9443/ws/btcusdt@trade")

    try:
        connector.start()
    except KeyboardInterrupt:
        connector.stop()
