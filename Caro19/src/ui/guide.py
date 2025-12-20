"""
Guide screen for Caro19
Màn hình hướng dẫn chơi
"""

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
    FONT_SIZE_TEXT,
    FONT_SIZE_BUTTON,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_BORDER_RADIUS
)

from src.core.constants import ACTION_EXIT


def draw_button(screen, rect, text, font, mouse_pos):
    """Vẽ nút bấm"""
    color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=BUTTON_BORDER_RADIUS)

    text_surf = font.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


def show_guide(screen):
    """
    Hiển thị màn hình hướng dẫn
    Nhấn 'Quay lại' để trở về menu chính
    """

    clock = pygame.time.Clock()

    title_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TITLE)
    text_font = pygame.font.Font(FONT_NAME, FONT_SIZE_TEXT)
    button_font = pygame.font.Font(FONT_NAME, FONT_SIZE_BUTTON)

    # ===== TITLE =====
    title_surf = title_font.render("HƯỚNG DẪN CHƠI", True, TEXT_COLOR)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))

    # ===== GUIDE CONTENT =====
    guide_text = [
        "LUẬT CHƠI:",
        "- Bàn cờ gồm 15 x 15 ô.",
        "- Hai bên X và O sẽ đánh ô màu Đỏ và Xanh.",
        "- Bên nào tạo được 5 quân liên tiếp",
        "  theo hàng ngang, hàng dọc hoặc đường chéo",
        "  sẽ giành chiến thắng.",
        "- Mỗi bên có 5 phút để chơi.",
        "",
        "CHẾ ĐỘ CHƠI:",
        "- Người vs Người.",
        "- Người vs Máy (3 mức độ khó).",
        "",
        "ĐIỀU KHIỂN:",
        "- Chuột trái: Đặt quân cờ.",
        "- Undo: Quay lại nước đi trước.",
        "- Redo: Thực hiện lại nước vừa Undo.",
        "- Chơi lại: Bắt đầu ván mới sau khi kết thúc.",
        "- Trang chủ: Quay về menu chính.",
    ]

    text_surfaces = [
        text_font.render(line, True, TEXT_COLOR)
        for line in guide_text
    ]

    #BUTTON "QUAY LẠI"
    button_rect = pygame.Rect(
        (SCREEN_WIDTH - BUTTON_WIDTH) // 2,
        SCREEN_HEIGHT - 120,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    #LOOP
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BACKGROUND_COLOR)

        # Draw title
        screen.blit(title_surf, title_rect)

        # Draw guide text
        start_y = 150
        line_gap = 28
        for i, surf in enumerate(text_surfaces):
            screen.blit(
                surf,
                (
                    SCREEN_WIDTH // 2 - surf.get_width() // 2,
                    start_y + i * line_gap
                )
            )

        # Draw back button
        draw_button(screen, button_rect, "Quay lại", button_font, mouse_pos)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ACTION_EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and button_rect.collidepoint(event.pos):
                    return ACTION_EXIT
