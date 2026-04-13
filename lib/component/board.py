import pygame
import random
import math
from collections import Counter
from lib.component.tile import Tile


LETTER_WEIGHTS = {
    'a': 8, 'b': 3, 'c': 5, 'd': 4, 'e': 10, 'f': 2, 'g': 3, 'h': 4,
    'i': 9, 'j': 1, 'k': 2, 'l': 6, 'm': 4, 'n': 7, 'o': 7, 'p': 4,
    'q': 2, 'r': 7, 's': 8, 't': 7, 'u': 5, 'v': 2, 'w': 2, 'x': 2,
    'y': 3, 'z': 2
}

LETTERS = list(LETTER_WEIGHTS.keys())
WEIGHTS = list(LETTER_WEIGHTS.values())


def weighted_random_letter():
    return random.choices(LETTERS, weights=WEIGHTS, k=1)[0]


class Board:
    def __init__(self, sw, sh, bx, by, bw, bh, click_sound, game):
        self.sw, self.sh = sw, sh
        self.bx, self.by = bx, by
        self.bw, self.bh = bw, bh
        self.click_sound = click_sound
        self.game = game

        self.size = 4
        self.padding = 5
        self.selected_padding = 20

        self.tile_size = (bh - 50 - (self.size - 1) * self.padding) // self.size

        self.font = pygame.font.Font(
            "lib/font/minercraftory.regular.ttf",
            int(self.tile_size * 0.6)
        )

        self.grid = []
        self.selected = []

        self.word_data = self.load_word_data()

        self.generate_valid_board()

    def load_word_data(self):
        with open("lib/word_list/word_list.txt", "r", encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip()]

        data = {"guarantee_word": []}

        for w in words:
            if len(w) == 3:
                data["guarantee_word"].append(w)
            data.setdefault(str(len(w)), []).append(w)

        return data

    def is_valid_board(self, letters):
        """Check that at least one 3-letter guarantee word can be formed from letters."""
        board_counter = Counter(letters)
        return any(not (Counter(w) - board_counter) for w in self.word_data["guarantee_word"])

    def generate_random_letters(self):
        return [weighted_random_letter() for _ in range(self.size * self.size)]

    def generate_valid_board(self):
        while True:
            letters = self.generate_random_letters()
            if self.is_valid_board(letters):
                break
        self.build_grid(letters)

    def build_grid(self, letters):
        self.grid = []
        i = 0

        gw = self.size * self.tile_size + (self.size - 1) * self.padding
        gh = gw

        sx = self.bx + (self.bw - gw) // 2
        sy = self.by + (self.bh - gh) // 2 + 15

        for r in range(self.size):
            row = []
            for c in range(self.size):
                x = sx + c * (self.tile_size + self.padding)
                y = sy + r * (self.tile_size + self.padding)

                row.append(Tile(letters[i], r, c, self.tile_size, x, y, self.font))
                i += 1

            self.grid.append(row)

    def get_current_word(self):
        return "".join(t.letter.lower() for t in self.selected)

    def is_current_word_valid(self):
        w = self.get_current_word()
        return w in self.word_data.get(str(len(w)), []) if w else False

    def handle_event(self, e):
        if e.type != pygame.MOUSEBUTTONDOWN:
            return

        pos = e.pos

        for i, t in enumerate(self.selected):
            if t.contains(pos):
                for x in self.selected[i:]:
                    x.reset()
                self.selected = self.selected[:i]
                self.update_positions()
                return

        for row in self.grid:
            for t in row:
                if t.letter != "" and t.contains(pos) and not t.selected:
                    t.selected = True
                    self.selected.append(t)
                    self.update_positions()
                    return

    def update_positions(self):
        y = int(self.sh * 0.15)

        total = sum(self.spacing(t) for t in self.selected)
        x = self.sw // 2 - total // 2

        for t in self.selected:
            t.move_to(x, y)
            x += self.spacing(t)

    def spacing(self, tile):
        return self.tile_size + (self.selected_padding if tile.selected else self.padding)

    def attack(self):
        if not self.selected:
            return
        if not self.is_current_word_valid():
            return

        word = self.get_current_word()
        self.game.player.attack_enemy(word)

        # Mark used tiles as empty
        for t in self.selected:
            t.letter = ""
            t.selected = False

        self.selected = []

        # Apply gravity first (existing tiles fall), then fill new tiles
        self.apply_gravity_and_fill()

    def get_tile_position(self, row, col):
        gw = self.size * self.tile_size + (self.size - 1) * self.padding
        sx = self.bx + (self.bw - gw) // 2
        sy = self.by + (self.bh - gw) // 2

        return (
            sx + col * (self.tile_size + self.padding),
            sy + row * (self.tile_size + self.padding)
        )

    def apply_gravity_and_fill(self):
        """
        Step 1: Existing non-empty tiles fall to the bottom of their column.
        Step 2: New tiles are created, spawn above the column's top slot,
                then fall into the empty top slots.
        Step 3: Validate board; if invalid, regenerate from scratch.
        """
        for c in range(self.size):
            # Collect existing non-empty tiles (bottom-first order)
            existing = []
            for r in range(self.size - 1, -1, -1):
                t = self.grid[r][c]
                if t.letter != "":
                    existing.append(t)

            empty_count = self.size - len(existing)

            # Assign existing tiles to bottom rows, animate them falling
            for idx, tile in enumerate(existing):
                target_row = self.size - 1 - idx
                tx, ty = self.get_tile_position(target_row, c)
                tile.original_x = tx
                tile.original_y = ty
                tile.move_to(tx, ty)
                self.grid[target_row][c] = tile

            # Create new tiles for the empty top slots
            new_letters = [weighted_random_letter() for _ in range(empty_count)]
            for idx in range(empty_count):
                target_row = idx  # top slots
                tx, ty = self.get_tile_position(target_row, c)

                new_tile = Tile(
                    new_letters[idx],
                    target_row, c,
                    self.tile_size,
                    tx, ty,
                    self.font
                )

                # Spawn above the board; x already at the correct column
                spawn_y = self.by - (empty_count - idx) * (self.tile_size + 10)
                new_tile.x = tx          # correct column x immediately
                new_tile.y = spawn_y     # above the board
                new_tile.target_x = tx
                new_tile.target_y = ty
                new_tile.is_falling = True

                self.grid[target_row][c] = new_tile

        # Validate that the merged board (remaining + new) can form a guarantee word
        self.resolve_board()

    def resolve_board(self):
        """If the current board cannot form a valid word, regenerate entirely."""
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
