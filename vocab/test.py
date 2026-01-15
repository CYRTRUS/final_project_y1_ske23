with open("vocab.txt", "r", encoding="utf-8") as f:
    temp_list = list(f)

    word_list = []

    for word in temp_list:
        word_list.append(str(word).strip().lower())

while True:
    find_word = input("\nWord: ").strip().lower()
    if find_word in word_list:
        print(">>> True")
    else:
        print(">>> False")
    print("\n--------------------------------")
