import sys
import asyncio
import websockets
import random

from ShamirCrypt import ShamirCrypt, gen_prime
from CardDeck import CardDeck, show_deck

async def start_game_host(websocket):
    print('2-й игрок подключён')
    print('Генерация простого числа для шифрования')
    p = gen_prime(128)
    cr = ShamirCrypt(p)

    print('Передача простого числа 2-му игроку')
    await websocket.send(f'{p}')

    print('Генерация колоды карт')
    cd = CardDeck()
    cards = cd.get_card_shuffle()

    print('Шифрование колоды')
    cards = cr.encrypt(cards)

    print('Отправка колоды 2-му игроку')
    await websocket.send(' '.join(map(str, cards)))

    print('Получение зашифрованной и перемешанной колоды от 2-го игрока')
    cards = list(map(int, (await websocket.recv()).split(' ')))

    print('Беру 2 карты из колоды и отправляю на расшифровку 2-му игроку')
    await websocket.send(' '.join(map(str, cards[:2])))

    print('Получаю карты обратно и снимаю свой уровень шифрования')
    my_cards = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    show_deck(my_cards)

    print('Получаю 2 карты игрока для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
    c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    await websocket.send(' '.join(map(str, c)))



    print('Беру 3 карты из колоды и отправляю их на расшифровку 2-му игроку')
    await websocket.send(' '.join(map(str, cards[4:7])))

    print('Получаю карты обратно и снимаю свой уровень шифрования')
    table = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    show_deck(table)

    print('Отправляю расшифрованные карты со стола 2-му игроку')
    await websocket.send(' '.join(map(str, table)))



    print('Беру 1 карту из колоды и отправляю ее на расшифровку 2-му игроку')
    await websocket.send(' '.join(map(str, cards[7:8])))

    print('Получаю карты обратно и снимаю свой уровень шифрования')
    table1 = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    show_deck(table1)
    #-------ПОДМЕНА КАРТЫ--------------
    table1[0] = 58473653
    show_deck(table1)
    #-------ПОДМЕНА КАРТЫ--------------
    
    print('Отправляю расшифрованную карту со стола 2-му игроку')
    await websocket.send(' '.join(map(str, table1)))
    

    print('Беру 1 карту из колоды и отправляю ее на расшифровку 2-му игроку')
    await websocket.send(' '.join(map(str, cards[8:9])))

    print('Получаю карты обратно и снимаю свой уровень шифрования')
    table2 = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    show_deck(table2)

    print('Отправляю расшифрованную карту со стола 2-му игроку')
    await websocket.send(' '.join(map(str, table2)))

    print('Отправляю свои карты 2-му игроку (КОНЕЦ ИГРЫ)')
    await websocket.send(' '.join(map(str, my_cards)))

    print('Получаю карты 2-го игрока')
    op_cards = list(map(int, (await websocket.recv()).split(' ')))

    print('\nВаша рука:')
    show_deck(my_cards)
    show_deck([*table, *table1, *table2])

    print('\nРука 2-го игрока:')
    show_deck(op_cards)
    show_deck([*table, *table1, *table2])



    print('\nПроверка корректности игры:')
    print('Отправляю свои ключи шифрования 2-му игроку')
    await websocket.send(' '.join(map(str, cr.key)))

    print('Получаю ключ шифрования от 2-го игрока')
    key = tuple(map(int, (await websocket.recv()).split(' ')))

    cr2 = ShamirCrypt(p)
    cr2.key = key

    print('Расшифровка колоды карт')
    c = cr2.decrypt(cr.decrypt(cards))
    show_deck(c)

    print(f'\nВсе карты в колоде уникальны: {len(c) == len(set(c))}')
    print(f'Первые 9 карт из колоды совпадают с картами игроков и картами на столе: {[*my_cards, *op_cards, *table, *table1, *table2] == c[:9]}')
    show_deck([*my_cards, *op_cards, *table, *table1, *table2])
    show_deck(c[:9])

    is_game_correct = all([len(c) == len(set(c)), [*my_cards, *op_cards, *table, *table1, *table2] == c[:9]])
    print(f'\nИгра корректная: {is_game_correct}')



async def start_game_client(websocket):
    print('Получение простого числа')
    p = await websocket.recv()
    cr = ShamirCrypt(int(p))

    print('Получение зашифрованной колоды карт')
    cards = list(map(int, (await websocket.recv()).split(' ')))

    print('Шифрование и перемешивание колоды')
    random.shuffle(cards)
    cards = cr.encrypt(cards)

    print('Отправка зашифрованной и перемешанной колоды 1-му игроку')
    await websocket.send(' '.join(map(str, cards)))

    print('Получаю 2 карты игрока для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
    c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    await websocket.send(' '.join(map(str, c)))

    print('Беру следующие 2 карты из колоды и отправляю на расшифровку 1-му игроку')
    await websocket.send(' '.join(map(str, cards[2:4])))

    print('Получаю карты обратно и снимаю свой уровень шифрования')
    my_cards = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    show_deck(my_cards)
    #-------ПОДМЕНА КАРТЫ--------------
    my_cards[0] = 58473653
    show_deck(my_cards)
    #-------ПОДМЕНА КАРТЫ--------------
    



    print('Получаю 3 карты из колоды для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
    c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    await websocket.send(' '.join(map(str, c)))

    print('Получаю карты со стола')
    table = list(map(int, (await websocket.recv()).split(' ')))
    show_deck(table)



    print('Получаю 1 карту из колоды для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
    c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    await websocket.send(' '.join(map(str, c)))

    print('Получаю карту со стола')
    table1 = list(map(int, (await websocket.recv()).split(' ')))
    show_deck(table1)



    print('Получаю 1 карту из колоды для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
    c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    await websocket.send(' '.join(map(str, c)))

    print('Получаю карту со стола')
    table2 = list(map(int, (await websocket.recv()).split(' ')))
    show_deck(table2)

    print('Отправляю свои карты 1-му игроку (КОНЕЦ ИГРЫ)')
    await websocket.send(' '.join(map(str, my_cards)))

    print('Получаю карты 1-го игрока')
    op_cards = list(map(int, (await websocket.recv()).split(' ')))

    print('\nВаша рука:')
    show_deck(my_cards)
    show_deck([*table, *table1, *table2])

    print('\nРука 2-го игрока:')
    show_deck(op_cards)
    show_deck([*table, *table1, *table2])



    print('\nПроверка корректности игры:')
    print('Отправляю свои ключи шифрования 1-му игроку')
    await websocket.send(' '.join(map(str, cr.key)))

    print('Получаю ключ шифрования от 1-го игрока')
    key = tuple(map(int, (await websocket.recv()).split(' ')))

    cr2 = ShamirCrypt(int(p))
    cr2.key = key

    print('Расшифровка колоды карт')
    c = cr2.decrypt(cr.decrypt(cards))
    show_deck(c)

    print(f'\nВсе карты в колоде уникальны: {len(c) == len(set(c))}')
    print(f'Первые 9 карт из колоды совпадают с картами игроков и картами на столе: {[*op_cards, *my_cards, *table, *table1, *table2] == c[:9]}')
    show_deck([*op_cards, *my_cards, *table, *table1, *table2])
    show_deck(c[:9])

    is_game_correct = all([len(c) == len(set(c)), [*op_cards, *my_cards, *table, *table1, *table2] == c[:9]])
    print(f'\nИгра корректная: {is_game_correct}')



async def main():
    ip, port, status = sys.argv[1:4]

    if status == 'host':
        print('Ожидание игрока...')
        server = await websockets.serve(start_game_host, ip, port)

        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")
        finally:
            server.close()
            await server.wait_closed()

    else:
        server = await websockets.connect(f'ws://{ip}:{port}')
        await start_game_client(server)
        

if __name__ == "__main__":
    asyncio.run(main())
