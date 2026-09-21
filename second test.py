import pygame
import sys
import math
import random

# ============================================================
# 一箭又一箭
# 软件工程课程第二次个人作业
# Python + Pygame
#
# 完整版功能：
# 1. 首页
# 2. 选择关卡
# 3. 游戏规则
# 4. 游戏玩法说明
# 5. 5 个游戏关卡
# 6. 点击箭头进行消除
# 7. 判断箭头前方是否有阻挡
# 8. 错误次数限制
# 9. 倒计时
# 10. 通关/失败页面
# 11. 重新开始
# 12. 鼠标悬停动画
# 13. 粒子效果
# 14. 页面切换动画
# ============================================================


# ============================================================
# 一、初始化
# ============================================================

pygame.init()

# 屏幕大小
WIDTH = 1200
HEIGHT = 760

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()

FPS = 60


# ============================================================
# 二、颜色
# ============================================================

# 整体采用暖色系，不使用蓝天白云风格
BG = (255, 246, 238)
BG_LIGHT = (255, 250, 245)

CREAM = (255, 250, 242)
WHITE = (255, 255, 255)

DARK = (74, 58, 72)
DARK_2 = (105, 86, 102)

PINK = (238, 111, 151)
PINK_LIGHT = (255, 218, 229)

PEACH = (255, 157, 103)
PEACH_LIGHT = (255, 224, 203)

PURPLE = (157, 118, 224)
PURPLE_LIGHT = (229, 216, 250)

YELLOW = (255, 199, 92)
YELLOW_LIGHT = (255, 239, 188)

GREEN = (91, 196, 133)
GREEN_LIGHT = (208, 241, 220)

RED = (231, 88, 105)

GRAY = (150, 139, 150)
GRAY_LIGHT = (235, 226, 230)

BOARD_BG = (88, 73, 91)
BOARD_CELL = (106, 89, 108)
BOARD_LINE = (137, 119, 139)

ARROW_MAIN = (255, 190, 72)
ARROW_LIGHT = (255, 221, 121)

SHADOW = (221, 204, 211)

# 选择关卡页面统一使用这一种主色
LEVEL_COLOR = (221, 122, 158)
LEVEL_COLOR_DARK = (194, 91, 130)
LEVEL_COLOR_LIGHT = (255, 222, 233)


# ============================================================
# 三、中文字体
# ============================================================

def get_chinese_font(size, bold=False):
    """
    自动寻找 Windows 常见中文字体。
    如果电脑中没有这些字体，则使用 pygame 默认字体。
    """

    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simkai.ttf",
        r"C:\Windows\Fonts\STSONG.TTF",
    ]

    if bold:
        preferred = [
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\msyh.ttc",
        ]
    else:
        preferred = font_paths

    for path in preferred:
        try:
            return pygame.font.Font(path, size)
        except:
            pass

    return pygame.font.SysFont("microsoftyahei", size, bold=bold)


FONT_SMALL = get_chinese_font(20)
FONT_NORMAL = get_chinese_font(25)
FONT_MEDIUM = get_chinese_font(30, True)
FONT_LARGE = get_chinese_font(44, True)
FONT_TITLE = get_chinese_font(72, True)
FONT_BIG = get_chinese_font(92, True)

FONT_NUMBER = get_chinese_font(34, True)


# ============================================================
# 四、辅助函数
# ============================================================

def draw_text(text, font, color, x, y, center=True):
    """
    绘制文字
    """
    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)

    return rect


def draw_shadow_rect(rect, color, radius=18, shadow_offset=7):
    """
    绘制带阴影的圆角矩形
    """

    shadow_rect = rect.copy()
    shadow_rect.y += shadow_offset

    pygame.draw.rect(
        screen,
        SHADOW,
        shadow_rect,
        border_radius=radius
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=radius
    )


def draw_button(rect, text, color, text_color=DARK, hover=True):
    """
    游戏按钮
    """

    mouse_pos = pygame.mouse.get_pos()

    is_hover = rect.collidepoint(mouse_pos) if hover else False

    if is_hover:
        draw_color = tuple(min(255, c + 15) for c in color)
        offset = -3
    else:
        draw_color = color
        offset = 0

    draw_rect = rect.copy()
    draw_rect.y += offset

    shadow = draw_rect.copy()
    shadow.y += 7

    pygame.draw.rect(
        screen,
        SHADOW,
        shadow,
        border_radius=22
    )

    pygame.draw.rect(
        screen,
        draw_color,
        draw_rect,
        border_radius=22
    )

    # 上方高光
    highlight = pygame.Rect(
        draw_rect.x + 12,
        draw_rect.y + 7,
        draw_rect.width - 24,
        5
    )

    pygame.draw.rect(
        screen,
        WHITE,
        highlight,
        border_radius=3
    )

    draw_text(
        text,
        FONT_MEDIUM,
        text_color,
        draw_rect.centerx,
        draw_rect.centery
    )

    return is_hover


