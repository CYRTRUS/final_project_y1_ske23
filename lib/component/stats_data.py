import csv
import time
from lib.component.config import Config

FILE_PATH = f"lib/stats/{Config.log_filename}"
TIME_INTERVAL = 20


def parse_time(ts):
    return time.mktime(time.strptime(ts, "%Y%m%d_%H%M%S"))


def _read_rows(limit=None):
    """Read CSV rows, skipping header. Optionally limit to first N data rows."""
    rows = []
    try:
        with open(FILE_PATH, newline="") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                rows.append(row)
                if limit is not None and len(rows) >= limit:
                    break
    except FileNotFoundError:
        pass
    return rows


def get_tile_clicked(limit=None):
    """Tile Clicking bucketed every 20s - Line graph data."""
    rows = _read_rows(limit)
    base_time = None
    prev_time = None
    num = 0
    tile_clicked_num = []

    for row in rows:
        if not row[1] or row[1] != "True":
            continue

        curr_time = parse_time(row[0])

        if base_time is None:
            base_time = curr_time
            prev_time = curr_time

        gap = curr_time - prev_time  # type: ignore

        if gap > TIME_INTERVAL or gap < 0:
            tile_clicked_num.append(num)
            base_time = curr_time
            num = 0

        if curr_time - base_time < TIME_INTERVAL:
            num += 1
        else:
            tile_clicked_num.append(num)
            base_time = curr_time
            num = 1

        prev_time = curr_time

    if num > 0:
        tile_clicked_num.append(num)

    return tile_clicked_num


def get_word_created(limit=None):
    """Words Created grouped by length - Table data."""
    rows = _read_rows(limit)
    word_created = {}

    for row in rows:
        word = row[3]
        if word != "":
            length = len(word)
            if length not in word_created:
                word_created[length] = [word]
            else:
                word_created[length].append(word)

    return dict(sorted(word_created.items()))


def get_damage_dealt(limit=None):
    """Damage Dealt - Histogram data (list of float values)."""
    rows = _read_rows(limit)
    damage_dealt = []

    for row in rows:
        if row[4] != "":
            try:
                damage_dealt.append(float(row[4]))
            except ValueError:
                pass

    return damage_dealt


def get_word_length(limit=None):
    """Word lengths - Boxplot data (list of ints)."""
    rows = _read_rows(limit)
    word_length = []

    for row in rows:
        word = row[3]
        if word != "":
            word_length.append(len(word))

    return word_length


def get_beat_time(limit=None):
    """Time to Complete Level - Bar graph data."""
    rows = _read_rows(limit)
    beat_time = {"less_than_1": 0, "1_to_3": 0, "more_than_3": 0}
    prev_level = None
    prev_time = None

    for row in rows:
        curr_level = row[5]
        try:
            curr_time = parse_time(row[0])
        except Exception:
            continue

        if prev_level is None:
            prev_level = curr_level
            prev_time = curr_time
            continue

        if curr_level != prev_level:
            diff = curr_time - prev_time  # type: ignore
            minutes = diff / 60

            if minutes < 1:
                beat_time["less_than_1"] += 1
            elif minutes <= 3:
                beat_time["1_to_3"] += 1
            else:
                beat_time["more_than_3"] += 1

            prev_time = curr_time
            prev_level = curr_level

    return beat_time
