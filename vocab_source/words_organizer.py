from collections import defaultdict

# Read vocab.txt
with open("vocab_source/vocab.txt", "r", encoding="utf-8") as f:
    words = [line.strip().lower() for line in f if line.strip()]

# Group words by first letter
groups = defaultdict(list)
for word in words:
    groups[word[0]].append(word)

# Write files into letters/ folder
for letter, word_list in groups.items():
    with open(f"vocab_source/letters/{letter}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(word_list))

print("\n>>> Done Organising")
