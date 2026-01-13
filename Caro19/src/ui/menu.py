
import pygame

from config.ui_config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BACKGROUND_COLOR,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    TEXT_COLOR,
    FONT_NAME,
    FONT_SIZE_TITLE,
    FONT_SIZE_BUTTON,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_BORDER_RADIUS,
    MENU_START_Y,
    MENU_GAP
)

from src.core.constants import (
    ACTION_PLAY,
    ACTION_GUIDE,
    ACTION_EXIT
)


def draw_button(screen, rect, text, font, mouse_pos):
    """Vẽ nút bấm"""
    color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=BUTTON_BORDER_RADIUS)

    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


def main_menu(screen):
    """
    Hiển thị menu chính
    Trả về: ACTION_PLAY / ACTION_GUIDE / ACTION_EXIT
    """

    clock = pygame.time.Clock()

    # Fonts
    title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
    button_font = pygame.font.Font(FONT_NAME, FONT_SIZE_BUTTON)

    # Title
    title_surf = title_font.render("CARO19", True, TEXT_COLOR)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))

    # Buttons
    buttons = [
        (ACTION_PLAY, "Chơi"),
        (ACTION_GUIDE, "Hướng dẫn"),
        (ACTION_EXIT, "Thoát game"),
    ]

    button_rects = []
    start_y = MENU_START_Y

    for i, (_, text) in enumerate(buttons):
        rect = pygame.Rect(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
            start_y + i * MENU_GAP,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )
        button_rects.append(rect)

    # Loop menu
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BACKGROUND_COLOR)

        # Draw title
        screen.blit(title_surf, title_rect)

        # Draw buttons
        for i, rect in enumerate(button_rects):
            draw_button(
                screen,
                rect,
                buttons[i][1],
                button_font,
                mouse_pos
            )

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ACTION_EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    for i, rect in enumerate(button_rects):
                        if rect.collidepoint(event.pos):
                            return buttons[i][0]
