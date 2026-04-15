import os
import pygame
from lib.component.scene_base import BaseScene
from lib.component.button import Button
from lib.component.board import Board
from lib.component.enemy import Enemy
from lib.component.config import Config
from lib.component.tile import ABILITY_DEFS


class GameplayScene(BaseScene):
    noti_sound = None

    def __init__(self, screen, switch_scene_callback, click_sound, player, enemy, data_collector, game):
        super().__init__(screen, switch_scene_callback)

        if GameplayScene.noti_sound is None:
            GameplayScene.noti_sound = pygame.mixer.Sound(
                os.path.join("lib", "sfx", "noti_sound.mp3")
            )
            GameplayScene.noti_sound.set_volume(Config.noti_volume/100)

        self.player = player
        self.enemy = enemy
        self.game = game
        self.click_sound = click_sound
        self.data_collector = data_collector
        self.attack_locked = False
        self.rerolls = Config.max_reroll
        self._last_reroll_lvl = 0
        self.leveling_up = False
        self._show_help = False

        # Track last valid word so sound only plays on change
        self._last_valid_word = ""

        # True while player is attacking (draw enemy first so player appears on top)
        self.player_turn_over = True

        self.death_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 90)
        self.score_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 32)
        self.hint_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 26)
        self.help_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 18)
        self.help_title_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 30)

        self.attack_button = Button(
            675, 425, 250, 75, "Attack",
            self._try_attack, click_sound, font_size=36, color=(120, 120, 120)
        )
        self.hint_button = Button(
            20, 730, 150, 50, "Hint",
            self._use_hint, click_sound, font_size=24, color=(80, 80, 200)
        )
        self.reroll_button = Button(
            1270, 730, 150, 50, "Reroll",
            self._use_reroll, click_sound, font_size=24, color=(160, 100, 20)
        )
        self.help_button = Button(
            180, 730, 200, 50, "How to Play",
            self._toggle_help, click_sound, font_size=22, color=(40, 120, 40)
        )

        def _back():
            self.game.data_collector.log_program_closed(
                getattr(self.game, "current_level", 1)
            )
            self.game.data_collector.save_game(self.game)
            self.switch_scene_callback("menu")

        self.back_button = Button(
            1430, 730, 150, 50, "Back",
            _back, click_sound, color=(200, 50, 50)
        )

        self.buttons = [
            self.back_button, self.attack_button,
            self.hint_button, self.reroll_button, self.help_button
        ]

        board_path = os.path.join("lib", "asset", "board.png")
        original = pygame.image.load(board_path).convert_alpha()
        target_w = int(self.width * 0.4)
        target_h = int(original.get_height() * (target_w / original.get_width()))
        self.board_image = pygame.transform.scale(original, (target_w, target_h))
        rect = self.board_image.get_rect()
        self.board_x = self.width // 2 - rect.width // 2
        self.board_y = self.height - rect.height

        self.board = Board(
            self.width, self.height,
            self.board_x, self.board_y, rect.width, rect.height,
            self.click_sound, self.game
        )

    def restore_from_save(self, save_data):
        self.rerolls = save_data.get("player_rerolls", Config.max_reroll)
        if "tiles" in save_data:
            self.board.load_from_save(save_data["tiles"])

    def _toggle_help(self):
        self._show_help = not self._show_help

    def _use_hint(self):
        if self.attack_locked or self.game.player._is_dead or self._show_help:
            return
        word = self.board.get_longest_possible_word()
        if word:
            self.game.enemy.hint_text.show(f"The word is {word}", (255, 255, 255))
        self.game.player.hint_penalty_turns += Config.hint_penalty
        self.game.player.hint_grace = True

    def _use_reroll(self):
        if self.rerolls <= 0 or self.game.player._is_dead or self._show_help:
            return
        self.rerolls -= 1
        self.board.reroll_board()

    def _try_attack(self):
        if self.attack_locked or self.game.player._is_dead or self._show_help:
            return
        if self.board.is_current_word_valid():
            self.attack_locked = True
            self.player_turn_over = True

            # Reset so next valid word can trigger sound again
            self._last_valid_word = ""

            self.board.attack(on_complete=self._on_player_anim_done)

    def _on_player_anim_done(self):
        enemy = self.game.enemy

        if enemy.health <= 0 or enemy._is_dead:
            self._handle_level_complete()
            return

        if self.leveling_up:
            return

        if enemy.frozen_turns > 0:
            enemy.frozen_turns -= 1
            enemy.frozen_turns = max(enemy.frozen_turns, 0)
            if enemy.frozen_turns == 0:
                enemy.hp_bar.override_color = None  # clear blue tint when freeze ends
            self.attack_locked = False
            self.player_turn_over = False
            return

        self.player_turn_over = False
        enemy.trigger_attack_sequence(on_complete=self._on_enemy_anim_done)

    def _handle_level_complete(self):
        self.leveling_up = True
        self.game.current_level += 1
        new_lvl = self.game.current_level

        self.game.player.set_level(new_lvl)
        self.game.player.health = self.game.player.max_health

        self.game.enemy = Enemy(self.game, new_lvl)
        self.enemy = self.game.enemy

        self.leveling_up = False
        self.attack_locked = False
        self.player_turn_over = False
        self.game.data_collector.save_game(self.game)

    def _on_enemy_anim_done(self):
        if self.game.player._is_dead:
            return
        self.attack_locked = False
        self.player_turn_over = True

    def handle_event(self, event):
        if self._show_help:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._show_help = False
            return

        if self.game.player._is_dead:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.game.data_collector.delete_save()
                pygame.mixer.music.stop()
                self.switch_scene_callback("menu")
            return

        super().handle_event(event)
        self.board.handle_event(event)

    def update(self):
        self.board.update()
        self.enemy = self.game.enemy

        lvl = getattr(self.game, "current_level", 1)
        if lvl % 5 == 0 and lvl != self._last_reroll_lvl:
            self._last_reroll_lvl = lvl
            self.rerolls = min(Config.max_reroll, self.rerolls + 1)

        current_word = self.board.get_current_word()
        is_valid = self.board.is_current_word_valid()

        # Play sound when word becomes valid or changes to another valid word
        if is_valid:
            self.attack_button.set_color((50, 200, 80))

            if GameplayScene.noti_sound and current_word != self._last_valid_word:
                GameplayScene.noti_sound.play()
                self._last_valid_word = current_word

        else:
            self.attack_button.set_color((80, 80, 80))

            # Reset so next valid word will trigger sound
            self._last_valid_word = ""

        self.reroll_button.text = f"Reroll ({self.rerolls})"
        self.reroll_button.color_idle = (160, 100, 20) if self.rerolls > 0 else (80, 60, 40)

    def draw(self):
        self.draw_background()

        # Draw order: when player is attacking, draw enemy first so player appears on top
        if self.player_turn_over:
            self.game.enemy.draw(self.screen)
            self.game.player.draw(self.screen)
        else:
            self.game.player.draw(self.screen)
            self.game.enemy.draw(self.screen)

        self.screen.blit(self.board_image, (self.board_x, self.board_y))
        for b in self.buttons:
            b.draw(self.screen)
        self.board.draw(self.screen)
        self._draw_hud()

        if self.game.player._is_dead:
            self._draw_death_overlay()
        elif self._show_help:
            self._draw_help_overlay()

    def _draw_hud(self):
        lvl = getattr(self.game, "current_level", 1)
        score = getattr(self.game.player, "score", 0)
        text = f"LEVEL {lvl} ({score})"
        shadow = self.score_font.render(text, True, (20, 20, 20))
        label = self.score_font.render(text, True, (255, 220, 100))
        cx = self.width // 2
        self.screen.blit(shadow, shadow.get_rect(centerx=cx + 2, top=12))
        self.screen.blit(label, label.get_rect(centerx=cx, top=10))

    def _draw_death_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(255 * 0.8)))
        self.screen.blit(overlay, (0, 0))
        cx = self.width // 2
        cy = self.height // 2
        score = getattr(self.game.player, "score", 0)
        fail_sh = self.death_font.render("You Failed", True, (60, 0, 0))
        fail_lb = self.death_font.render("You Failed", True, (220, 50, 50))
        self.screen.blit(fail_sh, fail_sh.get_rect(centerx=cx + 4, centery=cy - 60 + 4))
        self.screen.blit(fail_lb, fail_lb.get_rect(centerx=cx, centery=cy - 60))
        sc_lb = self.score_font.render(f"Score {score}", True, (255, 220, 100))
        self.screen.blit(sc_lb, sc_lb.get_rect(centerx=cx, centery=cy + 30))
        tip = self.hint_font.render("Click anywhere to continue", True, (180, 180, 180))
        self.screen.blit(tip, tip.get_rect(centerx=cx, centery=cy + 100))

    def _draw_help_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(255 * 0.9)))
        self.screen.blit(overlay, (0, 0))

        cx = self.width // 2
        y_start = 10
        line_h = 25

        def draw_line(text, color=(230, 230, 230), y_off=0, font=None):
            f = font or self.help_font
            lbl = f.render(text, True, color)
            self.screen.blit(lbl, lbl.get_rect(centerx=cx, top=y_start + y_off))

        draw_line("HOW TO PLAY", (255, 220, 80), 0, self.help_title_font)

        lines = [
            ("Build words from the tiles on the board.", (220, 220, 220), 40),
            ("Click tiles to select them, click again to deselect.", (220, 220, 220), 40 + line_h),
            ("Press Attack to deal damage when a valid word is selected.", (220, 220, 220), 40 + line_h * 2),
            ("Damage depends on word length.", (255, 40, 40), 40 + line_h * 3),
            ("After your attack the enemy strikes back.", (220, 220, 220), 40 + line_h * 4),
            ("Survive as many levels as you can!", (220, 220, 220), 40 + line_h * 5),
        ]
        for text, color, y_off in lines:
            draw_line(text, color, y_off)

        section_y = 40 + line_h * 7
        draw_line("TILE ABILITIES", (255, 220, 80), section_y, self.help_title_font)

        ability_info = [
            ("n", "Normal - no bonus"),
            ("g", "Green - heals you for 10 percent of your max HP per tile"),
            ("o", "Orange - add 25 percent damage multiplier"),
            ("r", "Red - add 50 percent damage multiplier"),
            ("w", "Gray - add 100 percent damage multiplier"),
            ("b", "Blue - freezes enemy for 1 turn (skip their attack)"),
            ("p", "Purple - weakens enemy for 1 turn (reduces enemy damage by 50 percent)"),
        ]
        dot_size = 16
        row_h = line_h
        for i, (key, desc) in enumerate(ability_info):
            color = ABILITY_DEFS[key]["color"]
            y = y_start + section_y + 44 + i * row_h
            dot_rect = pygame.Rect(cx - 340, y + (row_h - dot_size) // 2, dot_size, dot_size)
            pygame.draw.rect(self.screen, color, dot_rect, border_radius=4)
            lbl = self.help_font.render(desc, True, (220, 220, 220))
            self.screen.blit(lbl, (cx - 310, y))

        enemy_section_y = section_y + 44 + len(ability_info) * row_h + 20
        draw_line("ENEMY ABILITIES", (255, 100, 100), enemy_section_y, self.help_title_font)
        enemy_info = [
            "Green - enemy heals itself",
            "Blue - enemy attacks twice in a row",
            "Purple - weakens player for 1 turn (reduces player damage by 50 percent)",
        ]
        for i, desc in enumerate(enemy_info):
            y = y_start + enemy_section_y + 44 + i * row_h
            lbl = self.help_font.render(desc, True, (220, 180, 180))
            self.screen.blit(lbl, lbl.get_rect(centerx=cx, top=y))

        misc_y = enemy_section_y + 44 + len(enemy_info) * row_h + 20
        draw_line("HINTS and REROLLS", (255, 220, 80), misc_y, self.help_title_font)
        misc = [
            f"Hint - reveals the longest possible word. Penalises you for {Config.hint_penalty} turns (0 damage).",
            f"Reroll - shuffles the entire board. You get {Config.max_reroll} rerolls, and add 1 every 5 completed levels.",
        ]
        for i, desc in enumerate(misc):
            y = y_start + misc_y + 44 + i * row_h
            lbl = self.help_font.render(desc, True, (220, 220, 220))
            self.screen.blit(lbl, lbl.get_rect(centerx=cx, top=y))

        dismiss_y = y_start + misc_y + 44 + len(misc) * row_h + 30
        dismiss = self.hint_font.render("Click anywhere to close", True, (180, 180, 180))
        self.screen.blit(dismiss, dismiss.get_rect(centerx=cx, top=dismiss_y))
