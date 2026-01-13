import time
import pygame

from src.core.game import Game
from src.core.constants import MODE_PVP, MODE_PVE
from config.game_config import BOARD_ROWS, BOARD_COLS
from config.ui_config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME


class GameScreen:
    def __init__(self, screen, mode, ai_level=None):
        self.screen = screen
        self.mode = mode
        self.ai_level = ai_level

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 22)
        self.big_font = pygame.font.Font(FONT_NAME, 28)

        self._new_game()

        # AI
        self.ai_thinking = False
        self.ai_start_time = 0.0
        self.AI_THINK_DELAY = 0.35

        # UX
        self.player_just_moved = False

        # Layout
        self.HUD_HEIGHT = 70
        self.SIDE_PANEL_WIDTH = 260
        self.PADDING = 30

        self._calculate_layout()

    # GAME CONTROL
    def _new_game(self):
        self.game = Game(self.mode, self.ai_level)
        self.last_move = None
        self.ai_thinking = False
        self.player_just_moved = False

    # LAYOUT
    def _calculate_layout(self):
        board_area_w = SCREEN_WIDTH - self.SIDE_PANEL_WIDTH - self.PADDING * 3
        board_area_h = SCREEN_HEIGHT - self.HUD_HEIGHT - self.PADDING * 2

        self.cell_size = min(
            board_area_w // BOARD_COLS,
            board_area_h // BOARD_ROWS
        )

        self.board_size = self.cell_size * BOARD_COLS
        self.board_x = self.PADDING
        self.board_y = self.HUD_HEIGHT + self.PADDING

        self.panel_x = self.board_x + self.board_size + self.PADDING
        self.panel_y = self.board_y
        self.panel_h = self.board_size

    # MAIN LOOP
    def run(self):
        while True:
            self.clock.tick(60)
            self.screen.fill((18, 28, 38))

            # ⏱️ CHỈ GỌI – KHÔNG CAN THIỆP
            self.game.update_time()

            self._create_buttons()
            result = self._handle_events()
            if result:
                return result

            self._ai_move()
            self._draw()

            pygame.display.flip()

    # BUTTONS
    def _create_buttons(self):
        y = self.panel_y + 40

        self.btn_restart = None
        if self.game.game_over:
            self.btn_restart = pygame.Rect(self.panel_x + 30, y, 200, 44)
            y += 65

        self.btn_undo = pygame.Rect(self.panel_x + 30, y, 200, 44)
        y += 55

        self.btn_redo = pygame.Rect(self.panel_x + 30, y, 200, 44)

        self.btn_home = pygame.Rect(
            self.panel_x + 30,
            self.panel_y + self.panel_h - 60,
            200,
            44
        )

    # EVENTS
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_home.collidepoint(event.pos):
                    return "HOME"

                if self.btn_restart and self.btn_restart.collidepoint(event.pos):
                    self._new_game()
                    return None

                if not self.game.game_over:
                    if self.btn_undo.collidepoint(event.pos):
                        self._handle_undo()
                        return None

                    if self.btn_redo.collidepoint(event.pos):
                        self.game.redo()
                        self.last_move = self.game.last_move
                        return None

                    self._handle_board_click(event.pos)

        return None

    # UNDO
    def _handle_undo(self):
        if self.mode == MODE_PVE:
            self.game.undo()
            self.game.undo()
        else:
            self.game.undo()

        self.last_move = self.game.last_move
        self.ai_thinking = False
        self.player_just_moved = False

    # BOARD CLICK
    def _handle_board_click(self, pos):
        mx, my = pos
        col = (mx - self.board_x) // self.cell_size
        row = (my - self.board_y) // self.cell_size

        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            if self.game.make_move(row, col):
                self.last_move = (row, col)
                self.player_just_moved = True

    # AI MOVE
    def _ai_move(self):
        # Frame ngay sau khi người chơi đánh → chỉ render
        if self.player_just_moved:
            self.player_just_moved = False
            return

        if self.mode != MODE_PVE or self.game.game_over:
            self.ai_thinking = False
            return

        if self.game.current_player != "O":
            self.ai_thinking = False
            return

        if not self.ai_thinking:
            self.ai_thinking = True
            self.ai_start_time = time.time()
            return

        if time.time() - self.ai_start_time < self.AI_THINK_DELAY:
            return

        if self.game.ai_move():
            self.last_move = self.game.last_move

        self.ai_thinking = False

    # DRAW
    def _draw(self):
        self._draw_hud()
        self._draw_board()
        self._draw_pieces()
        self._draw_panel()

    def _format_time(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def _draw_hud(self):
        pygame.draw.rect(
            self.screen,
            (15, 25, 35),
            (0, 0, SCREEN_WIDTH, self.HUD_HEIGHT)
        )

        self.screen.blit(
            self.font.render(
                f"X ⏱ {self._format_time(self.game.time_left['X'])}",
                True,
                (220, 230, 240)
            ),
            (20, 20)
        )

        self.screen.blit(
            self.big_font.render(
                f"Lượt: {self.game.current_player}",
                True,
                (220, 230, 240)
            ),
            (SCREEN_WIDTH // 2 - 70, 18)
        )

        self.screen.blit(
            self.font.render(
                f"O ⏱ {self._format_time(self.game.time_left['O'])}",
                True,
                (220, 230, 240)
            ),
            (SCREEN_WIDTH - 200, 20)
        )

    def _draw_board(self):
        pygame.draw.rect(
            self.screen,
            (24, 40, 56),
            (self.board_x, self.board_y, self.board_size, self.board_size),
            border_radius=10
        )

        for i in range(BOARD_ROWS + 1):
            pygame.draw.line(
                self.screen,
                (60, 80, 100),
                (self.board_x, self.board_y + i * self.cell_size),
                (self.board_x + self.board_size,
                 self.board_y + i * self.cell_size)
            )

        for i in range(BOARD_COLS + 1):
            pygame.draw.line(
                self.screen,
                (60, 80, 100),
                (self.board_x + i * self.cell_size, self.board_y),
                (self.board_x + i * self.cell_size,
                 self.board_y + self.board_size)
            )

    def _draw_pieces(self):
        win_cells = set(self.game.win_cells) if self.game.win_cells else set()

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = self.game.board.grid[r][c]
                if not piece:
                    continue

                cx = self.board_x + c * self.cell_size + self.cell_size // 2
                cy = self.board_y + r * self.cell_size + self.cell_size // 2
                radius = self.cell_size // 2 - 4

                color = (255, 90, 90) if piece == "X" else (60, 220, 180)
                pygame.draw.circle(self.screen, color, (cx, cy), radius)

                if self.last_move == (r, c):
                    pygame.draw.circle(
                        self.screen,
                        (255, 215, 0),
                        (cx, cy),
                        radius + 3,
                        2
                    )

                if (r, c) in win_cells:
                    pygame.draw.circle(
                        self.screen,
                        (255, 230, 150),
                        (cx, cy),
                        radius + 6,
                        3
                    )

    def _draw_panel(self):
        pygame.draw.rect(
            self.screen,
            (30, 45, 60),
            (self.panel_x, self.panel_y,
             self.SIDE_PANEL_WIDTH, self.panel_h),
            border_radius=12
        )

        if self.btn_restart:
            self._draw_button(self.btn_restart, "Chơi lại")

        self._draw_button(self.btn_undo, "Undo")
        self._draw_button(self.btn_redo, "Redo")
        self._draw_button(self.btn_home, "Trang chủ")

        if self.game.game_over:
            text = f"{self.game.winner} thắng!" if self.game.winner else "Hòa!"
            label = self.big_font.render(text, True, (220, 230, 240))
            self.screen.blit(label, (self.panel_x + 40, self.panel_y + 220))

    def _draw_button(self, rect, text):
        hover = rect.collidepoint(pygame.mouse.get_pos())
        color = (80, 140, 180) if hover else (50, 90, 120)

        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        label = self.font.render(text, True, (220, 230, 240))
        self.screen.blit(label, label.get_rect(center=rect.center))


def game_screen(screen, mode, ai_level=None):
    return GameScreen(screen, mode, ai_level).run()
