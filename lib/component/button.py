import pygame
import os
from lib.component.config import Config
import random


class Button:
    hover_sound = None

    def __init__(self, x, y, w, h, text, callback, click_sound=None, font_size=None, color=(200, 50, 50)):
        if Button.hover_sound is None:
            Button.hover_sound = pygame.mixer.Sound(pygame.mixer.Sound(os.path.join(
                "lib", "sfx", f"{Config.btn_hovering}_{random.randint(1, Config.btn_hovering_var)}.mp3")))
            Button.hover_sound.set_volume(Config.hover_volume/100)

        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

        self.click_sound = click_sound

        if text.lower() == "attack":
            pass

        self.base_font_size = font_size or int(h * 0.5)

        self.h = h
        self.base_color = color
        self.color_idle = color
        self.color_hover = self._brighten(color, 30)

        self.base_w = w
        self.base_h = h

        self._was_hovered = False

        self.font_cache = {}
        self._get_font(self.base_font_size)
        self._get_font(int(self.base_font_size * 1.05))

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

    def _get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(
                "lib/font/minercraftory.regular.ttf",
                size
            )
        return self.font_cache[size]

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos):
            if self.click_sound:
                self.click_sound.play()
            self.callback()

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse)

        # play hover sound only once
        if hovered and not self._was_hovered:
            if Button.hover_sound:
                Button.hover_sound.play()

        self._was_hovered = hovered

        color = self.color_hover if hovered else self.color_idle

        scale = 1.05 if hovered else 1.0

        draw_w = int(self.base_w * scale)
        draw_h = int(self.base_h * scale)

        draw_rect = pygame.Rect(0, 0, draw_w, draw_h)
        draw_rect.center = self.rect.center

        pygame.draw.rect(screen, color, draw_rect)

        font_size = int(self.base_font_size * scale)
        font = self._get_font(font_size)

        shadow_offset = self.h * 0.05

        shadow_color = (
            int(self.color_idle[0] * 0.5),
            int(self.color_idle[1] * 0.5),
            int(self.color_idle[2] * 0.5)
        )

        txt_shadow = font.render(self.text, True, shadow_color)
        screen.blit(
            txt_shadow,
            txt_shadow.get_rect(
                center=(
                    draw_rect.center[0] + shadow_offset,
                    draw_rect.center[1] + shadow_offset
                )
            )
        )

        txt = font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=draw_rect.center))
