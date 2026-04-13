import pygame
import os
from lib.component.scene_manager import SceneManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.WIDTH = 1200
        self.HEIGHT = 800

        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT)
        )

        pygame.display.set_caption(
            "WordForge"
        )

        self.clock = pygame.time.Clock()

        self.running = True

        # Load click sound ONCE
        sound_path = os.path.join(
            "lib",
            "sfx",
            "minecraft_click.mp3"
        )

        self.click_sound = pygame.mixer.Sound(
            sound_path
        )

        self.click_sound.set_volume(1.0)

        self.scene_manager = SceneManager(
            self.screen,
            self.switch_scene,
            self.quit_game,
            self.click_sound
        )

    def switch_scene(self, name):
        self.scene_manager.switch_scene(name)

    def quit_game(self):

        # Play exit sound
        self.click_sound.play()

        # Let sound finish
        pygame.time.delay(100)

        self.running = False

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            self.scene_manager.handle_event(event)

    def update(self):
        self.scene_manager.update()

    def draw(self):
        self.scene_manager.draw()
