import pygame
import random
from lib.component.config import Config

# Ability definitions: key -> display color and label
ABILITY_DEFS = {
    "n": {"color": (240, 240, 240), "label": "Normal"},
    "g": {"color": (80, 200,  80),  "label": "Green"},
    "o": {"color": (230, 140,  40), "label": "Orange"},
    "r": {"color": (220,  50,  50), "label": "Red"},
    "w": {"color": (160, 160, 160), "label": "Gray"},
    "b": {"color": (60, 120, 240),  "label": "Blue"},
    "p": {"color": (160,  60, 220), "label": "Purple"},
}


def roll_player_ability(level):
    """Pick a random ability for a newly spawned player tile."""
    bonus = min(level - 1, Config.player_ability_max)
    weights = {
        k: (v + bonus if k != "n" else v)
        for k, v in Config.player_ability_weights_base.items()
    }
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


def roll_enemy_ability(level):
    """Pick a random ability for an enemy attack."""
    bonus = min(level - 1, Config.enemy_ability_max)
    weights = {
        k: (v + bonus if k != "n" else v)
        for k, v in Config.enemy_ability_weights_base.items()
    }
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


class Tile:
    def __init__(self, letter, row, col, size, x, y, font, ability="n", click_sound=None):
        self.letter = letter.upper()
        self.row = row
        self.col = col
        self.ability = ability
        self.click_sound = click_sound
        self.base_size = size
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.selected = False
        self.rect = pygame.Rect(x, y, size, size)
        self.font = font
        self.is_falling = False
        self.fall_speed = 0.18

    @property
    def tile_color(self):
        return ABILITY_DEFS.get(self.ability, ABILITY_DEFS["n"])["color"]

    @property
    def border_color(self):
        return tuple(min(c + 60, 255) for c in self.tile_color)

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y

    def reset(self):
        self.selected = False
        self.move_to(self.original_x, self.original_y)

    def update(self):
        # Smoothly slide toward target position
        self.x += (self.target_x - self.x) * 0.15
        self.y += (self.target_y - self.y) * self.fall_speed
        if abs(self.y - self.target_y) < 1:
            self.y = self.target_y
            self.is_falling = False
        self.rect.topleft = (int(self.x), int(self.y))

    def get_draw_rect(self):
        scale = 1.2 if self.selected else 1.0
        size = int(self.base_size * scale)
        return pygame.Rect(
            self.rect.centerx - size // 2,
            self.rect.centery - size // 2,
            size, size
        )

    def draw(self, screen):
        rect = self.get_draw_rect()
        base = self.tile_color
        if self.selected:
            color  = tuple(min(c + 55, 255) for c in base)
            border = (255, 210, 40)
        else:
            color  = base
            border = self.border_color
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)
        txt = self.font.render(self.letter, True, (60, 30, 5))
        screen.blit(txt, txt.get_rect(center=rect.center))
