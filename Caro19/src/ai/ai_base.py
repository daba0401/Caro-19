"""
Base AI class for Caro19
Lớp nền cho tất cả các AI (Easy / Normal / Hard)
"""

from abc import ABC, abstractmethod

class AIBase(ABC):
    def __init__(self, symbol):

        self.symbol = symbol

    @abstractmethod
    def get_move(self, board):
        pass

    def get_opponent_symbol(self):
        #Lấy ký hiệu đối thủ
        return "O" if self.symbol == "X" else "X"
