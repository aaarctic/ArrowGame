# pages.py
import pygame
import math
from config import (screen, WIDTH, HEIGHT, BG, PANEL, INK, MUTED,
                    PURPLE, PURPLE_DARK, YELLOW, RED, GREEN, WHITE,
                    FONT_TITLE, FONT_BIG, FONT_H1, FONT_BODY,
                    FONT_SMALL)
from draw import draw_text, draw_button, draw_arrow
from board import draw_board
from levels import LEVELS


def draw_decorations():
    pygame.draw.circle(screen, (255, 226, 207), (95, 110), 48)
    pygame.draw.circle(screen, (234, 220, 250), (1185, 105), 52)
    pygame.draw.circle(screen, (255, 225, 236), (92, 680), 58)
    pygame.draw.circle(screen, (255, 232, 190), (1185, 680), 55)


def draw_home():
    screen.fill(BG)
    draw_decorations()

    title_box = pygame.Rect(280, 70, 720, 150)
    pygame.draw.rect(screen, PANEL, title_box, border_radius=28)
    pygame.draw.rect(screen, (248, 208, 226), title_box, 3, border_radius=28)
    draw_text("一箭又一箭", FONT_TITLE, INK, (WIDTH // 2, 120))
    draw_text("观察方向 · 规划顺序 · 清空所有箭头",
              FONT_BODY, (194, 87, 123), (WIDTH // 2, 184))

    start_button = pygame.Rect(470, 505, 340, 66)
    select_button = pygame.Rect(470, 595, 340, 58)
    rule_button = pygame.Rect(150, 585, 250, 58)
    help_button = pygame.Rect(880, 585, 250, 58)

    draw_button(start_button, "开始游戏", (238, 92, 135))
    draw_button(select_button, "选择关卡", (155, 111, 232))
    draw_button(rule_button, "游戏规则", (255, 170, 91))
    draw_button(help_button, "操作提示", (255, 205, 84), text_color=INK)
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
        pygame.draw.rect(screen, PANEL, rect, border_radius=24)
        pygame.draw.circle(screen, PURPLE, (rect.centerx, y + 58), 34)
        draw_text(str(i + 1), FONT_H1, WHITE, (rect.centerx, y + 58))
        draw_text(f"第 {i + 1} 关", FONT_H1, PURPLE_DARK,
                  (rect.centerx, y + 118))
        draw_text(data["name"], FONT_SMALL, PURPLE, (rect.centerx, y + 155))
        draw_text(f"{data['count']} 个箭头", FONT_SMALL, INK,
                  (rect.centerx, y + 205))
        draw_text(f"{data['time']} 秒", FONT_SMALL, MUTED,
                  (rect.centerx, y + 245))

    back_button = pygame.Rect(515, 620, 250, 58)
    draw_button(back_button, "返回主页", PURPLE)
    return rects, back_button


def draw_help():
    screen.fill(BG)
    draw_decorations()
    draw_text("怎么玩？", FONT_TITLE, PURPLE_DARK, (WIDTH // 2, 95))

    panel = pygame.Rect(250, 180, 780, 410)
    pygame.draw.rect(screen, PANEL, panel, border_radius=28)
    lines = [
        "① 点击一个箭头",
        "② 箭头正前方没有其他箭头时，可以飞出",
        "③ 前方被挡住：本次点击算一次失误",
        "④ 失误会扣除机会，并给出红色反馈",
        "⑤ 箭头成功飞出，会有绿色反馈和飞行动画",
        "⑥ 清空全部箭头即可通关",
        "⑦ 倒计时结束或 3 次失误用完，则挑战失败",
    ]
    for i, line in enumerate(lines):
        draw_text(line, FONT_BODY, INK, (WIDTH // 2, 230 + i * 45))

    back_button = pygame.Rect(515, 625, 250, 58)
    draw_button(back_button, "返回", PURPLE)
    return back_button


def draw_game(state):
    screen.fill(BG)
    pygame.draw.rect(screen, PANEL, (0, 0, WIDTH, 160))
    pygame.draw.line(screen, (232, 220, 238), (0, 159), (WIDTH, 159), 2)

    data = LEVELS[state.selected_level]
    draw_text("一箭又一箭", FONT_BIG, INK, (170, 50))
    draw_text(f"第 {state.selected_level + 1} 关 · {data['name']}",
              FONT_H1, PURPLE, (180, 105))
    draw_text("剩余箭头", FONT_SMALL, MUTED, (510, 40))
    draw_text(str(len(state.game_arrows)), FONT_BIG, INK, (510, 85))
    draw_text("剩余失误", FONT_SMALL, MUTED, (690, 40))
    draw_text(str(state.mistakes), FONT_BIG,
              RED if state.mistakes <= 1 else INK, (690, 85))

    draw_text("剩余时间", FONT_SMALL, MUTED, (875, 40))
    draw_text(f"{math.ceil(state.remaining_time())}s", FONT_BIG,
              PURPLE, (875, 85))

    restart_button = pygame.Rect(1160, 40, 100, 50)
    draw_button(restart_button, "重来", (224, 213, 246),
                text_color=PURPLE_DARK)

    success_cell = state.last_success_cell if state.feedback == "success" else None
    fail_cell = state.last_fail_cell if state.feedback == "blocked" else None
    bx, by, cell, gap = draw_board(
        state.game_arrows, success_cell, fail_cell, state.shake)
    return restart_button


def draw_result(state):
    screen.fill(BG)
    draw_decorations()
    box = pygame.Rect(300, 125, 680, 470)
    pygame.draw.rect(screen, PANEL, box, border_radius=30)

    if state.result_win:
        draw_text("挑战成功！", FONT_TITLE, GREEN, (WIDTH // 2, 205))
        draw_text("太棒了，你清空了全部箭头",
                  FONT_BODY, INK, (WIDTH // 2, 265))
    else:
        draw_text("挑战失败", FONT_TITLE, RED, (WIDTH // 2, 205))
        reason = "失误次数已经用完" if state.mistakes <= 0 else "时间已经用完"
        draw_text(reason, FONT_BODY, INK, (WIDTH // 2, 265))

    draw_text(f"第 {state.selected_level + 1} 关", FONT_H1, PURPLE,
              (WIDTH // 2, 335))
    draw_text(f"本次得分：{state.last_score}", FONT_BIG, INK,
              (WIDTH // 2, 395))

    again_button = pygame.Rect(400, 465, 210, 58)
    select_button = pygame.Rect(670, 465, 210, 58)
    home_button = pygame.Rect(515, 540, 250, 58)
    draw_button(again_button, "再玩一次", (238, 92, 135))
    draw_button(select_button, "选择关卡", PURPLE)
    draw_button(home_button, "返回主页", (224, 213, 246),
                text_color=PURPLE_DARK)
    return again_button, select_button, home_button