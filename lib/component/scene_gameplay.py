import pygame
from lib.component import assets
from lib.component.ability import ABILITY_COLORS
from lib.component.board import Board
from lib.component.button import Button
from lib.component.config import Config
from lib.component.scene_base import BaseScene, MENU_RED
from lib.component.ui import dim_screen, shadow_text

ATTACK_READY = (50, 200, 80)
ATTACK_IDLE = (80, 80, 80)
REROLL_READY = (160, 100, 20)
REROLL_EMPTY = (80, 60, 40)

TEXT = (220, 220, 220)
GOLD = (255, 220, 80)

HELP_INTRO = [
    ("Build words from the tiles on the board.", TEXT),
    ("Click tiles to select them, click again to deselect.", TEXT),
    ("Press Attack to deal damage when a valid word is selected.", TEXT),
    ("Damage depends on word length.", (255, 40, 40)),
    ("After your attack the enemy strikes back.", TEXT),
    ("Survive as many levels as you can!", TEXT),
]
HELP_TILES = [
    ("n",      "Normal - no bonus"),
    ("green",  "Green - heals you for 10 percent of your max HP per tile"),
    ("orange", "Orange - add 25 percent damage multiplier"),
    ("red",    "Red - add 50 percent damage multiplier"),
    ("gray",   "Gray - add 100 percent damage multiplier"),
    ("blue",   "Blue - freezes enemy for 1 turn (skip their attack)"),
    ("purple", "Purple - weakens enemy for 1 turn (reduces enemy damage by 50 percent)"),
]
HELP_ENEMY = [
    "Green - enemy heals itself",
    "Blue - enemy attacks twice in a row",
    "Purple - weakens player for 1 turn (reduces player damage by 50 percent)",
]
HELP_TOOLS = [
    f"Hint - reveals the longest possible word. Penalises you for {Config.hint_penalty} turns (0 damage).",
    f"Reroll - shuffles the entire board. You get {Config.max_reroll} rerolls, "
    f"and add 1 every {Config.reroll_bonus_every} completed levels.",
]


