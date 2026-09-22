# logic.py
from config import DIRS


def is_clear(r, c, direction, arrow_map):
    """判断 (r, c) 的箭头沿 direction 方向能否飞出棋盘。"""
    dx, dy = DIRS[direction]
    current_c = c + dx
    current_r = r + dy

    while 0 <= current_r < 6 and 0 <= current_c < 6:
        if (current_r, current_c) in arrow_map:
            return False
        current_c += dx
        current_r += dy
    return True