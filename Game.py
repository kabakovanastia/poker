class PokerGame:
    def __init__(self):
        self.pot = 0
        self.current_bet = 0
        self.last_raiser = None
        self.player_bets = [0, 0]
        self.folded = [False, False]
        self.game_over = False

    def place_bet(self, player_id, amount):
        if self.folded[player_id]:
            return False
        self.pot += amount
        self.player_bets[player_id] += amount
        self.current_bet = max(self.player_bets)
        if amount > 0:
            self.last_raiser = player_id
        return True

    def fold(self, player_id):
        self.folded[player_id] = True
        self.game_over = True

    def check(self, player_id):
        return self.player_bets[player_id] >= self.current_bet