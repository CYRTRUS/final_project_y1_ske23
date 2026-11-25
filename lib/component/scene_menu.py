from lib.component import assets
from lib.component.button import Button
from lib.component.config import Config
from lib.component.scene_base import BaseScene, MENU_RED
from lib.component.ui import shadow_text


class MenuScene(BaseScene):
    BUTTON_W = 260
    BUTTON_H = 100
    PADDING = 20

    def __init__(self, game):
        super().__init__(game)
        entries = [
            ("Start", lambda: game.switch_scene("gameplay")),
            ("Stats", lambda: game.switch_scene("stats")),
            ("Quit",  game.quit_game),
        ]
        stack_h = self.BUTTON_H * len(entries) + self.PADDING * (len(entries) - 1)
        start_x = (self.width - self.BUTTON_W) // 2
        start_y = (self.height - stack_h) // 2 + 50

        self.buttons = [
            Button(start_x, start_y + i * (self.BUTTON_H + self.PADDING), self.BUTTON_W, self.BUTTON_H,
                   text, callback, self.click_sound, color=MENU_RED)
            for i, (text, callback) in enumerate(entries)
        ]
        self.title_font = assets.font(120)
        self._title_y = start_y - 220

    def draw(self):
        self.draw_background()
        shadow_text(self.screen, self.title_font, Config.title, (255, 255, 255),
                    shadow_color=(0, 0, 0), offset=(8, 8), centerx=self.width // 2, top=self._title_y)
        self.draw_buttons()
