import pygame
from lib.component import assets


class EffectText:
    """A shadowed line of text shown above an entity, optionally auto-hiding."""

    def __init__(self, font_size=26, shadow_offset=(2, 2), duration=3000):
        self.font = assets.font(font_size)
        self.shadow_offset = shadow_offset
        self.duration = duration    # milliseconds; None = stay until hide()
        self.text = ""
        self.color = (255, 255, 255)
        self.start_time = 0

    @property
    def visible(self):
        return bool(self.text)

    def show(self, text, color):
        self.text = text
        self.color = color
        self.start_time = pygame.time.get_ticks()

    def hide(self):
        self.text = ""

    def draw(self, screen, cx, y):
        if not self.text:
            return
        if self.duration is not None and pygame.time.get_ticks() - self.start_time >= self.duration:
            self.hide()
            return
        label = self.font.render(self.text, True, self.color)
        shadow = self.font.render(self.text, True, (20, 20, 20))
        x = cx - label.get_width() // 2
        screen.blit(shadow, (x + self.shadow_offset[0], y + self.shadow_offset[1]))
        screen.blit(label, (x, y))
