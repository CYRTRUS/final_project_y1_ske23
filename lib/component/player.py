from lib.component.animated_sprite import AnimatedSprite
import os


class Player:
    def __init__(self, game):
        self.game = game
        self.health = 100
        self.score = 0
        self.words_created = []

        temp_sprite = AnimatedSprite(
            os.path.join("lib", "asset", "Soldier-Idle.png"),
            scale=6
        )

        h = temp_sprite.get_size()[1]

        self.sprite = AnimatedSprite(
            os.path.join("lib", "asset", "Soldier-Idle.png"),
            scale=6,
            x=0,
            y=game.HEIGHT//2 - h//2 - 20,
            speed=12
        )

    def update_anim(self):
        self.sprite.update()

    def draw(self, screen):
        self.sprite.draw(screen)

    def attack_enemy(self, word):
        dmg = len(word)*10
        self.game.enemy.receive_damage(dmg)
        self.score += dmg
        self.words_created.append(word)

    def receive_damage(self, dmg):
        self.health -= dmg
        self.game.data_collector.log_event("player_damage", dmg)

    def heal(self, amt):
        self.health = min(100, self.health+amt)
