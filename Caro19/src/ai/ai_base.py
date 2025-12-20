"""
Base AI class for Caro19
Lớp nền cho tất cả các AI (Easy / Normal / Hard)
"""

from abc import ABC, abstractmethod


class AIBase(ABC):
    def __init__(self, symbol):
        """
        symbol: ký hiệu của AI ('X' hoặc 'O')
        """
        self.symbol = symbol

    @abstractmethod
    def get_move(self, board):
        """
        Trả về nước đi (row, col)
        board: đối tượng Board
        """
        pass

    def get_opponent_symbol(self):
        """Lấy ký hiệu đối thủ"""
        return "O" if self.symbol == "X" else "X"
