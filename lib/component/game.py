import pygame
import os
from lib.component.scene_manager import SceneManager
from lib.component.scene_gameplay import GameplayScene
from lib.component.player import Player
from lib.component.enemy import Enemy
from lib.component.data_collection import DataCollection
from lib.component.config import Config


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.WIDTH, self.HEIGHT = 1600, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("WordForge")
        self.clock = pygame.time.Clock()
        self.running = True

        self.click_sound = pygame.mixer.Sound(os.path.join("lib", "sfx", "minecraft_click.mp3"))
        self.click_sound.set_volume(Config.click_volume / 100)

        self.data_collector = DataCollection()
        self.current_level = 1
        self.player = Player(self)
        self.enemy = Enemy(self, self.current_level)

        self.scene_manager = SceneManager(
            self.screen, self.switch_scene, self.quit_game,
            self.click_sound, self.player, self.enemy, self.data_collector, self
        )

        save = self.data_collector.load_game()
        if save:
            self._restore(save)
        else:
            self.data_collector.save_game(self)

    def _restore(self, save):
        self.current_level = save.get("current_level", 1)
        self.player = Player(self, health=save.get("player_health"), score=save.get("player_score", 0))
        self.player.set_level(self.current_level)
        self.enemy = Enemy(self, self.current_level, health=save.get("enemy_health"))
        self.scene_manager = SceneManager(
            self.screen, self.switch_scene, self.quit_game,
            self.click_sound, self.player, self.enemy, self.data_collector, self
        )
        gameplay = self.scene_manager.scenes.get("gameplay")
        if gameplay:
            gameplay.restore_from_save(save)

    def switch_scene(self, name):
        if name == "gameplay" and self.player._is_dead:
            self._start_fresh()
        self.scene_manager.switch_scene(name)

    def _start_fresh(self):
        self.current_level = 1
        self.player = Player(self)
        self.enemy = Enemy(self, 1)
        new_gameplay = GameplayScene(
            self.screen, self.switch_scene, self.click_sound,
            self.player, self.enemy, self.data_collector, self
        )
        self.scene_manager.scenes["gameplay"] = new_gameplay
        self.data_collector.save_game(self)

    def reset_to_level1(self):
        """Reset in-memory state to level 1 (called after stats reset)."""
        self.current_level = 1
        self.player = Player(self)
        self.enemy = Enemy(self, 1)
        new_gameplay = GameplayScene(
            self.screen, self.switch_scene, self.click_sound,
            self.player, self.enemy, self.data_collector, self
        )
        self.scene_manager.scenes["gameplay"] = new_gameplay

    def _save_and_quit(self):
        self.data_collector.log_program_closed(self.current_level)
        self.data_collector.save_game(self)
        self.running = False

    def quit_game(self):
        self._save_and_quit()
        self.click_sound.play()
        pygame.time.delay(100)

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.quit_game()
                self.scene_manager.handle_event(e)
            self.scene_manager.update()
            self.scene_manager.draw()
            self.player.update_anim()
            self.enemy.update_anim()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
