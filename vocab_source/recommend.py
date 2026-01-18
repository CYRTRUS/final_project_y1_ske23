from collections import Counter

# Load vocabulary
with open("vocab.txt", "r", encoding="utf-8") as file:
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
                result_list.append(word.strip())

    return result_list


while True:
    scrambled_letters = input(f"\n{'Available letters:':<24}").strip().lower()
    if not scrambled_letters or scrambled_letters in ["q", "quit"]:
        break

    result_list = longest_word_from_letters(scrambled_letters, word_list)

    if result_list:
        print(f"{'Longest possible word:':<23}", ", ".join(result_list))
    else:
        print(f"{'Longest possible word:':<23}", "No valid word found")

    print()
