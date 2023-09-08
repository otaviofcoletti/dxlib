import threading
import asyncio
import websockets
from http.server import BaseHTTPRequestHandler, HTTPServer


class Connector:
    def __init__(self):
        self.servers: dict[str, str] = {}
        self.clients: dict[str, websockets.WebSocketClientProtocol] = {}
        self.stop_event = threading.Event()
        self.http_server = None

    def add_server(self, name, uri):
        self.servers[name] = uri

    async def connect_server(self, name):
        uri = self.servers.get(name)
        if uri:
            async with websockets.connect(uri) as websocket:
                while not self.stop_event.is_set():
                    try:
                        message = await websocket.recv()
                        await self.forward_to_clients(message)
                    except Exception as e:
                        print(f"Error receiving from {name}: {e}")
                        break

    async def forward_to_clients(self, message):
        for client in self.clients.values():
            await client.send(message)

    def add_client(self, uri):
        # creates a websocket connection that will be used to forward messages to the client
        async def connect_client():
            async with websockets.connect(uri) as websocket:
                self.clients[uri] = websocket
                while not self.stop_event.is_set():
                    try:
                        pass
                    except Exception as e:
                        print(f"Error receiving from {uri}: {e}")
                        break

        asyncio.run(connect_client())

    def remove_client(self, websocket):
        self.clients.pop(websocket)

    def start(self, http_port=4000):
        class ClientHandler(BaseHTTPRequestHandler):
            connector = self

            def do_GET(self):
                # if has path besides '/', return specific server_name string, else return dict of all servers
                if self.path == "/":
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(str(self.connector.servers), "utf-8"))
                    return
                # path is of format '/{server_name}'
                elif self.path.startswith("/?server="):
                    server = self.path.split("=")[1]
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(bytes(server, "utf-8"))
                    return
                # path is not accepted
                return self.send_response(404)

            def do_POST(self):
                # Test if posting a client, specifically with data = {'uri': 'wss://...'}
                if self.path == "/":
                    content_length = int(self.headers["Content-Length"])
                    post_data = self.rfile.read(content_length)
                    self.send_response(200)
                    self.end_headers()
                    self.connector.add_client(post_data.decode("utf-8"))
                    return
                else:
                    self.send_response(404)
                    self.end_headers()
                    return

        def run_http_server():
            server_address = ("localhost", http_port)
            httpd = HTTPServer(server_address, ClientHandler)
            httpd.serve_forever()

        http_thread = threading.Thread(target=run_http_server)
        http_thread.start()

        # Start WebSocket server connections
        threads = []
        for server_name in self.servers.keys():
            thread = threading.Thread(target=asyncio.run, args=(self.connect_server(server_name),))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def stop(self):
        self.stop_event.set()


if __name__ == "__main__":
    connector = Connector()
    connector.add_server("binance", "wss://stream.binance.com:9443/ws/btcusdt@trade")

    try:
        connector.start()
    except KeyboardInterrupt:
        connector.stop()
