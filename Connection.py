import asyncio
import websockets
from typing import Dict, Set

class Connection:
    def __init__(self, status):
        self.clients: List[websockets.WebSocketServerProtocol] = []
        self.status = status
        self.connecttion

    async def connect(self, ip: str, port: int):
        self.connecttion = await websockets.connect(f'ws://{ip}:{port}')
        print(f"Подключено к хосту {ip}:{port}")

        self.clients.append(self.connecttion)

    async def broadcast(self, message: str, sender: websockets.WebSocketServerProtocol = None):
        if not self.clients:
            return
        await asyncio.gather(
            *[
                client.send(message)
                for client in self.clients
                if client != sender
            ],
            return_exceptions=True
        )
    
    async def send_to_client(msg: str, ind: int):
        await self.clients[ind].send(msg)

    async def get_client_amount():
        return len(self.clients)

    async def handle_client(self, websocket: websockets.WebSocketServerProtocol):
        ip_, port_ = websocket.remote_address
        print(f'Подключился клиент {ip_}:{port_}')

        self.clients.append(websocket)

    def start_server(self, host: str = "localhost", port: int = 8765):
        start_server = websockets.serve(self.handle_client, host, port)
        return start_server