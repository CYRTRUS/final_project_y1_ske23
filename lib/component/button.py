import pygame
from lib.component import assets
from lib.component.config import Config
from lib.component.ui import HoverSound, brighten

HOVER_SCALE = 1.05


class Button:
    def __init__(self, x, y, w, h, text, callback, click_sound=None, font_size=None, color=(200, 50, 50)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.click_sound = click_sound
        self.base_font_size = font_size or int(h * 0.5)
        self._hover = HoverSound()
        self.set_color(color)

    def set_color(self, color):
        self.color_idle = color
        self.color_hover = brighten(color, Config.hover_brightness)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

    def handle_event(self, event):
        if not self.is_clicked(event):
            return False
        if self.click_sound:
            self.click_sound.play()
        self.callback()
        return True

    def draw(self, screen):
        hovered = self._hover.update(self.rect)
        scale = HOVER_SCALE if hovered else 1.0

        draw_rect = pygame.Rect(0, 0, int(self.rect.w * scale), int(self.rect.h * scale))
        draw_rect.center = self.rect.center
        pygame.draw.rect(screen, self.color_hover if hovered else self.color_idle, draw_rect)

        font = assets.font(self.base_font_size * scale)
        shadow_offset = self.rect.h * 0.05
        shadow_color = tuple(int(c * 0.5) for c in self.color_idle)

        txt_shadow = font.render(self.text, True, shadow_color)
        screen.blit(txt_shadow, txt_shadow.get_rect(
            center=(draw_rect.centerx + shadow_offset, draw_rect.centery + shadow_offset)))
        txt = font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=draw_rect.center))
