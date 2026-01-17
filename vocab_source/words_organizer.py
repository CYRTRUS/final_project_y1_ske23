import os
from collections import defaultdict

# Create the output folder if it doesn't exist
os.makedirs("letters", exist_ok=True)

# Read vocab.txt
with open("vocab.txt", "r", encoding="utf-8") as f:
    words = [line.strip().lower() for line in f if line.strip()]

# Group words by first letter
groups = defaultdict(list)
for word in words:
    groups[word[0]].append(word)

# Write files into letters/ folder
for letter, word_list in groups.items():
    file_path = os.path.join("letters", f"{letter}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(word_list))

print("\n>>> Done Organising")
