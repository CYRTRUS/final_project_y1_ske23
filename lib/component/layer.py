import random
import pygame
from lib.component import assets


def scale_to_height(image, height):
    w, h = image.get_size()
    return pygame.transform.scale(image, (int(w * height / h), height))


class Layer:
    """One parallax background layer, tiled horizontally across the screen."""

    def __init__(self, image_name, screen_width, screen_height,
                 x=0, y=0, height_scale=1.0, random_scale=False):
        self.screen_width = screen_width
        self.x = x
        self.y = y
        base = scale_to_height(assets.image(image_name), int(screen_height * height_scale))

        if random_scale:
            self.pieces = self._random_pieces(base)
        else:
            self.pieces = []
            x_off = 0
            while x + x_off < screen_width:
                self.pieces.append((base, x_off, 0))
                x_off += base.get_width()

    def _random_pieces(self, base):
        pieces = []
        x_off = 0
        bw, bh = base.get_size()
        while x_off < self.screen_width * 2:
            sf = random.uniform(1.0, 1.2)
            img = pygame.transform.scale(base, (int(bw * sf), int(bh * sf)))
            img = pygame.transform.flip(img, random.choice([True, False]), False)
            pieces.append((img, x_off, random.randint(-100, 0)))
            x_off += img.get_width()
        return pieces

    def draw(self, screen):
        for img, x_off, y_off in self.pieces:
            screen.blit(img, (self.x + x_off, self.y + y_off))
