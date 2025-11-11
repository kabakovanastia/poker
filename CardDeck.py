from collections import defaultdict
import random

# Карточная колода
deck = {49773332: (2, 1), 74598670: (3, 1), 17708808: (4, 1), 27047573: (5, 1), 16292670: (6, 1), 60166302: (7, 1), 90004622: (8, 1), 99036622: (9, 1), 43948341: (10, 1), 8889509: (11, 1), 75771787: (12, 1), 52637205: (13, 1), 34558225: (14, 1), 51057104: (2, 2), 28119000: (3, 2), 18039282: (4, 2), 10754258: (5, 2), 35544667: (6, 2), 60111821: (7, 2), 7737019: (8, 2), 65146206: (9, 2), 58402587: (10, 2), 26778106: (11, 2), 86635986: (12, 2), 92621042: (13, 2), 83018349: (14, 2), 81831411: (2, 3), 33364818: (3, 3), 98762735: (4, 3), 71486908: (5, 3), 88896404: (6, 3), 47207287: (7, 3), 4830095: (8, 3), 54441094: (9, 3), 28900819: (10, 3), 285806: (11, 3), 71925511: (12, 3), 80529542: (13, 3), 63838381: (14, 3), 10450366: (2, 4), 38406037: (3, 4), 94417991: (4, 4), 69900722: (5, 4), 95767970: (6, 4), 78947780: (7, 4), 73907707: (8, 4), 42830248: (9, 4), 89281639: (10, 4), 58473653: (11, 4), 2975390: (12, 4), 98508597: (13, 4), 22613269: (14, 4)}

card_str = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
card_suit = {1: '♣', 2: '♦', 3: '♥', 4: '♠'}

class CardDeck:
    def __init__(self):
        self.cards = list(deck.keys())

    def get_card_shuffle(self):
        shuffled = self.cards[:]
        random.shuffle(shuffled)
        return shuffled

def show_deck(cards):
    c = []
    for i in cards:
        if i in deck:
            card = deck[i]
            c.append(f'{card_str[card[0]]}{card_suit[card[1]]}')
        else:
            c.append('??')
    print(' '.join(c))

def get_hand_rank(hand):
    """Определяет ранг комбинации (упрощённо)"""
    hand_cards = [deck[c] for c in hand if c in deck]
    values = [c[0] for c in hand_cards]
    suits = [c[1] for c in hand_cards]
    value_counts = defaultdict(int)
    for v in values:
        value_counts[v] += 1
    
    counts = sorted(value_counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    is_straight = len(set(values)) == 5 and max(values) - min(values) == 4
    
    if is_straight and is_flush:
        return (9, max(values))  # Стрит-флеш
    elif counts[0] == 4:
        return (8, max(v for v, c in value_counts.items() if c == 4))  # Каре
    elif counts[0] == 3 and counts[1] == 2:
        return (7, max(v for v, c in value_counts.items() if c == 3))  # Фулл-хаус
    elif is_flush:
        return (6, sorted(values, reverse=True))  # Флеш
    elif is_straight:
        return (5, max(values))  # Стрит
    elif counts[0] == 3:
        return (4, max(v for v, c in value_counts.items() if c == 3))  # Сет
    elif counts[0] == 2 and counts[1] == 2:
        pair1 = max(v for v, c in value_counts.items() if c == 2)
        pair2 = min(v for v, c in value_counts.items() if c == 2)
        return (3, (pair1, pair2))  # Две пары
    elif counts[0] == 2:
        return (2, max(v for v, c in value_counts.items() if c == 2))  # Пара
    else:
        return (1, sorted(values, reverse=True))  # Старшая карта