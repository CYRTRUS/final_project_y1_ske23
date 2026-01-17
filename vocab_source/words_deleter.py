# Load banned
with open("banned_words.txt", "r", encoding="utf-8") as f:
    temp_list = list(f)

    banned_word_list = []

    for word in temp_list:
        banned_word_list.append(str(word).strip().lower())

# Load vocab
with open("vocab.txt", "r", encoding="utf-8") as f:
    temp_list = list(f)

    word_list = []

    for word in temp_list:
        word_list.append(str(word).strip().lower())

for word in banned_word_list:
    word_list.pop(word_list.index(word))

with open("vocab.txt", "w", encoding="utf-8") as file:
    for word in word_list:
        file.write(word + "\n")

print("\n>>> Done Deleting")
