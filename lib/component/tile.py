import pygame


class Tile:
    def __init__(self, letter, row, col, size, x, y, font):
        self.letter = letter.upper()
        self.row = row
        self.col = col
        self.size = size
        self.original_x = x
        self.original_y = y

        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y

        self.selected = False
        self.tile_color = (240, 240, 240)
        self.rect = pygame.Rect(x, y, size, size)
        self.font = font

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y

    def reset_position(self):
        self.selected = False
        self.move_to(self.original_x, self.original_y)

    def update(self):
        self.x += (self.target_x - self.x) * 0.1
        self.y += (self.target_y - self.y) * 0.1
        self.rect.topleft = (int(self.x), int(self.y))

    def display_tile(self, screen):
        scale = 1.2 if self.selected else 1.0

        size = int(self.size * scale)

        rect = pygame.Rect(
            self.rect.centerx - size // 2,
            self.rect.centery - size // 2,
            size,
            size
        )

        color = (255, 220, 120) if self.selected else self.tile_color

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (150, 100, 40), rect, 2, border_radius=8)

        txt = self.font.render(self.letter, True, (120, 65, 6))
        screen.blit(txt, txt.get_rect(center=rect.center))
