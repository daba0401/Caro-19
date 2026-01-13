"""
AI mức Dễ:
- Biết thắng nếu có thể
- Biết chặn người chơi
- Đánh gần quân đã có
"""

import random
from src.ai.ai_base import AIBase


class AIEasy(AIBase):

    def get_move(self, board):
        """
        Thứ tự ưu tiên:
        1. Có thể thắng → đánh
        2. Đối thủ sắp thắng → chặn
        3. Đánh gần quân đã có
        4. Random fallback
        """

        opponent = self.get_opponent_symbol()

        # 1 Thắng nếu có thể
        win_move = self._find_winning_move(board, self.symbol)
        if win_move:
            return win_move

        # 2 Chặn đối thủ
        block_move = self._find_winning_move(board, opponent)
        if block_move:
            return block_move

        # 3 Đánh gần quân đã có
        near_move = self._find_near_move(board)
        if near_move:
            return near_move

        # 4 Random
        return self._random_move(board)

    # WIN / BLOCK LOGIC

    def _find_winning_move(self, board, symbol):
        for row in range(board.rows):
            for col in range(board.cols):
                if board.is_empty(row, col):
                    board.grid[row][col] = symbol
                    if board.check_win(row, col, symbol):
                        board.grid[row][col] = None
                        return row, col
                    board.grid[row][col] = None
        return None

    # NEAR MOVE
    def _find_near_move(self, board):
        #Chọn ô trống gần quân đã có (bán kính 1)
        candidates = set()

        for row in range(board.rows):
            for col in range(board.cols):
                if not board.is_empty(row, col):
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            r = row + dr
                            c = col + dc
                            if (
                                0 <= r < board.rows
                                and 0 <= c < board.cols
                                and board.is_empty(r, c)
                            ):
                                candidates.add((r, c))

        if candidates:
            return random.choice(list(candidates))

        return None

    # RANDOM
    def _random_move(self, board):
        empty_cells = [
            (r, c)
            for r in range(board.rows)
            for c in range(board.cols)
            if board.is_empty(r, c)
        ]

        if not empty_cells:
            return None, None

        return random.choice(empty_cells)