def draw_star(x, y, size, color):
    """
    绘制五角星
    """

    points = []

    for i in range(10):

        angle = -math.pi / 2 + i * math.pi / 5

        if i % 2 == 0:
            radius = size
        else:
            radius = size * 0.42

        px = x + math.cos(angle) * radius
        py = y + math.sin(angle) * radius

        points.append((px, py))

    pygame.draw.polygon(
        screen,
        color,
        points
    )


def draw_circle_decoration(x, y, radius, color):
    pygame.draw.circle(
        screen,
        color,
        (x, y),
        radius
    )


def draw_background():
    """
    全局暖色背景
    """

    screen.fill(BG)

    # 左上装饰圆
    draw_circle_decoration(
        90,
        100,
        55,
        (255, 229, 210)
    )

    # 右上装饰圆
    draw_circle_decoration(
        1110,
        110,
        70,
        (238, 221, 246)
    )

    # 左下装饰圆
    draw_circle_decoration(
        100,
        690,
        90,
        (255, 226, 235)
    )

    # 右下装饰圆
    draw_circle_decoration(
        1110,
        680,
        85,
        (255, 235, 205)
    )

    # 小星星
    draw_star(180, 160, 14, YELLOW)
    draw_star(1040, 170, 13, PINK)
    draw_star(250, 680, 10, PURPLE)
    draw_star(980, 650, 11, PEACH)

    # 小圆点
    pygame.draw.circle(screen, PURPLE, (145, 270), 6)
    pygame.draw.circle(screen, PEACH, (1060, 300), 6)
    pygame.draw.circle(screen, PINK, (300, 110), 5)
    pygame.draw.circle(screen, YELLOW, (910, 110), 5)


# ============================================================
# 五、按钮区域
# ============================================================

HOME_START_BUTTON = pygame.Rect(
    430,
    475,
    340,
    70
)

HOME_LEVEL_BUTTON = pygame.Rect(
    430,
    565,
    340,
    65
)

HOME_RULE_BUTTON = pygame.Rect(
    245,
    650,
    250,
    60
)

HOME_HOW_BUTTON = pygame.Rect(
    705,
    650,
    250,
    60
)


# ============================================================
# 六、页面状态
# ============================================================

PAGE_HOME = "home"
PAGE_LEVELS = "levels"
PAGE_RULES = "rules"
PAGE_HOW = "how"
PAGE_GAME = "game"
PAGE_RESULT = "result"

page = PAGE_HOME


# ============================================================
# 七、关卡数据
# ============================================================

# 每个元组：
# (行, 列, 方向)

LEVELS = {

    1: [
        (4, 4, "上"),
        (4, 5, "右"),
        (5, 5, "右"),
        (5, 2, "右"),
        (2, 0, "上"),
        (0, 5, "下"),
        (4, 1, "右"),
    ],

    2: [
        (1, 2, "上"),
        (2, 3, "右"),
        (0, 1, "下"),
        (4, 4, "下"),
        (1, 5, "左"),
        (3, 4, "上"),
        (0, 3, "上"),
        (3, 5, "左"),
    ],

    3: [
        (1, 4, "左"),
        (2, 2, "左"),
        (2, 5, "右"),
        (5, 0, "下"),
        (1, 5, "上"),
        (3, 2, "右"),
        (4, 4, "右"),
        (3, 1, "左"),
        (2, 4, "右"),
        (5, 5, "右"),
    ],

    4: [
        (4, 2, "下"),
        (5, 3, "下"),
        (1, 1, "上"),
        (1, 5, "下"),
        (4, 0, "左"),
        (5, 4, "右"),
        (1, 3, "右"),
        (0, 0, "左"),
        (5, 0, "右"),
        (0, 3, "左"),
        (3, 0, "下"),
        (4, 4, "上"),
    ],

    5: [
        (0, 5, "上"),
        (2, 0, "右"),
        (1, 3, "上"),
        (3, 1, "上"),
        (5, 5, "右"),
        (3, 5, "下"),
        (5, 1, "下"),
        (5, 3, "右"),
        (0, 2, "右"),
        (1, 5, "右"),
        (5, 0, "右"),
        (3, 3, "右"),
    ],
}


# 每关时间限制
LEVEL_TIME = {
    1: 90,
    2: 80,
    3: 75,
    4: 70,
    5: 65,
}


# 每关名称
LEVEL_NAME = {
    1: "入门练习",
    2: "简单挑战",
    3: "中等难度",
    4: "困难模式",
    5: "终极挑战",
}


