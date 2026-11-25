import pygame

TEXT_COLOR = (220, 220, 220)


class HpBar:
    def __init__(self, x, y, w, h, fill_color, bg_color, border_color, font, pad=20, rtl=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.fill_color = fill_color    # base colour (green / red)
        self.bg_color = bg_color
        self.border_color = border_color
        self.font = font
        self.pad = pad
        self.rtl = rtl                  # fill right-to-left (enemy bar)
        self.override_color = None      # blue / purple while a status effect is active
        self.ratio = 1.0                # smoothly animated fill ratio

    def snap(self, current, maximum):
        """Jump straight to the value without animating."""
        self.ratio = current / max(maximum, 1)

    def tick(self, current, maximum):
        target = current / max(maximum, 1)
        self.ratio += (target - self.ratio) * 0.1
        if abs(self.ratio - target) < 0.001:
            self.ratio = target

    def draw(self, screen, left_text=None, right_text=None):
        r = self.rect
        fill_w = int(r.w * max(0.0, self.ratio))
        pygame.draw.rect(screen, self.bg_color, r, border_radius=5)
        if fill_w > 0:
            fill_x = r.right - fill_w if self.rtl else r.x
            pygame.draw.rect(screen, self.override_color or self.fill_color,
                             (fill_x, r.y, fill_w, r.h), border_radius=5)
        pygame.draw.rect(screen, self.border_color, r, 2, border_radius=5)

        if left_text:
            lbl = self.font.render(left_text, True, TEXT_COLOR)
            screen.blit(lbl, lbl.get_rect(left=r.x + self.pad, centery=r.centery))
        if right_text:
            lbl = self.font.render(right_text, True, TEXT_COLOR)
            screen.blit(lbl, lbl.get_rect(right=r.right - self.pad, centery=r.centery))
