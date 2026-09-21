import pygame
import sys
import math
import random
import os

# ============================================================
# 一箭又一箭
# 软件工程课程第二次个人作业
# Python + Pygame 增强交互版
# ============================================================

pygame.init()

# ============================================================
# 1. 基本设置
# ============================================================

WIDTH = 1100
HEIGHT = 760

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭 - AIGC辅助开发小游戏")

CLOCK = pygame.time.Clock()
FPS = 60


# ============================================================
# 2. 字体
# ============================================================

FONT_PATHS = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]

FONT_PATH = None

for path in FONT_PATHS:
    if os.path.exists(path):
        FONT_PATH = path
        break


def get_font(size, bold=False):
    if FONT_PATH:
        return pygame.font.Font(FONT_PATH, size)

    return pygame.font.SysFont(
        "Microsoft YaHei",
        size,
        bold=bold
    )


FONT_TITLE = get_font(46, True)
FONT_BIG = get_font(34, True)
FONT_MEDIUM = get_font(25, True)
FONT_NORMAL = get_font(21)
FONT_SMALL = get_font(17)
FONT_TINY = get_font(14)


# ============================================================
# 3. 颜色
# ============================================================

BG = (17, 21, 38)
BG2 = (23, 29, 51)

PANEL = (32, 40, 67)
PANEL_LIGHT = (43, 53, 84)

CELL = (25, 31, 52)
CELL_HOVER = (39, 51, 80)

BORDER = (70, 83, 120)
BORDER_LIGHT = (96, 113, 157)

WHITE = (245, 247, 255)
GRAY = (170, 181, 208)
GRAY2 = (125, 137, 165)

BLUE = (74, 184, 255)
BLUE_LIGHT = (117, 210, 255)

YELLOW = (255, 210, 72)
YELLOW_LIGHT = (255, 230, 125)

GREEN = (70, 225, 145)
GREEN_LIGHT = (120, 245, 175)

RED = (255, 91, 110)
RED_LIGHT = (255, 135, 145)

PURPLE = (150, 120, 255)

SHADOW = (8, 10, 20)


# ============================================================
# 4. 游戏参数
# ============================================================

ROWS = 5
COLS = 5

CELL_SIZE = 88

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE

BOARD_X = 80
BOARD_Y = 205

MAX_MISTAKES = 3


# ============================================================
# 5. 关卡数据
# ============================================================

# U = 上
# D = 下
# L = 左
# R = 右
# . = 空

LEVELS = [

    [
        [".", "D", ".", ".", "."],
        [".", ".", ".", "L", "L"],
        [".", ".", ".", "D", "."],
        ["R", "R", ".", "R", "."],
        ["R", ".", "D", "R", "."],
    ],

    [
        [".", "U", ".", "U", "."],
        ["U", ".", ".", ".", "."],
        [".", ".", "U", "L", "U"],
        ["U", "L", ".", "L", "."],
        [".", ".", "D", ".", "."],
    ],

    [
        [".", ".", "L", ".", "."],
        ["D", "L", "U", "R", "."],
        [".", "L", ".", ".", "."],
        [".", "R", ".", ".", "."],
        [".", "D", ".", "L", "R"],
    ]

]


# ============================================================
# 6. 游戏状态
# ============================================================

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSE = "pause"
STATE_LEVEL_CLEAR = "level_clear"
STATE_WIN = "win"
STATE_FAIL = "fail"

game_state = STATE_MENU

current_level = 0

board = []

mistakes = MAX_MISTAKES

hint_cell = None
hint_timer = 0

message = ""
message_timer = 0

level_clear_timer = 0


# ============================================================
# 7. 动画
# ============================================================

animation = None

particles = []

shake_timer = 0

shake_strength = 0


# ============================================================
# 8. 鼠标悬停
# ============================================================

hover_cell = None


# ============================================================
# 9. 工具函数
# ============================================================

def clone_level(level_index):

    return [
        row[:]
        for row in LEVELS[level_index]
    ]


def arrow_count():

    return sum(
        1
        for row in board
        for value in row
        if value != "."
    )


