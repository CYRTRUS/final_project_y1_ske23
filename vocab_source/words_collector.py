import re

TRIPLE_REPEAT_RE = re.compile(r"(.)\1\1")
VOWELS = set("aeiou")


def has_triple_repeat(word: str) -> bool:
    return bool(TRIPLE_REPEAT_RE.search(word))


def is_valid_word(word: str, seen: set[str]) -> bool:
    if not (2 <= len(word) <= 16):
        return False
    if not word.isalpha():
        return False
    if len(set(word)) == 1:
        return False
    if has_triple_repeat(word):
        return False
    if word in seen:
        return False
    if not (VOWELS & set(word)):
        return False
    return True


seen: set[str] = set()
collected_words: list[str] = []

i = 1
while True:
    try:
        with open(f"vocab_source/mix_words/words_0{i}.txt", "r", encoding="utf-8") as f:
            for word in f:
                word = word.strip().lower()
                if is_valid_word(word, seen):
                    seen.add(word)
                    collected_words.append(word)
        i += 1
    except FileNotFoundError:
        break

# Sort before writing
collected_words.sort()

with open("vocab_source/vocab.txt", "w", encoding="utf-8") as f:
    for word in collected_words:
        f.write(word + "\n")

print("\n>>> Done Collecting")
