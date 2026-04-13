import pygame


class Tile:
    def __init__(self, letter, row, col, size, x, y, font):
        self.letter = letter.upper()
        self.row = row
        self.col = col

        self.base_size = size

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

        # falling state
        self.is_falling = False
        self.fall_speed = 0.18

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y

    def reset(self):
        self.selected = False
        self.move_to(self.original_x, self.original_y)

    def set_spawn(self, spawn_x, spawn_y):
        """Spawn tile at (spawn_x, spawn_y) above board then fall into place."""
        self.x = spawn_x
        self.y = spawn_y
        self.is_falling = True

    def update(self):
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
            size,
            size
        )

    def draw(self, screen):
        rect = self.get_draw_rect()

        color = (255, 220, 120) if self.selected else self.tile_color

        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (150, 100, 40), rect, 2, border_radius=8)

        txt = self.font.render(self.letter, True, (120, 65, 6))
        screen.blit(txt, txt.get_rect(center=rect.center))
