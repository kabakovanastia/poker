import asyncio
import websockets
from typing import Dict, Set

class Connection:
    def __init__(self, status):
        self.status = status

    async def connect(self, ip: str, port: int):
        self.connection = await websockets.connect(f'ws://{ip}:{port}')
        print(f"Подключено к хосту {ip}:{port}")

        return self.connection

    async def send(msg: str):
        await self.client.send(msg)

    async def recv(self):
        return await self.connection.recv()

    async def handle_client(self, websocket: websockets.WebSocketServerProtocol):
        ip_, port_ = websocket.remote_address
        print(f'Подключился клиент {ip_}:{port_}')

        self.client = websocket

    def start_server(self, host: str = "localhost", port: int = 8765, game=None):
        start_server = websockets.serve(self.handle_client, host, port)
        return start_server