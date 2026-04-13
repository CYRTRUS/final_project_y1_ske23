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
        self.data_collector = data_collector
        self.game = game
        self.click_sound = click_sound

        board_path = os.path.join("lib", "asset", "board.png")
        original = pygame.image.load(board_path).convert_alpha()

        target_w = int(self.width*0.4)
        ratio = target_w/original.get_width()
        target_h = int(original.get_height()*ratio)

        self.board_image = pygame.transform.scale(original, (target_w, target_h))
        rect = self.board_image.get_rect()

        self.board_x = self.width//2-rect.width//2
        self.board_y = self.height-rect.height

        self.board = Board(
            self.width,
            self.height,
            self.board_x,
            self.board_y,
            rect.width,
            rect.height,
            self.click_sound,
            self.game
        )

        self.buttons.append(
            Button(
                20, 20, 150, 50, "Back",
                lambda: self.switch_scene_callback("menu"),
                click_sound
            )
        )

    def handle_event(self, event):
        super().handle_event(event)
        self.board.handle_event(event)

    def update(self):
        self.board.update()

    def draw(self):
        self.draw_background()
        self.game.player.draw(self.screen)
        self.game.enemy.draw(self.screen)
        self.screen.blit(self.board_image, (self.board_x, self.board_y))
        self.board.draw(self.screen)
        for b in self.buttons:
            b.draw(self.screen)
