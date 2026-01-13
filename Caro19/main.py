import sys
import pygame

from config.ui_config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WINDOW_TITLE,
)

from src.core.constants import (
    ACTION_PLAY,
    ACTION_GUIDE,
    ACTION_EXIT,
    ACTION_PVP,
    ACTION_PVE,
    ACTION_EASY,
    ACTION_NORMAL,
    ACTION_HARD,
)

from src.ui.menu import main_menu
from src.ui.play_menu import play_menu
from src.ui.difficulty_menu import difficulty_menu
from src.ui.guide import show_guide
from src.ui.game_screen import game_screen


def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    return screen, clock


def main():
    screen, clock = init_pygame()
    running = True

    while running:
        clock.tick(FPS)

        action = main_menu(screen)

        if action == ACTION_PLAY:
            mode = play_menu(screen)

            if mode == ACTION_PVP:
                result = game_screen(screen, mode=ACTION_PVP)
                if result == "QUIT":
                    running = False

            elif mode == ACTION_PVE:
                level = difficulty_menu(screen)
                if level in (ACTION_EASY, ACTION_NORMAL, ACTION_HARD):
                    result = game_screen(
                        screen,
                        mode=ACTION_PVE,
                        ai_level=level
                    )
                    if result == "QUIT":
                        running = False

        elif action == ACTION_GUIDE:
            show_guide(screen)

        elif action == ACTION_EXIT:
            running = False

    pygame.quit()
    sys.exit()


# 🚨 DÒNG NÀY BẮT BUỘC PHẢI CÓ
if __name__ == "__main__":
    main()
