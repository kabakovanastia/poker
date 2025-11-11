import sys
import asyncio
import websockets
import random
from ShamirCrypt import ShamirCrypt, gen_prime
from CardDeck import CardDeck, show_deck, get_hand_rank
from SchnorrBlind import SchnorrSigner
from Game import PokerGame

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

    # --- Ставки ---
    game = PokerGame()
    print("\n--- НАЧАЛО ИГРЫ (ПОКЕР) ---")
    print("Ваши карты:", end=' ')
    show_deck(my_cards)

    # Предварительные ставки (блайнды)
    small_blind = 10
    big_blind = 20
    game.place_bet(0, small_blind)
    game.place_bet(1, big_blind)
    print(f"Блайнды: {small_blind} и {big_blind}. Общий банк: {game.pot}")

    # --- Префлоп ---
    print("\n--- ПРЕФЛОП ---")
    action = await websocket.recv()
    if action == 'fold':
        game.fold(1)
        print("Оппонент сбросил. Вы выиграли!")
        await websocket.send('win_fold')
        return
    elif action == 'check':
        game.check(1)
    else: # raise
        amount = int(action.split()[1])
        game.place_bet(1, amount)
        print(f"Оппонент повысил ставку на {amount}")

    # Ваш ход
    print("Ваш ход (fold/check/raise N): ", end='', flush=True)
    move = input().strip().split()
    if move[0] == 'fold':
        game.fold(0)
        await websocket.send('fold')
        print("Вы сбросили. Оппонент выиграл!")
        return
    elif move[0] == 'check':
        game.check(0)
        await websocket.send('check')
    elif move[0] == 'raise':
        amount = int(move[1])
        game.place_bet(0, amount)
        await websocket.send(f'raise {amount}')
        print(f"Вы повысили ставку на {amount}")

    # --- Флоп ---
    if not game.game_over:
        print("\n--- ФЛОП ---")
        print('Беру 3 карты из колоды и отправляю на расшифровку 2-му игроку')
        await websocket.send(' '.join(map(str, cards[4:7])))

        print('Получаю карты обратно и снимаю свой уровень шифрования')
        table = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
        show_deck(table)

        print('Отправляю расшифрованные карты со стола 2-му игроку')
        await websocket.send(' '.join(map(str, table)))

        # Ходы после флопа
        action = await websocket.recv()
        if action == 'fold':
            game.fold(1)
        else:
            amount = int(action.split()[1]) if action.startswith('raise') else 0
            game.place_bet(1, amount)

        print("Ваш ход (fold/check/raise N): ", end='', flush=True)
        move = input().strip().split()
        if move[0] == 'fold':
            game.fold(0)
            await websocket.send('fold')
        else:
            amount = int(move[1]) if move[0] == 'raise' else 0
            game.place_bet(0, amount)
            await websocket.send(f'{move[0]} {amount}' if move[0] == 'raise' else move[0])

    # --- Тёрн ---
    if not game.game_over:
        print("\n--- ТЁРН ---")
        print('Беру 1 карту из колоды и отправляю ее на расшифровку 2-му игроку')
        await websocket.send(' '.join(map(str, cards[7:8])))

        print('Получаю карту обратно и снимаю свой уровень шифрования')
        table1 = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
        show_deck(table1)

        print('Отправляю расшифрованную карту со стола 2-му игроку')
        await websocket.send(' '.join(map(str, table1)))

        # Ходы после тёрна
        action = await websocket.recv()
        if action == 'fold':
            game.fold(1)
        else:
            amount = int(action.split()[1]) if action.startswith('raise') else 0
            game.place_bet(1, amount)

        print("Ваш ход (fold/check/raise N): ", end='', flush=True)
        move = input().strip().split()
        if move[0] == 'fold':
            game.fold(0)
            await websocket.send('fold')
        else:
            amount = int(move[1]) if move[0] == 'raise' else 0
            game.place_bet(0, amount)
            await websocket.send(f'{move[0]} {amount}' if move[0] == 'raise' else move[0])

    # --- Ривер ---
    if not game.game_over:
        print("\n--- РИВЕР ---")
        print('Беру 1 карту из колоды и отправляю ее на расшифровку 2-му игроку')
        await websocket.send(' '.join(map(str, cards[8:9])))

        print('Получаю карту обратно и снимаю свой уровень шифрования')
        table2 = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
        show_deck(table2)

        print('Отправляю расшифрованную карту со стола 2-му игроку')
        await websocket.send(' '.join(map(str, table2)))

        # Ходы после ривера
        action = await websocket.recv()
        if action == 'fold':
            game.fold(1)
        else:
            amount = int(action.split()[1]) if action.startswith('raise') else 0
            game.place_bet(1, amount)

        print("Ваш ход (fold/check/raise N): ", end='', flush=True)
        move = input().strip().split()
        if move[0] == 'fold':
            game.fold(0)
            await websocket.send('fold')
        else:
            amount = int(move[1]) if move[0] == 'raise' else 0
            game.place_bet(0, amount)
            await websocket.send(f'{move[0]} {amount}' if move[0] == 'raise' else move[0])

    # --- Вскрытие ---
    print("\n--- ВСКРЫТИЕ КАРТ ---")
    print('Отправляю свои карты 2-му игроку (КОНЕЦ ИГРЫ)')
    await websocket.send(' '.join(map(str, my_cards)))

    print('Получаю карты 2-го игрока')
    op_cards = list(map(int, (await websocket.recv()).split(' ')))

    print('\nВаша рука:')
    show_deck(my_cards)
    print('Карты на столе:')
    all_table = table + table1 + table2
    show_deck(all_table)

    print('\nРука 2-го игрока:')
    show_deck(op_cards)
    show_deck(all_table)

    # Определение победителя
    winner = "Ничья"
    if not game.folded[0] and not game.folded[1]: # Оба не сбросили
        my_hand = my_cards + all_table
        op_hand = op_cards + all_table
        my_rank = get_hand_rank(my_hand)
        op_rank = get_hand_rank(op_hand)
        if my_rank > op_rank:
            winner = "Вы"
        elif op_rank > my_rank:
            winner = "Оппонент"
    elif game.folded[0]:
        winner = "Оппонент"
    else:
        winner = "Вы"
    print(f"\nПобедитель: {winner} (по комбинации)")
    print(f"Банк: {game.pot}")

    # --- Проверка честности (с добавлением Шнорра) ---
    print('\nПроверка корректности игры:')
    print('Отправляю свои ключи шифрования 2-му игроку')
    await websocket.send(' '.join(map(str, cr.key)))

    print('Получаю ключ шифрования от 2-го игрока')
    key = tuple(map(int, (await websocket.recv()).split(' ')))

    cr2 = ShamirCrypt(p)
    cr2.key = key

    print('Расшифровка колоды карт')
    decrypted_deck = cr2.decrypt(cr.decrypt(cards))
    show_deck(decrypted_deck)

    # Слепая подпись для честности
    schnorr = SchnorrSigner()
    signature = schnorr.sign(tuple(decrypted_deck))
    print(f'Подпись Шнорра для колоды: {signature}')
    # Отправляем подпись оппоненту
    await websocket.send(f'{signature[0]} {signature[1]}')

    # Получаем подпись от оппонента
    op_signature_data = list(map(int, (await websocket.recv()).split(' ')))
    op_signature = (op_signature_data[0], op_signature_data[1])
    print(f'Подпись оппонента: {op_signature}')
    is_valid = schnorr.verify(tuple(decrypted_deck), op_signature)
    print(f'Подпись оппонента действительна: {is_valid}')

    print(f'\nВсе карты в колоде уникальны: {len(decrypted_deck) == len(set(decrypted_deck))}')
    cards_on_table = my_cards + op_cards + all_table
    first_9_match = cards_on_table[:len(cards_on_table)] == decrypted_deck[:len(cards_on_table)]
    print(f'Карты игроков и стола совпадают с колодой: {first_9_match}')
    is_game_correct = all([
        len(decrypted_deck) == len(set(decrypted_deck)),
        first_9_match,
        is_valid
    ])
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

    # === ИСПРАВЛЕНО: Сначала получаем, расшифровываем, отправляем ===
    print('Получаю 2 карты игрока для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
    c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    await websocket.send(' '.join(map(str, c)))

    # === Потом отправляем свои 2 карты ===
    print('Беру следующие 2 карты из колоды и отправляю на расшифровку 1-му игроку')
    await websocket.send(' '.join(map(str, cards[2:4])))

    # === И получаем их обратно ===
    print('Получаю карты обратно и снимаю свой уровень шифрования')
    my_cards = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
    show_deck(my_cards)

    # --- Ставки ---
    game = PokerGame()
    print("\n--- НАЧАЛО ИГРЫ (ПОКЕР) ---")
    print("Ваши карты:", end=' ')
    show_deck(my_cards)

    # Ожидание блайндов
    await websocket.recv() # small blind
    await websocket.recv() # big blind
    print("Блайнды установлены.")

    # --- Префлоп ---
    print("\n--- ПРЕФЛОП ---")
    # Ваш ход
    move = input("Ваш ход (fold/check/raise N): ").strip().split()
    if move[0] == 'fold':
        game.fold(1)
        await websocket.send('fold')
        print("Вы сбросили. Оппонент выиграл!")
        return
    elif move[0] == 'check':
        game.check(1)
        await websocket.send('check')
    elif move[0] == 'raise':
        amount = int(move[1])
        game.place_bet(1, amount)
        await websocket.send(f'raise {amount}')
        print(f"Вы повысили ставку на {amount}")

    # Ожидание ответа оппонента
    action = await websocket.recv()
    if action == 'fold':
        game.fold(0)
        print("Оппонент сбросил. Вы выиграли!")
        return
    elif action == 'check':
        game.check(0)
    else: # raise
        amount = int(action.split()[1])
        game.place_bet(0, amount)
        print(f"Оппонент повысил ставку на {amount}")

    # --- Флоп ---
    if not game.game_over:
        print("\n--- ФЛОП ---")
        print('Получаю 3 карты из колоды для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
        c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
        await websocket.send(' '.join(map(str, c)))

        print('Получаю карты со стола')
        table = list(map(int, (await websocket.recv()).split(' ')))
        show_deck(table)

        # Ходы после флопа
        move = input("Ваш ход (fold/check/raise N): ").strip().split()
        if move[0] == 'fold':
            game.fold(1)
            await websocket.send('fold')
        else:
            amount = int(move[1]) if move[0] == 'raise' else 0
            game.place_bet(1, amount)
            await websocket.send(f'{move[0]} {amount}' if move[0] == 'raise' else move[0])

        action = await websocket.recv()
        if action != 'fold':
            amount = int(action.split()[1]) if action.startswith('raise') else 0
            game.place_bet(0, amount)

    # --- Тёрн ---
    if not game.game_over:
        print("\n--- ТЁРН ---")
        print('Получаю 1 карту из колоды для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
        c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
        await websocket.send(' '.join(map(str, c)))

        print('Получаю карту со стола')
        table1 = list(map(int, (await websocket.recv()).split(' ')))
        show_deck(table1)

        # Ходы после тёрна
        move = input("Ваш ход (fold/check/raise N): ").strip().split()
        if move[0] == 'fold':
            game.fold(1)
            await websocket.send('fold')
        else:
            amount = int(move[1]) if move[0] == 'raise' else 0
            game.place_bet(1, amount)
            await websocket.send(f'{move[0]} {amount}' if move[0] == 'raise' else move[0])

        action = await websocket.recv()
        if action != 'fold':
            amount = int(action.split()[1]) if action.startswith('raise') else 0
            game.place_bet(0, amount)

    # --- Ривер ---
    if not game.game_over:
        print("\n--- РИВЕР ---")
        print('Получаю 1 карту из колоды для расшифровки, снимаю свой уровень шифрования и отправляю обратно')
        c = cr.decrypt(list(map(int, (await websocket.recv()).split(' '))))
        await websocket.send(' '.join(map(str, c)))

        print('Получаю карту со стола')
        table2 = list(map(int, (await websocket.recv()).split(' ')))
        show_deck(table2)

        # Ходы после ривера
        move = input("Ваш ход (fold/check/raise N): ").strip().split()
        if move[0] == 'fold':
            game.fold(1)
            await websocket.send('fold')
        else:
            amount = int(move[1]) if move[0] == 'raise' else 0
            game.place_bet(1, amount)
            await websocket.send(f'{move[0]} {amount}' if move[0] == 'raise' else move[0])

        action = await websocket.recv()
        if action != 'fold':
            amount = int(action.split()[1]) if action.startswith('raise') else 0
            game.place_bet(0, amount)

    # --- Вскрытие ---
    print("\n--- ВСКРЫТИЕ КАРТ ---")
    print('Отправляю свои карты 1-му игроку (КОНЕЦ ИГРЫ)')
    await websocket.send(' '.join(map(str, my_cards)))

    print('Получаю карты 1-го игрока')
    op_cards = list(map(int, (await websocket.recv()).split(' ')))

    print('\nВаша рука:')
    show_deck(my_cards)
    print('Карты на столе:')
    all_table = table + table1 + table2
    show_deck(all_table)

    print('\nРука 1-го игрока:')
    show_deck(op_cards)
    show_deck(all_table)

    # Определение победителя
    winner = "Ничья"
    if not game.folded[0] and not game.folded[1]: # Оба не сбросили
        my_hand = my_cards + all_table
        op_hand = op_cards + all_table
        my_rank = get_hand_rank(my_hand)
        op_rank = get_hand_rank(op_hand)
        if my_rank > op_rank:
            winner = "Вы"
        elif op_rank > my_rank:
            winner = "Оппонент"
    elif game.folded[1]:
        winner = "Оппонент"
    else:
        winner = "Вы"
    print(f"\nПобедитель: {winner} (по комбинации)")
    print(f"Банк: {game.pot}")

    # --- Проверка честности (с добавлением Шнорра) ---
    print('\nПроверка корректности игры:')
    print('Отправляю свои ключи шифрования 1-му игроку')
    await websocket.send(' '.join(map(str, cr.key)))

    print('Получаю ключ шифрования от 1-го игрока')
    key = tuple(map(int, (await websocket.recv()).split(' ')))

    cr2 = ShamirCrypt(int(p))
    cr2.key = key

    print('Расшифровка колоды карт')
    decrypted_deck = cr2.decrypt(cr.decrypt(cards))
    show_deck(decrypted_deck)

    # Получаем подпись от оппонента
    host_signature_data = list(map(int, (await websocket.recv()).split(' ')))
    host_signature = (host_signature_data[0], host_signature_data[1])
    print(f'Подпись оппонента: {host_signature}')

    # Создаем свою подпись и отправляем
    schnorr = SchnorrSigner()
    my_signature = schnorr.sign(tuple(decrypted_deck))
    print(f'Моя подпись Шнорра: {my_signature}')
    await websocket.send(f'{my_signature[0]} {my_signature[1]}')

    is_valid = schnorr.verify(tuple(decrypted_deck), host_signature)
    print(f'Подпись оппонента действительна: {is_valid}')

    print(f'\nВсе карты в колоде уникальны: {len(decrypted_deck) == len(set(decrypted_deck))}')
    cards_on_table = my_cards + op_cards + all_table
    first_9_match = cards_on_table[:] == decrypted_deck[:len(cards_on_table)]
    print(f'Карты игроков и стола совпадают с колодой: {first_9_match}')
    is_game_correct = all([
        len(decrypted_deck) == len(set(decrypted_deck)),
        first_9_match,
        is_valid
    ])
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