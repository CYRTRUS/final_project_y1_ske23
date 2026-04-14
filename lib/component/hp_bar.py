import pygame


class HpBar:
    def __init__(self, x, y, w, h, fill_color, bg_color, border_color, font, pad=20, rtl=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.fill_color = fill_color   # static base colour (green / red)
        self.bg_color = bg_color
        self.border_color = border_color
        self.font = font
        self.pad = pad
        self.rtl = rtl                 # right-to-left fill for enemy bar
        self.override_color = None     # blue or purple when a status effect is active
        self._ratio = 1.0              # smoothly animated fill ratio

    def tick(self, current, maximum):
        target = current / max(maximum, 1)
        self._ratio += (target - self._ratio) * 0.1
        if abs(self._ratio - target) < 0.001:
            self._ratio = target

    def draw(self, screen, left_text=None, right_text=None):
        fill_w = int(self.w * max(0.0, self._ratio))
        color = self.override_color or self.fill_color
        pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.w, self.h), border_radius=5)
        if fill_w > 0:
            if self.rtl:
                pygame.draw.rect(screen, color, (self.x + self.w - fill_w, self.y, fill_w, self.h), border_radius=5)
            else:
                pygame.draw.rect(screen, color, (self.x, self.y, fill_w, self.h), border_radius=5)
        pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.w, self.h), 2, border_radius=5)
        cy = self.y + self.h // 2
        if left_text:
            lbl = self.font.render(left_text, True, (220, 220, 220))
            screen.blit(lbl, (self.x + self.pad, cy - lbl.get_height() // 2))
        if right_text:
            lbl = self.font.render(right_text, True, (220, 220, 220))
            screen.blit(lbl, (self.x + self.w - lbl.get_width() - self.pad, cy - lbl.get_height() // 2))
