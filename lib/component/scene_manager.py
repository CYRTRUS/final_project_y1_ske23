from lib.component.scene_gameplay import GameplayScene
from lib.component.scene_menu import MenuScene
from lib.component.scene_stats import StatsScene


class SceneManager:
    def __init__(self, game):
        self.game = game
        self.scenes = {
            "menu": MenuScene(game),
            "gameplay": GameplayScene(game),
            "stats": StatsScene(game),
        }
        self.current_scene = self.scenes["menu"]

    @property
    def gameplay(self):
        return self.scenes["gameplay"]

    def reset_gameplay(self):
        """Replace the gameplay scene with a brand new one (fresh board, rerolls...)."""
        self.scenes["gameplay"] = GameplayScene(self.game)
        return self.scenes["gameplay"]

    def switch_scene(self, name):
        self.current_scene = self.scenes[name]
        self.current_scene.on_enter()

    def handle_event(self, event):
        self.current_scene.handle_event(event)

    def update(self):
        self.current_scene.update()

    def draw(self):
        self.current_scene.draw()
