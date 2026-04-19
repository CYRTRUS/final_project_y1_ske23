import math
import os
import random
import pygame
from lib.component.animated_sprite import AnimatedSprite
from lib.component.hp_bar import HpBar
from lib.component.effect_text import EffectText
from lib.component.tile import roll_enemy_ability
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


class Enemy:
    def __init__(self, game, level=1, health=None):
        self.game = game
        self.level = level

        self.max_health = Config.enemy_base_hp + Config.enemy_factor_hp * (level - 1)
        self.health = health if health is not None else self.max_health

        threshold = Config.enemy_threshold_dmg
        attack_damage_min = round(Config.enemy_base_dmg + Config.enemy_factor_dmg * (level - 1) * (100 - threshold)/100, 0)
        attack_damage_max = round(Config.enemy_base_dmg + Config.enemy_factor_dmg * (level - 1) * (100 + threshold)/100, 0)
        self.attack_damage = random.randint(int(attack_damage_min), int(attack_damage_max))

        self.frozen_turns = 0
        self.weakened_turns = 0
        self.leveling_up = False

        self._steps = []
        self._step_idx = 0
        self._busy = False
        self._is_dead = False
        self._is_hurting = False
        self._on_complete = None
        self._walk_step = Config.entity_walking_speed
        self._cur_x = 0.0
        self._pending_ability = "n"

        scale = getattr(game, "enemy_scale", 6)

        def make(name, one_shot=False, speed=8, flip=False):
            sp = AnimatedSprite(os.path.join("lib", "asset", name), scale=scale, x=0, y=0, speed=speed, one_shot=one_shot)
            if flip:
                sp.flip(True, False)
            return sp

        self.sprites = {
            "idle":    make("Orc-Idle.png", flip=True),
            "walk_f":  make("Orc-Walk.png", flip=True),
            "walk_b":  make("Orc-Walk.png"),
            "attack1": make("Orc-Attack01.png", one_shot=True, flip=True),
            "attack2": make("Orc-Attack02.png", one_shot=True, flip=True),
            "hurt":    make("Orc-Hurt.png", one_shot=True, flip=True),
            "death":   make("Orc-Death.png", one_shot=True, flip=True),
        }

        w, h = self.sprites["idle"].get_size()
        self._base_x = game.WIDTH - w - 50
        self._base_y = game.HEIGHT // 2 - h // 2 - 20
        self._cur_x = float(self._base_x)
        self._target_x = int(game.WIDTH * 0.05)

        for sp in self.sprites.values():
            sp.x = self._base_x
            sp.y = self._base_y

        self._cur_sprite = self.sprites["idle"]

        bar_x = game.WIDTH - 500 - 20
        font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 22)
        self.hp_bar = HpBar(bar_x, 10, 500, 22, (200, 50, 50), (80, 20, 20), (200, 160, 100), font, pad=20, rtl=True)

        self.hint_y_offset = -60
        self.hint_font_size = 26
        self.hint_shadow = (2, 2)
        self.hint_text = EffectText("lib/font/minercraftory.regular.ttf", self.hint_font_size, self.hint_shadow, duration=None)

    def _update_hp_bar_color(self):
        # Purple is drawn first, blue overrides (blue has higher priority)
        if self.weakened_turns > 0:
            self.hp_bar.override_color = (160, 60, 220)
        if self.frozen_turns > 0:
                self.hp_bar.override_color = (60, 120, 240)
        if self.weakened_turns == 0 and self.frozen_turns == 0:
            self.hp_bar.override_color = None

    def receive_damage(self, dmg):
        if self.frozen_turns > 1:
            self.frozen_turns -= 1
        self.health = max(0, self.health - max(0, dmg))

    def trigger_hurt_animation(self):
        if self._is_dead or self._busy or self.leveling_up:
            return
        self._is_hurting = True
        sp = self.sprites["hurt"]
        sp.x = int(self._cur_x)
        sp.y = self._base_y
        sp.reset()
        self._cur_sprite = sp
        _play_sfx(Config.enemy_hurt, Config.enemy_hurt_var)

    def trigger_death_animation(self):
        self._is_dead = True
        self._busy = True
        self._on_complete = None
        self.leveling_up = True
        sp = self.sprites["death"]
        sp.x = int(self._cur_x)
        sp.y = self._base_y
        sp.reset()
        self._cur_sprite = sp
        _play_sfx(Config.enemy_die, Config.enemy_die_var)

    def trigger_attack_sequence(self, on_complete=None):
        if self._busy or self._is_dead or self.leveling_up:
            return

        self._on_complete = on_complete
        self._busy = True

        self._pending_ability = roll_enemy_ability(self.level)
        ability = self._pending_ability

        if ability != "n":
            self._walk_step = int(Config.entity_walking_speed / Config.entity_lunge_speed)
            _play_sfx(Config.enemy_idle, Config.enemy_idle_var)
        else:
            self._walk_step = Config.entity_walking_speed

        atk1 = f"attack{random.randint(1, 2)}"
        atk2 = f"attack{random.randint(1, 2)}"

        if ability == "blue":
            self._steps = [
                ("walk_f",),
                ("attack", atk1, 1),
                ("attack", atk2, 2),
                ("walk_b",),
                ("idle",),
            ]
        else:
            self._steps = [
                ("walk_f",),
                ("attack", atk1, 1),
                ("walk_b",),
                ("idle",),
            ]

        self._step_idx = 0
        self._exec_step()

    def _exec_step(self):
        if self._step_idx >= len(self._steps):
            self._finish()
            return

        step = self._steps[self._step_idx]
        tag = step[0]

        if tag == "walk_f":
            sp = self.sprites["walk_f"]
            sp.speed = self._walk_step
            sp.reset()
            sp.x = int(self._cur_x)
            sp.y = self._base_y
            self._cur_sprite = sp

        elif tag == "attack":
            sp = self.sprites[step[1]]
            hit_num = step[2]
            sp.reset()
            sp.x = int(self._cur_x)
            sp.y = self._base_y
            self._cur_sprite = sp
            _play_sfx(Config.enemy_attack, Config.enemy_attack_var)
            self._resolve_attack(hit_num)

        elif tag == "walk_b":
            sp = self.sprites["walk_b"]
            sp.speed = self._walk_step
            sp.reset()
            sp.x = int(self._cur_x)
            sp.y = self._base_y
            self._cur_sprite = sp

        elif tag == "idle":
            self._finish()

    def _finish(self):
        self._busy = False
        self._cur_x = float(self._base_x)
        self._walk_step = Config.entity_walking_speed
        self._cur_sprite = self.sprites["idle"]
        self.sprites["idle"].reset()
        self._sync_sprites()

        if self._on_complete:
            cb = self._on_complete
            self._on_complete = None
            cb()

    def _resolve_attack(self, hit_num=1):
        if self.leveling_up or self.health <= 0 or self._is_dead:
            return

        player = self.game.player
        ability = self._pending_ability
        dmg = self.attack_damage

        if self.weakened_turns > 0:
            dmg = math.ceil(dmg * Config.weaken_amount)
            self.weakened_turns -= 1
            self._update_hp_bar_color()

        if not player._is_dead:
            player.receive_damage(max(0, dmg))

        # Blue: hit1 applies freeze to player, hit2 clears it (enemy attacks twice)
        if ability == "blue":
            if hit_num == 1:
                player.frozen_turns += Config.num_frozen_turn
                player._update_hp_bar_color()
                player.effect_text.show("Enemy attacks twice!", (60, 120, 240))
                _play_sfx(Config.freeze, Config.freeze_var)
            else:
                # Second hit clears the freeze state display
                player._update_hp_bar_color()
            return

        if hit_num != 1:
            return

        if ability == "green":
            if self.health != self.max_health:
                heal_amt = math.ceil(Config.heal_amount * self.max_health)
                self.health = min(self.max_health, self.health + heal_amt)
                _play_sfx(Config.heal, Config.heal_var)
                player.effect_text.show(f"Enemy healed {heal_amt} HP!", (60, 200, 80))

        elif ability == "purple":
            player.weakened_turns += Config.num_weaken_turn
            player._update_hp_bar_color()
            player.effect_text.show("Weakened! Your damage reduced!", (160, 60, 220))
            _play_sfx(Config.weaken, Config.weaken_var)

    def update_anim(self):
        sp = self._cur_sprite
        sp.update()

        if self._is_dead:
            if sp.done:
                self._busy = False
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
                self._cur_x -= self._walk_step
                if self._cur_x <= self._target_x:
                    self._cur_x = float(self._target_x)
                    self._step_idx += 1
                    self._exec_step()

            elif tag == "attack":
                if sp.done:
                    self._step_idx += 1
                    self._exec_step()

            elif tag == "walk_b":
                self._cur_x += self._walk_step
                if self._cur_x >= self._base_x:
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
        self.hp_bar.draw(screen, left_text=f"Lv.{self.level}", right_text=f"HP {int(self.health)}({self.max_health})")
        sprite_w = self.sprites["idle"].get_size()[0]
        cx = int(self._cur_x) + sprite_w // 2
        self.hint_text.draw(screen, cx, 250)
