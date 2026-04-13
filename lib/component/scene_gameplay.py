from lib.component.scene_base import BaseScene
from lib.component.button import Button
from lib.component.board import Board
import pygame
import os


class GameplayScene(BaseScene):
    def __init__(self, screen, switch_scene_callback, click_sound, player, enemy, data_collector, game):
        super().__init__(screen, switch_scene_callback)

        self.player = player
        self.enemy = enemy
        self.game = game
        self.click_sound = click_sound

        self.attack_button = Button(
            675, 425, 250, 75, "Attack",
            lambda: self.board.attack(),
            click_sound,
            font_size=36,
            color=(120, 120, 120)  # gray default
        )

        self.buttons = [
            Button(1430, 730, 150, 50, "Back",
                   lambda: self.switch_scene_callback("menu"),
                   click_sound,
                   color=(200, 50, 50)),  # red default

            self.attack_button
        ]

        board_path = os.path.join("lib", "asset", "board.png")
        original = pygame.image.load(board_path).convert_alpha()

        target_w = int(self.width * 0.4)
        ratio = target_w / original.get_width()
        target_h = int(original.get_height() * ratio)

        self.board_image = pygame.transform.scale(original, (target_w, target_h))
        rect = self.board_image.get_rect()

        self.board_x = self.width // 2 - rect.width // 2
        self.board_y = self.height - rect.height

        self.board = Board(
            self.width, self.height,
            self.board_x, self.board_y,
            rect.width, rect.height,
            self.click_sound,
            self.game
        )

    def handle_event(self, event):
        super().handle_event(event)
        self.board.handle_event(event)

    def update(self):
        self.board.update()

        valid = self.board.is_current_word_valid()

        # base color logic
        if valid:
            base = (50, 200, 80)  # green
        else:
            base = (120, 120, 120)  # gray

        self.attack_button.color_idle = base

        # hover = +30 brightness
        mx, my = pygame.mouse.get_pos()
        if self.attack_button.rect.collidepoint((mx, my)):
            self.attack_button.color_hover = (
                min(base[0] + 30, 255),
                min(base[1] + 30, 255),
                min(base[2] + 30, 255),
            )
        else:
            self.attack_button.color_hover = base

    def draw(self):
        self.draw_background()
        self.game.player.draw(self.screen)
        self.game.enemy.draw(self.screen)

        self.screen.blit(self.board_image, (self.board_x, self.board_y))

        for b in self.buttons:
            b.draw(self.screen)

        self.board.draw(self.screen)
