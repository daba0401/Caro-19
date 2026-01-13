
import random
from src.ai.ai_base import AIBase

from config.ai_config import (
    NORMAL_ATTACK_WEIGHT,
    NORMAL_DEFENSE_WEIGHT,
    NORMAL_RANDOM_RATE
)


class AINormal(AIBase):

    def get_move(self, board):
        """
        Chiến lược:
        1. Nếu có thể thắng → đánh ngay
        2. Nếu đối thủ sắp thắng → chặn
        3. Đánh ô có điểm heuristic cao nhất
        """

        opponent = self.get_opponent_symbol()

        #  Thắng ngay nếu có thể
        win_move = self._find_winning_move(board, self.symbol)
        if win_move:
            return win_move

        # Chặn đối thủ
        block_move = self._find_winning_move(board, opponent)
        if block_move:
            return block_move

        # Đánh theo heuristic
        best_move = self._heuristic_move(board)

        # Random nhẹ
        if random.random() < NORMAL_RANDOM_RATE:
            return self._random_move(board)

        return best_move

    # WIN / BLOCK
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

    # HEURISTIC
    def _heuristic_move(self, board):
        best_score = -float("inf")
        best_moves = []

        for row in range(board.rows):
            for col in range(board.cols):
                if board.is_empty(row, col):
                    score = self._evaluate_position(board, row, col)

                    if score > best_score:
                        best_score = score
                        best_moves = [(row, col)]
                    elif score == best_score:
                        best_moves.append((row, col))

        if best_moves:
            return random.choice(best_moves)

        return self._random_move(board)

    def _evaluate_position(self, board, row, col):
        #Chấm điểm ô (row, col)
        attack_score = self._count_max_chain(board, row, col, self.symbol)
        defense_score = self._count_max_chain(board, row, col, self.get_opponent_symbol())

        return (
            attack_score * NORMAL_ATTACK_WEIGHT +
            defense_score * NORMAL_DEFENSE_WEIGHT
        )

    def _count_max_chain(self, board, row, col, symbol):
        #Đếm chuỗi dài nhất nếu đặt symbol tại (row, col)
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        max_count = 0
        board.grid[row][col] = symbol

        for dr, dc in directions:
            count = 1
            count += self._count_direction(board, row, col, dr, dc, symbol)
            count += self._count_direction(board, row, col, -dr, -dc, symbol)
            max_count = max(max_count, count)

        board.grid[row][col] = None
        return max_count

    def _count_direction(self, board, row, col, dr, dc, symbol):
        r = row + dr
        c = col + dc
        count = 0

        while (
            0 <= r < board.rows
            and 0 <= c < board.cols
            and board.grid[r][c] == symbol
        ):
            count += 1
            r += dr
            c += dc

        return count


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