def total_arrows(level_index):

    return sum(
        1
        for row in LEVELS[level_index]
        for value in row
        if value != "."
    )


def show_message(text, duration=120):

    global message
    global message_timer

    message = text
    message_timer = duration


# ============================================================
# 10. 游戏初始化
# ============================================================

def start_level():

    global board
    global mistakes
    global animation
    global particles
    global hint_cell
    global hint_timer
    global game_state
    global shake_timer

    board = clone_level(current_level)

    mistakes = MAX_MISTAKES

    animation = None

    particles.clear()

    hint_cell = None
    hint_timer = 0

    shake_timer = 0

    game_state = STATE_PLAYING

    show_message(
        "观察箭头方向，优先点击前方没有阻挡的箭头",
        180
    )


def start_game():

    global current_level

    current_level = 0

    start_level()


def restart_current_level():

    start_level()


def restart_game():

    global current_level

    current_level = 0

    start_level()


def go_next_level():

    global current_level

    current_level += 1

    if current_level >= len(LEVELS):

        globals()["game_state"] = STATE_WIN

    else:

        start_level()


# ============================================================
# 11. 箭头方向
# ============================================================

DIRECTIONS = {

    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1)

}


# ============================================================
# 12. 判断箭头是否可以飞出
# ============================================================

def can_arrow_leave(r, c):

    direction = board[r][c]

    if direction == ".":
        return False

    dr, dc = DIRECTIONS[direction]

    rr = r + dr
    cc = c + dc

    while 0 <= rr < ROWS and 0 <= cc < COLS:

        if board[rr][cc] != ".":

            return False

        rr += dr
        cc += dc

    return True


# ============================================================
# 13. 寻找可飞出的箭头
# ============================================================

def find_available_arrow():

    for r in range(ROWS):

        for c in range(COLS):

            if board[r][c] != ".":

                if can_arrow_leave(r, c):

                    return r, c

    return None


# ============================================================
# 14. 粒子系统
# ============================================================

def create_particles(x, y, good=True):

    for _ in range(18):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            1.5,
            4.5
        )

        particles.append({

            "x": x,
            "y": y,

            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,

            "life": random.randint(
                25,
                50
            ),

            "size": random.randint(
                2,
                5
            ),

            "good": good

        })


def update_particles():

    for particle in particles[:]:

        particle["x"] += particle["vx"]

        particle["y"] += particle["vy"]

        particle["vy"] += 0.08

        particle["life"] -= 1

        if particle["life"] <= 0:

            particles.remove(particle)


def draw_particles():

    for particle in particles:

        if particle["good"]:

            color = GREEN

        else:

            color = RED

        pygame.draw.circle(

            SCREEN,

            color,

            (
                int(particle["x"]),
                int(particle["y"])
            ),

            particle["size"]

        )


# ============================================================
# 15. 开始箭头动画
# ============================================================

def start_arrow_animation(r, c):

    global animation

    direction = board[r][c]

    dr, dc = DIRECTIONS[direction]

    animation = {

        "r": r,
        "c": c,

        "direction": direction,

        "dr": dr,
        "dc": dc,

        "progress": 0.0

    }


# ============================================================
# 16. 更新箭头动画
# ============================================================

def update_arrow_animation():

    global animation

    if animation is None:
        return

    animation["progress"] += 0.075

    if animation["progress"] >= 1:

        r = animation["r"]
        c = animation["c"]

        x = (
            BOARD_X
            + c * CELL_SIZE
            + CELL_SIZE // 2
        )

        y = (
            BOARD_Y
            + r * CELL_SIZE
            + CELL_SIZE // 2
        )

        create_particles(
            x,
            y,
            True
        )

        board[r][c] = "."

        animation = None

        # 检查是否清空
        if arrow_count() == 0:

            globals()["game_state"] = STATE_LEVEL_CLEAR

            globals()["level_clear_timer"] = 1000

            show_message(
                "本关完成！",
                100
            )


# ============================================================
# 17. 点击箭头
# ============================================================

