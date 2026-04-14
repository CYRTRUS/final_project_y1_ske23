import pygame
import random
from collections import Counter
from lib.component.tile import Tile, roll_player_ability
from lib.component.config import Config

# Build letter pool from config
LETTERS = list(Config.letter_weights.keys())
WEIGHTS = list(Config.letter_weights.values())
VOWELS = ["a", "e", "i", "o", "u"]


def weighted_random_letter():
    return random.choices(LETTERS, weights=WEIGHTS, k=1)[0]


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
        self.font = pygame.font.Font(
            "lib/font/minercraftory.regular.ttf", int(self.tile_size * 0.6)
        )
        self.grid = []
        self.selected = []
        self.word_data = self._load_word_data()
        self.generate_valid_board()

    def _load_word_data(self):
        with open("lib/word_list/word_list.txt", "r", encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip()]
        data = {"guarantee_word": []}
        for w in words:
            if len(w) == 3:
                data["guarantee_word"].append(w)
            data.setdefault(str(len(w)), []).append(w)
        return data

    def is_valid_board(self, letters):
        bc = Counter(letters)
        return any(not (Counter(w) - bc) for w in self.word_data["guarantee_word"])

    def get_longest_possible_word(self):
        bc = Counter(t.letter.lower() for row in self.grid for t in row if t.letter)
        for length in range(16, 2, -1):
            for w in self.word_data.get(str(length), []):
                if not (Counter(w) - bc):
                    return w
        return ""

    def generate_valid_board(self):
        """Generate a board with controlled vowel distribution and at least one valid word."""
        while True:
            total_tiles = self.size * self.size
            letters = []

            for _ in range(random.randint(Config.max_vowel, Config.max_vowel+2)):
                letters.append(random.choice(VOWELS))

            letter_pool = list(Config.letter_weights.keys())
            letter_weights = [1 if l in VOWELS else Config.letter_weights[l] for l in letter_pool]

            while len(letters) < total_tiles:
                letters.append(random.choices(letter_pool, weights=letter_weights, k=1)[0])

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
                row.append(
                    Tile(
                        letters[i], r, c, self.tile_size, x, y,
                        self.font, ability=ability, click_sound=self.click_sound
                    )
                )
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
        return (sx + col * (self.tile_size + self.padding),
                sy + row * (self.tile_size + self.padding))

    def get_current_word(self):
        return "".join(t.letter.lower() for t in self.selected)

    def get_selected_abilities(self):
        return [t.ability for t in self.selected]

    def is_current_word_valid(self):
        w = self.get_current_word()
        return bool(w) and w in self.word_data.get(str(len(w)), [])

    def handle_event(self, e):
        if e.type != pygame.MOUSEBUTTONDOWN:
            return
        pos = e.pos
        # Check if clicking a tile already selected → deselect from that point
        for i, t in enumerate(self.selected):
            if t.contains(pos):
                if self.click_sound:
                    self.click_sound.play()
                self.game.data_collector.log_tile_clicked(
                    getattr(self.game, "current_level", 1)
                )
                for x in self.selected[i:]:
                    x.reset()
                self.selected = self.selected[:i]
                self.update_positions()
                return
        # Otherwise select a new unselected tile
        for row in self.grid:
            for t in row:
                if t.letter != "" and t.contains(pos) and not t.selected:
                    if self.click_sound:
                        self.click_sound.play()
                    self.game.data_collector.log_tile_clicked(
                        getattr(self.game, "current_level", 1)
                    )
                    t.selected = True
                    self.selected.append(t)
                    self.update_positions()
                    return

    def update_positions(self):
        """Lay out selected tiles in a row near the top of the screen."""
        y = int(self.sh * 0.15)
        total = sum(
            self.tile_size + (self.selected_padding if t.selected else self.padding)
            for t in self.selected
        )
        x = self.sw // 2 - total // 2
        for t in self.selected:
            t.move_to(x, y)
            x += self.tile_size + (self.selected_padding if t.selected else self.padding)

    def attack(self, on_complete=None):
        if not self.selected or not self.is_current_word_valid():
            return
        word = self.get_current_word()
        abilities = self.get_selected_abilities()
        # Clear selected tiles from the board
        for t in self.selected:
            t.letter = ""
            t.selected = False
        self.selected = []
        self.apply_gravity_and_fill()
        self.game.player.attack_enemy(word, abilities, on_complete=on_complete)

    def apply_gravity_and_fill(self):
        """Drop tiles and refill board with correct vowel + weighted system."""
        lvl = getattr(self.game, "current_level", 1)

        for c in range(self.size):
            existing = [
                self.grid[r][c]
                for r in range(self.size - 1, -1, -1)
                if self.grid[r][c].letter != ""
            ]

            empty_count = self.size - len(existing)

            remaining_vowels = sum(1 for t in existing if t.letter.lower() in VOWELS)

            target_vowels = max(Config.max_vowel, Config.max_vowel - remaining_vowels)
            target_vowels = min(target_vowels, empty_count)

            for idx, tile in enumerate(existing):
                target_row = self.size - 1 - idx
                tx, ty = self.get_tile_position(target_row, c)
                tile.original_x, tile.original_y = tx, ty
                tile.move_to(tx, ty)
                self.grid[target_row][c] = tile

            remaining_letters = [t.letter.lower() for t in existing if t.letter]

            dynamic_weights = dict(Config.letter_weights)

            for l in remaining_letters:
                if l in dynamic_weights:
                    dynamic_weights[l] = max(1, dynamic_weights[l] // 2)

            letters_pool = list(dynamic_weights.keys())
            letters_weights = list(dynamic_weights.values())

            def weighted_letter():
                return random.choices(letters_pool, weights=letters_weights, k=1)[0]

            vowel_pool = VOWELS
            vowel_weights = [1 for _ in VOWELS]

            def weighted_vowel():
                return random.choices(vowel_pool, weights=vowel_weights, k=1)[0]

            new_letters = []

            for _ in range(target_vowels):
                new_letters.append(weighted_vowel())

            while len(new_letters) < empty_count:
                new_letters.append(weighted_letter())

            random.shuffle(new_letters)

            for idx in range(empty_count):
                target_row = idx
                tx, ty = self.get_tile_position(target_row, c)

                new_tile = Tile(
                    new_letters[idx],
                    target_row,
                    c,
                    self.tile_size,
                    tx,
                    ty,
                    self.font,
                    ability=roll_player_ability(lvl),
                    click_sound=self.click_sound
                )

                spawn_y = self.by - (empty_count - idx) * (self.tile_size + 10)
                new_tile.x = tx
                new_tile.y = spawn_y
                new_tile.target_x = tx
                new_tile.target_y = ty
                new_tile.is_falling = True

                self.grid[target_row][c] = new_tile

        self._resolve_board()

    def reroll_board(self):
        self.selected = []
        self.generate_valid_board()

    def _resolve_board(self):
        """If the refilled board has no valid 3-letter word, regenerate it."""
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
