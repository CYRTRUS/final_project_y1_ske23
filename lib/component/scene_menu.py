from lib.component.scene_base import BaseScene
from lib.component.button import Button


class MenuScene(BaseScene):

    def __init__(
        self,
        screen,
        switch_scene_callback,
        quit_callback,
        click_sound
    ):

        super().__init__(screen, switch_scene_callback)

        button_w = 260
        button_h = 100
        padding = 20

        start_y = (self.height - (button_h * 3 + padding * 2)) // 2
        start_x = (self.width - button_w) // 2

        self.buttons = [
            Button(
                start_x,
                start_y + ((button_h + padding) * 0),
                button_w,
                button_h,
                "Start",
                lambda: self.switch_scene_callback("gameplay"),
                click_sound,
                color=(200, 50, 50)
            ),

            Button(
                start_x,
                start_y + ((button_h + padding) * 1),
                button_w,
                button_h,
                "Stats",
                lambda: self.switch_scene_callback("stats"),
                click_sound,
                color=(200, 50, 50)
            ),

            Button(
                start_x,
                start_y + ((button_h + padding) * 2),
                button_w,
                button_h,
                "Quit",
                quit_callback,
                click_sound,
                color=(200, 50, 50)
            )
        ]