# ============================================================
# 八、游戏变量
# ============================================================

current_level = 1

arrows = []

mistakes = 3

game_start_time = 0

result_success = False

result_time = 0

result_mistakes = 0

message = ""

message_until = 0

shake_until = 0

flash_until = 0

last_clicked = None

particles = []

button_click_effect = 0


# ============================================================
# 九、箭头方向
# ============================================================

DIRECTION_VECTOR = {

    "上": (-1, 0),

    "下": (1, 0),

    "左": (0, -1),

    "右": (0, 1),
}


# ============================================================
# 十、创建游戏
# ============================================================

def start_level(level_number):

    global current_level
    global arrows
    global mistakes
    global game_start_time
    global page
    global message
    global particles
    global last_clicked

    current_level = level_number

    arrows = []

    for r, c, direction in LEVELS[level_number]:

        arrows.append({
            "row": r,
            "col": c,
            "direction": direction,
            "scale": 1.0,
            "alpha": 255,
            "remove": False,
        })

    mistakes = 3

    game_start_time = pygame.time.get_ticks()

    message = "观察箭头方向，找到可以飞出的箭头"

    particles = []

    last_clicked = None

    page = PAGE_GAME


# ============================================================
# 十一、重新开始当前关卡
# ============================================================

def restart_level():

    start_level(current_level)


# ============================================================
# 十二、判断箭头是否可以飞出
# ============================================================

def arrow_can_leave(target):

    target_row = target["row"]
    target_col = target["col"]
    direction = target["direction"]

    dr, dc = DIRECTION_VECTOR[direction]

    occupied = set()

    for arrow in arrows:

        if arrow["remove"]:
            continue

        occupied.add(
            (
                arrow["row"],
                arrow["col"]
            )
        )

    r = target_row + dr
    c = target_col + dc

    while 0 <= r < 6 and 0 <= c < 6:

        if (r, c) in occupied:

            return False

        r += dr
        c += dc

    return True


# ============================================================
# 十三、添加粒子
# ============================================================

def add_particles(x, y, color):

    for _ in range(16):

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
            "life": random.randint(25, 45),
            "color": color,
            "size": random.randint(3, 6),
        })


# ============================================================
# 十四、更新粒子
# ============================================================

def update_particles():

    for particle in particles[:]:

        particle["x"] += particle["vx"]

        particle["y"] += particle["vy"]

        particle["vy"] += 0.08

        particle["life"] -= 1

        if particle["life"] <= 0:

            particles.remove(particle)


# ============================================================
# 十五、绘制粒子
# ============================================================

def draw_particles():

    for particle in particles:

        pygame.draw.circle(
            screen,
            particle["color"],
            (
                int(particle["x"]),
                int(particle["y"])
            ),
            particle["size"]
        )


# ============================================================
# 十六、箭头绘制
# ============================================================

def draw_arrow(x, y, direction, scale=1.0, color=ARROW_MAIN):

    """
    手工绘制箭头。
    不需要图片。
    """

    length = int(42 * scale)

    width = int(12 * scale)

    head = int(22 * scale)

    shaft = int(25 * scale)

    # 上
    if direction == "上":

        pygame.draw.rect(
            screen,
            color,
            (
                x - width // 2,
                y - 2,
                width,
                shaft
            ),
            border_radius=5
        )

        pygame.draw.polygon(
            screen,
            color,
            [
                (x, y - length),
                (x - head, y - length + head),
                (x + head, y - length + head),
            ]
        )

    # 下
    elif direction == "下":

        pygame.draw.rect(
            screen,
            color,
            (
                x - width // 2,
                y - shaft + 2,
                width,
                shaft
            ),
            border_radius=5
        )

        pygame.draw.polygon(
            screen,
            color,
            [
                (x, y + length),
                (x - head, y + length - head),
                (x + head, y + length - head),
            ]
        )

    # 左
    elif direction == "左":

        pygame.draw.rect(
            screen,
            color,
            (
                x - 2,
                y - width // 2,
                shaft,
                width
            ),
            border_radius=5
        )

        pygame.draw.polygon(
            screen,
            color,
            [
                (x - length, y),
                (x - length + head, y - head),
                (x - length + head, y + head),
            ]
        )

    # 右
    elif direction == "右":

        pygame.draw.rect(
            screen,
            color,
            (
                x - shaft + 2,
                y - width // 2,
                shaft,
                width
            ),
            border_radius=5
        )

        pygame.draw.polygon(
            screen,
            color,
            [
                (x + length, y),
                (x + length - head, y - head),
                (x + length - head, y + head),
            ]
        )


# ============================================================
# 十七、游戏棋盘参数
# ============================================================

BOARD_SIZE = 540

CELL_SIZE = 82

