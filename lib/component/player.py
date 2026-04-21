import math
import os
import random
import pygame
from lib.component.animated_sprite import AnimatedSprite
from lib.component.hp_bar import HpBar
from lib.component.effect_text import EffectText
from lib.component.config import Config

SFX = {}


def _load_sfx(name):
    if name not in SFX:
        try:
            SFX[name] = pygame.mixer.Sound(os.path.join("lib", "sfx", name))
        except Exception:
            SFX[name] = None
    return SFX[name]


def _play(name):
    s = _load_sfx(name)
    if s:
        s.set_volume(Config.sfx_volume / 100)
        s.play()


def _play_sfx(base, var):
    _play(f"{base}_{random.randint(1, var)}.mp3")


class Player:
    def __init__(self, game, health=None, score=0):
        self.game = game
        self._level = getattr(game, "current_level", 1)

        self.max_health = self._calc_max_hp(self._level)
        self.health = health if health is not None else self.max_health
        self.score = score
        self.words_created = []

        self.frozen_turns = 0
        self.weakened_turns = 0
        self.hint_penalty_turns = 0
        self.hint_grace = False

        self._pending_word = ""
        self._pending_abilities = []
        self._on_complete = None
        self._steps = []
        self._step_idx = 0
        self._busy = False
        self._is_dead = False
        self._is_hurting = False
        self._cur_x = 0.0
        self._cur_walk_step = Config.entity_walking_speed

        self._build_sprites()

        font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 22)
        self.hp_bar = HpBar(20, 10, 500, 22, (60, 200, 80), (20, 60, 20), (100, 200, 120), font, pad=20, rtl=False)

        self.effect_y_offset = -60
        self.effect_font_size = 26
        self.effect_shadow = (2, 2)
        self.effect_text = EffectText("lib/font/minercraftory.regular.ttf", self.effect_font_size, self.effect_shadow)

    @staticmethod
    def _calc_max_hp(level):
        return int(Config.player_base_hp + Config.player_factor_hp * (level - 1))

    def set_level(self, level):
        self._level = level
        self.max_health = self._calc_max_hp(level)
        self.health = min(self.health, self.max_health)
        self.hp_bar._ratio = self.health / max(self.max_health, 1)

    def _build_sprites(self):
        scale = 6
        temp = AnimatedSprite(os.path.join("lib", "asset", "Soldier-Idle.png"), scale=scale)
        h = temp.get_size()[1]
        self._base_y = self.game.HEIGHT // 2 - h // 2 - 20
        self._base_x = 0
        self._cur_x = float(self._base_x)
        self._target_x = int(self.game.WIDTH * 0.55)

        def make(name, one_shot=False, speed=8, flip=False):
            sp = AnimatedSprite(os.path.join("lib", "asset", name), scale=scale, x=self._base_x, y=self._base_y, speed=speed, one_shot=one_shot)
            if flip:
                sp.flip(True, False)
            return sp

        self.sprites = {
            "idle":    make("Soldier-Idle.png"),
            "walk_f":  make("Soldier-Walk.png"),
            "walk_b":  make("Soldier-Walk.png", flip=True),
            "attack1": make("Soldier-Attack01.png", one_shot=True),
            "attack2": make("Soldier-Attack02.png", one_shot=True),
            "hurt":    make("Soldier-Hurt.png", one_shot=True),
            "death":   make("Soldier-Death.png", one_shot=True),
        }
        self._cur_sprite = self.sprites["idle"]

    def _update_hp_bar_color(self):
        # Purple is drawn first, blue overrides (blue has higher priority)
        if self.weakened_turns > 0:
            self.hp_bar.override_color = (160, 60, 220) # type: ignore
        if self.frozen_turns > 0:
            self.hp_bar.override_color = (60, 120, 240) # type: ignore
        if self.weakened_turns == 0 and self.frozen_turns == 0:
            self.hp_bar.override_color = None

    def attack_enemy(self, word, abilities, on_complete=None):
        if self._busy or self._is_dead:
            return
        gameplay = self.game.scene_manager.scenes.get("gameplay")
        if gameplay:
            gameplay.attack_locked = True
        self._start_attack(word, abilities, on_complete)

    def _start_attack(self, word, abilities, on_complete=None):
        self._pending_word = word
        self._pending_abilities = abilities
        self._on_complete = on_complete
        self._busy = True

        boosted = any(a in abilities for a in ("orange", "red", "gray"))
        if boosted:
            _play_sfx(Config.boosted, Config.boosted_var)
            self._cur_walk_step = int(Config.entity_walking_speed / Config.entity_lunge_speed)
            anim_speed = 2
        else:
            self._cur_walk_step = Config.entity_walking_speed
            anim_speed = 8

        atk_key = "attack2" if boosted else "attack1"
        swing_sfx = f"{Config.player_attack}_{2 if boosted else 1}.mp3"

        self._steps = [
            ("walk_f", anim_speed),
            ("attack", atk_key, swing_sfx),
            ("walk_b", anim_speed),
            ("idle",),
        ]
        self._step_idx = 0
        self._exec_step()

    def receive_damage(self, dmg):
        dmg = max(0, dmg)
        if self.frozen_turns > 0:
            self.frozen_turns -= 1
        self.health = max(0, self.health - dmg)
        self.game.data_collector.log_damage_received(dmg, getattr(self.game, "current_level", 1))
        if self.health <= 0:
            self.trigger_death_animation()
            self.game.data_collector.log_death()
        else:
            self.trigger_hurt_animation()

    def heal(self, amt):
        self.health = min(self.max_health, self.health + amt)

    def trigger_hurt_animation(self):
        if self._is_dead or self._busy:
            return
        self._is_hurting = True
        sp = self.sprites["hurt"]
        sp.x = int(self._cur_x)
        sp.y = self._base_y
        sp.reset()
        self._cur_sprite = sp
        _play_sfx(Config.blood_sound, Config.blood_sound_var)

    def trigger_death_animation(self):
        self._is_dead = True
        sp = self.sprites["death"]
        sp.x = int(self._cur_x)
        sp.y = self._base_y
        sp.reset()
        self._cur_sprite = sp
        _play_sfx(Config.player_die, Config.player_die_var)
        _play_sfx(Config.fail_sound, Config.fail_sound_var)

    def _exec_step(self):
        if self._step_idx >= len(self._steps):
            self._finish()
            return
        step = self._steps[self._step_idx]
        tag = step[0]

        if tag == "walk_f":
            sp = self.sprites["walk_f"]
            sp.speed = step[1]
            sp.reset()
            sp.x = int(self._cur_x)
            sp.y = self._base_y
            self._cur_sprite = sp

        elif tag == "attack":
            sp = self.sprites[step[1]]
            sp.reset()
            sp.x = int(self._cur_x)
            sp.y = self._base_y
            self._cur_sprite = sp
            _play(step[2])
            self._resolve_attack()

        elif tag == "walk_b":
            sp = self.sprites["walk_b"]
            sp.speed = step[1]
            sp.reset()
            sp.x = int(self._cur_x)
            sp.y = self._base_y
            self._cur_sprite = sp

        elif tag == "idle":
            self._finish()

    def _finish(self):
        self._busy = False
        self._cur_x = float(self._base_x)
        self._cur_sprite = self.sprites["idle"]
        self.sprites["idle"].reset()
        self._sync_sprites()
        if self._on_complete:
            cb = self._on_complete
            self._on_complete = None
            cb()

    def _resolve_attack(self):
        word = self._pending_word
        abilities = self._pending_abilities
        lvl = self._level

        self.game.enemy.hint_text.hide()

        base_dmg = int(len(word) * math.ceil(lvl ** 0.55) + Config.player_base_dmg)

        mult = Config.base_dmg_multiplier

        # Ability calculation order: green, blue, purple, orange, red, gray
        green_count = abilities.count("green")
        blue_count = abilities.count("blue")
        purple_count = abilities.count("purple")
        orange_count = abilities.count("orange")
        red_count = abilities.count("red")
        gray_count = abilities.count("gray")

        if green_count > 0:
            if self.health != self.max_health:
                heal_amt = math.ceil(green_count * Config.heal_amount * self.max_health)
                self.heal(heal_amt)
                _play_sfx(Config.heal, Config.heal_var)

        if blue_count > 0:
            self.game.enemy.frozen_turns += blue_count * Config.num_frozen_turn + 1
            self.game.enemy._update_hp_bar_color()
            _play_sfx(Config.freeze, Config.freeze_var)

        if purple_count > 0:
            self.game.enemy.weakened_turns += purple_count * Config.num_weaken_turn
            self.game.enemy._update_hp_bar_color()
            _play_sfx(Config.weaken, Config.weaken_var)

        # If word contains x, y, z or ends with r, y, es, or {none_vowel}s will dealt more damgae
        mult *= 1.05**(word.count("x") + word.count("y") + word.count("z") + word.endswith("r") +
                       word.endswith("y") + word.endswith("es") + (word.endswith("s") and word[-2] not in "aeiou"))

        # Calculate damage boost
        if orange_count > 0:
            mult *= Config.orange_boost ** orange_count
        if red_count > 0:
            mult *= Config.red_boost ** red_count
        if gray_count > 0:
            mult *= Config.gray_boost ** gray_count

        if self.hint_grace:
            self.hint_grace = False
        elif self.hint_penalty_turns > 0:
            mult = 0.0
            self.hint_penalty_turns -= 1

        if self.weakened_turns > 0:
            mult *= Config.weaken_amount
            self.weakened_turns -= 1
            self._update_hp_bar_color()

        dmg = max(0, math.ceil(base_dmg * mult))

        # Easter egg
        for e_w in ["nigg", "plummet"]:
            if e_w in word:
                dmg = 1000000000

        self.game.enemy.receive_damage(dmg)
        self.score += len(word)
        self.words_created.append(word)
        self.game.data_collector.log_attack(word, dmg, getattr(self.game, "current_level", 1))

        if self.game.enemy.health <= 0:
            self.game.enemy.trigger_death_animation()
            _play_sfx(Config.level_up, Config.level_up_var)
        else:
            self.game.enemy.trigger_hurt_animation()

    def update_anim(self):
        sp = self._cur_sprite
        sp.update()

        if self._is_dead:
            self._sync_sprites()
            self.hp_bar.tick(self.health, self.max_health)
            return

        if self._is_hurting:
            if sp.done:
                self._is_hurting = False
                self._cur_sprite = self.sprites["idle"]
                self.sprites["idle"].reset()
            self._sync_sprites()
            self.hp_bar.tick(self.health, self.max_health)
            return

        if self._busy and self._step_idx < len(self._steps):
            tag = self._steps[self._step_idx][0]
            if tag == "walk_f":
                self._cur_x += self._cur_walk_step
                if self._cur_x >= self._target_x:
                    self._cur_x = float(self._target_x)
                    self._step_idx += 1
                    self._exec_step()
            elif tag == "attack":
                if sp.done:
                    self._step_idx += 1
                    self._exec_step()
            elif tag == "walk_b":
                self._cur_x -= self._cur_walk_step
                if self._cur_x <= self._base_x:
                    self._cur_x = float(self._base_x)
                    self._step_idx += 1
                    self._exec_step()

        self._sync_sprites()
        self.hp_bar.tick(self.health, self.max_health)

    def _sync_sprites(self):
        for s in self.sprites.values():
            s.x = int(self._cur_x)
            s.y = self._base_y

    def draw(self, screen):
        self._cur_sprite.draw(screen)
        self.hp_bar.draw(screen, left_text=f"HP {int(self.health)}({self.max_health})")
        sprite_w = self.sprites["idle"].get_size()[0]
        cx = int(self._cur_x) + sprite_w // 2
        self.effect_text.draw(screen, cx, 250)
