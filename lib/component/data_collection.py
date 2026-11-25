import csv
import json
import os
from datetime import datetime
from lib.component.ability import FREEZE, VALID_ABILITIES, WEAKEN
from lib.component.config import Config

LOG_HEADER = [
    "timestamp", "tile_clicked", "damage_received",
    "created_word", "damage_dealt", "current_level", "program_closed"
]
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

SAVE_INT_FIELDS = [
    "current_level", "player_health", "player_max_health",
    "player_score", "player_rerolls", "enemy_health", "enemy_max_health",
]
SAVE_REQUIRED_FIELDS = SAVE_INT_FIELDS + ["tiles"]
DEBUFF_KEYS = (FREEZE, WEAKEN)


def _clean_debuffs(raw):
    if not isinstance(raw, dict):
        return {}
    return {k: int(v) for k, v in raw.items()
            if k in DEBUFF_KEYS and isinstance(v, (int, float)) and v > 0}


def _valid_tile(tile):
    if not isinstance(tile, dict):
        return False
    letter, ability = tile.get("letter"), tile.get("ability")
    return (isinstance(letter, str) and len(letter) == 1 and letter.isalpha()
            and isinstance(ability, str) and ability in VALID_ABILITIES)


def validate_save(data):
    """Return a cleaned copy of a save dict, or None if it is unusable."""
    if not isinstance(data, dict) or any(k not in data for k in SAVE_REQUIRED_FIELDS):
        return None

    for key in SAVE_INT_FIELDS:
        value = data[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            return None
        data[key] = int(value)

    if data["player_health"] <= 0:
        return None
    data["player_health"] = min(data["player_health"], data["player_max_health"])
    data["enemy_health"] = min(data["enemy_health"], data["enemy_max_health"])
    data["player_debuffs"] = _clean_debuffs(data.get("player_debuffs"))
    data["enemy_debuffs"] = _clean_debuffs(data.get("enemy_debuffs"))

    tiles = data["tiles"]
    if not isinstance(tiles, list) or len(tiles) != Config.board_size ** 2:
        return None
    if not all(_valid_tile(t) for t in tiles):
        return None
    for t in tiles:
        t["letter"] = t["letter"].upper()
    return data


class DataCollection:
    """Gameplay event log (CSV) and the save file (JSON)."""

    def __init__(self, log_path=Config.log_path, save_path=Config.save_path):
        self.log_path = log_path
        self.save_path = save_path
        self._ensure_log()

    # CSV log

    def _ensure_log(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="") as f:
                csv.writer(f).writerow(LOG_HEADER)

    def _log(self, level, **fields):
        row = dict.fromkeys(LOG_HEADER, "")
        row.update(timestamp=datetime.now().strftime(TIMESTAMP_FORMAT), current_level=level, **fields)
        self._ensure_log()
        with open(self.log_path, "a", newline="") as f:
            csv.DictWriter(f, fieldnames=LOG_HEADER).writerow(row)

    def log_tile_clicked(self, level):
        self._log(level, tile_clicked="True")

    def log_death(self):
        self._log(0)

    def log_attack(self, word, dmg, level):
        self._log(level, created_word=word, damage_dealt=dmg)

    def log_damage_received(self, dmg, level):
        self._log(level, damage_received=dmg)

    def log_program_closed(self, level):
        self._log(level, program_closed="True")

    def clear_log(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        self._ensure_log()

    # Save file

    def save_game(self, data):
        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_game(self):
        try:
            with open(self.save_path) as f:
                raw = f.read().strip()
            return validate_save(json.loads(raw)) if raw else None
        except (OSError, json.JSONDecodeError):
            return None

    def delete_save(self):
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
