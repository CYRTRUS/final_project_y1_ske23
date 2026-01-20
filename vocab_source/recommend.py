from collections import Counter

alphabet = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
    "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
    "u", "v", "w", "x", "y", "z"
]

dictionary = {}

for letter in alphabet:
    dictionary[letter] = []
    try:
        with open(f"vocab_source/letters/{letter}.txt", "r", encoding="utf-8") as file:
            for line in file:
                word = line.strip().lower()
                if word:
                    dictionary[letter].append(word)
    except FileNotFoundError:
        raise FileNotFoundError("No letter files available.")


def has_vowels(word):
    for vowel in ["a", "e", "i", "o", "u"]:
        if vowel in word:
            return True
    return False


def longest_word_from_letters(scrambled_letters, dictionary):
    available = Counter(scrambled_letters)
    result_list = []
    longest_length = 0

    checked_letters = set(scrambled_letters)

    for letter in checked_letters:
        for word in dictionary.get(letter, []):

            if len(word) <= longest_length or len(word) > len(scrambled_letters):
                continue

            word_count = Counter(word)

            if word_count - available:
                continue

            word_len = len(word)

            if word_len > longest_length:
                longest_length = word_len
                result_list = [word]
            elif word_len == longest_length:
                if scrambled_letters == word:
                    result_list.insert(0, word)
                else:
                    result_list.append(word)

    return result_list


while True:
    scrambled_letters = input(f"{'\nAvailable letters:':<32}").strip().lower()

    if scrambled_letters in ("q", "quit"):
        break

    if len(scrambled_letters) < 2 or not has_vowels(scrambled_letters):
        print(f"{'Longest possible word:':<30}", "No valid word found")
        continue

    result_list = longest_word_from_letters(scrambled_letters, dictionary)

    if result_list:
        print(
            f"{f'Longest possible word ({len(result_list[0])}):':<30}",
            ", ".join(result_list)
        )
    else:
        print(f"{'Longest possible word:':<30}", "No valid word found")
