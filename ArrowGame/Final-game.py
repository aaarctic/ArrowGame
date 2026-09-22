import pygame
import sys
import os
import math

# ============================================================
# 基础设置
# ============================================================

WIDTH = 1280
HEIGHT = 880  # 调整高度，确保所有元素可见

pygame.init()
pygame.display.set_caption("一箭又一箭")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ============================================================
# 颜色
# ============================================================

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

# ============================================================
# 字体
# ============================================================

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

FONT_TITLE = make_font(58, True)
FONT_BIG = make_font(38, True)
FONT_H1 = make_font(30, True)
FONT_BODY = make_font(22)
FONT_SMALL = make_font(18)
FONT_TINY = make_font(16)

# ============================================================
# 游戏方向
# ============================================================

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# ============================================================
# 关卡数据（已重新设计，确保可解）
# ============================================================
LEVELS = [
    {
        "name": "入门练习", "count": 7, "time": 90,
        "arrows": [(0, 0, 1), (5, 0, 2), (2, 1, 0), (0, 2, 1), (2, 3, 0), (4, 4, 3), (5, 5, 2)]
    },
    {
        "name": "简单挑战", "count": 8, "time": 80,
        "arrows": [(1, 0, 2), (4, 0, 3), (0, 1, 1), (2, 1, 0), (5, 2, 2), (3, 3, 1), (1, 4, 0), (4, 5, 3)]
    },
    {
        "name": "中等难度", "count": 8, "time": 75,
        "arrows": [(0, 0, 2), (5, 0, 2), (2, 1, 1), (3, 2, 0), (1, 3, 1), (4, 3, 3), (2, 4, 2), (5, 5, 3)]
    },
    {
        "name": "困难模式", "count": 12, "time": 70,
        "arrows": [(0, 0, 2), (2, 0, 1), (5, 0, 2), (1, 1, 1), (4, 1, 3), (3, 2, 0), (0, 3, 1), (2, 3, 2), (5, 3, 3), (1, 5, 0), (3, 5, 1), (5, 5, 3)]
    },
    {
        "name": "终极挑战", "count": 10, "time": 75,
        # 外圈四角朝外；内圈四个箭头朝外但被外圈挡住；中心两个箭头自由
        "arrows": [
            (0, 0, 0),  # 左上 → 上（外圈，第一步可飞出）
            (0, 5, 3),  # 右上 ← 左（外圈，第一步可飞出）
            (5, 0, 2),  # 左下 ↓ 下（外圈，第一步可飞出）
            (5, 5, 2),  # 右下 ↓ 下（外圈，第一步可飞出）
            (2, 2, 1),  # 中心 → 右（前方同排无阻挡，随时可飞出）
            (3, 3, 3),  # 中心 ← 左（前方同排无阻挡，随时可飞出）
            (1, 1, 3),  # 内圈 ← 左，被 (1, 0) 挡住，外圈清掉后可飞出
            (1, 4, 1),  # 内圈 → 右，被 (1, 5) 挡住，外圈清掉后可飞出
            (4, 1, 3),  # 内圈 ← 左，被 (4, 0) 挡住，外圈清掉后可飞出
            (4, 4, 1),  # 内圈 → 右，被 (4, 5) 挡住，外圈清掉后可飞出
        ]
    }
]


# ============================================================
# 全局状态
# ============================================================

screen_name = "home"
selected_level = 0
game_arrows = []
mistakes = 3
start_time = 0
time_limit = 90
feedback = ""
feedback_until = 0
animating = []
last_success_cell = None
last_fail_cell = None
result_win = False
last_score = 0

# ============================================================
# 工具函数
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))

def draw_text(text, fnt, color, center, surface=screen):
    image = fnt.render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)
    return rect

# ============================================================
# 按钮
# ============================================================

