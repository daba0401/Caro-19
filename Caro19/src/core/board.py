from config.game_config import BOARD_ROWS, BOARD_COLS, WIN_CONDITION


class Board:
    def __init__(self):
        self.rows = BOARD_ROWS
        self.cols = BOARD_COLS
        self.grid = [
            [None for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

    # BASIC
    def reset(self):
        """Reset toàn bộ bàn cờ"""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = None

    def is_inside(self, row, col):
        """Kiểm tra ô có nằm trong bàn không"""
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_empty(self, row, col):
        """Kiểm tra ô trống"""
        return self.is_inside(row, col) and self.grid[row][col] is None

    def place(self, row, col, symbol):
        """
        Đặt quân tại (row, col)
        Trả về True nếu đặt thành công
        """
        if not self.is_empty(row, col):
            return False

        self.grid[row][col] = symbol
        return True

    def remove(self, row, col):
        """
        Gỡ quân tại (row, col) – dùng cho Undo
        """
        if not self.is_inside(row, col):
            return False

        self.grid[row][col] = None
        return True

    # WIN CHECK
    def check_win(self, row, col, symbol):
        """
        Kiểm tra thắng tại (row, col)

        Nếu thắng:
            trả về list 5 ô [(r,c), ...]
        Nếu không:
            trả về None
        """
        if not self.is_inside(row, col):
            return None

        directions = [
            (0, 1),    # ngang →
            (1, 0),    # dọc ↓
            (1, 1),    # chéo \
            (1, -1),   # chéo /
        ]

        for dr, dc in directions:
            cells = [(row, col)]

            # Đi xuôi
            r, c = row + dr, col + dc
            while self.is_inside(r, c) and self.grid[r][c] == symbol:
                cells.append((r, c))
                r += dr
                c += dc

            # Đi ngược
            r, c = row - dr, col - dc
            while self.is_inside(r, c) and self.grid[r][c] == symbol:
                cells.insert(0, (r, c))
                r -= dr
                c -= dc

            if len(cells) >= WIN_CONDITION:
                return cells[:WIN_CONDITION]

        return None


    # FULL CHECK
    def is_full(self):
        """Kiểm tra bàn cờ đã đầy chưa"""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] is None:
                    return False
        return True
