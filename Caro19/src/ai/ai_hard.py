from __future__ import annotations

import math
import time
from typing import List, Tuple, Optional, Set

from src.ai.ai_base import AIBase
from config.ai_config import HARD_TIME_LIMIT, HARD_MAX_CANDIDATES, HARD_SEARCH_DEPTH

DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]
WIN_SCORE = 10_000_000


class AIHard(AIBase):
    """
    HARD (Game+ Stable)
    - Rule priorities đúng chuẩn:
        1) Win now
        2) Block opponent win now (NO validation)
        3) Block opponent open-four (NO validation)
        4) Create open-four
        5) Block/Make closed-four & double-three (WITH validation)
        6) Counter-threat (ép ngược)
        7) Alpha-beta fallback (safe)
    - Defensive validation: loại nước chặn vô nghĩa (nhưng KHÔNG áp dụng cho win/open4)
    - Không out game: không trả về ±inf
    """

    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.start_time: float = 0.0

        self.max_depth = max(2, int(HARD_SEARCH_DEPTH))
        self.near_radius = 2
        self.cand_limit = max(10, int(HARD_MAX_CANDIDATES))


    # PUBLIC
    def get_move(self, board) -> Tuple[int, int]:
        self.start_time = time.time()
        me = self.symbol
        opp = self.get_opponent_symbol()

        if not self._has_any_piece(board):
            return board.rows // 2, board.cols // 2

        # 1) RULES
        mv = self._rule_move(board, me, opp)
        if mv:
            return mv

        # 2) SEARCH (iterative deepening within time limit)
        root_moves = self._generate_candidates(board, me, opp)
        if not root_moves:
            return self._first_empty(board)

        best_move = root_moves[0]
        best_score = -math.inf

        for depth in range(1, self.max_depth + 1):
            if self._time_up():
                break
            score, move = self._root_search(board, root_moves, depth, me, opp)
            if move is not None:
                best_score, best_move = score, move
            if best_score >= WIN_SCORE // 2:
                break

        return best_move

    # RULE MOVE

    def _rule_move(self, board, me: str, opp: str) -> Optional[Tuple[int, int]]:
        # 1) Win now
        w = self._find_winning_move(board, me)
        if w:
            return w

        # 2) Block opponent win now  (NO validation!)
        b = self._find_winning_move(board, opp)
        if b:
            return b

        # 3) Block opponent OPEN-FOUR (NO validation!)
        block_open4 = self._find_open_four_move(board, opp)
        if block_open4:
            return block_open4

        # 4) Create OPEN-FOUR
        make_open4 = self._find_open_four_move(board, me)
        if make_open4:
            return make_open4

        # 5) Block opponent CLOSED-FOUR / DOUBLE-THREE with validation
        block_cf = self._find_closed_four_move(board, opp)
        if block_cf and self._defense_valid(board, block_cf, me, opp):
            return block_cf

        block_d3 = self._find_double_open_three_move(board, opp)
        if block_d3 and self._defense_valid(board, block_d3, me, opp):
            return block_d3

        # 6) Create CLOSED-FOUR / DOUBLE-THREE (tấn công)
        make_cf = self._find_closed_four_move(board, me)
        if make_cf:
            return make_cf

        make_d3 = self._find_double_open_three_move(board, me)
        if make_d3:
            return make_d3

        # 7) Counter-threat (ép ngược) – nếu có
        ct = self._best_counter_threat(board, me, opp)
        if ct:
            return ct

        return None

    # DEFENSIVE VALIDATION
    def _defense_valid(self, board, move: Tuple[int, int], me: str, opp: str) -> bool:
        """
        Dùng cho các nước block "mơ hồ" (closed-four/double3).
        Sau khi me đi, nếu opp có:
        - thắng ngay
        - tạo open-four
        - tạo double open-three
        => nước block này là vô nghĩa.
        """
        r, c = move
        if board.grid[r][c] is not None:
            return False

        board.grid[r][c] = me

        # Opponent win immediately?
        if self._find_winning_move(board, opp):
            board.grid[r][c] = None
            return False

        # Opponent has open-four or double-three immediately?
        for rr, cc in self._near_candidates(board, radius=2):
            if board.grid[rr][cc] is not None:
                continue
            board.grid[rr][cc] = opp
            danger = self._is_open_four(board, rr, cc, opp) or (self._count_open_three_dirs(board, rr, cc, opp) >= 2)
            board.grid[rr][cc] = None
            if danger:
                board.grid[r][c] = None
                return False

        board.grid[r][c] = None
        return True


    # COUNTER THREAT
    def _best_counter_threat(self, board, me: str, opp: str) -> Optional[Tuple[int, int]]:
        """
        Nếu không có rule bắt buộc, ưu tiên tạo đe doạ khiến đối thủ phải thủ.
        """
        best = None
        best_score = -1

        for r, c in self._near_candidates(board, radius=2):
            if board.grid[r][c] is not None:
                continue

            board.grid[r][c] = me

            score = 0
            # tạo open-four => cực mạnh
            if self._is_open_four(board, r, c, me):
                score += 1000
            # double open-three
            d3 = self._count_open_three_dirs(board, r, c, me)
            if d3 >= 2:
                score += 400
            # open-three
            score += d3 * 80

            score += self._center_bonus(board, r, c)

            board.grid[r][c] = None

            if score > best_score:
                best_score = score
                best = (r, c)

        return best if best_score >= 200 else None

    # SEARCH
    def _root_search(self, board, moves: List[Tuple[int, int]], depth: int, me: str, opp: str) -> Tuple[int, Optional[Tuple[int, int]]]:
        alpha = -math.inf
        beta = math.inf

        ordered = self._order_moves(board, moves, me, opp)

        best_score = -math.inf
        best_move = None

        for r, c in ordered:
            if self._time_up():
                break
            if board.grid[r][c] is not None:
                continue

            board.grid[r][c] = me
            score = self._alphabeta(board, depth - 1, alpha, beta, False, me, opp)
            board.grid[r][c] = None

            # safety (không bao giờ để inf lọt ra)
            if score == math.inf:
                score = WIN_SCORE
            elif score == -math.inf:
                score = -WIN_SCORE

            if score > best_score:
                best_score = score
                best_move = (r, c)

            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return int(best_score), best_move

    def _alphabeta(self, board, depth: int, alpha: float, beta: float, maximizing: bool, me: str, opp: str) -> int:
        if self._time_up():
            return self._evaluate(board, me, opp)

        # terminal
        if self._check_win_board(board, me):
            return WIN_SCORE
        if self._check_win_board(board, opp):
            return -WIN_SCORE

        if depth <= 0:
            return self._evaluate(board, me, opp)

        moves = self._generate_candidates(board, me, opp)
        if not moves:
            return self._evaluate(board, me, opp)

        moves = self._order_moves(board, moves, me, opp)

        if maximizing:
            v = -math.inf
            for r, c in moves:
                if self._time_up():
                    break
                if board.grid[r][c] is not None:
                    continue
                board.grid[r][c] = me
                score = self._alphabeta(board, depth - 1, alpha, beta, False, me, opp)
                board.grid[r][c] = None
                v = max(v, score)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break

            if v == math.inf or v == -math.inf:
                return self._evaluate(board, me, opp)
            return int(v)

        else:
            v = math.inf
            for r, c in moves:
                if self._time_up():
                    break
                if board.grid[r][c] is not None:
                    continue
                board.grid[r][c] = opp
                score = self._alphabeta(board, depth - 1, alpha, beta, True, me, opp)
                board.grid[r][c] = None
                v = min(v, score)
                beta = min(beta, v)
                if beta <= alpha:
                    break

            if v == math.inf or v == -math.inf:
                return self._evaluate(board, me, opp)
            return int(v)

    # EVALUATION
    def _evaluate(self, board, me: str, opp: str) -> int:
        """
        Evaluation nhanh nhưng ưu tiên đúng threat:
        open4 > closed4 > double3 > open3 > open2...
        """
        return self._pattern_score(board, me) - self._pattern_score(board, opp)

    def _pattern_score(self, board, sym: str) -> int:
        total = 0
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] != sym:
                    continue
                for dr, dc in DIRECTIONS:
                    # chỉ tính nếu là đầu chuỗi theo hướng (tránh đếm đôi)
                    pr, pc = r - dr, c - dc
                    if board.is_inside(pr, pc) and board.grid[pr][pc] == sym:
                        continue

                    cnt, open_ends = self._count_chain_forward(board, r, c, dr, dc, sym)

                    if cnt >= 5:
                        total += 200_000
                    elif cnt == 4 and open_ends == 2:
                        total += 35_000
                    elif cnt == 4 and open_ends == 1:
                        total += 8_000
                    elif cnt == 3 and open_ends == 2:
                        total += 2_500
                    elif cnt == 3 and open_ends == 1:
                        total += 700
                    elif cnt == 2 and open_ends == 2:
                        total += 250
        return total

    # MOVE GENERATION + ORDER
    def _generate_candidates(self, board, me: str, opp: str) -> List[Tuple[int, int]]:
        cands = self._near_candidates(board, radius=self.near_radius)
        if not cands:
            return [self._first_empty(board)]

        scored = []
        for r, c in cands:
            if board.grid[r][c] is not None:
                continue
            scored.append((self._quick_score(board, r, c, me, opp), r, c))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [(r, c) for _, r, c in scored[: self.cand_limit]]

    def _order_moves(self, board, moves: List[Tuple[int, int]], me: str, opp: str) -> List[Tuple[int, int]]:
        scored = []
        for r, c in moves:
            if board.grid[r][c] is not None:
                continue
            scored.append((self._quick_score(board, r, c, me, opp), r, c))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [(r, c) for _, r, c in scored]

    def _quick_score(self, board, r: int, c: int, me: str, opp: str) -> int:
        """
        Move ordering mạnh:
        - thắng/chặn thắng
        - open4/closed4/double3
        - center bonus
        """
        score = 0
        score += self._center_bonus(board, r, c)

        # thử me
        board.grid[r][c] = me
        if self._check_win_from(board, r, c, me):
            board.grid[r][c] = None
            return 9_000_000
        if self._is_open_four(board, r, c, me):
            score += 600_000
        if self._is_closed_four(board, r, c, me):
            score += 120_000
        if self._count_open_three_dirs(board, r, c, me) >= 2:
            score += 80_000
        score += self._local_chain_bonus(board, r, c, me) * 10
        board.grid[r][c] = None

        # thử opp (để ưu tiên chặn)
        board.grid[r][c] = opp
        if self._check_win_from(board, r, c, opp):
            board.grid[r][c] = None
            return 8_500_000
        if self._is_open_four(board, r, c, opp):
            score += 550_000
        if self._is_closed_four(board, r, c, opp):
            score += 110_000
        if self._count_open_three_dirs(board, r, c, opp) >= 2:
            score += 70_000
        score += self._local_chain_bonus(board, r, c, opp) * 8
        board.grid[r][c] = None

        return int(score)

    def _local_chain_bonus(self, board, r: int, c: int, sym: str) -> int:
        b = 0
        for dr, dc in DIRECTIONS:
            cnt, oe = self._count_chain_around(board, r, c, dr, dc, sym)
            b += cnt * cnt * (3 if oe == 2 else 1)
        return b

    # THREAT FINDERS (rules)
    def _find_winning_move(self, board, sym: str) -> Optional[Tuple[int, int]]:
        # chỉ thử vùng gần để nhanh
        cands = self._near_candidates(board, radius=2)
        if not cands:
            cands = [(r, c) for r in range(board.rows) for c in range(board.cols) if board.grid[r][c] is None]

        for r, c in cands:
            if board.grid[r][c] is not None:
                continue
            board.grid[r][c] = sym
            ok = self._check_win_from(board, r, c, sym)
            board.grid[r][c] = None
            if ok:
                return (r, c)
        return None

    def _find_open_four_move(self, board, sym: str) -> Optional[Tuple[int, int]]:
        for r, c in self._near_candidates(board, radius=2):
            if board.grid[r][c] is not None:
                continue
            board.grid[r][c] = sym
            ok = self._is_open_four(board, r, c, sym)
            board.grid[r][c] = None
            if ok:
                return (r, c)
        return None

    def _find_closed_four_move(self, board, sym: str) -> Optional[Tuple[int, int]]:
        for r, c in self._near_candidates(board, radius=2):
            if board.grid[r][c] is not None:
                continue
            board.grid[r][c] = sym
            ok = self._is_closed_four(board, r, c, sym)
            board.grid[r][c] = None
            if ok:
                return (r, c)
        return None

    def _find_double_open_three_move(self, board, sym: str) -> Optional[Tuple[int, int]]:
        best = None
        best_k = 0
        for r, c in self._near_candidates(board, radius=2):
            if board.grid[r][c] is not None:
                continue
            board.grid[r][c] = sym
            k = self._count_open_three_dirs(board, r, c, sym)
            board.grid[r][c] = None
            if k >= 2 and k > best_k:
                best_k = k
                best = (r, c)
        return best

    # PATTERN CHECKS
    def _is_open_four(self, board, r: int, c: int, sym: str) -> bool:
        for dr, dc in DIRECTIONS:
            cnt, oe = self._count_chain_around(board, r, c, dr, dc, sym)
            if cnt == 4 and oe == 2:
                return True
        return False

    def _is_closed_four(self, board, r: int, c: int, sym: str) -> bool:
        for dr, dc in DIRECTIONS:
            cnt, oe = self._count_chain_around(board, r, c, dr, dc, sym)
            if cnt == 4 and oe == 1:
                return True
        return False

    def _count_open_three_dirs(self, board, r: int, c: int, sym: str) -> int:
        k = 0
        for dr, dc in DIRECTIONS:
            cnt, oe = self._count_chain_around(board, r, c, dr, dc, sym)
            if cnt == 3 and oe == 2:
                k += 1
        return k


    # WIN CHECKS
    def _check_win_board(self, board, sym: str) -> bool:
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] == sym and self._check_win_from(board, r, c, sym):
                    return True
        return False

    def _check_win_from(self, board, r: int, c: int, sym: str) -> bool:
        for dr, dc in DIRECTIONS:
            cnt = 1
            cnt += self._count_dir(board, r, c, dr, dc, sym)
            cnt += self._count_dir(board, r, c, -dr, -dc, sym)
            if cnt >= 5:
                return True
        return False

    def _count_dir(self, board, r: int, c: int, dr: int, dc: int, sym: str) -> int:
        cnt = 0
        rr, cc = r + dr, c + dc
        while board.is_inside(rr, cc) and board.grid[rr][cc] == sym:
            cnt += 1
            rr += dr
            cc += dc
        return cnt

    # CHAIN COUNTS
    def _count_chain_around(self, board, r: int, c: int, dr: int, dc: int, sym: str) -> Tuple[int, int]:
        cnt = 1

        rr, cc = r + dr, c + dc
        while board.is_inside(rr, cc) and board.grid[rr][cc] == sym:
            cnt += 1
            rr += dr
            cc += dc
        end1 = board.is_inside(rr, cc) and board.grid[rr][cc] is None

        rr, cc = r - dr, c - dc
        while board.is_inside(rr, cc) and board.grid[rr][cc] == sym:
            cnt += 1
            rr -= dr
            cc -= dc
        end2 = board.is_inside(rr, cc) and board.grid[rr][cc] is None

        oe = (1 if end1 else 0) + (1 if end2 else 0)
        return cnt, oe

    def _count_chain_forward(self, board, r: int, c: int, dr: int, dc: int, sym: str) -> Tuple[int, int]:
        # assumes (r,c) is sym and is "start" for this direction
        cnt = 0
        rr, cc = r, c
        while board.is_inside(rr, cc) and board.grid[rr][cc] == sym:
            cnt += 1
            rr += dr
            cc += dc

        open_ends = 0
        if board.is_inside(rr, cc) and board.grid[rr][cc] is None:
            open_ends += 1

        pr, pc = r - dr, c - dc
        if board.is_inside(pr, pc) and board.grid[pr][pc] is None:
            open_ends += 1

        return cnt, open_ends

    # CANDIDATES
    def _near_candidates(self, board, radius: int = 2) -> List[Tuple[int, int]]:
        s: Set[Tuple[int, int]] = set()
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] is None:
                    continue
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        rr, cc = r + dr, c + dc
                        if board.is_inside(rr, cc) and board.grid[rr][cc] is None:
                            s.add((rr, cc))
        return list(s)

    def _center_bonus(self, board, r: int, c: int) -> int:
        cr, cc = board.rows // 2, board.cols // 2
        return max(0, 120 - (abs(r - cr) + abs(c - cc)) * 6)

    def _first_empty(self, board) -> Tuple[int, int]:
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] is None:
                    return (r, c)
        return (0, 0)

    @staticmethod
    def _has_any_piece(board) -> bool:
        for r in range(board.rows):
            for c in range(board.cols):
                if board.grid[r][c] is not None:
                    return True
        return False

    # TIME
    def _time_up(self) -> bool:
        return (time.time() - self.start_time) >= float(HARD_TIME_LIMIT)
