"""Cached loading of fonts, images and sounds, plus small audio helpers."""
import os
import random
import pygame
from lib.component.config import Config

_fonts = {}
_images = {}
_sounds = {}


def font(size):
    """Return the game font at `size`, falling back to Arial if the TTF is missing."""
    size = int(size)
    if size not in _fonts:
        try:
            _fonts[size] = pygame.font.Font(Config.font_path, size)
        except (OSError, FileNotFoundError):
            _fonts[size] = pygame.font.SysFont("Arial", size)
    return _fonts[size]


def image(name):
    """Load an image from the asset folder (shared, do not mutate the returned surface)."""
    if name not in _images:
        _images[name] = pygame.image.load(os.path.join(Config.asset_dir, name)).convert_alpha()
    return _images[name]


def sfx_file(name, variant=None):
    """Path of a sound effect. Picks a random variant when `variant` is None."""
    if variant is None:
        count = Config.sfx_variants.get(name, 1)
        variant = random.randint(1, count) if count > 1 else 1
    return os.path.join(Config.sfx_dir, f"{name}_{variant}.mp3")


def sound(name, variant=None, volume=None):
    """Return a cached pygame Sound (or None if it cannot be loaded)."""
    path = sfx_file(name, variant)
    if path not in _sounds:
        try:
            _sounds[path] = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError):
            _sounds[path] = None
    snd = _sounds[path]
    if snd is not None and volume is not None:
        snd.set_volume(volume / 100)
    return snd


def play_sfx(name, variant=None, volume=None):
    snd = sound(name, variant, Config.sfx_volume if volume is None else volume)
    if snd is not None:
        snd.play()


def play_music(name, volume=None):
    try:
        pygame.mixer.music.load(sfx_file(name))
        pygame.mixer.music.set_volume((Config.ambient_volume if volume is None else volume) / 100)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass


def stop_music():
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