BOARD_X = (WIDTH - BOARD_SIZE) // 2

BOARD_Y = 155


def get_cell_center(row, col):

    x = BOARD_X + 40 + col * CELL_SIZE

    y = BOARD_Y + 40 + row * CELL_SIZE

    return x, y


# ============================================================
# 十八、绘制游戏棋盘
# ============================================================

def draw_board():

    board_rect = pygame.Rect(
        BOARD_X,
        BOARD_Y,
        540,
        540
    )

    # 棋盘阴影
    shadow = board_rect.copy()

    shadow.y += 9

    pygame.draw.rect(
        screen,
        SHADOW,
        shadow,
        border_radius=28
    )

    # 棋盘
    pygame.draw.rect(
        screen,
        BOARD_BG,
        board_rect,
        border_radius=28
    )

    # 六乘六格子
    for row in range(6):

        for col in range(6):

            x = BOARD_X + 10 + col * CELL_SIZE

            y = BOARD_Y + 10 + row * CELL_SIZE

            rect = pygame.Rect(
                x,
                y,
                72,
                72
            )

            pygame.draw.rect(
                screen,
                BOARD_CELL,
                rect,
                border_radius=12
            )

            pygame.draw.rect(
                screen,
                BOARD_LINE,
                rect,
                width=2,
                border_radius=12
            )

    # 绘制箭头
    for index, arrow in enumerate(arrows):

        if arrow["remove"]:
            continue

        x, y = get_cell_center(
            arrow["row"],
            arrow["col"]
        )

        color = ARROW_MAIN

        if last_clicked is arrow:

            color = PINK

        draw_arrow(
            x,
            y,
            arrow["direction"],
            arrow["scale"],
            color
        )


# ============================================================
# 十九、绘制游戏顶部
# ============================================================

def draw_game_header():

    # 顶部区域
    pygame.draw.rect(
        screen,
        CREAM,
        (0, 0, WIDTH, 125)
    )

    # 标题
    draw_text(
        "一箭又一箭",
        FONT_LARGE,
        DARK,
        180,
        48
    )

    draw_text(
        f"第 {current_level} 关",
        FONT_NORMAL,
        LEVEL_COLOR_DARK,
        180,
        92
    )

    # 剩余箭头
    remain = sum(
        1
        for arrow in arrows
        if not arrow["remove"]
    )

    draw_text(
        f"剩余箭头：{remain}",
        FONT_NORMAL,
        DARK,
        520,
        42
    )

    # 剩余错误
    error_color = (
        RED
        if mistakes <= 1
        else DARK
    )

    draw_text(
        f"剩余失误：{mistakes}",
        FONT_NORMAL,
        error_color,
        520,
        82
    )

    # 时间
    elapsed_ms = pygame.time.get_ticks() - game_start_time

    elapsed = elapsed_ms / 1000

    remain_time = max(
        0,
        LEVEL_TIME[current_level] - elapsed
    )

    draw_text(
        f"时间：{remain_time:04.1f}s",
        FONT_NORMAL,
        PURPLE,
        800,
        42
    )

    # 进度条
    bar_x = 800
    bar_y = 78
    bar_w = 250
    bar_h = 14

    pygame.draw.rect(
        screen,
        GRAY_LIGHT,
        (
            bar_x,
            bar_y,
            bar_w,
            bar_h
        ),
        border_radius=7
    )

    progress = remain_time / LEVEL_TIME[current_level]

    progress = max(
        0,
        min(1, progress)
    )

    pygame.draw.rect(
        screen,
        PINK,
        (
            bar_x,
            bar_y,
            int(bar_w * progress),
            bar_h
        ),
        border_radius=7
    )

    # 重新开始
    restart_rect = pygame.Rect(
        1060,
        30,
        110,
        55
    )

    draw_button(
        restart_rect,
        "重来",
        PURPLE_LIGHT,
        PURPLE
    )


# ============================================================
# 二十、绘制游戏提示
# ============================================================

def draw_game_message():

    if pygame.time.get_ticks() < message_until:

        draw_text(
            message,
            FONT_NORMAL,
            DARK_2,
            WIDTH // 2,
            715
        )

    else:

        draw_text(
            "观察箭头方向，优先点击前方没有阻挡的箭头",
            FONT_NORMAL,
            GRAY,
            WIDTH // 2,
            715
        )


# ============================================================
# 二十一、首页
# ============================================================

