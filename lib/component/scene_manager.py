import os
import json
import pygame
from lib.component.scene_menu import MenuScene
from lib.component.scene_gameplay import GameplayScene
from lib.component.scene_stats import StatsScene
from lib.component.config import Config


SAVE_PATH = "game_save.json"


class SceneManager:
    def __init__(self, screen, switch_scene_callback, quit_callback, click_sound,
                 player, enemy, data_collector, game):
        self.screen = screen
        self.game = game

        self.scenes = {}
        self.scenes["menu"] = MenuScene(screen, switch_scene_callback, quit_callback, click_sound)
        self.scenes["gameplay"] = GameplayScene(
            screen, switch_scene_callback, click_sound, player, enemy, data_collector, game
        )
        self.scenes["stats"] = StatsScene(screen, switch_scene_callback, click_sound, game)

        self.current_scene = self.scenes["menu"]

    def _load_save(self):
        if not os.path.exists(SAVE_PATH):
            return {}
        try:
            with open(SAVE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def switch_scene(self, name):
        if name == "gameplay":
            save_data = self._load_save()
            self.scenes["gameplay"].restore_from_save(save_data)
            try:
                pygame.mixer.music.load(os.path.join("lib", "sfx", "forest_ambient.mp3"))
                pygame.mixer.music.set_volume(Config.ambient_volume / 100)
                pygame.mixer.music.play(-1)
            except Exception:
                pass
        elif name == "stats":
            self.scenes["stats"]._refresh()
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

        self.current_scene = self.scenes[name]

    def handle_event(self, event):
        self.current_scene.handle_event(event)

    def update(self):
        self.current_scene.update()

    def draw(self):
        self.current_scene.draw()
