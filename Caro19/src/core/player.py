
class Player:
    def __init__(self, symbol, is_ai=False, name=None):
        self.symbol = symbol
        self.is_ai = is_ai
        self.name = name if name else self._default_name()

    def _default_name(self):
        if self.is_ai:
            return "Computer"
        return f"Player {self.symbol}"

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Player(symbol={self.symbol}, is_ai={self.is_ai})"