def draw_home():

    draw_background()

    # 中央标题区域
    title_box = pygame.Rect(
        280,
        65,
        640,
        180
    )

    pygame.draw.rect(
        screen,
        CREAM,
        title_box,
        border_radius=35
    )

    pygame.draw.rect(
        screen,
        PINK_LIGHT,
        title_box,
        width=3,
        border_radius=35
    )

    # 小装饰
    draw_star(
        335,
        105,
        18,
        YELLOW
    )

    draw_star(
        870,
        105,
        18,
        PEACH
    )

    # 游戏标题
    draw_text(
        "一箭又一箭",
        FONT_BIG,
        DARK,
        WIDTH // 2,
        125
    )

    draw_text(
        "观察方向 · 规划顺序 · 消除所有箭头",
        FONT_NORMAL,
        LEVEL_COLOR_DARK,
        WIDTH // 2,
        205
    )

    # 左侧玩法介绍
    info_rect = pygame.Rect(
        115,
        285,
        400,
        150
    )

    draw_shadow_rect(
        info_rect,
        WHITE,
        25
    )

    draw_text(
        "怎么玩？",
        FONT_MEDIUM,
        PURPLE,
        160,
        325,
        center=False
    )

    draw_text(
        "点击可以飞出的箭头",
        FONT_NORMAL,
        DARK_2,
        160,
        370,
        center=False
    )

    draw_text(
        "避开阻挡 · 用完失误 · 清空通关",
        FONT_NORMAL,
        DARK_2,
        160,
        410,
        center=False
    )

    # 右侧装饰棋盘
    mini_board = pygame.Rect(
        700,
        280,
        385,
        155
    )

    draw_shadow_rect(
        mini_board,
        (247, 238, 246),
        25
    )

    # 小棋盘
    for r in range(3):

        for c in range(6):

            cell_x = 720 + c * 57
            cell_y = 305 + r * 45

            pygame.draw.rect(
                screen,
                (231, 220, 233),
                (
                    cell_x,
                    cell_y,
                    45,
                    34
                ),
                border_radius=8
            )

    # 小箭头
    draw_arrow(
        800,
        322,
        "右",
        0.55
    )

    draw_arrow(
        910,
        367,
        "下",
        0.55
    )

    draw_arrow(
        970,
        322,
        "左",
        0.55
    )

    # 开始游戏
    draw_button(
        HOME_START_BUTTON,
        "开始游戏",
        PINK,
        WHITE
    )

    # 选择关卡
    draw_button(
        HOME_LEVEL_BUTTON,
        "选择关卡",
        PURPLE_LIGHT,
        PURPLE
    )

    # 底部两个按钮
    draw_button(
        HOME_RULE_BUTTON,
        "游戏规则",
        PEACH_LIGHT,
        PEACH
    )

    draw_button(
        HOME_HOW_BUTTON,
        "怎么玩？",
        YELLOW_LIGHT,
        DARK
    )

    # 底部提示
    draw_text(
        "共 5 个关卡 · 每关都有时间挑战",
        FONT_SMALL,
        GRAY,
        WIDTH // 2,
        735
    )


# ============================================================
# 二十二、选择关卡页面
# ============================================================

def draw_levels():

    draw_background()

    # 标题
    draw_text(
        "选择关卡",
        FONT_TITLE,
        DARK,
        WIDTH // 2,
        85
    )

    draw_text(
        "选择一个关卡开始挑战",
        FONT_NORMAL,
        DARK_2,
        WIDTH // 2,
        155
    )

    # 五个卡片
    card_width = 190
    card_height = 360

    gap = 25

    total_width = (
        card_width * 5
        + gap * 4
    )

    start_x = (
        WIDTH - total_width
    ) // 2

    y = 235

    for level in range(1, 6):

        x = start_x + (
            level - 1
        ) * (
            card_width + gap
        )

        rect = pygame.Rect(
            x,
            y,
            card_width,
            card_height
        )

        mouse_pos = pygame.mouse.get_pos()

        hover = rect.collidepoint(
            mouse_pos
        )

        # 统一颜色
        card_color = (
            LEVEL_COLOR_LIGHT
            if hover
            else WHITE
        )

        # 阴影
        shadow = rect.copy()
        shadow.y += 8

        pygame.draw.rect(
            screen,
            SHADOW,
            shadow,
            border_radius=28
        )

        # 卡片
        pygame.draw.rect(
            screen,
            card_color,
            rect,
            border_radius=28
        )

        # 统一边框
        pygame.draw.rect(
            screen,
            LEVEL_COLOR,
            rect,
            width=4,
            border_radius=28
        )

        # 编号圆
        pygame.draw.circle(
            screen,
            LEVEL_COLOR,
            (
                rect.centerx,
                rect.y + 65
            ),
            42
        )

        draw_text(
            level,
            FONT_NUMBER,
            WHITE,
            rect.centerx,
            rect.y + 65
        )

        # 关卡名称
        draw_text(
            f"第 {level} 关",
            FONT_MEDIUM,
            DARK,
            rect.centerx,
            rect.y + 135
        )

        draw_text(
            LEVEL_NAME[level],
            FONT_SMALL,
            LEVEL_COLOR_DARK,
            rect.centerx,
            rect.y + 180
        )

        # 箭头数量
        draw_text(
            f"{len(LEVELS[level])} 个箭头",
            FONT_NORMAL,
            DARK_2,
            rect.centerx,
            rect.y + 235
        )

        # 时间
        draw_text(
            f"{LEVEL_TIME[level]} 秒",
            FONT_NORMAL,
            DARK_2,
            rect.centerx,
            rect.y + 275
        )

        # 点击提示
        draw_text(
            "点击挑战",
            FONT_SMALL,
            LEVEL_COLOR_DARK,
            rect.centerx,
            rect.y + 325
        )

    # 返回首页
    back_rect = pygame.Rect(
        470,
        655,
        260,
        65
    )

    draw_button(
        back_rect,
        "返回首页",
        PURPLE_LIGHT,
        PURPLE
    )


