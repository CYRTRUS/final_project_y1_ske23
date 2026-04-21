import pygame
import random
from collections import Counter
from lib.component.tile import Tile, roll_player_ability
from lib.component.config import Config

LETTERS = list(Config.letter_weights.keys())
WEIGHTS = list(Config.letter_weights.values())
VOWELS = ["a", "e", "i", "o", "u"]


class Board:
    def __init__(self, sw, sh, bx, by, bw, bh, click_sound, game):
        self.sw = sw
        self.sh = sh
        self.bx = bx
        self.by = by
        self.bw = bw
        self.bh = bh
        self.click_sound = click_sound
        self.game = game
        self.size = 4
        self.padding = 5
        self.selected_padding = 20
        self.tile_size = (bh - 50 - (self.size - 1) * self.padding) // self.size
        self.font = pygame.font.Font("lib/font/minercraftory.regular.ttf", int(self.tile_size * 0.6))
        self.grid = []
        self.selected = []
        self.previous_selected = []
        self.word_data = self._load_word_data()
        self.generate_valid_board()

    def _load_word_data(self):
        with open("lib/word_list/word_list.txt", "r", encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip()]
        data = {}
        for w in words:
            length = len(w)
            first = w[0]
            if length not in data:
                data[length] = {}
            if first not in data[length]:
                data[length][first] = []
            data[length][first].append(w)
        return data

    def is_valid(self, word):
        length = len(word)
        first = word[0] if word else ""
        return word in self.word_data.get(length, {}).get(first, [])

    def is_valid_board(self, letters):
        bc = Counter(letters)
        guarantee_words = self.word_data.get(3, {})
        all_three = [w for ws in guarantee_words.values() for w in ws]
        return any(not (Counter(w) - bc) for w in all_three)

    def get_longest_possible_word(self):
        bc = Counter(t.letter.lower() for row in self.grid for t in row if t.letter)
        for length in range(16, 2, -1):
            if length not in self.word_data:
                continue
            for l in set(bc):
                try:
                    for w in self.word_data[length][l]:
                        if not (Counter(w) - bc):
                            return w
                except KeyError:
                    continue
        return ""

    def generate_valid_board(self):
        while True:
            letters = []

            vowel_pool = [v for v in VOWELS if v in Config.letter_weights]
            vowel_w = [Config.letter_weights[v] for v in vowel_pool]
            for _ in range(Config.max_vowel):
                letters.append(random.choices(vowel_pool, weights=vowel_w, k=1)[0])

            temp_w = dict(Config.letter_weights)
            for v in VOWELS:
                if v in temp_w:
                    temp_w[v] = 1
            pool = list(temp_w.keys())
            wts = list(temp_w.values())
            while len(letters) < 16:
                letters.append(random.choices(pool, weights=wts, k=1)[0])

            random.shuffle(letters)
            if self.is_valid_board(letters):
                break

        self.build_grid(letters)

    def build_grid(self, letters, abilities=None):
        self.grid = []
        gw = self.size * self.tile_size + (self.size - 1) * self.padding
        sx = self.bx + (self.bw - gw) // 2
        sy = self.by + (self.bh - gw) // 2 + 15
        i = 0
        for r in range(self.size):
            row = []
            for c in range(self.size):
                x = sx + c * (self.tile_size + self.padding)
                y = sy + r * (self.tile_size + self.padding)
                lvl = getattr(self.game, "current_level", 1)
                ability = abilities[i] if abilities else roll_player_ability(lvl)
                row.append(Tile(letters[i], r, c, self.tile_size, x, y, self.font, ability=ability, click_sound=self.click_sound))
                i += 1
            self.grid.append(row)

    def load_from_save(self, tile_data):
        letters = [td["letter"].lower() for td in tile_data]
        abilities = [td.get("ability", "n") for td in tile_data]
        self.build_grid(letters, abilities)

    def get_tile_position(self, row, col):
        gw = self.size * self.tile_size + (self.size - 1) * self.padding
        sx = self.bx + (self.bw - gw) // 2
        sy = self.by + (self.bh - gw) // 2 + 15
        return (sx + col * (self.tile_size + self.padding), sy + row * (self.tile_size + self.padding))

    def get_current_word(self):
        return "".join(t.letter.lower() for t in self.selected)

    def get_selected_abilities(self):
        return [t.ability for t in self.selected]

    def is_current_word_valid(self):
        w = self.get_current_word()
        return bool(w) and self.is_valid(w)

    def compare_last_word(self):
        return self.selected == self.previous_selected

    def handle_event(self, e):
        if e.type != pygame.MOUSEBUTTONDOWN or e.button != 1:
            return
        pos = e.pos
        for i, t in enumerate(self.selected):
            if t.contains(pos):
                if self.click_sound:
                    self.click_sound.play()
                self.game.data_collector.log_tile_clicked(getattr(self.game, "current_level", 1))
                for x in self.selected[i:]:
                    x.reset()
                self.selected = self.selected[:i]
                self.update_positions()
                return
        for row in self.grid:
            for t in row:
                if t.letter != "" and t.contains(pos) and not t.selected:
                    if self.click_sound:
                        self.click_sound.play()
                    self.game.data_collector.log_tile_clicked(getattr(self.game, "current_level", 1))
                    t.selected = True
                    self.selected.append(t)
                    self.update_positions()
                    return

    def update_positions(self):
        y = int(self.sh * 0.15)
        total = sum(self.tile_size + (self.selected_padding if t.selected else self.padding) for t in self.selected)
        x = self.sw // 2 - total // 2
        for t in self.selected:
            t.move_to(x, y)
            x += self.tile_size + (self.selected_padding if t.selected else self.padding)

    def attack(self, on_complete=None):
        if not self.selected or not self.is_current_word_valid():
            return
        word = self.get_current_word()
        abilities = self.get_selected_abilities()
        for t in self.selected:
            t.letter = ""
            t.selected = False
        self.selected = []
        self.apply_gravity_and_fill()
        self.game.player.attack_enemy(word, abilities, on_complete=on_complete)

    def apply_gravity_and_fill(self):
        lvl = getattr(self.game, "current_level", 1)
        empty_spots = []
        remaining = []

        for c in range(self.size):
            col_tiles = [self.grid[r][c] for r in range(self.size - 1, -1, -1) if self.grid[r][c].letter != ""]
            empty_count = self.size - len(col_tiles)

            for idx, tile in enumerate(col_tiles):
                target_row = self.size - 1 - idx
                tx, ty = self.get_tile_position(target_row, c)
                tile.original_x, tile.original_y = tx, ty
                tile.move_to(tx, ty)
                self.grid[target_row][c] = tile
                remaining.append(tile.letter.lower())

            for r in range(empty_count):
                empty_spots.append((r, c))

        vowel_in_grid = sum(1 for l in remaining if l in VOWELS)
        target_vowels = min(max(0, Config.max_vowel - vowel_in_grid), len(empty_spots))

        while True:
            new_letters = []
            for _ in range(target_vowels):
                new_letters.append(random.choice(VOWELS))
            temp_w = dict(Config.letter_weights)
            for v in VOWELS:
                if v in temp_w:
                    temp_w[v] = 1
            pool = list(temp_w.keys())
            wts = list(temp_w.values())
            while len(new_letters) < len(empty_spots):
                new_letters.append(random.choices(pool, weights=wts, k=1)[0])
            if self.is_valid_board(remaining + new_letters):
                break

        random.shuffle(new_letters)

        for i, (r, c) in enumerate(empty_spots):
            tx, ty = self.get_tile_position(r, c)
            new_tile = Tile(new_letters[i], r, c, self.tile_size, tx, ty, self.font, ability=roll_player_ability(lvl), click_sound=self.click_sound)
            spawn_y = self.by - (r + 1) * (self.tile_size + self.padding)
            new_tile.x = tx
            new_tile.y = spawn_y
            new_tile.target_x = tx
            new_tile.target_y = ty
            new_tile.is_falling = True
            self.grid[r][c] = new_tile

        self._resolve_board()

    def reroll_board(self):
        self.selected = []
        self.generate_valid_board()

    def _resolve_board(self):
        letters = [t.letter.lower() for row in self.grid for t in row]
        if not self.is_valid_board(letters):
            self.generate_valid_board()

    def update(self):
        for row in self.grid:
            for t in row:
                t.update()
        for t in self.selected:
            t.update()

    def draw(self, screen):
        for row in self.grid:
            for t in row:
                t.draw(screen)
