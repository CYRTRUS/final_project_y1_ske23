import pygame
import os


class Button:
    def __init__(self, x, y, w, h, text, callback, click_sound, font_size=None, color=(200, 50, 50)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.click_sound = click_sound

        self.font = pygame.font.Font(
            "lib/font/minercraftory.regular.ttf",
            font_size or int(h * 0.5)
        )

        self.h = h
        self.base_color = color
        self.color_idle = color
        self.color_hover = self._brighten(color, 30)

    def _brighten(self, color, amt):
        return (
            min(color[0] + amt, 255),
            min(color[1] + amt, 255),
            min(color[2] + amt, 255),
        )

    def set_color(self, color):
        self.base_color = color
        self.color_idle = color
        self.color_hover = self._brighten(color, 30)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            if self.click_sound:
                self.click_sound.play()
            self.callback()

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        color = self.color_hover if self.rect.collidepoint(mouse) else self.color_idle

        pygame.draw.rect(screen, color, self.rect)

        shadow_offset = self.h*0.05
        shadow_color = (int(self.color_idle[0] * 0.5), int(self.color_idle[1] * 0.5), int(self.color_idle[2] * 0.5))

        txt_shadow = self.font.render(self.text, True, shadow_color)
        screen.blit(txt_shadow, txt_shadow.get_rect(center=(self.rect.center[0] + shadow_offset, self.rect.center[1] + shadow_offset)))
        txt = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))
