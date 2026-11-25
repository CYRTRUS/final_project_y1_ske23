import math
import random
from lib.component import assets
from lib.component.ability import ABILITY_COLORS, NORMAL, roll_enemy_ability
from lib.component.config import Config
from lib.component.entity import Entity
from lib.component.hp_bar import HpBar


class Enemy(Entity):
    SPRITE_PREFIX = "Orc"
    FACES_LEFT = True
    HURT_SFX = "enemy_hurt"
    STATUS_TEXT_DURATION = None     # the hint stays until the next attack

    def __init__(self, game, level=1, health=None):
        super().__init__(game, level, self.max_hp_for(level), health)
        self.attack_damage = self.roll_attack_damage(level)
        self._ability = NORMAL

    @staticmethod
    def max_hp_for(level):
        return Config.enemy_base_hp + Config.enemy_factor_hp * (level - 1)

    @staticmethod
    def roll_attack_damage(level):
        """Base damage for the level, +/- enemy_threshold_dmg percent."""
        threshold = Config.enemy_threshold_dmg
        scaled = Config.enemy_factor_dmg * (level - 1)
        low = round(Config.enemy_base_dmg + scaled * (100 - threshold) / 100)
        high = round(Config.enemy_base_dmg + scaled * (100 + threshold) / 100)
        return random.randint(low, high)

    # Entity hooks

    def _get_home_x(self, sprite_w):
        return self.game.WIDTH - sprite_w - 50

    def _get_target_x(self):
        return int(self.game.WIDTH * 0.05)

    def _make_hp_bar(self):
        return HpBar(self.game.WIDTH - 500 - 20, 10, 500, 22, (200, 50, 50), (80, 20, 20), (200, 160, 100),
                     assets.font(22), pad=20, rtl=True)

    def _hp_bar_labels(self):
        return f"Lv.{self.level}", f"HP {int(self.health)}({self.max_health})"

    def _on_death(self):
        self._busy = True
        self._on_complete = None
        assets.play_sfx("enemy_die")

    # Taking damage

    def receive_damage(self, dmg):
        if self.frozen_turns > 1:
            self.frozen_turns -= 1
        self.health = max(0, self.health - max(0, dmg))
        if self.health <= 0:
            self.play_death()
            assets.play_sfx("level_up")
        else:
            self.play_hurt()

    # Attacking

    def trigger_attack_sequence(self, on_complete=None):
        if self._busy or self._is_dead:
            return

        self._ability = roll_enemy_ability(self.level)
        if self._ability != NORMAL:
            walk_step = int(Config.entity_walking_speed / Config.entity_lunge_speed)
            assets.play_sfx("enemy_idle")
        else:
            walk_step = Config.entity_walking_speed

        first = f"attack{random.randint(1, 2)}"
        second = f"attack{random.randint(1, 2)}"
        attacks = [(first, 1)]
        if self._ability == "blue":      # blue: the enemy hits twice
            attacks.append((second, 2))

        # The orc's walk animation runs at the same tick rate as its walk step
        self._start_sequence(attacks, walk_step, walk_step, on_complete)

    def _on_attack_frame(self, hit_num):
        assets.play_sfx("enemy_attack")
        self._resolve_attack(hit_num)

    def _resolve_attack(self, hit_num):
        if self._is_dead or self.health <= 0:
            return

        player = self.game.player
        dmg = self.attack_damage
        if self.weakened_turns > 0:
            dmg = math.ceil(dmg * Config.weaken_amount)
            self.weakened_turns -= 1
            self.refresh_status_color()

        if not player.is_dead:
            player.receive_damage(max(0, dmg))

        if self._ability == "blue":
            if hit_num == 1:
                player.apply_freeze(Config.num_frozen_turn)
                player.status_text.show("Enemy attacks twice!", ABILITY_COLORS["blue"])
                assets.play_sfx("freeze")
            else:
                player.refresh_status_color()
        elif self._ability == "green":
            if self.health != self.max_health:
                heal_amt = math.ceil(Config.heal_amount * self.max_health)
                self.heal(heal_amt)
                assets.play_sfx("heal")
                player.status_text.show(f"Enemy healed {heal_amt} HP!", ABILITY_COLORS["green"])
        elif self._ability == "purple":
            player.apply_weaken(Config.num_weaken_turn)
            player.status_text.show("Weakened! Your damage reduced!", ABILITY_COLORS["purple"])
            assets.play_sfx("weaken")
