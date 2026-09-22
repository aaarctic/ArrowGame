# draw.py
import pygame
from config import (screen, YELLOW, WHITE, SHADOW, BOARD, CELL,
                    CELL_EDGE, FONT_H1, FONT_TITLE, FONT_BODY,
                    FONT_SMALL, PURPLE, PURPLE_DARK, GREEN, RED)


def draw_text(text, fnt, color, center, surface=screen):
    image = fnt.render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)
    return rect


def draw_button(rect, text, color, text_color=WHITE, hover_color=None):
    mouse = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse)
    draw_color = hover_color if (hovered and hover_color) else color

    pygame.draw.rect(screen, SHADOW, rect.move(0, 7), border_radius=18)
    pygame.draw.rect(screen, draw_color, rect, border_radius=18)
    pygame.draw.rect(screen, WHITE,
                     pygame.Rect(rect.x + 8, rect.y + 5, rect.w - 16, 4),
                     border_radius=3)
    draw_text(text, FONT_H1, text_color, rect.center)
    return hovered


def draw_arrow(cx, cy, direction, color=YELLOW, scale=1.0, alpha=255):
    size = int(110 * scale)
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    shaft_width = max(8, int(13 * scale))
    head = max(20, int(34 * scale))
    shaft_length = max(28, int(45 * scale))

    if direction == 0:
        shaft = pygame.Rect(center - shaft_width // 2, center - 5,
                            shaft_width, shaft_length)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center, center - head),
                  (center - head + 4, center),
                  (center + head - 4, center)]
        pygame.draw.polygon(surface, (*color, alpha), points)
    elif direction == 1:
        shaft = pygame.Rect(center - shaft_length, center - shaft_width // 2,
                            shaft_length, shaft_width)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center + head, center),
                  (center, center - head + 4),
                  (center, center + head - 4)]
        pygame.draw.polygon(surface, (*color, alpha), points)
    elif direction == 2:
        shaft = pygame.Rect(center - shaft_width // 2, center - shaft_length,
                            shaft_width, shaft_length)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center, center + head),
                  (center - head + 4, center),
                  (center + head - 4, center)]
        pygame.draw.polygon(surface, (*color, alpha), points)
    else:
        shaft = pygame.Rect(center, center - shaft_width // 2,
                            shaft_length, shaft_width)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center - head, center),
                  (center, center - head + 4),
                  (center, center + head - 4)]
        pygame.draw.polygon(surface, (*color, alpha), points)

    screen.blit(surface, (int(cx - size / 2), int(cy - size / 2)))