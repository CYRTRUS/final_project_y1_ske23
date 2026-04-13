from lib.component.layer import Layer
import random as rd


class BaseScene:

    def __init__(self, screen, switch_scene_callback):

        self.screen = screen

        self.switch_scene_callback = switch_scene_callback

        self.width = screen.get_width()

        self.height = screen.get_height()

        self.layers = [
            # Yellow bg
            Layer(
                "back.png",
                self.width,
                self.height,
                x=rd.randint(-200, 0),
                y=-200,
            ),
            # Green trees
            Layer(
                "far.png",
                self.width,
                self.height,
                x=rd.randint(-200, 0),
                y=-200,
            ),
            # Actual trees
            Layer(
                "middle.png",
                self.width,
                self.height,
                x=rd.randint(-100, 0),
                y=-200,
                random_scale=True
            ),
            # Ground
            Layer(
                "front.png",
                self.width,
                self.height,
                x=rd.randint(-200, 0),
                y=int(self.height * 0.5),
                height_scale=0.5
            )

        ]

        self.buttons = []

    def handle_event(self, event):

        for button in self.buttons:

            button.handle_event(event)

    def update(self):
        pass

    def draw_background(self):

        for layer in self.layers:

            layer.draw(self.screen)

    def draw(self):

        self.draw_background()

        for button in self.buttons:

            button.draw(self.screen)
