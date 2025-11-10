from typing import List
from Connection import Connection
from CardDeck import CardDeck
from ShamirCrypt import gen_prime, KEY_SIZE

class Game():
    player_num: int
    me: int
    dealer: int
    card_deck: List[int]
    status: str
    connections: Connection
    client_amount: int
    p: int
    

    def __init__(status, client_amount, connections):
        self.status = status
        self.client_amount = client_amount
        self.connections = connections

    async def start(self):
        if self.status == 'host':
            while self.connections.get_client_amount() < self.client_amount:
                print(f"Ожидаю подключений... Сейчас: {self.connections.get_client_amount()}")
                await asyncio.sleep(1)

            self.p = gen_prime(KEY_SIZE)
            

            cd = CardDeck().get_card_shuffle_ind()

            
            
        else:
            pass


            