def draw_button(rect, text, color, text_color=WHITE, hover_color=None):
    mouse = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse)
    draw_color = color
    if hovered and hover_color:
        draw_color = hover_color

    shadow_rect = rect.move(0, 7)
    pygame.draw.rect(screen, SHADOW, shadow_rect, border_radius=18)
    pygame.draw.rect(screen, draw_color, rect, border_radius=18)

    highlight = pygame.Rect(rect.x + 8, rect.y + 5, rect.w - 16, 4)
    pygame.draw.rect(screen, WHITE, highlight, border_radius=3)

    draw_text(text, FONT_H1, text_color, rect.center)
    return hovered

# ============================================================
# 背景装饰
# ============================================================

def draw_decorations():
    pygame.draw.circle(screen, (255, 226, 207), (95, 110), 48)
    pygame.draw.circle(screen, (234, 220, 250), (1185, 105), 52)
    pygame.draw.circle(screen, (255, 225, 236), (92, 680), 58)
    pygame.draw.circle(screen, (255, 232, 190), (1185, 680), 55)

    stars = [(190, 95, YELLOW), (1090, 130, PURPLE), (170, 625, GREEN), (1080, 610, RED)]
    for x, y, color in stars:
        points = [
            (x, y - 10), (x + 3, y - 3), (x + 11, y - 3), (x + 5, y + 2),
            (x + 8, y + 10), (x, y + 5), (x - 8, y + 10), (x - 5, y + 2),
            (x - 11, y - 3), (x - 3, y - 3)
        ]
        pygame.draw.polygon(screen, color, points)

# ============================================================
# 箭头绘制
# ============================================================

