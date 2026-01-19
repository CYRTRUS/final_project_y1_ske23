from collections import Counter

# Load vocabulary
try:
    file = open("vocab.txt", "r", encoding="utf-8")
except FileNotFoundError:
    file = open("vocab_source/vocab.txt", "r", encoding="utf-8")

word_list = [word.strip().lower() for word in file]


def longest_word_from_letters(scrambled_letters, word_list):
    result_list = []
    available = Counter(scrambled_letters.lower())
    longest_length = 0

    for word in word_list:
        word_count = Counter(word)

        # Check if word can be formed
        if not (word_count - available):
            len_word = len(word)

            if len_word > longest_length:
                longest_length = len_word
                result_list = [word]   # reset list with new longest word
            elif len_word == longest_length:
                if scrambled_letters == word:
                    result_list.insert(0, word.strip())
                else:
                    result_list.append(word.strip())

    return result_list


def has_vowels(word):
    for vowel in ["a", "e", "i", "o", "u"]:
        if vowel in word:
            return True
    return False


while True:
    scrambled_letters = input(f"{'\nAvailable letters:':<32}").strip().lower()[:16]

    if scrambled_letters in ["q", "quit"]:
        break
    elif len(scrambled_letters) < 2 or not has_vowels(scrambled_letters):
        print(f"{'Longest possible word:':<30}", "No valid word found")
    else:
        result_list = longest_word_from_letters(scrambled_letters, word_list)

        if result_list:
            print(f"{f'Longest possible word ({len(result_list[0])}):':<30}", ", ".join(result_list))
        else:
            print(f"{'Longest possible word:':<30}", "No valid word found")