class GameplayScene(BaseScene):

    def __init__(self, game):
        super().__init__(game)
        self.attack_locked = False
        self.rerolls = Config.max_reroll
        self._last_reroll_lvl = 0
        self._show_help = False
        self._last_valid_word = ""
        self._player_in_front = True    # whoever is attacking is drawn on top

        self.death_font = assets.font(90)
        self.score_font = assets.font(32)
        self.hint_font = assets.font(26)
        self.help_font = assets.font(18)
        self.help_title_font = assets.font(30)

        sound = self.click_sound
        self.attack_button = Button(675, 425, 250, 75, "Attack", self._try_attack, sound,
                                    font_size=36, color=(120, 120, 120))
        self.hint_button = Button(20, 730, 150, 50, "Hint", self._use_hint, sound,
                                  font_size=24, color=(80, 80, 200))
        self.reroll_button = Button(1270, 730, 150, 50, "Reroll", self._use_reroll, sound,
                                    font_size=24, color=REROLL_READY)
        self.help_button = Button(180, 730, 200, 50, "How to Play", self._toggle_help, sound,
                                  font_size=22, color=(40, 120, 40))
        self.back_button = Button(1430, 730, 150, 50, "Back", self._back_to_menu, sound, color=MENU_RED)
        self.buttons = [self.back_button, self.attack_button, self.hint_button,
                        self.reroll_button, self.help_button]

        original = assets.image("board.png")
        target_w = int(self.width * 0.4)
        target_h = int(original.get_height() * target_w / original.get_width())
        self.board_image = pygame.transform.scale(original, (target_w, target_h))
        self.board_rect = self.board_image.get_rect(centerx=self.width // 2, bottom=self.height)
        self.board = Board((self.width, self.height), self.board_rect, game, self.click_sound)

    @property
    def player(self):
        return self.game.player

    @property
    def enemy(self):
        return self.game.enemy

    @property
    def _input_blocked(self):
        return self.player.is_dead or self._show_help

    # Scene hooks

    def on_enter(self):
        assets.play_music("ambient")

    def restore_from_save(self, save_data):
        self.rerolls = save_data.get("player_rerolls", Config.max_reroll)
        if "tiles" in save_data:
            self.board.load_snapshot(save_data["tiles"])

    # Button actions

    def _back_to_menu(self):
        self.game.save_and_log_close()
        self.game.switch_scene("menu")

    def _toggle_help(self):
        self._show_help = not self._show_help

    def _use_hint(self):
        if self.attack_locked or self._input_blocked:
            return
        word = self.board.longest_possible_word()
        if word:
            self.enemy.status_text.show(f"The word is {word}", (255, 255, 255))
        self.player.use_hint()

    def _use_reroll(self):
        if self.rerolls <= 0 or self._input_blocked:
            return
        self.rerolls -= 1
        self.board.reroll()

    def _try_attack(self):
        if self.attack_locked or self._input_blocked:
            return
        taken = self.board.take_word()
        if taken is None:
            return
        self.attack_locked = True
        self._player_in_front = True
        self._last_valid_word = ""
        word, abilities = taken
        self.player.attack_enemy(word, abilities, on_complete=self._on_player_turn_done)

    # Turn flow

    def _on_player_turn_done(self):
        enemy = self.enemy
        if enemy.health <= 0 or enemy.is_dead:
            self._on_level_complete()
            return

        self._player_in_front = False
        if enemy.frozen_turns > 0:
            # Frozen enemies skip their turn
            enemy.frozen_turns -= 1
            enemy.refresh_status_color()
            self.attack_locked = False
            return

        enemy.trigger_attack_sequence(on_complete=self._on_enemy_turn_done)

    def _on_enemy_turn_done(self):
        if self.player.is_dead:
            return
        self.attack_locked = False
        self._player_in_front = True

    def _on_level_complete(self):
        self.game.next_level()
        self.attack_locked = False
        self._player_in_front = False
        self.game.save()

    # Frame

    def handle_event(self, event):
        clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

        if self._show_help:
            if clicked:
                self._show_help = False
            return

        if self.player.is_dead:
            if clicked:
                self.game.data_collector.delete_save()
                self.game.switch_scene("menu")
            return

        super().handle_event(event)
        self.board.handle_event(event)

    def update(self):
        self.board.update()

        lvl = self.game.current_level
        if lvl % Config.reroll_bonus_every == 0 and lvl != self._last_reroll_lvl:
            self._last_reroll_lvl = lvl
            self.rerolls = min(Config.max_reroll, self.rerolls + 1)

        if self.board.is_current_word_valid():
            self.attack_button.set_color(ATTACK_READY)
            word = self.board.current_word()
            if word != self._last_valid_word:
                assets.play_sfx("notify", volume=Config.noti_volume)
                self._last_valid_word = word
        else:
            self.attack_button.set_color(ATTACK_IDLE)
            self._last_valid_word = ""

        self.reroll_button.text = f"Reroll ({self.rerolls})"
        self.reroll_button.set_color(REROLL_READY if self.rerolls > 0 else REROLL_EMPTY)

    def draw(self):
        self.draw_background()

        back, front = (self.enemy, self.player) if self._player_in_front else (self.player, self.enemy)
        back.draw(self.screen)
        front.draw(self.screen)

        self.screen.blit(self.board_image, self.board_rect)
        self.draw_buttons()
        self.board.draw(self.screen)
        self._draw_hud()

        if self.player.is_dead:
            self._draw_death_overlay()
        elif self._show_help:
            self._draw_help_overlay()

    # Drawing helpers

    def _draw_hud(self):
        text = f"LEVEL {self.game.current_level} ({self.player.score})"
        shadow_text(self.screen, self.score_font, text, (255, 220, 100),
                    centerx=self.width // 2, top=10)

    def _draw_death_overlay(self):
        dim_screen(self.screen, 255 * 0.8)
        cx, cy = self.width // 2, self.height // 2
        shadow_text(self.screen, self.death_font, "You Failed", (220, 50, 50),
                    shadow_color=(60, 0, 0), offset=(4, 4), centerx=cx, centery=cy - 60)
        score = self.score_font.render(f"Score {self.player.score}", True, (255, 220, 100))
        self.screen.blit(score, score.get_rect(centerx=cx, centery=cy + 30))
        tip = self.hint_font.render("Click anywhere to continue", True, (180, 180, 180))
        self.screen.blit(tip, tip.get_rect(centerx=cx, centery=cy + 100))

    def _draw_help_overlay(self):
        dim_screen(self.screen, 255 * 0.9)
        cx = self.width // 2
        top = 10
        line_h = 25

        def centered(text, y, color=TEXT, font=None):
            lbl = (font or self.help_font).render(text, True, color)
            self.screen.blit(lbl, lbl.get_rect(centerx=cx, top=top + y))

        def title(text, y, color=GOLD):
            centered(text, y, color, self.help_title_font)

        title("HOW TO PLAY", 0)
        for i, (text, color) in enumerate(HELP_INTRO):
            centered(text, 40 + i * line_h, color)

        y = 40 + line_h * 7
        title("TILE ABILITIES", y)
        dot = 16
        for i, (key, desc) in enumerate(HELP_TILES):
            row_y = top + y + 44 + i * line_h
            pygame.draw.rect(self.screen, ABILITY_COLORS[key],
                             (cx - 340, row_y + (line_h - dot) // 2, dot, dot), border_radius=4)
            self.screen.blit(self.help_font.render(desc, True, TEXT), (cx - 310, row_y))

        y += 44 + len(HELP_TILES) * line_h + 20
        title("ENEMY ABILITIES", y, (255, 100, 100))
        for i, desc in enumerate(HELP_ENEMY):
            centered(desc, y + 44 + i * line_h, (220, 180, 180))

        y += 44 + len(HELP_ENEMY) * line_h + 20
        title("HINTS and REROLLS", y)
        for i, desc in enumerate(HELP_TOOLS):
            centered(desc, y + 44 + i * line_h)

        y += 44 + len(HELP_TOOLS) * line_h + 30
        centered("Click anywhere to close", y, (180, 180, 180), self.hint_font)
