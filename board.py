# board.py
import pygame
from config import (screen, WIDTH, SHADOW, BOARD, CELL, CELL_EDGE,
                    YELLOW, GREEN, RED)
from draw import draw_arrow


def draw_board(arrows, success_cell=None, fail_cell=None, shake=0):
    rows, cols = 6, 6
    cell, gap = 78, 12

    board_width = cols * cell + (cols - 1) * gap + 40
    board_height = rows * cell + (rows - 1) * gap + 40
    bx = (WIDTH - board_width) // 2 + shake
    by = 180

    pygame.draw.rect(screen, SHADOW,
                     (bx, by + 10, board_width, board_height),
                     border_radius=28)
    pygame.draw.rect(screen, BOARD,
                     (bx, by, board_width, board_height),
                     border_radius=28)

    arrow_map = {(r, c): d for r, c, d in arrows}

    for r in range(rows):
        for c in range(cols):
            x = bx + 20 + c * (cell + gap)
            y = by + 20 + r * (cell + gap)
            rect = pygame.Rect(x, y, cell, cell)

            fill, edge = CELL, CELL_EDGE
            if success_cell == (r, c):
                fill, edge = GREEN, GREEN
            if fail_cell == (r, c):
                fill, edge = RED, RED

            pygame.draw.rect(screen, fill, rect, border_radius=16)
            pygame.draw.rect(screen, edge, rect, 2, border_radius=16)

            if (r, c) in arrow_map:
                draw_arrow(rect.centerx, rect.centery,
                           arrow_map[(r, c)], YELLOW, 0.78)

    return bx, by, cell, gap


def cell_from_mouse(mx, my, bx, by, cell, gap):
    for r in range(6):
        for c in range(6):
            rect = pygame.Rect(bx + 20 + c * (cell + gap),
                               by + 20 + r * (cell + gap),
                               cell, cell)
            if rect.collidepoint(mx, my):
                return r, c
    return None