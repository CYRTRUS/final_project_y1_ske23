import random
import pygame
from lib.component.ability import roll_player_ability
from lib.component.config import Config
from lib.component.tile import Tile
from lib.component.word_bank import WordBank

VOWELS = ("a", "e", "i", "o", "u")
MAX_REFILL_ATTEMPTS = 500


def _consonant_heavy_letters(count):
    """Letters drawn from the normal weights but with every vowel's weight dropped to 1."""
    weights = {k: (1 if k in VOWELS else w) for k, w in Config.letter_weights.items()}
    return random.choices(list(weights), weights=list(weights.values()), k=count)


class Board:
    """4x4 grid of letter tiles plus the row of tiles the player has selected."""

    SIZE = Config.board_size
    PADDING = 5
    SELECTED_PADDING = 20

    def __init__(self, screen_size, area, game, click_sound=None):
        self.screen_w, self.screen_h = screen_size
        self.area = pygame.Rect(area)
        self.game = game
        self.click_sound = click_sound
        self.words = WordBank.shared()

        self.tile_size = (self.area.h - 50 - (self.SIZE - 1) * self.PADDING) // self.SIZE
        grid_w = self.SIZE * self.tile_size + (self.SIZE - 1) * self.PADDING
        self._origin = (self.area.x + (self.area.w - grid_w) // 2,
                        self.area.y + (self.area.h - grid_w) // 2 + 15)

        self.grid = []
        self.selected = []
        self.generate_valid_board()

    # Layout / iteration

    @property
    def level(self):
        return self.game.current_level

    def tiles(self):
        for row in self.grid:
            yield from row

    def letters(self):
        return [t.letter.lower() for t in self.tiles()]

    def tile_position(self, row, col):
        step = self.tile_size + self.PADDING
        return self._origin[0] + col * step, self._origin[1] + row * step

    # Generation

    def generate_valid_board(self):
        vowel_weights = [Config.letter_weights[v] for v in VOWELS]
        while True:
            letters = random.choices(VOWELS, weights=vowel_weights, k=Config.max_vowel)
            letters += _consonant_heavy_letters(self.SIZE ** 2 - len(letters))
            random.shuffle(letters)
            if self.words.has_guaranteed_word(letters):
                break
        self._build_grid(letters)

    def _build_grid(self, letters, abilities=None):
        self.selected = []
        self.grid = []
        letters = iter(letters)
        abilities = iter(abilities) if abilities else None
        for r in range(self.SIZE):
            row = []
            for c in range(self.SIZE):
                ability = next(abilities) if abilities else roll_player_ability(self.level)
                row.append(Tile(next(letters), self.tile_size, *self.tile_position(r, c), ability=ability))
            self.grid.append(row)

    def load_snapshot(self, tile_data):
        self._build_grid([td["letter"].lower() for td in tile_data],
                         [td.get("ability", "n") for td in tile_data])

    def snapshot(self):
        return [{"letter": t.letter, "ability": t.ability} for t in self.tiles()]

    def reroll(self):
        self.generate_valid_board()

    # Words

    def current_word(self):
        return "".join(t.letter.lower() for t in self.selected)

    def is_current_word_valid(self):
        word = self.current_word()
        return bool(word) and self.words.is_word(word)

    def longest_possible_word(self):
        return self.words.longest_word([t.letter.lower() for t in self.tiles() if not t.is_empty])

    def take_word(self):
        """Remove the selected (valid) word from the board, refill it and return (word, abilities)."""
        if not self.is_current_word_valid():
            return None
        word = self.current_word()
        abilities = [t.ability for t in self.selected]
        for t in self.selected:
            t.letter = ""
            t.selected = False
        self.selected = []
        self._apply_gravity_and_fill()
        return word, abilities

    # Input

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        # Clicking a selected tile deselects it and everything picked after it
        for i, tile in enumerate(self.selected):
            if tile.contains(event.pos):
                self._on_tile_clicked()
                for t in self.selected[i:]:
                    t.reset()
                self.selected = self.selected[:i]
                self._layout_selected()
                return

        for tile in self.tiles():
            if not tile.is_empty and not tile.selected and tile.contains(event.pos):
                self._on_tile_clicked()
                tile.selected = True
                self.selected.append(tile)
                self._layout_selected()
                return

    def _on_tile_clicked(self):
        if self.click_sound:
            self.click_sound.play()
        self.game.data_collector.log_tile_clicked(self.level)

    def _layout_selected(self):
        """Line the selected tiles up, centred, near the top of the screen."""
        step = self.tile_size + self.SELECTED_PADDING
        y = int(self.screen_h * 0.15)
        x = self.screen_w // 2 - (step * len(self.selected)) // 2
        for t in self.selected:
            t.move_to(x, y)
            x += step

    # Gravity / refill

    def _apply_gravity_and_fill(self):
        empty_spots = []
        remaining = []

        for c in range(self.SIZE):
            column = [self.grid[r][c] for r in range(self.SIZE - 1, -1, -1) if not self.grid[r][c].is_empty]
            for idx, tile in enumerate(column):
                row = self.SIZE - 1 - idx
                tile.set_home(*self.tile_position(row, c))
                self.grid[row][c] = tile
                remaining.append(tile.letter.lower())
            empty_spots += [(r, c) for r in range(self.SIZE - len(column))]

        new_letters = self._refill_letters(remaining, len(empty_spots))
        if new_letters is None:
            # Remaining tiles can't be completed into a playable board - start over
            self.generate_valid_board()
            return

        for (r, c), letter in zip(empty_spots, new_letters):
            tx, ty = self.tile_position(r, c)
            tile = Tile(letter, self.tile_size, tx, ty, ability=roll_player_ability(self.level))
            tile.y = self.area.y - (r + 1) * (self.tile_size + self.PADDING)   # drop in from above
            self.grid[r][c] = tile

    def _refill_letters(self, remaining, count):
        vowels_on_board = sum(1 for letter in remaining if letter in VOWELS)
        vowel_count = min(max(0, Config.max_vowel - vowels_on_board), count)

        for _ in range(MAX_REFILL_ATTEMPTS):
            letters = [random.choice(VOWELS) for _ in range(vowel_count)]
            letters += _consonant_heavy_letters(count - vowel_count)
            if self.words.has_guaranteed_word(remaining + letters):
                random.shuffle(letters)
                return letters
        return None

    # Frame

    def update(self):
        for t in self.tiles():
            t.update()
        for t in self.selected:
            t.update()

    def draw(self, screen):
        for t in self.tiles():
            t.draw(screen)