# ============================================================
# 二十三、规则页面
# ============================================================

def draw_rules():

    draw_background()

    draw_text(
        "游戏规则",
        FONT_TITLE,
        DARK,
        WIDTH // 2,
        80
    )

    rule_rect = pygame.Rect(
        220,
        170,
        760,
        450
    )

    draw_shadow_rect(
        rule_rect,
        WHITE,
        30
    )

    rules = [
        ("①", "点击箭头，让箭头沿自身方向飞出棋盘"),
        ("②", "如果箭头前方存在其他箭头，就不能飞出"),
        ("③", "点击被阻挡的箭头，会消耗一次失误机会"),
        ("④", "清除当前关卡全部箭头后即可通关"),
        ("⑤", "每关都有时间限制，需要在规定时间内完成"),
        ("⑥", "失误次数用完或者时间结束，则挑战失败"),
    ]

    y = 225

    for icon, text in rules:

        draw_text(
            icon,
            FONT_MEDIUM,
            PINK,
            290,
            y
        )

        draw_text(
            text,
            FONT_NORMAL,
            DARK_2,
            335,
            y,
            center=False
        )

        y += 62

    back_rect = pygame.Rect(
        470,
        655,
        260,
        65
    )

    draw_button(
        back_rect,
        "返回首页",
        PURPLE_LIGHT,
        PURPLE
    )


# ============================================================
# 二十四、怎么玩页面
# ============================================================

def draw_how():

    draw_background()

    draw_text(
        "怎么玩？",
        FONT_TITLE,
        DARK,
        WIDTH // 2,
        80
    )

    # 三个步骤
    steps = [
        (
            "1",
            "观察",
            "先观察所有箭头的方向，寻找前方没有阻挡的箭头。",
            PINK
        ),
        (
            "2",
            "点击",
            "点击可以直接飞出棋盘的箭头，箭头会自动消失。",
            PURPLE
        ),
        (
            "3",
            "通关",
            "不断寻找新的可飞箭头，直到棋盘全部清空。",
            PEACH
        ),
    ]

    x_positions = [220, 600, 980]

    for i, step in enumerate(steps):

        number, title, desc, color = step

        x = x_positions[i]

        rect = pygame.Rect(
            x - 150,
            205,
            300,
            330
        )

        draw_shadow_rect(
            rect,
            WHITE,
            28
        )

        pygame.draw.circle(
            screen,
            color,
            (x, 280),
            45
        )

        draw_text(
            number,
            FONT_NUMBER,
            WHITE,
            x,
            280
        )

        draw_text(
            title,
            FONT_LARGE,
            color,
            x,
            355
        )

        # 自动换行
        lines = [
            desc[:12],
            desc[12:]
        ]

        draw_text(
            lines[0],
            FONT_SMALL,
            DARK_2,
            x,
            420
        )

        draw_text(
            lines[1],
            FONT_SMALL,
            DARK_2,
            x,
            455
        )

    back_rect = pygame.Rect(
        470,
        625,
        260,
        65
    )

    draw_button(
        back_rect,
        "返回首页",
        PURPLE_LIGHT,
        PURPLE
    )


# ============================================================
# 二十五、结果页面
# ============================================================

