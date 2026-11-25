"""Tile / enemy ability definitions and weighted rolls."""
import random
from lib.component.config import Config

NORMAL = "n"

ABILITY_COLORS = {
    "n":      (240, 240, 240),
    "green":  (80, 200, 80),
    "orange": (230, 140, 40),
    "red":    (220, 50, 50),
    "gray":   (160, 160, 160),
    "blue":   (60, 120, 240),
    "purple": (160, 60, 220),
}

VALID_ABILITIES = frozenset(ABILITY_COLORS)

# Abilities that multiply player damage, in the order they are applied
BOOST_MULTIPLIERS = {
    "orange": Config.orange_boost,
    "red":    Config.red_boost,
    "gray":   Config.gray_boost,
}

# Status effects that can stick to an entity (saved as debuffs)
FREEZE = "blue"
WEAKEN = "purple"


def _roll(weights_base, cap, level):
    bonus = min(level - 1, cap)
    keys = list(weights_base)
    weights = [w if k == NORMAL else w + bonus for k, w in weights_base.items()]
    return random.choices(keys, weights=weights, k=1)[0]


def roll_player_ability(level):
    return _roll(Config.player_ability_weights_base, Config.player_ability_max, level)


def roll_enemy_ability(level):
    return _roll(Config.enemy_ability_weights_base, Config.enemy_ability_max, level)
