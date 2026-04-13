import pygame
import os
from lib.component.scene_manager import SceneManager
from lib.component.player import Player
from lib.component.enemy import Enemy
from lib.component.data_collection import DataCollection


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
        self.click_sound.set_volume(1.0)

        self.data_collector = DataCollection()

        self.current_level = 1
        self.player = Player(self)
        self.enemy = Enemy(self, self.current_level)

        self.scene_manager = SceneManager(
            self.screen,
            self.switch_scene,
            self.quit_game,
            self.click_sound,
            self.player,
            self.enemy,
            self.data_collector,
            self
        )

    def start_game(self):
        self.current_level = 1
        self.player = Player(self)
        self.enemy = Enemy(self, self.current_level)

        self.scene_manager = SceneManager(
            self.screen,
            self.switch_scene,
            self.quit_game,
            self.click_sound,
            self.player,
            self.enemy,
            self.data_collector,
            self
        )

    def update_game_state(self):
        if self.enemy.health <= 0:
            self.next_level()
        if self.player.health <= 0:
            self.end_game()

    def next_level(self):
        self.current_level += 1
        self.enemy = Enemy(self, self.current_level)
        self.player.set_level(self.current_level)
        self.data_collector.log_event("level_up", self.current_level)

        # Update the gameplay scene's reference to the new enemy
        gameplay = self.scene_manager.scenes.get("gameplay")
        if gameplay:
            gameplay.enemy = self.enemy

    def end_game(self):
        self.running = False
        self.data_collector.save_to_csv()

    def switch_scene(self, name):
        self.scene_manager.switch_scene(name)

    def quit_game(self):
        self.click_sound.play()
        pygame.time.delay(100)
        self.running = False

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.quit_game()
                self.scene_manager.handle_event(e)

            self.scene_manager.update()
            self.update_game_state()
            self.scene_manager.draw()

            self.player.update_anim()
            self.enemy.update_anim()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