def draw_result():

    draw_background()

    if result_success:

        title = "挑战成功！"

        title_color = GREEN

        subtitle = "太棒了，你清空了全部箭头！"

        icon = "✓"

    else:

        title = "挑战失败"

        title_color = RED

        subtitle = "别灰心，再试一次就能找到正确顺序。"

        icon = "×"

    # 中央卡片
    rect = pygame.Rect(
        310,
        100,
        580,
        500
    )

    draw_shadow_rect(
        rect,
        WHITE,
        35
    )

    pygame.draw.circle(
        screen,
        title_color,
        (
            rect.centerx,
            200
        ),
        60
    )

    draw_text(
        icon,
        FONT_BIG,
        WHITE,
        rect.centerx,
        200
    )

    draw_text(
        title,
        FONT_TITLE,
        title_color,
        rect.centerx,
        305
    )

    draw_text(
        subtitle,
        FONT_NORMAL,
        DARK_2,
        rect.centerx,
        365
    )

    draw_text(
        f"第 {current_level} 关",
        FONT_NORMAL,
        DARK,
        rect.centerx,
        415
    )

    draw_text(
        f"用时：{result_time:.1f} 秒",
        FONT_NORMAL,
        DARK_2,
        rect.centerx,
        455
    )

    draw_text(
        f"剩余失误：{result_mistakes}",
        FONT_NORMAL,
        DARK_2,
        rect.centerx,
        490
    )

    # 按钮
    again_rect = pygame.Rect(
        350,
        640,
        230,
        65
    )

    level_rect = pygame.Rect(
        620,
        640,
        230,
        65
    )

    draw_button(
        again_rect,
        "再玩一次",
        PINK,
        WHITE
    )

    draw_button(
        level_rect,
        "选择关卡",
        PURPLE_LIGHT,
        PURPLE
    )


# ============================================================
# 二十六、游戏页面
# ============================================================

def draw_game():

    draw_background()

    draw_game_header()

    # 棋盘位置
    draw_board()

    draw_game_message()

    draw_particles()


# ============================================================
# 二十七、获取鼠标对应箭头
# ============================================================

def get_clicked_arrow(pos):

    mouse_x, mouse_y = pos

    for arrow in reversed(arrows):

        if arrow["remove"]:
            continue

        x, y = get_cell_center(
            arrow["row"],
            arrow["col"]
        )

        distance = math.sqrt(
            (mouse_x - x) ** 2
            + (mouse_y - y) ** 2
        )

        if distance <= 35:

            return arrow

    return None


# ============================================================
# 二十八、点击箭头
# ============================================================

def click_arrow(arrow):

    global mistakes
    global message
    global message_until
    global shake_until
    global flash_until
    global last_clicked
    global page
    global result_success
    global result_time
    global result_mistakes

    if arrow is None:
        return

    last_clicked = arrow

    # 判断箭头能否飞出
    if arrow_can_leave(arrow):

        arrow["remove"] = True

        x, y = get_cell_center(
            arrow["row"],
            arrow["col"]
        )

        add_particles(
            x,
            y,
            ARROW_MAIN
        )

        message = "成功！箭头飞出棋盘"

        message_until = (
            pygame.time.get_ticks()
            + 900
        )

        # 判断是否全部清除
        remaining = sum(
            1
            for a in arrows
            if not a["remove"]
        )

        if remaining == 0:

            elapsed = (
                pygame.time.get_ticks()
                - game_start_time
            ) / 1000

            result_success = True

            result_time = elapsed

            result_mistakes = mistakes

            page = PAGE_RESULT

    else:

        mistakes -= 1

        message = "前方有阻挡！这支箭头暂时不能飞出"

        message_until = (
            pygame.time.get_ticks()
            + 1500
        )

        shake_until = (
            pygame.time.get_ticks()
            + 350
        )

        flash_until = (
            pygame.time.get_ticks()
            + 220
        )

        if mistakes <= 0:

            elapsed = (
                pygame.time.get_ticks()
                - game_start_time
            ) / 1000

            result_success = False

            result_time = elapsed

            result_mistakes = 0

            page = PAGE_RESULT


# ============================================================
# 二十九、游戏点击处理
# ============================================================

def handle_game_click(pos):

    # 重新开始按钮
    restart_rect = pygame.Rect(
        1060,
        30,
        110,
        55
    )

    if restart_rect.collidepoint(pos):

        restart_level()

        return

    arrow = get_clicked_arrow(pos)

    if arrow:

        click_arrow(arrow)


# ============================================================
# 三十、页面点击处理
# ============================================================

def handle_home_click(pos):

    global page

    if HOME_START_BUTTON.collidepoint(pos):

        start_level(1)

    elif HOME_LEVEL_BUTTON.collidepoint(pos):

        page = PAGE_LEVELS

    elif HOME_RULE_BUTTON.collidepoint(pos):

        page = PAGE_RULES

    elif HOME_HOW_BUTTON.collidepoint(pos):

        page = PAGE_HOW


