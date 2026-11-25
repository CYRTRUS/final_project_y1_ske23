import math
from collections import Counter
from lib.component import assets
from lib.component.ability import BOOST_MULTIPLIERS
from lib.component.config import Config
from lib.component.entity import Entity
from lib.component.hp_bar import HpBar


def base_damage(word, level):
    return int(len(word) * math.ceil(level ** 0.55) + Config.player_base_dmg)


def word_bonus_multiplier(word):
    """Bonus for words with x / y / z, or ending in r, y, es or <consonant>s."""
    hits = (word.count("x") + word.count("y") + word.count("z")
            + word.endswith("r") + word.endswith("y") + word.endswith("es")
            + (word.endswith("s") and len(word) > 1 and word[-2] not in "aeiou"))
    return Config.word_bonus_multiplier ** hits


class Player(Entity):
    SPRITE_PREFIX = "Soldier"
    HURT_SFX = "blood_sound"

    def __init__(self, game, level=1, health=None, score=0):
        max_health = self.max_hp_for(level)
        health = max_health if health is None else min(health, max_health)
        super().__init__(game, level, max_health, health)
        self.score = score
        self.hint_penalty_turns = 0
        self.hint_grace = False
        self._pending_attack = None

    @staticmethod
    def max_hp_for(level):
        return int(Config.player_base_hp + Config.player_factor_hp * (level - 1))

    def set_level(self, level):
        self.level = level
        self.max_health = self.max_hp_for(level)
        self.health = min(self.health, self.max_health)
        self.hp_bar.snap(self.health, self.max_health)

    def use_hint(self):
        self.hint_penalty_turns += Config.hint_penalty
        self.hint_grace = True

    # Entity hooks

    def _get_home_x(self, sprite_w):
        return 0

    def _get_target_x(self):
        return int(self.game.WIDTH * 0.55)

    def _make_hp_bar(self):
        return HpBar(20, 10, 500, 22, (60, 200, 80), (20, 60, 20), (100, 200, 120),
                     assets.font(22), pad=20, rtl=False)

    def _on_death(self):
        assets.play_sfx("player_die")
        assets.play_sfx("fail_sound")

    # Attacking

    def attack_enemy(self, word, abilities, on_complete=None):
        if self._busy or self._is_dead:
            return
        self._pending_attack = (word, abilities)

        boosted = any(a in BOOST_MULTIPLIERS for a in abilities)
        if boosted:
            assets.play_sfx("boosted")
            walk_step = int(Config.entity_walking_speed / Config.entity_lunge_speed)
            anim_speed = 2
        else:
            walk_step = Config.entity_walking_speed
            anim_speed = 8

        attack = ("attack2", 2) if boosted else ("attack1", 1)   # (sprite, swing sfx variant)
        self._start_sequence([attack], walk_step, anim_speed, on_complete)

    def _on_attack_frame(self, swing_variant):
        assets.play_sfx("player_attack", variant=swing_variant)
        self._resolve_attack()

    def _resolve_attack(self):
        word, abilities = self._pending_attack
        enemy = self.game.enemy
        enemy.status_text.hide()

        counts = Counter(abilities)
        self._apply_support_abilities(counts, enemy)

        dmg = max(0, math.ceil(base_damage(word, self.level) * self._damage_multiplier(word, counts)))
        if any(cheat in word for cheat in Config.cheat_words):
            dmg = Config.cheat_damage

        self.score += len(word)
        self.game.data_collector.log_attack(word, dmg, self.game.current_level)
        enemy.receive_damage(dmg)

    def _apply_support_abilities(self, counts, enemy):
        """Green heals the player, blue freezes the enemy, purple weakens it."""
        if counts["green"] and self.health != self.max_health:
            self.heal(math.ceil(counts["green"] * Config.heal_amount * self.max_health))
            assets.play_sfx("heal")

        if counts["blue"]:
            enemy.apply_freeze(counts["blue"] * Config.num_frozen_turn + 1)
            assets.play_sfx("freeze")

        if counts["purple"]:
            enemy.apply_weaken(counts["purple"] * Config.num_weaken_turn)
            assets.play_sfx("weaken")

    def _damage_multiplier(self, word, counts):
        mult = Config.base_dmg_multiplier
        mult *= word_bonus_multiplier(word)
        for ability, boost in BOOST_MULTIPLIERS.items():
            if counts[ability]:
                mult *= boost ** counts[ability]

        # Hint penalty: the attack right after using a hint is free, the next ones deal 0
        if self.hint_grace:
            self.hint_grace = False
        elif self.hint_penalty_turns > 0:
            mult = 0.0
            self.hint_penalty_turns -= 1

        if self.weakened_turns > 0:
            mult *= Config.weaken_amount
            self.weakened_turns -= 1
            self.refresh_status_color()
        return mult

    # Taking damage

    def receive_damage(self, dmg):
        dmg = max(0, dmg)
        if self.frozen_turns > 0:
            self.frozen_turns -= 1
            self.refresh_status_color()
        self.health = max(0, self.health - dmg)
        self.game.data_collector.log_damage_received(dmg, self.game.current_level)
        if self.health <= 0:
            self.play_death()
            self.game.data_collector.log_death()
        else:
            self.play_hurt()
