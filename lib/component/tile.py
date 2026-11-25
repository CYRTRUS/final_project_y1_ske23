import pygame
from lib.component import assets
from lib.component.ability import ABILITY_COLORS, NORMAL
from lib.component.ui import HoverSound, brighten, darken

LETTER_COLOR = (60, 30, 5)
SELECTED_BORDER = (255, 210, 40)
HOVER_SCALE = 1.1
SELECTED_SCALE = 1.2
MOVE_SPEED_X = 0.15
MOVE_SPEED_Y = 0.2


class Tile:
    def __init__(self, letter, size, x, y, ability=NORMAL):
        self.letter = letter.upper()
        self.ability = ability
        self.size = size
        self.selected = False

        self.home = (x, y)          # resting place on the grid
        self.x, self.y = x, y       # current (animated) position
        self.target = (x, y)
        self.rect = pygame.Rect(x, y, size, size)
        self._hover = HoverSound()

    @property
    def is_empty(self):
        return self.letter == ""

    @property
    def color(self):
        return ABILITY_COLORS.get(self.ability, ABILITY_COLORS[NORMAL])

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def move_to(self, x, y):
        self.target = (x, y)

    def set_home(self, x, y):
        self.home = (x, y)
        self.move_to(x, y)

    def reset(self):
        self.selected = False
        self.move_to(*self.home)

    def update(self):
        tx, ty = self.target
        self.x += (tx - self.x) * MOVE_SPEED_X
        self.y += (ty - self.y) * MOVE_SPEED_Y
        if abs(self.y - ty) < 1:
            self.y = ty
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, screen):
        scale = HOVER_SCALE if self._hover.update(self.rect) else 1.0

        if self.selected:
            scale *= SELECTED_SCALE
            fill = darken(self.color, 20)
            border = SELECTED_BORDER
        else:
            fill = self.color
            border = brighten(self.color, 60)

        size = int(self.size * scale)
        rect = pygame.Rect(0, 0, size, size)
        rect.center = self.rect.center

        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)

        txt = assets.font(size * 0.65).render(self.letter, True, LETTER_COLOR)
        screen.blit(txt, txt.get_rect(center=rect.center))
