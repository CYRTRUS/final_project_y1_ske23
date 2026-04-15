import pygame
from lib.component.scene_base import BaseScene
from lib.component.button import Button


class MenuScene(BaseScene):

    def __init__(self, screen, switch_scene_callback, quit_callback, click_sound):
        super().__init__(screen, switch_scene_callback)

        self.click_sound = click_sound

        button_w = 260
        button_h = 100
        padding = 20

        start_y = ((self.height - (button_h * 3 + padding * 2)) // 2) + 50
        start_x = (self.width - button_w) // 2

        self.buttons = [
            Button(start_x, start_y + (button_h + padding) * 0,
                   button_w, button_h, "Start",
                   lambda: self.switch_scene_callback("gameplay"),
                   click_sound, color=(200, 50, 50)),
            Button(start_x, start_y + (button_h + padding) * 1,
                   button_w, button_h, "Stats",
                   lambda: self.switch_scene_callback("stats"),
                   click_sound, color=(200, 50, 50)),
            Button(start_x, start_y + (button_h + padding) * 2,
                   button_w, button_h, "Quit",
                   quit_callback,
                   click_sound, color=(200, 50, 50)),
        ]

        try:
            self.title_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 120)
        except Exception:
            self.title_font = pygame.font.SysFont("Arial", 120)

        self._title_y = start_y - 220

    def draw(self):
        self.draw_background()

        cx = self.width // 2
        shadow = self.title_font.render("WordForge", True, (0, 0, 0))
        self.screen.blit(shadow, shadow.get_rect(centerx=cx + 8, top=self._title_y + 8))
        title = self.title_font.render("WordForge", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(centerx=cx, top=self._title_y))

        for b in self.buttons:
            b.draw(self.screen)
