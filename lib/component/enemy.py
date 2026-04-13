import os
import math
import pygame
from lib.component.animated_sprite import AnimatedSprite


class Enemy:
    def __init__(self, game, level=1):
        self.game = game
        self.level = level

        # HP: 10 + 5*(lvl-1)   Damage: int(2 + 0.3*(lvl-1))
        self.max_health = 10 + 5 * (level - 1)
        self.health = self.max_health
        self.attack_damage = int(2 + 0.3 * (level - 1))

        self.x = 1050
        self.y = game.HEIGHT // 2

        scale = getattr(game, "enemy_scale", 6)

        self.sprite = AnimatedSprite(
            os.path.join("lib", "asset", "Orc-Idle.png"),
            scale=scale,
            x=self.x,
            y=0,
            speed=8
        )

        self.sprite.flip(True, False)

        h = self.sprite.get_size()[1]
        self.sprite.y = game.HEIGHT // 2 - h // 2 - 20

        # Font for HP display
        self.font = pygame.font.Font(
            "lib/font/minercraftory.regular.ttf", 24
        )

    def update_anim(self):
        self.sprite.update()

    def draw(self, screen):
        self.sprite.draw(screen)
        self._draw_health(screen)

    def _draw_health(self, screen):
        sw, _ = self.sprite.get_size()
        sprite_cx = int(self.sprite.x + sw // 2)
        sprite_top = int(self.sprite.y)

        # HP bar dimensions
        bar_w = max(sw, 120)
        bar_h = 14
        bar_x = sprite_cx - bar_w // 2
        bar_y = sprite_top - bar_h - 28

        # Background bar
        pygame.draw.rect(screen, (80, 20, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        # Health fill
        ratio = max(0, self.health / self.max_health)
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            color = (200, 50, 50) if ratio > 0.4 else (220, 120, 30)
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        # Border
        pygame.draw.rect(screen, (200, 160, 100), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        # HP text above bar
        hp_text = self.font.render(
            f"HP  {self.health}({self.max_health})", True, (255, 220, 150)
        )
        text_rect = hp_text.get_rect(centerx=sprite_cx, bottom=bar_y - 4)
        screen.blit(hp_text, text_rect)

        # Level label
        lvl_text = self.font.render(f"Lv.{self.level}", True, (255, 200, 80))
        lvl_rect = lvl_text.get_rect(centerx=sprite_cx, bottom=text_rect.top - 2)
        screen.blit(lvl_text, lvl_rect)

    def receive_damage(self, dmg):
        self.health = max(0, self.health - dmg)
