import csv
import os
import gc
import json
from datetime import datetime
from lib.component.config import Config

# Build log path from config filename
LOG_PATH = os.path.join("lib", "stats", Config.log_filename)
SAVE_PATH = "game_save.json"
LOG_HEADER = [
    "timestamp", "tile_clicked", "damage_received",
    "created_word", "damage_dealt", "current_level", "program_closed"
]


def _ensure_log():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", newline="") as f:
            csv.writer(f).writerow(LOG_HEADER)


def _ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


class DataCollection:
    def __init__(self):
        _ensure_log()

    def _write_row(self, row):
        _ensure_log()
        with open(LOG_PATH, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=LOG_HEADER).writerow(row)

    def _base_row(self, level):
        return {h: "" for h in LOG_HEADER} | {"timestamp": _ts(), "current_level": level}

    def log_tile_clicked(self, level):
        row = self._base_row(level)
        row["tile_clicked"] = "True"
        self._write_row(row)

    def log_death(self):
        row = self._base_row(0)
        self._write_row(row)

    def log_attack(self, word, dmg, level):
        row = self._base_row(level)
        row["created_word"] = word
        row["damage_dealt"] = dmg
        self._write_row(row)

    def log_damage_received(self, dmg, level):
        row = self._base_row(level)
        row["damage_received"] = dmg
        self._write_row(row)

    def log_program_closed(self, level):
        row = self._base_row(level)
        row["program_closed"] = "True"
        self._write_row(row)

    def save_game(self, game):
        gameplay = game.scene_manager.scenes.get("gameplay")
        tiles = []
        if gameplay and gameplay.board:
            tiles = [
                {"letter": t.letter, "ability": t.ability}
                for row in gameplay.board.grid for t in row
            ]
        data = {
            "current_level":      game.current_level,
            "player_health":      game.player.health,
            "player_max_health":  game.player.max_health,
            "player_score":       game.player.score,
            "player_rerolls":     getattr(gameplay, "rerolls", Config.max_reroll) if gameplay else Config.max_reroll,
            "enemy_health":       game.enemy.health,
            "enemy_max_health":   game.enemy.max_health,
            "tiles":              tiles,
        }
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def load_game(self):
        if not os.path.exists(SAVE_PATH):
            return None

        try:
            with open(SAVE_PATH) as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return None

            required_keys = [
                "current_level",
                "player_health",
                "player_max_health",
                "player_score",
                "player_rerolls",
                "enemy_health",
                "enemy_max_health",
                "tiles",
            ]

            for key in required_keys:
                if key not in data:
                    return None

            int_fields = [
                "current_level",
                "player_health",
                "player_max_health",
                "player_score",
                "player_rerolls",
                "enemy_health",
                "enemy_max_health",
            ]

            for key in int_fields:
                if not isinstance(data[key], int):
                    return None
                if data[key] < 0:
                    return None

            # Clamp HP
            if data["player_health"] <= 0:
                return None

            data["player_health"] = min(
                data["player_health"],
                data["player_max_health"]
            )

            data["enemy_health"] = min(
                data["enemy_health"],
                data["enemy_max_health"]
            )

            tiles = data["tiles"]

            if not isinstance(tiles, list):
                return None

            expected_tile_count = 16

            if len(tiles) != expected_tile_count:
                return None

            valid_abilities = {"n", "g", "o", "r", "w", "b", "p"}

            for tile in tiles:
                if not isinstance(tile, dict):
                    return None

                if "letter" not in tile or "ability" not in tile:
                    return None

                letter = tile["letter"]
                ability = tile["ability"]

                if not isinstance(letter, str):
                    return None

                if len(letter) != 1 or not letter.isalpha():
                    return None

                if not isinstance(ability, str):
                    return None

                if ability not in valid_abilities:
                    return None

                # Uppercase
                tile["letter"] = letter.upper()

            return data

        except Exception:
            return None

    def delete_save(self):
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)

    def delete_all(self):
        # GC to release any lingering file handles before deletion (important on Windows)
        gc.collect()
        for p in [LOG_PATH, SAVE_PATH]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except PermissionError:
                open(p, "w").close()
        _ensure_log()
