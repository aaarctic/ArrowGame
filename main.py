# main.py
import pygame
import sys
import math

from config import (WIDTH, HEIGHT, screen, clock, DIRS)
from levels import LEVELS
from logic import is_clear
from board import draw_board, cell_from_mouse
from pages import (draw_home, draw_select, draw_help,
                   draw_game, draw_result)


class GameState:
    def __init__(self):
        self.screen_name = "home"
        self.selected_level = 0
        self.game_arrows = []
        self.mistakes = 3
        self.start_time = 0
        self.time_limit = 90
        self.feedback = ""
        self.feedback_until = 0
        self.animating = []
        self.last_success_cell = None
        self.last_fail_cell = None
        self.result_win = False
        self.last_score = 0
        self.shake = 0

    def remaining_time(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        return max(0, self.time_limit - elapsed)

    def reset(self, level_index):
        data = LEVELS[level_index]
        self.game_arrows = list(data["arrows"])
        self.mistakes = 3
        self.time_limit = data["time"]
        self.start_time = pygame.time.get_ticks()
        self.feedback = ""
        self.feedback_until = 0
        self.animating = []
        self.last_success_cell = None
        self.last_fail_cell = None

    def finish(self, win):
        self.result_win = win
        elapsed = self.time_limit - self.remaining_time()
        count = len(LEVELS[self.selected_level]["arrows"])
        self.last_score = max(
            0, int(count * 100 - elapsed * 2 + self.mistakes * 50))
        self.screen_name = "result"


state = GameState()


def try_click(cell):
    if cell is None:
        return
    r, c = cell
    arrow_map = {(rr, cc): dd for rr, cc, dd in state.game_arrows}

    if cell not in arrow_map:
        state.feedback = "empty"
        state.feedback_until = pygame.time.get_ticks() + 650
        return

    direction = arrow_map[cell]
    if is_clear(r, c, direction, arrow_map):
        state.game_arrows = [(rr, cc, dd) for rr, cc, dd in state.game_arrows
                             if (rr, cc) != cell]
        state.feedback = "success"
        state.feedback_until = pygame.time.get_ticks() + 750
        state.last_success_cell = cell
        state.animating.append((r, c, direction, pygame.time.get_ticks()))
    else:
        state.mistakes -= 1
        state.feedback = "blocked"
        state.feedback_until = pygame.time.get_ticks() + 800
        state.last_fail_cell = cell


def main():
    running = True
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state.screen_name = "home"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if state.screen_name == "home":
                    b = draw_home()
                    if b[0].collidepoint(mx, my):
                        state.selected_level = 0
                        state.reset(0)
                        state.screen_name = "game"
                    elif b[1].collidepoint(mx, my):
                        state.screen_name = "select"
                    elif b[2].collidepoint(mx, my) or b[3].collidepoint(mx, my):
                        state.screen_name = "help"
                elif state.screen_name == "select":
                    rects, back = draw_select()
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mx, my):
                            state.selected_level = i
                            state.reset(i)
                            state.screen_name = "game"
                            break
                    if back.collidepoint(mx, my):
                        state.screen_name = "home"
                elif state.screen_name == "game":
                    restart = draw_game(state)
                    if restart.collidepoint(mx, my):
                        state.reset(state.selected_level)
                    else:
                        bx, by, cell, gap = draw_board(state.game_arrows)
                        try_click(cell_from_mouse(mx, my, bx, by, cell, gap))

        if state.screen_name == "game":
            if not state.game_arrows and state.feedback_until < now - 100:
                state.finish(True)
            elif state.mistakes <= 0 or state.remaining_time() <= 0:
                state.finish(False)

        if state.screen_name == "home":
            draw_home()
        elif state.screen_name == "select":
            draw_select()
        elif state.screen_name == "help":
            draw_help()
        elif state.screen_name == "game":
            draw_game(state)
        elif state.screen_name == "result":
            draw_result(state)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()