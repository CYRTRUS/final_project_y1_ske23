import pygame
import random
import math
import os
from lib.component.tile import Tile


class Board:
    def __init__(self, screen_width, screen_height, board_x, board_y, board_width, board_height, click_sound, game):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_x = board_x
        self.board_y = board_y
        self.board_width = board_width
        self.board_height = board_height
        self.click_sound = click_sound
        self.game = game

        font_path = os.path.join("lib", "font", "minercraftory.regular.ttf")
        self.board_size = 4
        self.tile_padding = 5

        self.selected_scale = 1.2
        self.selected_padding = 8

        available_height = self.board_height - 50 - (self.board_size - 1) * self.tile_padding
        self.tile_size = available_height // self.board_size
        self.font = pygame.font.Font(font_path, int(self.tile_size * 0.6))

        self.grid = []
        self.selected_tiles = []
        self.word_data = self.load_word_data()

        self.letter_weights = {
            'a': 10, 'b': 2, 'c': 5, 'd': 4, 'e': 13, 'f': 1, 'g': 3, 'h': 3,
            'i': 11, 'j': 1, 'k': 1, 'l': 6, 'm': 3, 'n': 8, 'o': 8, 'p': 3,
            'q': 1, 'r': 8, 's': 9, 't': 8, 'u': 4, 'v': 1, 'w': 1, 'x': 1,
            'y': 2, 'z': 1
        }

        self.generate_tiles()

    def load_word_data(self):
        path = os.path.join("lib", "word_list", "word_list.txt")
        with open(path, "r", encoding="utf-8") as f:
            words = list(set([l.strip().lower() for l in f if l.strip()]))

        words = sorted(words, key=lambda w: (len(w), w))
        data = {"guarantee_word": []}

        for w in words:
            if len(w) == 3:
                data["guarantee_word"].append(w)
            k = w[:min(math.ceil(len(w) / 2), 3)]
            if k not in data:
                data[k] = []
            data[k].append(w)

        return data

    def generate_tiles(self):
        self.grid = []

        g = random.choice(self.word_data["guarantee_word"])
        letters = list(g)

        pool = list(self.letter_weights.keys())
        weights = list(self.letter_weights.values())

        while len(letters) < 16:
            letters.append(random.choices(pool, weights=weights, k=1)[0])

        random.shuffle(letters)

        i = 0
        gw = self.board_size * self.tile_size + (self.board_size - 1) * self.tile_padding
        gh = gw

        sx = self.board_x + (self.board_width - gw) // 2
        sy = self.board_y + (self.board_height - gh) // 2

        for r in range(self.board_size):
            row = []
            for c in range(self.board_size):
                x = sx + c * (self.tile_size + self.tile_padding)
                y = sy + r * (self.tile_size + self.tile_padding) + 10
                row.append(Tile(letters[i], r, c, self.tile_size, x, y, self.font))
                i += 1
            self.grid.append(row)

    def get_tile_spacing(self, tile):
        if tile in self.selected_tiles:
            return int(self.tile_size * self.selected_scale) + self.selected_padding
        return self.tile_size + self.tile_padding

    def get_word(self):
        return "".join([t.letter.lower() for t in self.selected_tiles])

    def submit_word(self):
        w = self.get_word()
        if len(w) >= 3:
            if self.click_sound:
                self.click_sound.play()
            self.game.player.attack_enemy(w)
            self.selected_tiles = []
            self.generate_tiles()

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        pos = event.pos

        for i, t in enumerate(self.selected_tiles):
            if t.contains(pos):
                if self.click_sound:
                    self.click_sound.play()
                for x in self.selected_tiles[i:]:
                    x.reset_position()
                self.selected_tiles = self.selected_tiles[:i]
                self.update_selected_positions()
                return

        for row in self.grid:
            for t in row:
                if t.contains(pos) and not t.selected:
                    if self.click_sound:
                        self.click_sound.play()
                    t.selected = True
                    self.selected_tiles.append(t)
                    self.update_selected_positions()
                    return

    def update_selected_positions(self):
        top_y = int(self.screen_height * 0.15)

        total = 0
        spacings = []

        for t in self.selected_tiles:
            s = self.get_tile_spacing(t)
            spacings.append(s)
            total += s

        start_x = self.screen_width // 2 - total // 2

        x = start_x
        for i, t in enumerate(self.selected_tiles):
            t.move_to(x, top_y)
            x += spacings[i]

    def update(self):
        for row in self.grid:
            for t in row:
                t.update()
        for t in self.selected_tiles:
            t.update()

    def draw(self, screen):
        for row in self.grid:
            for t in row:
                t.display_tile(screen)
        for t in self.selected_tiles:
            t.display_tile(screen)
