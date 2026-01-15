import re

TRIPLE_REPEAT_RE = re.compile(r'(.)\1\1')


def has_triple_repeat(word: str) -> bool:
    return bool(TRIPLE_REPEAT_RE.search(word))


seen = set()
i = 1

with open("vocab.txt", "w", encoding="utf-8") as dictionary:
    while True:
        try:
            with open(f"words_0{i}.txt", "r", encoding="utf-8") as f:
                for word in f:
                    word = word.strip().lower()

                    if len(word) < 2 or len(word) > 16:
                        continue
                    if not word.isalpha():
                        continue
                    if len(set(word)) == 1:
                        continue
                    if has_triple_repeat(word):
                        continue
                    if word in seen:
                        continue

                    seen.add(word)
                    dictionary.write(word + "\n")

            i += 1

        except FileNotFoundError:
            break

with open("vocab.txt", "r", encoding="utf-8") as f:
    words = sorted(f)

with open("vocab.txt", "w", encoding="utf-8") as f:
    f.writelines(words)

print("\n>>> Done")
