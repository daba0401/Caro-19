
import pygame


# BASIC HELPERS
def clamp(value, min_value, max_value):
    #Giới hạn value trong [min_value, max_value].
    return max(min_value, min(value, max_value))


def point_in_rect(point, rect: pygame.Rect):
    #Kiểm tra một điểm (x, y) có nằm trong rect không.
    x, y = point
    return rect.collidepoint(x, y)



# TEXT HELPERS
def draw_text_center(screen, text, font, color, center):
    #Vẽ text căn giữa tại vị trí center (x, y).
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)
    return rect


def draw_text(screen, text, font, color, topleft):

    #Vẽ text tại góc trên trái topleft (x, y).

    surf = font.render(text, True, color)
    rect = surf.get_rect(topleft=topleft)
    screen.blit(surf, rect)
    return rect


def wrap_text(text, font, max_width):

    #Tự xuống dòng cho text để không vượt quá max_width (pixel).
    words = text.split(" ")
    if not words:
        return [""]

    lines = []
    current = words[0]

    for w in words[1:]:
        test = current + " " + w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = w

    lines.append(current)
    return lines



# BUTTON HELPERS
def make_button_rect(screen_width, x_center, y, width, height):
    #Tạo rect của button theo tâm x.
    return pygame.Rect(
        x_center - width // 2,
        y,
        width,
        height
    )


def draw_button(
    screen,
    rect: pygame.Rect,
    text,
    font,
    text_color,
    normal_color,
    hover_color,
    mouse_pos,
    border_radius=0
):

    is_hover = rect.collidepoint(mouse_pos)
    color = hover_color if is_hover else normal_color

    pygame.draw.rect(screen, color, rect, border_radius=border_radius)
    draw_text_center(screen, text, font, text_color, rect.center)

    return is_hover



# BOARD COORDINATE HELPERS

def mouse_to_cell(mouse_pos, board_margin, cell_size, rows, cols):

    #Chuyển tọa độ chuột (x, y) -> (row, col) trên bàn cờ.

    x, y = mouse_pos

    x -= board_margin
    y -= board_margin

    if x < 0 or y < 0:
        return None, None

    col = x // cell_size
    row = y // cell_size

    if 0 <= row < rows and 0 <= col < cols:
        return int(row), int(col)

    return None, None


def cell_to_pixel(row, col, board_margin, cell_size):

    #Chuyển (row, col) -> tọa độ pixel góc trên-trái của ô.
    x = board_margin + col * cell_size
    y = board_margin + row * cell_size
    return x, y
