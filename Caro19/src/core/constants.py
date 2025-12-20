"""
Core constants for Caro19
Các hằng số dùng chung trong core game
"""

# GAME MODES

MODE_PVP = "PVP"   # Người vs Người
MODE_PVE = "PVE"   # Người vs Máy


# GAME STATES

STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"


# MENU ACTIONS

ACTION_PLAY = "PLAY"
ACTION_GUIDE = "GUIDE"
ACTION_EXIT = "EXIT"

ACTION_PVP = "PVP"
ACTION_PVE = "PVE"

ACTION_EASY = "EASY"
ACTION_NORMAL = "NORMAL"
ACTION_HARD = "HARD"

ACTION_RESTART = "RESTART"
ACTION_HOME = "HOME"


# PLAYER SYMBOLS

SYMBOL_X = "X"
SYMBOL_O = "O"


# DIRECTIONS (for win check / AI)
DIRECTIONS = [
    (0, 1),    # →
    (1, 0),    # ↓
    (1, 1),    # ↘
    (1, -1),   # ↗
]
