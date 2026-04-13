from lib.component.scene_base import BaseScene
from lib.component.button import Button


class StatsScene(BaseScene):

    def __init__(
        self,
        screen,
        switch_scene_callback,
        click_sound
    ):

        super().__init__(
            screen,
            switch_scene_callback
        )

        back_button = Button(
            20,
            20,
            150,
            50,
            "Back",
            lambda:
                self.switch_scene_callback(
                    "menu"
                ),
            click_sound
        )

        self.buttons.append(back_button)
