# config.py
import pygame
import os

WIDTH = 1280
HEIGHT = 880

BG = (255, 248, 241)
PANEL = (255, 255, 255)
INK = (63, 51, 67)
MUTED = (125, 113, 128)
PURPLE = (142, 94, 235)
PURPLE_DARK = (109, 68, 194)
PURPLE_LIGHT = (235, 221, 255)
YELLOW = (255, 190, 70)
RED = (235, 91, 118)
RED_LIGHT = (255, 225, 232)
GREEN = (62, 196, 126)
GREEN_LIGHT = (221, 249, 235)
BOARD = (73, 61, 79)
CELL = (92, 79, 99)
CELL_EDGE = (119, 104, 127)
WHITE = (255, 255, 255)
SHADOW = (218, 205, 216)

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def find_font():
    fonts = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\Deng.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in fonts:
        if os.path.exists(path):
            return path
    return None


FONT_PATH = find_font()


def make_font(size, bold=False):
    if FONT_PATH:
        return pygame.font.Font(FONT_PATH, size)
    return pygame.font.SysFont("arial", size, bold=bold)