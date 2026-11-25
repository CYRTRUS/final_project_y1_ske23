import random
from lib.component import assets
from lib.component.layer import Layer

MENU_RED = (200, 50, 50)


class BaseScene:
    """A screen of the game. Subclasses override the hooks they need."""

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width, self.height = self.screen.get_size()
        self.click_sound = game.click_sound
        self.buttons = []
        self.layers = [
            Layer("back.png",   self.width, self.height, x=random.randint(-200, 0), y=-250),
            Layer("far.png",    self.width, self.height, x=random.randint(-200, 0), y=-250),
            Layer("middle.png", self.width, self.height, x=random.randint(-100, 0), y=-250, random_scale=True),
            Layer("front.png",  self.width, self.height, x=random.randint(-200, 0),
                  y=int(self.height * 0.48), height_scale=0.6),
        ]

    def on_enter(self):
        """Called every time the scene becomes the current one."""
        assets.stop_music()

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self):
        pass

    def draw_background(self):
        for layer in self.layers:
            layer.draw(self.screen)

    def draw_buttons(self):
        for button in self.buttons:
            button.draw(self.screen)

    def draw(self):
        self.draw_background()
        self.draw_buttons()
