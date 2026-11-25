"""Small drawing helpers shared by scenes and widgets."""
import pygame
from lib.component import assets
from lib.component.config import Config


def brighten(color, amount):
    return tuple(min(c + amount, 255) for c in color)


def darken(color, amount):
    return tuple(max(c - amount, 0) for c in color)


def shadow_text(screen, font, text, color, shadow_color=(20, 20, 20), offset=(2, 2), **rect_kwargs):
    """Blit `text` with a drop shadow. `rect_kwargs` positions it, e.g. centerx=..., top=..."""
    shadow = font.render(text, True, shadow_color)
    label = font.render(text, True, color)
    rect = label.get_rect(**rect_kwargs)
    screen.blit(shadow, rect.move(offset))
    screen.blit(label, rect)
    return rect


def dim_screen(screen, alpha):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, int(alpha)))
    screen.blit(overlay, (0, 0))


class HoverSound:
    """Plays the hover sound once each time the mouse enters a rect."""

    def __init__(self):
        self._was_hovered = False

    def update(self, rect):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        if hovered and not self._was_hovered:
            snd = assets.sound("btn_hovering", volume=Config.hover_volume)
            if snd is not None:
                snd.play()
        self._was_hovered = hovered
        return hovered
