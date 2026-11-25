import pygame
from lib.component import assets
from lib.component.button import Button
from lib.component.scene_base import BaseScene, MENU_RED
from lib.component.ui import dim_screen, shadow_text

FEEDBACK_MS = 3000


class StatsScene(BaseScene):
    """Opens the matplotlib stats window and offers reset / clear-log buttons."""

    BUTTON_W = 220
    BUTTON_H = 65
    PADDING = 20
    MARGIN = 40

    def __init__(self, game):
        super().__init__(game)
        self._font = assets.font(28)
        self._small_font = assets.font(18)
        self._msg_font = assets.font(20)
        self._feedback = ""
        self._feedback_time = 0

        right_x = self.width - self.BUTTON_W - self.MARGIN
        y = self.height - self.BUTTON_H - self.MARGIN
        self._btn_reset = Button(right_x - self.BUTTON_W - self.PADDING, y, self.BUTTON_W, self.BUTTON_H,
                                 "Reset Game", self._reset_game, self.click_sound, font_size=24, color=MENU_RED)
        self._btn_delete_log = Button(right_x, y, self.BUTTON_W, self.BUTTON_H,
                                      "Delete Log", self._delete_log, self.click_sound, font_size=24, color=MENU_RED)
        self.buttons = [self._btn_reset, self._btn_delete_log]

    def on_enter(self):
        super().on_enter()
        try:
            from lib.component.stats_window import StatsWindow   # heavy import (tk + matplotlib)
            StatsWindow.launch()
        except Exception as e:
            print(f"[StatsScene] Could not open stats window: {e}")

    # Button actions

    def _reset_game(self):
        self._run_action(self.game.data_collector.delete_save, "Save file deleted.")

    def _delete_log(self):
        self._run_action(self.game.data_collector.clear_log, "Log file cleared.")

    def _run_action(self, action, success_msg):
        try:
            action()
            self._set_feedback(success_msg)
        except OSError as e:
            self._set_feedback(f"Error: {e}")

    def _set_feedback(self, msg):
        self._feedback = msg
        self._feedback_time = pygame.time.get_ticks()

    # Frame

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not any(btn.handle_event(event) for btn in self.buttons):
                self.game.switch_scene("menu")      # clicked outside the buttons
        elif event.type == pygame.KEYDOWN:
            self.game.switch_scene("menu")

    def draw(self):
        self.draw_background()
        dim_screen(self.screen, 160)

        cx, cy = self.width // 2, self.height // 2
        shadow_text(self.screen, self._font, "Stats window opened!", (255, 220, 80),
                    offset=(3, 3), centerx=cx, centery=cy - 20)
        sub = self._small_font.render(
            "Click anywhere (outside buttons) or press any key to return to menu", True, (180, 180, 180))
        self.screen.blit(sub, sub.get_rect(centerx=cx, centery=cy + 30))

        if self._feedback and pygame.time.get_ticks() - self._feedback_time < FEEDBACK_MS:
            fb = self._msg_font.render(self._feedback, True, (120, 240, 120))
            self.screen.blit(fb, fb.get_rect(centerx=cx, bottom=self._btn_reset.rect.top - 10))

        self.draw_buttons()
