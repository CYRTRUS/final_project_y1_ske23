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

        super().__init__(
            screen,
            switch_scene_callback
        )

        start_button = Button(
            500,
            300,
            200,
            60,
            "Start",
            lambda:
                self.switch_scene_callback(
                    "gameplay"
                ),
            click_sound
        )

        stats_button = Button(
            500,
            380,
            200,
            60,
            "Stats",
            lambda:
                self.switch_scene_callback(
                    "stats"
                ),
            click_sound
        )

        quit_button = Button(
            500,
            460,
            200,
            60,
            "Quit",
            quit_callback,
            click_sound
        )

        self.buttons.extend([
            start_button,
            stats_button,
            quit_button
        ])