def draw_arrow(cx, cy, direction, color=YELLOW, scale=1.0, alpha=255):
    size = int(110 * scale)
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2

    shaft_width = max(8, int(13 * scale))
    head = max(20, int(34 * scale))
    shaft_length = max(28, int(45 * scale))

    if direction == 0:  # 上
        shaft = pygame.Rect(center - shaft_width // 2, center - 5, shaft_width, shaft_length)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center, center - head), (center - head + 4, center), (center + head - 4, center)]
        pygame.draw.polygon(surface, (*color, alpha), points)

    elif direction == 1:  # 右
        shaft = pygame.Rect(center - shaft_length, center - shaft_width // 2, shaft_length, shaft_width)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center + head, center), (center, center - head + 4), (center, center + head - 4)]
        pygame.draw.polygon(surface, (*color, alpha), points)

    elif direction == 2:  # 下
        shaft = pygame.Rect(center - shaft_width // 2, center - shaft_length, shaft_width, shaft_length)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center, center + head), (center - head + 4, center), (center + head - 4, center)]
        pygame.draw.polygon(surface, (*color, alpha), points)

    else:  # 左
        shaft = pygame.Rect(center, center - shaft_width // 2, shaft_length, shaft_width)
        pygame.draw.rect(surface, (*color, alpha), shaft, border_radius=5)
        points = [(center - head, center), (center, center - head + 4), (center, center + head - 4)]
        pygame.draw.polygon(surface, (*color, alpha), points)

    screen.blit(surface, (int(cx - size / 2), int(cy - size / 2)))

# ============================================================
# 游戏棋盘
# ============================================================

def draw_board(arrows, success_cell=None, fail_cell=None, shake=0):
    rows = 6
    cols = 6
    cell = 78
    gap = 12

    board_width = cols * cell + (cols - 1) * gap + 40
    board_height = rows * cell + (rows - 1) * gap + 40

    bx = (WIDTH - board_width) // 2 + shake
    by = 180  # 调整棋盘纵向位置

    pygame.draw.rect(screen, SHADOW, (bx, by + 10, board_width, board_height), border_radius=28)
    pygame.draw.rect(screen, BOARD, (bx, by, board_width, board_height), border_radius=28)

    arrow_map = {}
    for r, c, d in arrows:
        arrow_map[(r, c)] = d

    for r in range(rows):
        for c in range(cols):
            x = bx + 20 + c * (cell + gap)
            y = by + 20 + r * (cell + gap)
            rect = pygame.Rect(x, y, cell, cell)

            fill = CELL
            edge = CELL_EDGE

            if success_cell == (r, c):
                fill = GREEN
                edge = GREEN
            if fail_cell == (r, c):
                fill = RED
                edge = RED

            pygame.draw.rect(screen, fill, rect, border_radius=16)
            pygame.draw.rect(screen, edge, rect, 2, border_radius=16)

            if (r, c) in arrow_map:
                draw_arrow(rect.centerx, rect.centery, arrow_map[(r, c)], YELLOW, 0.78)

    return bx, by, cell, gap

# ============================================================
# 逻辑判断
# ============================================================

def is_clear(r, c, direction, arrow_map):
    dx, dy = DIRS[direction]
    current_c = c + dx
    current_r = r + dy

    while 0 <= current_r < 6 and 0 <= current_c < 6:
        if (current_r, current_c) in arrow_map:
            return False
        current_c += dx
        current_r += dy
    return True

def reset_game(level_index):
    global game_arrows, mistakes, start_time, time_limit, feedback, feedback_until, animating, last_success_cell, last_fail_cell
    data = LEVELS[level_index]
    game_arrows = list(data["arrows"])
    mistakes = 3
    time_limit = data["time"]
    start_time = pygame.time.get_ticks()
    feedback = ""
    feedback_until = 0
    animating = []
    last_success_cell = None
    last_fail_cell = None

def remaining_time():
    elapsed = (pygame.time.get_ticks() - start_time) / 1000
    return max(0, time_limit - elapsed)

def finish(win):
    global screen_name, result_win, last_score
    result_win = win
    elapsed = time_limit - remaining_time()
    arrow_count = len(LEVELS[selected_level]["arrows"])
    last_score = max(0, int(arrow_count * 100 - elapsed * 2 + mistakes * 50))
    screen_name = "result"

# ============================================================
# 页面绘制
# ============================================================

def draw_home():
    screen.fill(BG)
    draw_decorations()

    title_box = pygame.Rect(280, 70, 720, 150)
    pygame.draw.rect(screen, PANEL, title_box, border_radius=28)
    pygame.draw.rect(screen, (248, 208, 226), title_box, 3, border_radius=28)

    draw_text("一箭又一箭", FONT_TITLE, INK, (WIDTH // 2, 120))
    draw_text("观察方向 · 规划顺序 · 清空所有箭头", FONT_BODY, (194, 87, 123), (WIDTH // 2, 184))

    left = pygame.Rect(120, 275, 470, 180)
    pygame.draw.rect(screen, PANEL, left, border_radius=24)
    pygame.draw.rect(screen, (240, 228, 238), left, 2, border_radius=24)
    draw_text("怎么玩？", FONT_H1, PURPLE_DARK, (left.x + 85, left.y + 45))
    draw_text("点击可以飞出的箭头", FONT_BODY, INK, left.center)
    draw_text("前方无阻挡 → 箭头飞出", FONT_BODY, MUTED, (left.centerx, left.y + 130))

    right = pygame.Rect(690, 275, 470, 180)
    pygame.draw.rect(screen, PANEL, right, border_radius=24)
    pygame.draw.rect(screen, (240, 228, 238), right, 2, border_radius=24)
    draw_text("挑战目标", FONT_H1, PURPLE_DARK, (right.x + 90, right.y + 45))
    draw_text("清空棋盘上的全部箭头", FONT_BODY, INK, (right.centerx, right.y + 90))
    draw_text("3 次失误 · 限时挑战", FONT_BODY, MUTED, (right.centerx, right.y + 130))

    start_button = pygame.Rect(470, 505, 340, 66)
    select_button = pygame.Rect(470, 595, 340, 58)
    rule_button = pygame.Rect(150, 585, 250, 58)
    help_button = pygame.Rect(880, 585, 250, 58)

    draw_button(start_button, "开始游戏", (238, 92, 135), hover_color=(247, 112, 153))
    draw_button(select_button, "选择关卡", (155, 111, 232), hover_color=(174, 132, 242))
    draw_button(rule_button, "游戏规则", (255, 170, 91), hover_color=(255, 187, 112))
    draw_button(help_button, "操作提示", (255, 205, 84), text_color=INK, hover_color=(255, 217, 112))

    draw_text("共 5 个关卡 · 每关都有时间挑战", FONT_SMALL, MUTED, (WIDTH // 2, 720))
    return start_button, select_button, rule_button, help_button

def draw_select():
    screen.fill(BG)
    draw_decorations()
    draw_text("选择关卡", FONT_TITLE, PURPLE_DARK, (WIDTH // 2, 85))
    draw_text("选择一个关卡开始挑战", FONT_BODY, MUTED, (WIDTH // 2, 135))

    card_width, card_height, gap = 190, 300, 25
    total_width = 5 * card_width + 4 * gap
    start_x = (WIDTH - total_width) // 2
    rects = []

    for i, data in enumerate(LEVELS):
        x = start_x + i * (card_width + gap)
        y = 220
        rect = pygame.Rect(x, y, card_width, card_height)
        rects.append(rect)
        hovered = rect.collidepoint(pygame.mouse.get_pos())

        pygame.draw.rect(screen, SHADOW, rect.move(0, 8), border_radius=24)
        pygame.draw.rect(screen, PANEL, rect, border_radius=24)
        pygame.draw.rect(screen, PURPLE if hovered else (214, 192, 235), rect, 3, border_radius=24)

        pygame.draw.circle(screen, PURPLE, (rect.centerx, y + 58), 34)
        draw_text(str(i + 1), FONT_H1, WHITE, (rect.centerx, y + 58))
        draw_text(f"第 {i + 1} 关", FONT_H1, PURPLE_DARK, (rect.centerx, y + 118))
        draw_text(data["name"], FONT_SMALL, PURPLE, (rect.centerx, y + 155))
        draw_text(f"{data['count']} 个箭头", FONT_SMALL, INK, (rect.centerx, y + 205))
        draw_text(f"{data['time']} 秒", FONT_SMALL, MUTED, (rect.centerx, y + 245))
        draw_text("点击挑战", FONT_SMALL, PURPLE, (rect.centerx, y + 278))

    back_button = pygame.Rect(515, 620, 250, 58)
    draw_button(back_button, "返回主页", PURPLE, hover_color=(174, 132, 242))
    return rects, back_button

def draw_help():
    screen.fill(BG)
    draw_decorations()
    draw_text("怎么玩？", FONT_TITLE, PURPLE_DARK, (WIDTH // 2, 95))

    panel = pygame.Rect(250, 180, 780, 410)
    pygame.draw.rect(screen, PANEL, panel, border_radius=28)
    pygame.draw.rect(screen, (232, 220, 238), panel, 2, border_radius=28)

    lines = [
        "① 点击一个箭头",
        "② 箭头正前方没有其他箭头时，可以飞出",
        "③ 前方被挡住：本次点击算一次失误",
        "④ 失误会扣除机会，并给出红色反馈",
        "⑤ 箭头成功飞出，会有绿色反馈和飞行动画",
        "⑥ 清空全部箭头即可通关",
        "⑦ 倒计时结束或 3 次失误用完，则挑战失败"
    ]

    for i, line in enumerate(lines):
        draw_text(line, FONT_BODY, INK, (WIDTH // 2, 230 + i * 45))

    back_button = pygame.Rect(515, 625, 250, 58)
    draw_button(back_button, "返回", PURPLE, hover_color=(174, 132, 242))
    return back_button

def draw_game():
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 160))
    pygame.draw.line(screen, (232, 220, 238), (0, 159), (WIDTH, 159), 2)

    data = LEVELS[selected_level]
    draw_text("一箭又一箭", FONT_BIG, INK, (170, 50))
    draw_text(f"第 {selected_level + 1} 关 · {data['name']}", FONT_H1, PURPLE, (180, 105))
    
    draw_text("剩余箭头", FONT_SMALL, MUTED, (510, 40))
    draw_text(str(len(game_arrows)), FONT_BIG, INK, (510, 85))
    
    draw_text("剩余失误", FONT_SMALL, MUTED, (690, 40))
    draw_text(str(mistakes), FONT_BIG, RED if mistakes <= 1 else INK, (690, 85))

    current_time = remaining_time()
    draw_text("剩余时间", FONT_SMALL, MUTED, (875, 40))
    draw_text(f"{math.ceil(current_time)}s", FONT_BIG, PURPLE if current_time > 10 else RED, (875, 85))

    # 时间条
    bar = pygame.Rect(980, 50, 150, 18)
    pygame.draw.rect(screen, (237, 226, 239), bar, border_radius=9)
    ratio = current_time / time_limit if time_limit > 0 else 0
    pygame.draw.rect(screen, RED if ratio < 0.2 else PURPLE, (bar.x, bar.y, int(bar.w * ratio), bar.h), border_radius=9)

    # 重来按钮移动到右上角，避免被遮挡
    restart_button = pygame.Rect(1160, 40, 100, 50)
    draw_button(restart_button, "重来", (224, 213, 246), text_color=PURPLE_DARK, hover_color=(236, 226, 252))

    shake = 0
    now = pygame.time.get_ticks()
    if feedback_until > now and feedback == "blocked":
        shake = int(math.sin(now / 35) * 5)

    success_cell = None
    fail_cell = None
    if feedback == "success" and feedback_until > now:
        success_cell = last_success_cell
    if feedback == "blocked" and feedback_until > now:
        fail_cell = last_fail_cell

    bx, by, cell, gap = draw_board(game_arrows, success_cell=success_cell, fail_cell=fail_cell, shake=shake)

    still_animating = []
    for (ar, ac, ad, started) in animating:
        progress = (now - started) / 520.0
        if progress < 1:
            progress = clamp(progress, 0, 1)
            ease = 1 - (1 - progress) ** 3
            start_x = bx + 20 + ac * (cell + gap) + cell / 2
            start_y = by + 20 + ar * (cell + gap) + cell / 2
            dx, dy = DIRS[ad]
            end_x = start_x + dx * 170
            end_y = start_y + dy * 170
            arrow_x = start_x + (end_x - start_x) * ease
            arrow_y = start_y + (end_y - start_y) * ease
            draw_arrow(arrow_x, arrow_y, ad, GREEN, 0.78 * (1 - 0.25 * progress), int(255 * (1 - progress)))
            still_animating.append((ar, ac, ad, started))
    animating[:] = still_animating

    # 底部提示文字
    if feedback_until > now:
        if feedback == "success":
            draw_text("✓ 成功！箭头飞出", FONT_H1, GREEN, (WIDTH // 2, 810))
        elif feedback == "blocked":
            draw_text("× 前方有箭头，无法飞出！", FONT_H1, RED, (WIDTH // 2, 810))
        elif feedback == "empty":
            draw_text("这里没有箭头", FONT_H1, MUTED, (WIDTH // 2, 810))
    else:
        draw_text("观察箭头方向，优先点击前方没有阻挡的箭头", FONT_SMALL, MUTED, (WIDTH // 2, 810))

    return restart_button

def draw_result():
    screen.fill(BG)
    draw_decorations()
    box = pygame.Rect(300, 125, 680, 470)
    pygame.draw.rect(screen, PANEL, box, border_radius=30)
    pygame.draw.rect(screen, (232, 220, 238), box, 2, border_radius=30)

    if result_win:
        draw_text("挑战成功！", FONT_TITLE, GREEN, (WIDTH // 2, 205))
        draw_text("太棒了，你清空了全部箭头", FONT_BODY, INK, (WIDTH // 2, 265))
    else:
        draw_text("挑战失败", FONT_TITLE, RED, (WIDTH // 2, 205))
        reason = "失误次数已经用完" if mistakes <= 0 else "时间已经用完"
        draw_text(reason, FONT_BODY, INK, (WIDTH // 2, 265))

    draw_text(f"第 {selected_level + 1} 关", FONT_H1, PURPLE, (WIDTH // 2, 335))
    draw_text(f"本次得分：{last_score}", FONT_BIG, INK, (WIDTH // 2, 395))

    again_button = pygame.Rect(400, 465, 210, 58)
    select_button = pygame.Rect(670, 465, 210, 58)
    home_button = pygame.Rect(515, 540, 250, 58)

    draw_button(again_button, "再玩一次", (238, 92, 135), hover_color=(247, 112, 153))
    draw_button(select_button, "选择关卡", PURPLE, hover_color=(174, 132, 242))
    draw_button(home_button, "返回主页", (224, 213, 246), text_color=PURPLE_DARK, hover_color=(236, 226, 252))
    return again_button, select_button, home_button

# ============================================================
# 鼠标与逻辑
# ============================================================

def cell_from_mouse(mx, my, bx, by, cell, gap):
    for r in range(6):
        for c in range(6):
            rect = pygame.Rect(bx + 20 + c * (cell + gap), by + 20 + r * (cell + gap), cell, cell)
            if rect.collidepoint(mx, my):
                return r, c
    return None

def try_click(cell):
    global game_arrows, mistakes, feedback, feedback_until, animating, last_success_cell, last_fail_cell
    if cell is None: return
    r, c = cell
    arrow_map = {(rr, cc): dd for rr, cc, dd in game_arrows}

    if cell not in arrow_map:
        feedback = "empty"
        feedback_until = pygame.time.get_ticks() + 650
        last_success_cell = None
        last_fail_cell = None
        return

    direction = arrow_map[cell]
    if is_clear(r, c, direction, arrow_map):
        game_arrows = [(rr, cc, dd) for rr, cc, dd in game_arrows if (rr, cc) != cell]
        feedback = "success"
        feedback_until = pygame.time.get_ticks() + 750
        last_success_cell = cell
        last_fail_cell = None
        animating.append((r, c, direction, pygame.time.get_ticks()))
    else:
        mistakes -= 1
        feedback = "blocked"
        feedback_until = pygame.time.get_ticks() + 800
        last_fail_cell = cell
        last_success_cell = None

# ============================================================
# 主循环（专为 Jupyter 优化）
# ============================================================

running = True
while running:
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if screen_name == "game":
                    screen_name = "home"
                elif screen_name != "home":
                    screen_name = "home"
            elif screen_name == "home" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                selected_level = 0
                reset_game(selected_level)
                screen_name = "game"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if screen_name == "home":
                start_button, select_button, rule_button, help_button = draw_home()
                if start_button.collidepoint(mx, my):
                    selected_level = 0
                    reset_game(selected_level)
                    screen_name = "game"
                elif select_button.collidepoint(mx, my):
                    screen_name = "select"
                elif rule_button.collidepoint(mx, my) or help_button.collidepoint(mx, my):
                    screen_name = "help"

            elif screen_name == "select":
                level_rects, back_button = draw_select()
                for i, rect in enumerate(level_rects):
                    if rect.collidepoint(mx, my):
                        selected_level = i
                        reset_game(selected_level)
                        screen_name = "game"
                        break
                if back_button.collidepoint(mx, my):
                    screen_name = "home"

            elif screen_name == "help":
                back_button = draw_help()
                if back_button.collidepoint(mx, my):
                    screen_name = "home"

            elif screen_name == "game":
                restart_button = draw_game()
                if restart_button.collidepoint(mx, my):
                    reset_game(selected_level)
                else:
                    bx, by, cell_size, gap = draw_board(game_arrows)
                    target_cell = cell_from_mouse(mx, my, bx, by, cell_size, gap)
                    try_click(target_cell)

            elif screen_name == "result":
                again_button, select_button, home_button = draw_result()
                if again_button.collidepoint(mx, my):
                    reset_game(selected_level)
                    screen_name = "game"
                elif select_button.collidepoint(mx, my):
                    screen_name = "select"
                elif home_button.collidepoint(mx, my):
                    screen_name = "home"

    if screen_name == "game":
        if not game_arrows:
            if feedback_until < now - 100:
                finish(True)
        elif mistakes <= 0:
            finish(False)
        elif remaining_time() <= 0:
            finish(False)

    if screen_name == "home":
        draw_home()
    elif screen_name == "select":
        draw_select()
    elif screen_name == "help":
        draw_help()
    elif screen_name == "game":
        draw_game()
    elif screen_name == "result":
        draw_result()

    pygame.display.flip()
    clock.tick(60)

# 在 Jupyter 中不直接调用 sys.exit()，而是 pygame.quit()
pygame.quit()