import pygame
import random
import os
from lib.component.config import Config

ABILITY_DEFS = {
    "n": {"color": (240, 240, 240), "label": "Normal"},
    "green": {"color": (80, 200, 80),   "label": "Green"},
    "orange": {"color": (230, 140, 40),  "label": "Orange"},
    "red":    {"color": (220, 50, 50),   "label": "Red"},
    "gray":   {"color": (160, 160, 160), "label": "Gray"},
    "blue":   {"color": (60, 120, 240),  "label": "Blue"},
    "purple": {"color": (160, 60, 220),  "label": "Purple"},
}

# Short alias -> full name for internal use
ABILITY_ALIAS = {
    "n": "n",
    "g": "green",
    "o": "orange",
    "r": "red",
    "w": "gray",
    "b": "blue",
    "p": "purple",
}


def roll_player_ability(level):
    bonus = min(level - 1, Config.player_ability_max)
    weights = {k: (v + bonus if k != "n" else v) for k, v in Config.player_ability_weights_base.items()}
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


def roll_enemy_ability(level):
    bonus = min(level - 1, Config.enemy_ability_max)
    weights = {k: (v + bonus if k != "n" else v) for k, v in Config.enemy_ability_weights_base.items()}
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


class Tile:
    hover_sound = None

    def __init__(self, letter, row, col, size, x, y, font=None, ability="n", click_sound=None):
        if Tile.hover_sound is None:
            Tile.hover_sound = pygame.mixer.Sound(os.path.join("lib", "sfx", f"{Config.btn_hovering}_{random.randint(1, Config.btn_hovering_var)}.mp3"))
            Tile.hover_sound.set_volume(Config.hover_volume / 100)

        self.letter = letter.upper()
        self.row = row
        self.col = col
        self.ability = ability
        self.click_sound = click_sound

        self._was_hovered = False

        self.base_size = size
        self.original_x = x
        self.original_y = y

        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y

        self.selected = False
        self.rect = pygame.Rect(x, y, size, size)
        self.is_falling = False
        self.fall_speed = 0.2
        self.font_cache = {}

    @property
    def tile_color(self):
        key = ABILITY_ALIAS.get(self.ability, self.ability)
        return ABILITY_DEFS.get(key, ABILITY_DEFS["n"])["color"]

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
        self.x += (self.target_x - self.x) * 0.15
        self.y += (self.target_y - self.y) * self.fall_speed

        if abs(self.y - self.target_y) < 1:
            self.y = self.target_y
            self.is_falling = False

        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse)

        if hovered and not self._was_hovered:
            if Tile.hover_sound:
                Tile.hover_sound.play()

        self._was_hovered = hovered

        scale = 1.0

        if hovered:
            scale *= 1.1

        base = self.tile_color

        if self.selected:
            scale *= 1.2
            # Darken the selected tile color
            color = tuple(max(c - 20, 0) for c in base)
            border = (255, 210, 40)
        else:
            color = base
            border = self.border_color

        size = int(self.base_size * scale)

        rect = pygame.Rect(
            self.rect.centerx - size // 2,
            self.rect.centery - size // 2,
            size,
            size
        )

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)

        font_size = int(size * 0.65)

        if font_size not in self.font_cache:
            self.font_cache[font_size] = pygame.font.Font("lib/font/minercraftory.regular.ttf", font_size)

        font = self.font_cache[font_size]
        txt = font.render(self.letter, True, (60, 30, 5))
        screen.blit(txt, txt.get_rect(center=rect.center))
