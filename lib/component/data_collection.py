import csv
import os
import gc
import json
from datetime import datetime
from lib.component.config import Config

LOG_PATH = os.path.join("lib", "stats", Config.log_filename)
SAVE_PATH = "game_save.json"
LOG_HEADER = [
    "timestamp", "tile_clicked", "damage_received",
    "created_word", "damage_dealt", "current_level", "program_closed"
]

VALID_ABILITIES = {"n", "green", "orange", "red", "gray", "blue", "purple"}


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
            tiles = [{"letter": t.letter, "ability": t.ability} for row in gameplay.board.grid for t in row]

        player = game.player
        enemy = game.enemy

        # Debuffs stored as {ability_name: turns_remaining}
        player_debuffs = {}
        if player.frozen_turns > 0:
            player_debuffs["blue"] = player.frozen_turns
        if player.weakened_turns > 0:
            player_debuffs["purple"] = player.weakened_turns

        enemy_debuffs = {}
        if enemy.frozen_turns > 0:
            enemy_debuffs["blue"] = enemy.frozen_turns
        if enemy.weakened_turns > 0:
            enemy_debuffs["purple"] = enemy.weakened_turns

        data = {
            "current_level":     game.current_level,
            "player_health":     player.health,
            "player_max_health": player.max_health,
            "player_score":      player.score,
            "player_rerolls":    getattr(gameplay, "rerolls", Config.max_reroll) if gameplay else Config.max_reroll,
            "player_debuffs":    player_debuffs,
            "enemy_health":      enemy.health,
            "enemy_max_health":  enemy.max_health,
            "enemy_debuffs":     enemy_debuffs,
            "tiles":             tiles,
        }
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def load_game(self):
        if not os.path.exists(SAVE_PATH):
            return None

        try:
            with open(SAVE_PATH) as f:
                raw = f.read().strip()
            if not raw:
                return None
            data = json.loads(raw)
        except (json.JSONDecodeError, OSError):
            return None

        if not isinstance(data, dict):
            return None

        required_keys = [
            "current_level", "player_health", "player_max_health", "player_score",
            "player_rerolls", "enemy_health", "enemy_max_health", "tiles",
        ]

        for key in required_keys:
            if key not in data:
                return None

        int_fields = [
            "current_level", "player_health", "player_max_health",
            "player_score", "player_rerolls", "enemy_health", "enemy_max_health",
        ]

        for key in int_fields:
            if not isinstance(data[key], (int, float)):
                return None
            if data[key] < 0:
                return None
            data[key] = int(data[key])

        if data["player_health"] <= 0:
            return None

        data["player_health"] = min(data["player_health"], data["player_max_health"])
        data["enemy_health"] = min(data["enemy_health"], data["enemy_max_health"])

        # Load debuffs - default to empty dicts if missing or invalid
        player_debuffs = data.get("player_debuffs", {})
        enemy_debuffs = data.get("enemy_debuffs", {})

        if not isinstance(player_debuffs, dict):
            player_debuffs = {}
        if not isinstance(enemy_debuffs, dict):
            enemy_debuffs = {}

        data["player_debuffs"] = {k: int(v) for k, v in player_debuffs.items() if k in ("blue", "purple") and isinstance(v, (int, float)) and v > 0}
        data["enemy_debuffs"] = {k: int(v) for k, v in enemy_debuffs.items() if k in ("blue", "purple") and isinstance(v, (int, float)) and v > 0}

        tiles = data["tiles"]
        if not isinstance(tiles, list) or len(tiles) != 16:
            return None

        for tile in tiles:
            if not isinstance(tile, dict):
                return None
            if "letter" not in tile or "ability" not in tile:
                return None
            letter = tile["letter"]
            ability = tile["ability"]
            if not isinstance(letter, str) or len(letter) != 1 or not letter.isalpha():
                return None
            if not isinstance(ability, str) or ability not in VALID_ABILITIES:
                return None
            tile["letter"] = letter.upper()

        return data

    def delete_save(self):
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)

    def delete_all(self):
        gc.collect()
        for p in [LOG_PATH, SAVE_PATH]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except PermissionError:
                open(p, "w").close()
        _ensure_log()
