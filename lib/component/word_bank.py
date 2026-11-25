from collections import Counter, defaultdict
from lib.component.config import Config

MIN_GUARANTEED_LENGTH = 3


class WordBank:
    """Dictionary of valid words, loaded once and shared by every board."""

    _shared = None

    @classmethod
    def shared(cls):
        if cls._shared is None:
            cls._shared = cls(Config.word_list_path)
        return cls._shared

    def __init__(self, path):
        with open(path, "r", encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip()]

        self._words = set(words)
        # length -> first letter -> words (file order), used for the longest-word search
        self._index = defaultdict(lambda: defaultdict(list))
        for w in words:
            self._index[len(w)][w[0]].append(w)
        self._guarantee = [Counter(w) for w in words if len(w) == MIN_GUARANTEED_LENGTH]

    def is_word(self, word):
        return word in self._words

    def has_guaranteed_word(self, letters):
        """True if `letters` can spell at least one 3-letter word."""
        available = Counter(letters)
        return any(not (need - available) for need in self._guarantee)

    def longest_word(self, letters, max_length=Config.board_size ** 2):
        """Longest dictionary word that can be spelled from `letters` (or "")."""
        available = Counter(letters)
        for length in range(max_length, MIN_GUARANTEED_LENGTH - 1, -1):
            by_first = self._index.get(length)
            if not by_first:
                continue
            for first in sorted(available):
                for w in by_first.get(first, ()):
                    if not (Counter(w) - available):
                        return w
        return ""
