import time

from src.core.board import Board
from src.core.player import Player
from src.core.constants import (
    MODE_PVP,
    MODE_PVE,
    SYMBOL_X,
    SYMBOL_O,
)

from src.ai.ai_easy import AIEasy
from src.ai.ai_normal import AINormal
from src.ai.ai_hard import AIHard

from config.game_config import (
    PLAYER_TIME_LIMIT,
    ENABLE_TIME_CONTROL,
    ENABLE_IN_GAME_EXIT,
)


class Game:
    def __init__(self, mode, ai_level=None):
        self.mode = mode
        self.ai_level = ai_level

        self.board = Board()

        self.player_x = Player(SYMBOL_X)
        self.player_o = Player(SYMBOL_O)

        self.ai = None
        if self.mode == MODE_PVE:
            self._init_ai()

        self.reset()

    # INIT AI
    def _init_ai(self):
        if self.ai_level == "EASY":
            self.ai = AIEasy(SYMBOL_O)
        elif self.ai_level == "NORMAL":
            self.ai = AINormal(SYMBOL_O)
        elif self.ai_level == "HARD":
            self.ai = AIHard(SYMBOL_O)
        else:
            self.ai = AIEasy(SYMBOL_O)

    # =========================
    # RESET GAME
    # =========================
    def reset(self):
        self.board.reset()
        self.current_player = SYMBOL_X
        self.game_over = False
        self.winner = None
        self.win_cells = None
        self.last_move = None

        # ===== TIME CONTROL =====
        self.time_left = {
            SYMBOL_X: PLAYER_TIME_LIMIT,
            SYMBOL_O: PLAYER_TIME_LIMIT,
        }
        self.last_tick = time.time()

        # ===== UNDO / REDO =====
        self.move_history = []
        self.redo_stack = []

    # =========================
    # TIME UPDATE
    # =========================
    def update_time(self):
        """Cập nhật đồng hồ cho người đang đi"""
        if not ENABLE_TIME_CONTROL:
            return

        if self.game_over:
            return

        now = time.time()
        elapsed = now - self.last_tick
        self.last_tick = now

        self.time_left[self.current_player] -= elapsed

        if self.time_left[self.current_player] <= 0:
            self.time_left[self.current_player] = 0
            self.game_over = True
            self.winner = SYMBOL_O if self.current_player == SYMBOL_X else SYMBOL_X

    # =========================
    # SAVE STATE (UNDO / REDO)
    # =========================
    def _save_state(self, row, col, symbol):
        self.move_history.append({
            "row": row,
            "col": col,
            "symbol": symbol,
            "current_player": self.current_player,
        })
        self.redo_stack.clear()

    # =========================
    # PLAYER MOVE
    # =========================
    def make_move(self, row, col):
        if self.game_over:
            return False

        if not self.board.place(row, col, self.current_player):
            return False

        self._save_state(row, col, self.current_player)
        self.last_move = (row, col)

        win_cells = self.board.check_win(row, col, self.current_player)
        if win_cells:
            self.game_over = True
            self.winner = self.current_player
            self.win_cells = win_cells
            return True

        if self.board.is_full():
            self.game_over = True
            self.winner = None
            return True

        self._switch_turn()
        return True

    # =========================
    # AI MOVE
    # =========================
    def ai_move(self):
        if self.game_over:
            return False

        if self.mode != MODE_PVE or self.ai is None:
            return False

        if self.current_player != SYMBOL_O:
            return False

        row, col = self.ai.get_move(self.board)
        if row is None:
            return False

        if not self.board.place(row, col, SYMBOL_O):
            return False

        self._save_state(row, col, SYMBOL_O)
        self.last_move = (row, col)

        win_cells = self.board.check_win(row, col, SYMBOL_O)
        if win_cells:
            self.game_over = True
            self.winner = SYMBOL_O
            self.win_cells = win_cells
            return True

        if self.board.is_full():
            self.game_over = True
            self.winner = None
            return True

        self._switch_turn()
        return True

    # =========================
    # SWITCH TURN
    # =========================
    def _switch_turn(self):
        self.current_player = (
            SYMBOL_O if self.current_player == SYMBOL_X else SYMBOL_X
        )
        self.last_tick = time.time()

    # =========================
    # UNDO / REDO
    # =========================
    def undo(self):
        if not self.move_history:
            return False

        state = self.move_history.pop()
        self.redo_stack.append(state)

        self.board.grid[state["row"]][state["col"]] = None
        self.current_player = state["symbol"]
        self.last_move = None
        self.last_tick = time.time()

        self.game_over = False
        self.winner = None
        self.win_cells = None

        return True

    def redo(self):
        if not self.redo_stack:
            return False

        state = self.redo_stack.pop()
        self.move_history.append(state)

        self.board.grid[state["row"]][state["col"]] = state["symbol"]
        self.current_player = (
            SYMBOL_O if state["symbol"] == SYMBOL_X else SYMBOL_X
        )
        self.last_move = (state["row"], state["col"])
        self.last_tick = time.time()

        return True

    # =========================
    # IN-GAME EXIT
    # =========================
    def can_exit_game(self):
        """Core check cho phép thoát khi đang chơi"""
        return ENABLE_IN_GAME_EXIT
