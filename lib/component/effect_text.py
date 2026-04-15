import pygame


class EffectText:
    def __init__(self, font_path, font_size=26, shadow_offset=(2, 2), duration=3000):
        self.font = pygame.font.Font(font_path, font_size)
        self.shadow_offset = shadow_offset
        self.text = ""
        self.color = (255, 255, 255)
        self.visible = False
        self.duration = duration   # None = persist until hide() is called
        self.start_time = 0

    def show(self, text, color):
        self.text = text
        self.color = color
        self.visible = True
        self.start_time = pygame.time.get_ticks()

    def hide(self):
        self.visible = False
        self.text = ""

    def draw(self, screen, cx, y):
        if not self.visible or not self.text:
            return
        # Auto-hide after past set duration
        if self.duration is not None and pygame.time.get_ticks() - self.start_time >= self.duration:
            self.hide()
            return
        label = self.font.render(self.text, True, self.color)
        shadow = self.font.render(self.text, True, (20, 20, 20))
        x = cx - label.get_width() // 2
        screen.blit(shadow, (x + self.shadow_offset[0], y + self.shadow_offset[1]))
        screen.blit(label, (x, y))