def click_arrow(r, c):

    global mistakes
    global shake_timer
    global shake_strength
    global hint_cell

    if game_state != STATE_PLAYING:
        return

    if animation is not None:
        return

    if board[r][c] == ".":

        return

    # 可以飞
    if can_arrow_leave(r, c):

        hint_cell = None

        start_arrow_animation(
            r,
            c
        )

        show_message(
            "方向正确！箭头飞出棋盘",
            80
        )

    # 被阻挡
    else:

        mistakes -= 1

        shake_timer = 18

        shake_strength = 7

        x = (
            BOARD_X
            + c * CELL_SIZE
            + CELL_SIZE // 2
        )

        y = (
            BOARD_Y
            + r * CELL_SIZE
            + CELL_SIZE // 2
        )

        create_particles(
            x,
            y,
            False
        )

        show_message(
            "前方有箭头阻挡！失误次数 - 1",
            100
        )

        if mistakes <= 0:

            globals()["game_state"] = STATE_FAIL


# ============================================================
# 18. 获取棋盘格
# ============================================================

def get_cell_from_mouse(pos):

    mx, my = pos

    if not (
        BOARD_X <= mx < BOARD_X + BOARD_WIDTH
        and
        BOARD_Y <= my < BOARD_Y + BOARD_HEIGHT
    ):

        return None

    c = int(
        (mx - BOARD_X)
        // CELL_SIZE
    )

    r = int(
        (my - BOARD_Y)
        // CELL_SIZE
    )

    return r, c


# ============================================================
# 19. 绘制文字
# ============================================================

def draw_text(
    text,
    fnt,
    position,
    color=WHITE,
    center=False
):

    surface = fnt.render(
        text,
        True,
        color
    )

    rect = surface.get_rect()

    if center:

        rect.center = position

    else:

        rect.topleft = position

    SCREEN.blit(
        surface,
        rect
    )


# ============================================================
# 20. 绘制圆角按钮
# ============================================================

def draw_button(
    rect,
    text,
    enabled=True,
    small=False
):

    mouse = pygame.mouse.get_pos()

    hovered = (
        enabled
        and rect.collidepoint(mouse)
    )

    if not enabled:

        color = (55, 61, 80)

    elif hovered:

        color = (79, 103, 160)

    else:

        color = (57, 76, 123)

    pygame.draw.rect(
        SCREEN,
        color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        SCREEN,
        BORDER_LIGHT,
        rect,
        2,
        border_radius=12
    )

    fnt = (
        FONT_SMALL
        if small
        else FONT_NORMAL
    )

    text_color = (
        WHITE
        if enabled
        else GRAY2
    )

    draw_text(
        text,
        fnt,
        rect.center,
        text_color,
        center=True
    )


# ============================================================
# 21. 绘制箭头
# ============================================================