def handle_levels_click(pos):

    global page

    # 五个关卡卡片
    card_width = 190
    card_height = 360
    gap = 25

    total_width = (
        card_width * 5
        + gap * 4
    )

    start_x = (
        WIDTH - total_width
    ) // 2

    y = 235

    for level in range(1, 6):

        x = start_x + (
            level - 1
        ) * (
            card_width + gap
        )

        rect = pygame.Rect(
            x,
            y,
            card_width,
            card_height
        )

        if rect.collidepoint(pos):

            start_level(level)

            return

    back_rect = pygame.Rect(
        470,
        655,
        260,
        65
    )

    if back_rect.collidepoint(pos):

        page = PAGE_HOME


def handle_rules_click(pos):

    global page

    back_rect = pygame.Rect(
        470,
        655,
        260,
        65
    )

    if back_rect.collidepoint(pos):

        page = PAGE_HOME


def handle_how_click(pos):

    global page

    back_rect = pygame.Rect(
        470,
        625,
        260,
        65
    )

    if back_rect.collidepoint(pos):

        page = PAGE_HOME


def handle_result_click(pos):

    global page

    again_rect = pygame.Rect(
        350,
        640,
        230,
        65
    )

    level_rect = pygame.Rect(
        620,
        640,
        230,
        65
    )

    if again_rect.collidepoint(pos):

        start_level(current_level)

    elif level_rect.collidepoint(pos):

        page = PAGE_LEVELS


# ============================================================
# 三十一、检查倒计时
# ============================================================

def check_timer():

    global page
    global result_success
    global result_time
    global result_mistakes

    if page != PAGE_GAME:
        return

    elapsed = (
        pygame.time.get_ticks()
        - game_start_time
    ) / 1000

    if elapsed >= LEVEL_TIME[current_level]:

        result_success = False

        result_time = LEVEL_TIME[current_level]

        result_mistakes = mistakes

        page = PAGE_RESULT


# ============================================================
# 三十二、页面动画
# ============================================================

transition_alpha = 0


def draw_flash():

    if pygame.time.get_ticks() < flash_until:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT)
        )

        overlay.set_alpha(65)

        overlay.fill(
            (255, 100, 120)
        )

        screen.blit(
            overlay,
            (0, 0)
        )


def draw_shake_offset():

    if pygame.time.get_ticks() < shake_until:

        return random.randint(
            -5,
            5
        )

    return 0


# ============================================================
# 三十三、绘制页面
# ============================================================

def draw_current_page():

    if page == PAGE_HOME:

        draw_home()

    elif page == PAGE_LEVELS:

        draw_levels()

    elif page == PAGE_RULES:

        draw_rules()

    elif page == PAGE_HOW:

        draw_how()

    elif page == PAGE_GAME:

        draw_game()

    elif page == PAGE_RESULT:

        draw_result()


# ============================================================
# 三十四、主循环
# ============================================================

running = True

while running:

    # --------------------------------------------------------
    # 事件处理
    # --------------------------------------------------------

    for event in pygame.event.get():

        # 关闭窗口
        if event.type == pygame.QUIT:

            running = False

        # 鼠标点击
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if page == PAGE_HOME:

                    handle_home_click(
                        event.pos
                    )

                elif page == PAGE_LEVELS:

                    handle_levels_click(
                        event.pos
                    )

                elif page == PAGE_RULES:

                    handle_rules_click(
                        event.pos
                    )

                elif page == PAGE_HOW:

                    handle_how_click(
                        event.pos
                    )

                elif page == PAGE_GAME:

                    handle_game_click(
                        event.pos
                    )

                elif page == PAGE_RESULT:

                    handle_result_click(
                        event.pos
                    )

        # 键盘
        elif event.type == pygame.KEYDOWN:

            # ESC 返回
            if event.key == pygame.K_ESCAPE:

                if page == PAGE_GAME:

                    page = PAGE_LEVELS

                elif page in (
                    PAGE_LEVELS,
                    PAGE_RULES,
                    PAGE_HOW
                ):

                    page = PAGE_HOME

                elif page == PAGE_RESULT:

                    page = PAGE_LEVELS

            # ENTER / SPACE
            elif event.key in (
                pygame.K_RETURN,
                pygame.K_SPACE
            ):

                if page == PAGE_HOME:

                    start_level(1)

            # R 重新开始
            elif event.key == pygame.K_r:

                if page == PAGE_GAME:

                    restart_level()

                elif page == PAGE_RESULT:

                    start_level(
                        current_level
                    )

    # --------------------------------------------------------
    # 游戏更新
    # --------------------------------------------------------

    check_timer()

    update_particles()

    # --------------------------------------------------------
    # 绘制
    # --------------------------------------------------------

    draw_current_page()

    # 游戏页面的错误闪烁
    if page == PAGE_GAME:

        draw_flash()

    # --------------------------------------------------------
    # 刷新
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(FPS)


# ============================================================
# 三十五、退出
# ============================================================

pygame.quit()

sys.exit()