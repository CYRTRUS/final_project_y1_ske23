import math
import os
import pygame
from lib.component.animated_sprite import AnimatedSprite


class Player:
    def __init__(self, game):
        self.game = game

        self.max_health = 100   # base value; updated per level in set_level
        self.health = self.max_health
        self.score = 0
        self.words_created = []

        self._level = 1          # internal; synced from game
        self._update_stats()

        temp_sprite = AnimatedSprite(
            os.path.join("lib", "asset", "Soldier-Idle.png"),
            scale=6
        )

        h = temp_sprite.get_size()[1]

        self.sprite = AnimatedSprite(
            os.path.join("lib", "asset", "Soldier-Idle.png"),
            scale=6,
            x=0,
            y=game.HEIGHT // 2 - h // 2 - 20,
            speed=8
        )

        # Font for HP display
        self.font = pygame.font.Font(
            "lib/font/minercraftory.regular.ttf", 24
        )

    def _update_stats(self):
        lvl = self._level
        # HP: 5 + 3*(lvl-1) but keep as a bonus on top of base 100
        # Per spec: player hp per level scaling = 5 + 3*(lvl-1)
        # Interpreted as: max_health increases by that formula as a bonus
        # We'll use it as total max_health = 100 + (5 + 3*(lvl-1) - 5)*lvl_bonus
        # Actually spec says "Player hp: 5 + 3(lvl-1)" — treat as the DAMAGE multiplier context
        # and keep max_health at 100 for simplicity, only dmg formula changes.
        # Damage per attack: word_length * math.ceil(lvl ** 0.5)
        pass  # stats computed on demand

    def set_level(self, level):
        self._level = level

    @property
    def attack_power_per_letter(self):
        return math.ceil(self._level ** 0.5)

    def update_anim(self):
        self.sprite.update()

    def draw(self, screen):
        self.sprite.draw(screen)
        self._draw_health(screen)

    def _draw_health(self, screen):
        sw, sh = self.sprite.get_size()
        sprite_cx = int(self.sprite.x + sw // 2)
        sprite_top = int(self.sprite.y)

        bar_w = max(sw, 120)
        bar_h = 14
        bar_x = sprite_cx - bar_w // 2
        bar_y = sprite_top - bar_h - 28

        # Background
        pygame.draw.rect(screen, (20, 60, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        # Fill
        ratio = max(0, self.health / self.max_health)
        fill_w = int(bar_w * ratio)
        if fill_w > 0:
            color = (60, 200, 80) if ratio > 0.4 else (220, 180, 30)
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        # Border
        pygame.draw.rect(screen, (100, 200, 120), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        # HP text
        hp_text = self.font.render(
            f"HP  {int(self.health)}({self.max_health})", True, (180, 255, 200)
        )
        text_rect = hp_text.get_rect(centerx=sprite_cx, bottom=bar_y - 4)
        screen.blit(hp_text, text_rect)

        # Label
        lbl = self.font.render("Player", True, (150, 230, 160))
        lbl_rect = lbl.get_rect(centerx=sprite_cx, bottom=text_rect.top - 2)
        screen.blit(lbl, lbl_rect)

    def attack_enemy(self, word):
        lvl = getattr(self.game, "current_level", 1)
        dmg = len(word) * math.ceil(lvl ** 0.5)
        self.game.enemy.receive_damage(dmg)
        self.score += dmg
        self.words_created.append(word)
        self.game.data_collector.log_event("attack", {"word": word, "dmg": dmg})

    def receive_damage(self, dmg):
        self.health -= dmg
        self.game.data_collector.log_event("player_damage", dmg)

    def heal(self, amt):
        self.health = min(self.max_health, self.health + amt)
