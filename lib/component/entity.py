from lib.component import assets
from lib.component.ability import ABILITY_COLORS, FREEZE, WEAKEN
from lib.component.animated_sprite import AnimatedSprite
from lib.component.config import Config
from lib.component.effect_text import EffectText

FORWARD = "forward"
BACK = "back"
STATUS_TEXT_Y = 250


class Entity:
    """
    Shared behaviour of the player and the enemy:
    sprites, the walk -> attack -> walk back sequence, hurt / death animations,
    HP and the freeze / weaken status effects.
    """

    SPRITE_PREFIX = ""          # "Soldier" -> Soldier-Idle.png, Soldier-Walk.png, ...
    FACES_LEFT = False          # mirror every sprite (enemy stands on the right)
    HURT_SFX = ""
    STATUS_TEXT_DURATION = 3000

    def __init__(self, game, level, max_health, health=None):
        self.game = game
        self.level = level
        self.max_health = max_health
        self.health = max_health if health is None else health

        self.frozen_turns = 0
        self.weakened_turns = 0

        self._steps = []
        self._step_idx = 0
        self._busy = False
        self._is_dead = False
        self._is_hurting = False
        self._on_complete = None
        self._walk_step = Config.entity_walking_speed

        self.sprites = self._build_sprites()
        w, h = self.sprites["idle"].get_size()
        self._home_x = self._get_home_x(w)
        self._target_x = self._get_target_x()
        self._base_y = game.HEIGHT // 2 - h // 2 - 20
        self._cur_x = float(self._home_x)
        self._cur_sprite = self.sprites["idle"]
        self._sync_sprites()

        self.hp_bar = self._make_hp_bar()
        self.hp_bar.snap(self.health, self.max_health)
        self.status_text = EffectText(26, (2, 2), duration=self.STATUS_TEXT_DURATION)

    # Hooks for subclasses

    def _get_home_x(self, sprite_w):
        raise NotImplementedError

    def _get_target_x(self):
        raise NotImplementedError

    def _make_hp_bar(self):
        raise NotImplementedError

    def _hp_bar_labels(self):
        return f"HP {int(self.health)}({self.max_health})", None

    def _on_attack_frame(self, payload):
        """Called when an attack step starts (the moment the hit lands)."""

    def _on_death(self):
        """Extra work when the death animation starts (sounds, flags...)."""

    # State

    @property
    def is_dead(self):
        return self._is_dead

    @property
    def is_busy(self):
        return self._busy

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def apply_freeze(self, turns):
        self.frozen_turns += turns
        self.refresh_status_color()

    def apply_weaken(self, turns):
        self.weakened_turns += turns
        self.refresh_status_color()

    def refresh_status_color(self):
        """Tint the HP bar with the active status effect (freeze wins over weaken)."""
        if self.frozen_turns > 0:
            self.hp_bar.override_color = ABILITY_COLORS[FREEZE]
        elif self.weakened_turns > 0:
            self.hp_bar.override_color = ABILITY_COLORS[WEAKEN]
        else:
            self.hp_bar.override_color = None

    def debuffs(self):
        """Active status effects as {ability_name: turns_remaining} (used by the save file)."""
        found = {FREEZE: self.frozen_turns, WEAKEN: self.weakened_turns}
        return {k: v for k, v in found.items() if v > 0}

    def load_debuffs(self, debuffs):
        self.frozen_turns = debuffs.get(FREEZE, 0)
        self.weakened_turns = debuffs.get(WEAKEN, 0)
        self.refresh_status_color()

    # Sprites

    def _build_sprites(self):
        def make(action, one_shot=False, mirrored=False):
            return AnimatedSprite(f"{self.SPRITE_PREFIX}-{action}.png",
                                  scale=Config.entity_sprite_scale, one_shot=one_shot,
                                  flip=self.FACES_LEFT != mirrored)

        return {
            "idle":    make("Idle"),
            "walk_f":  make("Walk"),
            "walk_b":  make("Walk", mirrored=True),
            "attack1": make("Attack01", one_shot=True),
            "attack2": make("Attack02", one_shot=True),
            "hurt":    make("Hurt", one_shot=True),
            "death":   make("Death", one_shot=True),
        }

    def _set_sprite(self, key, speed=None):
        sprite = self.sprites[key]
        if speed is not None:
            sprite.speed = speed
        sprite.reset()
        sprite.x, sprite.y = int(self._cur_x), self._base_y
        self._cur_sprite = sprite

    def _sync_sprites(self):
        for s in self.sprites.values():
            s.x = int(self._cur_x)
            s.y = self._base_y

    # Hurt / death

    def play_hurt(self):
        if self._is_dead or self._busy:
            return
        self._is_hurting = True
        self._set_sprite("hurt")
        assets.play_sfx(self.HURT_SFX)

    def play_death(self):
        self._is_dead = True
        self._set_sprite("death")
        self._on_death()

    # Attack sequence: walk forward -> attack(s) -> walk back

    def _start_sequence(self, attacks, walk_step, anim_speed, on_complete=None):
        """`attacks` is a list of (sprite_key, payload); payload goes to _on_attack_frame."""
        self._busy = True
        self._on_complete = on_complete
        self._walk_step = walk_step
        self._steps = ([("walk", FORWARD, anim_speed)]
                       + [("attack", key, payload) for key, payload in attacks]
                       + [("walk", BACK, anim_speed)])
        self._step_idx = 0
        self._enter_step()

    def _enter_step(self):
        if self._step_idx >= len(self._steps):
            self._finish()
            return
        kind, arg, extra = self._steps[self._step_idx]
        if kind == "walk":
            self._set_sprite("walk_f" if arg == FORWARD else "walk_b", speed=extra)
        else:
            self._set_sprite(arg)
            self._on_attack_frame(extra)

    def _next_step(self):
        self._step_idx += 1
        self._enter_step()

    def _advance_step(self):
        kind, arg, _ = self._steps[self._step_idx]
        if kind == "attack":
            if self._cur_sprite.done:
                self._next_step()
            return

        dest = self._target_x if arg == FORWARD else self._home_x
        if dest > self._cur_x:
            self._cur_x = min(self._cur_x + self._walk_step, dest)
        else:
            self._cur_x = max(self._cur_x - self._walk_step, dest)
        if self._cur_x == dest:
            self._cur_x = float(dest)
            self._next_step()

    def _finish(self):
        self._busy = False
        self._cur_x = float(self._home_x)
        self._walk_step = Config.entity_walking_speed
        self._set_sprite("idle")
        self._sync_sprites()
        if self._on_complete:
            callback, self._on_complete = self._on_complete, None
            callback()

    # Frame

    def update_anim(self):
        sprite = self._cur_sprite
        sprite.update()

        if self._is_dead:
            if sprite.done:
                self._busy = False
        elif self._is_hurting:
            if sprite.done:
                self._is_hurting = False
                self._set_sprite("idle")
        elif self._busy and self._step_idx < len(self._steps):
            self._advance_step()

        self._sync_sprites()
        self.hp_bar.tick(self.health, self.max_health)

    def draw(self, screen):
        self._cur_sprite.draw(screen)
        self.hp_bar.draw(screen, *self._hp_bar_labels())
        cx = int(self._cur_x) + self.sprites["idle"].get_size()[0] // 2
        self.status_text.draw(screen, cx, STATUS_TEXT_Y)
