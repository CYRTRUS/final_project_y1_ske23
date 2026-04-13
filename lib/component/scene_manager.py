from lib.component.scene_menu import MenuScene
from lib.component.scene_gameplay import GameplayScene
from lib.component.scene_stats import StatsScene


class SceneManager:
    def __init__(self, screen, switch_scene_callback, quit_callback, click_sound, player, enemy, data_collector, game):
        self.screen = screen
        self.scenes = {}
        self.scenes["menu"] = MenuScene(screen, switch_scene_callback, quit_callback, click_sound)

        self.scenes["gameplay"] = GameplayScene(
            screen, switch_scene_callback, click_sound, player, enemy, data_collector, game
        )

        self.scenes["stats"] = StatsScene(screen, switch_scene_callback, click_sound)
        self.current_scene = self.scenes["menu"]

    def switch_scene(self, name):
        self.current_scene = self.scenes[name]

    def handle_event(self, event):
        self.current_scene.handle_event(event)

    def update(self):
        self.current_scene.update()

    def draw(self):
        self.current_scene.draw()
