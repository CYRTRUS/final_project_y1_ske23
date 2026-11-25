"""Read the gameplay CSV log and shape it for each stats chart."""
import csv
import time
from collections import defaultdict
from lib.component.config import Config
from lib.component.data_collection import TIMESTAMP_FORMAT

FILE_PATH = Config.log_path
TIME_INTERVAL = 20      # seconds per tile-click bucket


def parse_time(ts):
    return time.mktime(time.strptime(ts, TIMESTAMP_FORMAT))


def _read_rows():
    try:
        with open(FILE_PATH, newline="") as f:
            return [{k: (v or "") for k, v in row.items()} for row in csv.DictReader(f)]
    except FileNotFoundError:
        return []


def _head(values, limit):
    return values if limit is None else values[:limit]


def _words(rows):
    return [row["created_word"] for row in rows if row["created_word"]]


def get_tile_clicked(limit=None):
    """Tile clicks per TIME_INTERVAL bucket (line graph). Long pauses start a new bucket."""
    buckets = []
    bucket_start = prev_time = None
    count = 0

    for row in _read_rows():
        if row["tile_clicked"] != "True":
            continue
        now = parse_time(row["timestamp"])
        if bucket_start is None:
            bucket_start = prev_time = now

        gap = now - prev_time
        if gap > TIME_INTERVAL or gap < 0:
            buckets.append(count)
            bucket_start, count = now, 0

        if now - bucket_start < TIME_INTERVAL:
            count += 1
        else:
            buckets.append(count)
            bucket_start, count = now, 1
        prev_time = now

    if count > 0:
        buckets.append(count)
    return _head(buckets, limit)


def get_word_created(limit=None):
    """{word length: [words]} for the first `limit` words (table)."""
    grouped = defaultdict(list)
    for word in _head(_words(_read_rows()), limit):
        grouped[len(word)].append(word)
    return dict(sorted(grouped.items()))


def get_damage_dealt(limit=None):
    """Every damage value dealt by the player (boxplot)."""
    values = []
    for row in _read_rows():
        try:
            values.append(float(row["damage_dealt"]))
        except ValueError:
            pass
    return _head(values, limit)


def get_word_length(limit=None):
    """Length of every created word (histogram)."""
    return _head([len(w) for w in _words(_read_rows())], limit)


def get_beat_time(limit=None):
    """How many levels took <1, 1-3 or >3 minutes (bar graph)."""
    beat_time = {"less_than_1": 0, "1_to_3": 0, "more_than_3": 0}
    prev_level = prev_time = None
    beaten = 0

    for row in _read_rows():
        if limit is not None and beaten >= limit:
            break
        try:
            now = parse_time(row["timestamp"])
        except ValueError:
            continue
        level = row["current_level"]

        if prev_level is None:
            prev_level, prev_time = level, now
            continue
        if level == prev_level:
            continue

        minutes = (now - prev_time) / 60
        if minutes < 1:
            beat_time["less_than_1"] += 1
        elif minutes <= 3:
            beat_time["1_to_3"] += 1
        else:
            beat_time["more_than_3"] += 1
        beaten += 1
        prev_level, prev_time = level, now

    return beat_time
