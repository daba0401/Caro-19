"""
AI configuration for Caro19
Chứa cấu hình cho các mức độ AI
"""

# AI DIFFICULTY LEVELS

AI_EASY = "EASY"
AI_NORMAL = "NORMAL"
AI_HARD = "HARD"


# EASY MODE
# Đánh ngẫu nhiên

EASY_RANDOM_RATE = 1.0   # 100% nước đi ngẫu nhiên



# NORMAL MODE
# Heuristic đơn giản (ưu tiên thắng / chặn)

NORMAL_ATTACK_WEIGHT = 1.0
NORMAL_DEFENSE_WEIGHT = 1.0

# Tỷ lệ đánh ngẫu nhiên để tránh quá "máy"
NORMAL_RANDOM_RATE = 0.01

# HARD MODE
# Minimax + Alpha-Beta Pruning

HARD_SEARCH_DEPTH = 4     # độ sâu minimax
HARD_USE_ALPHA_BETA = True

# Giới hạn số nước đi xét (tối ưu hiệu năng)
HARD_MAX_CANDIDATES = 15

# Thời gian suy nghĩ tối đa (giây)
HARD_TIME_LIMIT = 7.36


# GENERAL AI SETTINGS

# Ký hiệu AI sử dụng
AI_PLAYER_SYMBOL = "O"

# Ký hiệu người chơi
HUMAN_PLAYER_SYMBOL = "X"

# Cho phép AI đi trước
AI_CAN_GO_FIRST = False
