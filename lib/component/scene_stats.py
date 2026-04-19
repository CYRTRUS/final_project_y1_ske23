import os
import sys
import pygame

from lib.component.scene_base import BaseScene
from lib.component.button import Button


class StatsScene(BaseScene):
    MENU_RED = (200, 50, 50)   # same colour as menu buttons

    def __init__(self, screen, switch_scene_callback, click_sound, game):
        super().__init__(screen, switch_scene_callback)
        self.game = game
        self.click_sound = click_sound

        self._font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 28)
        self._small_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 18)
        self._msg_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 20)

        self._feedback = ""          # one-line confirmation shown after an action
        self._feedback_time = 0           # tick when feedback was set

        btn_w, btn_h = 220, 65
        pad = 20
        # Place the two buttons in the bottom-right corner
        margin_x = self.width - btn_w - 40
        margin_y = self.height - btn_h - 40

        self._btn_reset = Button(
            margin_x - btn_w - pad, margin_y,
            btn_w, btn_h,
            "Reset Game",
            self._confirm_reset_game,
            click_sound,
            font_size=24,
            color=self.MENU_RED,
        )
        self._btn_delete_log = Button(
            margin_x, margin_y,
            btn_w, btn_h,
            "Delete Log",
            self._confirm_delete_log,
            click_sound,
            font_size=24,
            color=self.MENU_RED,
        )

        # Keep buttons list for drawing; handle_event routes manually
        self.buttons = [self._btn_reset, self._btn_delete_log]

    # SceneManager hook

    def _refresh(self):
        """Called by SceneManager just before this scene becomes current."""
        self._open_stats()

    def _open_stats(self):
        try:
            from lib.component.stats_window import StatsWindow
            StatsWindow.launch()
        except Exception as e:
            print(f"[StatsScene] Could not open stats window: {e}")

    # Button actions

    def _confirm_reset_game(self):
        """Delete game_save.json via data_collector."""
        try:
            self.game.data_collector.delete_save()
            self._set_feedback("Save file deleted.")
        except Exception as e:
            self._set_feedback(f"Error: {e}")

    def _confirm_delete_log(self):
        """Delete only the CSV log file, then recreate an empty one."""
        try:
            from lib.component.data_collection import LOG_PATH, _ensure_log
            if os.path.exists(LOG_PATH):
                os.remove(LOG_PATH)
            _ensure_log()          # recreate an empty CSV with the header
            self._set_feedback("Log file cleared.")
        except Exception as e:
            self._set_feedback(f"Error: {e}")

    def _set_feedback(self, msg):
        self._feedback = msg
        self._feedback_time = pygame.time.get_ticks()

    # Pygame lifecycle

    def handle_event(self, event):
        # Let buttons consume clicks first
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.rect.collidepoint(event.pos):
                    btn.handle_event(event)
                    return            # button handled it - don't go back to menu
            # Click was outside buttons - return to menu
            self.switch_scene_callback("menu")
            return

        if event.type == pygame.KEYDOWN:
            self.switch_scene_callback("menu")

    def update(self):
        pass

    def draw(self):
        self.draw_background()

        cx = self.width // 2
        cy = self.height // 2

        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Title
        sh = self._font.render("Stats window opened!", True, (20, 20, 20))
        lb = self._font.render("Stats window opened!", True, (255, 220, 80))
        self.screen.blit(sh, sh.get_rect(centerx=cx + 3, centery=cy - 20 + 3))
        self.screen.blit(lb, lb.get_rect(centerx=cx, centery=cy - 20))

        # Sub-hint
        sub = self._small_font.render(
            "Click anywhere (outside buttons) or press any key to return to menu",
            True, (180, 180, 180)
        )
        self.screen.blit(sub, sub.get_rect(centerx=cx, centery=cy + 30))

        # Feedback message (fades out after 3 s)
        if self._feedback and pygame.time.get_ticks() - self._feedback_time < 3000:
            fb = self._msg_font.render(self._feedback, True, (120, 240, 120))
            self.screen.blit(fb, fb.get_rect(
                centerx=self.width // 2,
                bottom=self._btn_reset.rect.top - 10
            ))

        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen)
