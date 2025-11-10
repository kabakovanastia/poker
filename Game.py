from typing import List
from Connection import Connection
from CardDeck import CardDeck, show_deck
from ShamirCrypt import gen_prime, KEY_SIZE
import asyncio

class Game():
    player_num: int
    me: int
    dealer: int
    card_deck: List[int]
    status: str
    connections: Connection
    client_amount: int
    p: int
    

    def __init__(self, status, client_amount, connections=None, conn=None):
        self.status = status
        self.client_amount = client_amount
        self.connections = connections
        self.conn = conn

    async def start(self):
        if self.status == 'host':
            while self.connections.get_client_amount() < int(self.client_amount):
                print(f"Ожидаю подключений... Сейчас: {self.connections.get_client_amount()}")
                await asyncio.sleep(1)

            self.p = gen_prime(KEY_SIZE)

            print('Отправка простого числа всем игрокам')
            for c in self.connections.clients:
                c.send(f'{self.p}')

            print('Генерация шифровальщика')
            self.crypt = ShamirCrypt(self.p)

            print('Генерация колоды карт и ее перемешивание')
            cd = CardDeck().get_card_shuffle_ind()
            show_deck(cd)

        else:
            print('Ожидание простого числа для шифрования от хоста')
            self.p = int(await self.conn.recv())
            print('Получено простое число')

            print('Генерация шифровальщика')
            self.crypt = ShamirCrypt(self.p)

            


            