def draw_arrow(
    x,
    y,
    direction,
    highlighted=False,
    alpha=255
):

    color = (
        BLUE_LIGHT
        if highlighted
        else BLUE
    )

    head_color = YELLOW_LIGHT

    # 使用临时 Surface 实现透明效果
    surface = pygame.Surface(
        (90, 90),
        pygame.SRCALPHA
    )

    cx = 45
    cy = 45

    length = 45
    width = 8
    head = 20

    if direction == "R":

        pygame.draw.line(
            surface,
            (*color, alpha),
            (cx - length // 2, cy),
            (cx + length // 2 - head, cy),
            width
        )

        pygame.draw.polygon(
            surface,
            (*head_color, alpha),
            [
                (cx + length // 2, cy),
                (
                    cx + length // 2 - head,
                    cy - head * 0.75
                ),
                (
                    cx + length // 2 - head,
                    cy + head * 0.75
                )
            ]
        )

    elif direction == "L":

        pygame.draw.line(
            surface,
            (*color, alpha),
            (cx + length // 2, cy),
            (cx - length // 2 + head, cy),
            width
        )

        pygame.draw.polygon(
            surface,
            (*head_color, alpha),
            [
                (cx - length // 2, cy),
                (
                    cx - length // 2 + head,
                    cy - head * 0.75
                ),
                (
                    cx - length // 2 + head,
                    cy + head * 0.75
                )
            ]
        )

    elif direction == "U":

        pygame.draw.line(
            surface,
            (*color, alpha),
            (cx, cy + length // 2),
            (cx, cy - length // 2 + head),
            width
        )

        pygame.draw.polygon(
            surface,
            (*head_color, alpha),
            [
                (cx, cy - length // 2),
                (
                    cx - head * 0.75,
                    cy - length // 2 + head
                ),
                (
                    cx + head * 0.75,
                    cy - length // 2 + head
                )
            ]
        )

    elif direction == "D":

        pygame.draw.line(
            surface,
            (*color, alpha),
            (cx, cy - length // 2),
            (cx, cy + length // 2 - head),
            width
        )

        pygame.draw.polygon(
            surface,
            (*head_color, alpha),
            [
                (cx, cy + length // 2),
                (
                    cx - head * 0.75,
                    cy + length // 2 - head
                ),
                (
                    cx + head * 0.75,
                    cy + length // 2 - head
                )
            ]
        )

    SCREEN.blit(
        surface,
        (
            int(x - 45),
            int(y - 45)
        )
    )


# ============================================================
# 22. 绘制棋盘
# ============================================================

def draw_board():

    # 棋盘背景
    board_rect = pygame.Rect(
        BOARD_X - 15,
        BOARD_Y - 15,
        BOARD_WIDTH + 30,
        BOARD_HEIGHT + 30
    )

    pygame.draw.rect(
        SCREEN,
        PANEL,
        board_rect,
        border_radius=20
    )

    # 每个格子
    for r in range(ROWS):

        for c in range(COLS):

            x = (
                BOARD_X
                + c * CELL_SIZE
            )

            y = (
                BOARD_Y
                + r * CELL_SIZE
            )

            rect = pygame.Rect(
                x + 3,
                y + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )

            hovered = (
                hover_cell == (r, c)
            )

            is_hint = (
                hint_cell == (r, c)
                and hint_timer > 0
            )

            cell_color = (
                CELL_HOVER
                if hovered
                else CELL
            )

            pygame.draw.rect(
                SCREEN,
                cell_color,
                rect,
                border_radius=10
            )

            border_color = (
                YELLOW
                if is_hint
                else BORDER
            )

            pygame.draw.rect(
                SCREEN,
                border_color,
                rect,
                2,
                border_radius=10
            )

            value = board[r][c]

            if value != ".":

                highlighted = hovered or is_hint

                # 抖动效果
                offset_x = 0
                offset_y = 0

                if (
                    shake_timer > 0
                    and hovered
                ):

                    offset_x = random.randint(
                        -shake_strength,
                        shake_strength
                    )

                    offset_y = random.randint(
                        -shake_strength,
                        shake_strength
                    )

                draw_arrow(
                    x + CELL_SIZE // 2 + offset_x,
                    y + CELL_SIZE // 2 + offset_y,
                    value,
                    highlighted
                )

    # 飞行动画
    if animation:

        r = animation["r"]
        c = animation["c"]

        direction = animation["direction"]

        dr = animation["dr"]
        dc = animation["dc"]

        progress = animation["progress"]

        start_x = (
            BOARD_X
            + c * CELL_SIZE
            + CELL_SIZE // 2
        )

        start_y = (
            BOARD_Y
            + r * CELL_SIZE
            + CELL_SIZE // 2
        )

        distance = 140

        x = (
            start_x
            + dc * distance * progress
        )

        y = (
            start_y
            + dr * distance * progress
        )

        alpha = max(
            0,
            int(255 * (1 - progress * 0.5))
        )

        draw_arrow(
            x,
            y,
            direction,
            True,
            alpha
        )


# ============================================================
# 23. 绘制顶部信息
# ============================================================

def draw_top_bar():

    pygame.draw.rect(
        SCREEN,
        PANEL,
        (0, 0, WIDTH, 125)
    )

    draw_text(
        "一箭又一箭",
        FONT_BIG,
        (38, 20)
    )

    draw_text(
        "AIGC 辅助开发 · 软件工程第二次个人作业",
        FONT_SMALL,
        (40, 66),
        GRAY
    )

    # 关卡
    draw_text(
        f"第 {current_level + 1} / {len(LEVELS)} 关",
        FONT_MEDIUM,
        (420, 22)
    )

    # 进度
    total = total_arrows(current_level)

    remaining = arrow_count()

    progress = (
        1 - remaining / total
        if total > 0
        else 1
    )

    draw_text(
        f"完成进度 {int(progress * 100)}%",
        FONT_SMALL,
        (420, 65),
        GRAY
    )

    progress_rect = pygame.Rect(
        420,
        92,
        270,
        10
    )

    pygame.draw.rect(
        SCREEN,
        (50, 58, 83),
        progress_rect,
        border_radius=5
    )

    fill_rect = pygame.Rect(
        420,
        92,
        int(270 * progress),
        10
    )

    pygame.draw.rect(
        SCREEN,
        BLUE,
        fill_rect,
        border_radius=5
    )

    # 剩余箭头
    draw_text(
        f"剩余箭头 {remaining}",
        FONT_SMALL,
        (725, 25)
    )

    # 失误
    draw_text(
        "失误",
        FONT_SMALL,
        (725, 62),
        GRAY
    )

    for i in range(MAX_MISTAKES):

        color = (
            RED
            if i < mistakes
            else (70, 75, 95)
        )

        pygame.draw.circle(
            SCREEN,
            color,
            (
                790 + i * 28,
                72
            ),
            9
        )


# ============================================================
# 24. 绘制右侧面板
# ============================================================

def draw_side_panel():

    x = 720
    y = 190
    w = 330
    h = 430

    panel = pygame.Rect(
        x,
        y,
        w,
        h
    )

    pygame.draw.rect(
        SCREEN,
        PANEL,
        panel,
        border_radius=18
    )

    pygame.draw.rect(
        SCREEN,
        BORDER,
        panel,
        2,
        border_radius=18
    )

    draw_text(
        "游戏操作",
        FONT_MEDIUM,
        (x + 25, y + 25)
    )

    draw_text(
        "点击箭头，让它沿自身方向飞出。",
        FONT_SMALL,
        (x + 25, y + 75),
        GRAY
    )

    draw_text(
        "如果前方有其它箭头，则会被阻挡。",
        FONT_SMALL,
        (x + 25, y + 105),
        GRAY
    )

    # 分割线
    pygame.draw.line(
        SCREEN,
        BORDER,
        (x + 25, y + 145),
        (x + w - 25, y + 145),
        1
    )

    draw_text(
        "快捷键",
        FONT_SMALL,
        (x + 25, y + 165),
        WHITE
    )

    shortcuts = [
        ("P", "暂停 / 继续"),
        ("R", "重新开始"),
        ("ESC", "退出游戏"),
    ]

    yy = y + 205

    for key, desc in shortcuts:

        key_rect = pygame.Rect(
            x + 25,
            yy,
            48,
            32
        )

        pygame.draw.rect(
            SCREEN,
            PANEL_LIGHT,
            key_rect,
            border_radius=7
        )

        draw_text(
            key,
            FONT_TINY,
            key_rect.center,
            BLUE_LIGHT,
            center=True
        )

        draw_text(
            desc,
            FONT_SMALL,
            (x + 90, yy + 5),
            GRAY
        )

        yy += 45

    # 按钮
    hint_rect = pygame.Rect(
        x + 25,
        y + 360,
        130,
        45
    )

    restart_rect = pygame.Rect(
        x + 170,
        y + 360,
        130,
        45
    )

    draw_button(
        hint_rect,
        "获取提示",
        small=True
    )

    draw_button(
        restart_rect,
        "重新开始",
        small=True
    )


# ============================================================
# 25. 游戏界面
# ============================================================

def draw_game():

    SCREEN.fill(BG)

    draw_top_bar()

    draw_board()

    draw_side_panel()

    # 底部提示
    if message_timer > 0:

        draw_text(
            message,
            FONT_SMALL,
            (
                WIDTH // 2,
                700
            ),
            YELLOW_LIGHT,
            center=True
        )

    draw_particles()


# ============================================================
# 26. 开始菜单
# ============================================================

def draw_menu():

    SCREEN.fill(BG)

    # 装饰圆
    pygame.draw.circle(
        SCREEN,
        (28, 38, 66),
        (120, 120),
        80
    )

    pygame.draw.circle(
        SCREEN,
        (30, 41, 70),
        (980, 630),
        110
    )

    draw_text(
        "一箭又一箭",
        FONT_TITLE,
        (
            WIDTH // 2,
            115
        ),
        WHITE,
        center=True
    )

    draw_text(
        "AIGC 辅助开发 · Python + Pygame",
        FONT_NORMAL,
        (
            WIDTH // 2,
            170
        ),
        GRAY,
        center=True
    )

    # 左侧规则卡片
    card = pygame.Rect(
        120,
        245,
        410,
        300
    )

    pygame.draw.rect(
        SCREEN,
        PANEL,
        card,
        border_radius=18
    )

    pygame.draw.rect(
        SCREEN,
        BORDER,
        card,
        2,
        border_radius=18
    )

    draw_text(
        "游戏规则",
        FONT_MEDIUM,
        (150, 275)
    )

    rules = [
        "① 点击箭头，让箭头飞出棋盘",
        "② 前方有箭头时不能飞出",
        "③ 错误操作会消耗失误次数",
        "④ 清除全部箭头即可通关",
        "⑤ 共设计 3 个游戏关卡"
    ]

    yy = 325

    for rule in rules:

        draw_text(
            rule,
            FONT_SMALL,
            (150, yy),
            GRAY
        )

        yy += 40

    # 右侧玩法卡片
    demo = pygame.Rect(
        580,
        245,
        400,
        300
    )

    pygame.draw.rect(
        SCREEN,
        PANEL,
        demo,
        border_radius=18
    )

    pygame.draw.rect(
        SCREEN,
        BORDER,
        demo,
        2,
        border_radius=18
    )

    draw_text(
        "玩法示意",
        FONT_MEDIUM,
        (610, 275)
    )

    # 示例箭头
    draw_arrow(
        700,
        350,
        "R",
        True
    )

    draw_arrow(
        820,
        350,
        "D",
        False
    )

    draw_arrow(
        700,
        450,
        "U",
        False
    )

    draw_arrow(
        820,
        450,
        "L",
        True
    )

    draw_text(
        "观察箭头方向，规划点击顺序",
        FONT_SMALL,
        (
            780,
            505
        ),
        GRAY,
        center=True
    )

    # 开始按钮
    start_rect = pygame.Rect(
        WIDTH // 2 - 125,
        610,
        250,
        65
    )

    draw_button(
        start_rect,
        "开始游戏"
    )

    draw_text(
        "按 Enter / Space 也可以开始",
        FONT_TINY,
        (
            WIDTH // 2,
            695
        ),
        GRAY2,
        center=True
    )


# ============================================================
# 27. 暂停界面
# ============================================================

def draw_pause():

    draw_game()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (5, 8, 18, 180)
    )

    SCREEN.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "游戏已暂停",
        FONT_TITLE,
        (
            WIDTH // 2,
            300
        ),
        WHITE,
        center=True
    )

    draw_text(
        "按 P 继续游戏",
        FONT_NORMAL,
        (
            WIDTH // 2,
            355
        ),
        GRAY,
        center=True
    )

    resume_rect = pygame.Rect(
        WIDTH // 2 - 110,
        410,
        220,
        55
    )

    draw_button(
        resume_rect,
        "继续游戏"
    )


# ============================================================
# 28. 关卡完成界面
# ============================================================

def draw_level_clear():

    draw_game()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (10, 20, 25, 175)
    )

    SCREEN.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "本关完成！",
        FONT_TITLE,
        (
            WIDTH // 2,
            280
        ),
        GREEN_LIGHT,
        center=True
    )

    draw_text(
        f"第 {current_level + 1} 关已成功清除全部箭头",
        FONT_NORMAL,
        (
            WIDTH // 2,
            345
        ),
        WHITE,
        center=True
    )

    if current_level < len(LEVELS) - 1:

        draw_text(
            "准备进入下一关",
            FONT_SMALL,
            (
                WIDTH // 2,
                385
            ),
            GRAY,
            center=True
        )

    else:

        draw_text(
            "所有关卡已经完成！",
            FONT_SMALL,
            (
                WIDTH // 2,
                385
            ),
            GRAY,
            center=True
        )


# ============================================================
# 29. 通关界面
# ============================================================

def draw_win():

    SCREEN.fill(BG)

    draw_text(
        "全部通关！",
        FONT_TITLE,
        (
            WIDTH // 2,
            220
        ),
        GREEN_LIGHT,
        center=True
    )

    draw_text(
        "恭喜完成全部 3 个关卡",
        FONT_BIG,
        (
            WIDTH // 2,
            290
        ),
        WHITE,
        center=True
    )

    draw_text(
        "你已经成功清除所有箭头。",
        FONT_NORMAL,
        (
            WIDTH // 2,
            345
        ),
        GRAY,
        center=True
    )

    restart_rect = pygame.Rect(
        WIDTH // 2 - 115,
        430,
        230,
        58
    )

    menu_rect = pygame.Rect(
        WIDTH // 2 - 115,
        510,
        230,
        58
    )

    draw_button(
        restart_rect,
        "重新挑战"
    )

    draw_button(
        menu_rect,
        "返回首页"
    )


# ============================================================
# 30. 失败界面
# ============================================================

def draw_fail():

    SCREEN.fill(BG)

    draw_text(
        "挑战失败",
        FONT_TITLE,
        (
            WIDTH // 2,
            220
        ),
        RED_LIGHT,
        center=True
    )

    draw_text(
        "本关的失误次数已经用完",
        FONT_BIG,
        (
            WIDTH // 2,
            290
        ),
        WHITE,
        center=True
    )

    draw_text(
        "重新规划箭头点击顺序，再试一次吧。",
        FONT_NORMAL,
        (
            WIDTH // 2,
            345
        ),
        GRAY,
        center=True
    )

    retry_rect = pygame.Rect(
        WIDTH // 2 - 115,
        430,
        230,
        58
    )

    menu_rect = pygame.Rect(
        WIDTH // 2 - 115,
        510,
        230,
        58
    )

    draw_button(
        retry_rect,
        "重新挑战"
    )

    draw_button(
        menu_rect,
        "返回首页"
    )


# ============================================================
# 31. 提示
# ============================================================

def use_hint():

    global hint_cell
    global hint_timer

    result = find_available_arrow()

    if result:

        hint_cell = result

        hint_timer = 180

        show_message(
            "提示：黄色高亮的箭头当前可以直接飞出",
            150
        )

    else:

        show_message(
            "当前没有可以直接飞出的箭头",
            120
        )


# ============================================================
# 32. 鼠标悬停更新
# ============================================================

def update_hover():

    global hover_cell

    if game_state == STATE_PLAYING:

        hover_cell = get_cell_from_mouse(
            pygame.mouse.get_pos()
        )

    else:

        hover_cell = None


# ============================================================
# 33. 更新游戏
# ============================================================

def update_game():

    global message_timer
    global hint_timer
    global shake_timer

    if game_state == STATE_PLAYING:

        update_arrow_animation()

        update_particles()

        if message_timer > 0:

            message_timer -= 1

        if hint_timer > 0:

            hint_timer -= 1

            if hint_timer <= 0:

                globals()["hint_cell"] = None

        if shake_timer > 0:

            shake_timer -= 1

    elif game_state == STATE_LEVEL_CLEAR:

        update_particles()

        if level_clear_timer > 0:

            globals()["level_clear_timer"] -= 16

        else:

            if current_level < len(LEVELS) - 1:

                go_next_level()

            else:

                globals()["game_state"] = STATE_WIN


# ============================================================
# 34. 主程序
# ============================================================

running = True

while running:

    dt = CLOCK.tick(FPS)

    # ========================================================
    # 事件
    # ========================================================

    for event in pygame.event.get():

        # ----------------------------------------------------
        # 退出
        # ----------------------------------------------------

        if event.type == pygame.QUIT:

            running = False

        # ----------------------------------------------------
        # 键盘
        # ----------------------------------------------------

        elif event.type == pygame.KEYDOWN:

            # ESC
            if event.key == pygame.K_ESCAPE:

                running = False

            # 开始
            elif (
                game_state == STATE_MENU
                and event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                )
            ):

                start_game()

            # 暂停
            elif event.key == pygame.K_p:

                if game_state == STATE_PLAYING:

                    game_state = STATE_PAUSE

                elif game_state == STATE_PAUSE:

                    game_state = STATE_PLAYING

            # 重开
            elif event.key == pygame.K_r:

                if game_state in (
                    STATE_PLAYING,
                    STATE_PAUSE,
                    STATE_FAIL
                ):

                    restart_current_level()

            # 空格 / Enter进入下一关
            elif event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE
            ):

                if game_state == STATE_LEVEL_CLEAR:

                    if current_level < len(LEVELS) - 1:

                        go_next_level()

                    else:

                        game_state = STATE_WIN

        # ----------------------------------------------------
        # 鼠标
        # ----------------------------------------------------

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            mouse = event.pos

            # =========================
            # 首页
            # =========================

            if game_state == STATE_MENU:

                start_rect = pygame.Rect(
                    WIDTH // 2 - 125,
                    610,
                    250,
                    65
                )

                if start_rect.collidepoint(mouse):

                    start_game()

            # =========================
            # 游戏
            # =========================

            elif game_state == STATE_PLAYING:

                cell = get_cell_from_mouse(mouse)

                if cell:

                    r, c = cell

                    click_arrow(r, c)

                # 右侧提示按钮
                hint_rect = pygame.Rect(
                    745,
                    550,
                    130,
                    45
                )

                # 右侧重新开始按钮
                restart_rect = pygame.Rect(
                    890,
                    550,
                    130,
                    45
                )

                if hint_rect.collidepoint(mouse):

                    use_hint()

                elif restart_rect.collidepoint(mouse):

                    restart_current_level()

            # =========================
            # 暂停
            # =========================

            elif game_state == STATE_PAUSE:

                resume_rect = pygame.Rect(
                    WIDTH // 2 - 110,
                    410,
                    220,
                    55
                )

                if resume_rect.collidepoint(mouse):

                    game_state = STATE_PLAYING

            # =========================
            # 通关
            # =========================

            elif game_state == STATE_WIN:

                restart_rect = pygame.Rect(
                    WIDTH // 2 - 115,
                    430,
                    230,
                    58
                )

                menu_rect = pygame.Rect(
                    WIDTH // 2 - 115,
                    510,
                    230,
                    58
                )

                if restart_rect.collidepoint(mouse):

                    restart_game()

                elif menu_rect.collidepoint(mouse):

                    game_state = STATE_MENU

            # =========================
            # 失败
            # =========================

            elif game_state == STATE_FAIL:

                retry_rect = pygame.Rect(
                    WIDTH // 2 - 115,
                    430,
                    230,
                    58
                )

                menu_rect = pygame.Rect(
                    WIDTH // 2 - 115,
                    510,
                    230,
                    58
                )

                if retry_rect.collidepoint(mouse):

                    restart_current_level()

                elif menu_rect.collidepoint(mouse):

                    game_state = STATE_MENU

    # ========================================================
    # 更新
    # ========================================================

    update_hover()

    update_game()

    # ========================================================
    # 绘制
    # ========================================================

    if game_state == STATE_MENU:

        draw_menu()

    elif game_state == STATE_PLAYING:

        draw_game()

    elif game_state == STATE_PAUSE:

        draw_pause()

    elif game_state == STATE_LEVEL_CLEAR:

        draw_level_clear()

    elif game_state == STATE_WIN:

        draw_win()

    elif game_state == STATE_FAIL:

        draw_fail()

    pygame.display.flip()


# ============================================================
# 退出
# ============================================================

pygame.quit()
sys.exit()