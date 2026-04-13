import pygame
import os
from lib.component.animated_sprite import AnimatedSprite


class Enemy:
    def __init__(self, game, level=1):
        self.game = game
        self.level = level
        self.health = 50 + level * 25
        self.attack_damage = 5 + level * 2

        self.x = 1050
        self.y = game.HEIGHT // 2

        self.flip = True

        scale = self.game.enemy_scale if hasattr(self.game, "enemy_scale") else 6

        temp = AnimatedSprite(
            os.path.join("lib", "asset", "Orc-Idle.png"),
            scale=scale
        )

        self.sprite = AnimatedSprite(
            os.path.join("lib", "asset", "Orc-Idle.png"),
            scale=scale,
            x=self.x,
            y=0,
            speed=12
        )

        h = self.sprite.get_size()[1]
        self.sprite.y = game.HEIGHT // 2 - h // 2 - 20

        self._apply_flip()

    def _apply_flip(self):
        for i in range(len(self.sprite.frames)):
            self.sprite.frames[i] = pygame.transform.flip(
                self.sprite.frames[i],
                self.flip,
                False
            )

    def update_anim(self):
        self.sprite.update()

    def draw(self, screen):
        self.sprite.draw(screen)

    def attack_player(self, player):
        player.receive_damage(self.attack_damage)

    def receive_damage(self, dmg):
        self.health -= dmg
        if self.health < 0:
            self.health = 0

    def scale_difficulty(self):
        self.level += 1
        self.health = 50 + self.level * 25
        self.attack_damage = 5 + self.level * 2
