import sys
import pygame
from lib.component import assets
from lib.component.config import Config
from lib.component.data_collection import DataCollection
from lib.component.enemy import Enemy
from lib.component.player import Player
from lib.component.scene_manager import SceneManager


class Game:
    WIDTH = Config.screen_width
    HEIGHT = Config.screen_height

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(Config.title)
        self.clock = pygame.time.Clock()
        self.running = True

        self.click_sound = assets.sound("btn_click", volume=Config.click_volume)
        self.data_collector = DataCollection()

        save = self.data_collector.load_game()
        self._create_combatants(save)
        self.scene_manager = SceneManager(self)
        if save:
            self.gameplay.restore_from_save(save)
        else:
            self.save()

    @property
    def gameplay(self):
        return self.scene_manager.gameplay

    # Run state

    def _create_combatants(self, save=None):
        save = save or {}
        self.current_level = save.get("current_level", 1)
        self.player = Player(self, self.current_level,
                             health=save.get("player_health"), score=save.get("player_score", 0))
        self.enemy = Enemy(self, self.current_level, health=save.get("enemy_health"))
        self.player.load_debuffs(save.get("player_debuffs", {}))
        self.enemy.load_debuffs(save.get("enemy_debuffs", {}))

    def start_new_run(self):
        self._create_combatants()
        self.scene_manager.reset_gameplay()
        self.save()

    def next_level(self):
        self.current_level += 1
        self.player.set_level(self.current_level)
        self.player.health = self.player.max_health
        self.enemy = Enemy(self, self.current_level)

    # Saving

    def snapshot(self):
        return {
            "current_level":     self.current_level,
            "player_health":     self.player.health,
            "player_max_health": self.player.max_health,
            "player_score":      self.player.score,
            "player_rerolls":    self.gameplay.rerolls,
            "player_debuffs":    self.player.debuffs(),
            "enemy_health":      self.enemy.health,
            "enemy_max_health":  self.enemy.max_health,
            "enemy_debuffs":     self.enemy.debuffs(),
            "tiles":             self.gameplay.board.snapshot(),
        }

    def save(self):
        self.data_collector.save_game(self.snapshot())

    def save_and_log_close(self):
        self.data_collector.log_program_closed(self.current_level)
        self.save()

    # Scenes

    def switch_scene(self, name):
        if name == "gameplay":
            save = self.data_collector.load_game()
            if self.player.is_dead or save is None:
                # Previous run ended, or the save was deleted (e.g. via Reset Game)
                self.start_new_run()
            else:
                self.gameplay.restore_from_save(save)
        self.scene_manager.switch_scene(name)

    def quit_game(self):
        self.save_and_log_close()
        self.running = False
        if self.click_sound:
            self.click_sound.play()
        pygame.time.delay(100)

    # Main loop

    def tick(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()
            self.scene_manager.handle_event(event)
        self.scene_manager.update()
        self.scene_manager.draw()
        self.player.update_anim()
        self.enemy.update_anim()

    def run(self):
        while self.running:
            self.tick(pygame.event.get())
            pygame.display.flip()
            self.clock.tick(Config.fps)
        pygame.quit()

        # Close the stats window if it was ever opened
        stats_window = sys.modules.get("lib.component.stats_window")
        if stats_window is not None:
            stats_window.StatsWindow.shutdown()
