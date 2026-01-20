import random
from collections import Counter

rows = 4
cols = 4

alphabet = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]


def random_letter():
    return random.choice(alphabet)


def create_board():
    return [[random_letter() for _ in range(cols)] for _ in range(rows)]


def print_board(board):
    for row in board:
        print(" ".join(row))
    print()


def board_counter(board):
    return Counter(ch for row in board for ch in row if ch != " ")


def can_form_word(board, word):
    return not (Counter(word) - board_counter(board))


def remove_word(board, word):
    remaining = Counter(word)
    for r in range(rows):
        for c in range(cols):
            if remaining[board[r][c]] > 0:
                remaining[board[r][c]] -= 1
                board[r][c] = " "


def apply_gravity(board):
    for c in range(cols):
        stack = [board[r][c] for r in range(rows) if board[r][c] != " "]
        for r in range(rows - 1, -1, -1):
            if stack:
                board[r][c] = stack.pop()
            else:
                board[r][c] = random_letter()


def game():
    board = create_board()

    while True:
        print_board(board)
        word = input("enter a word (or '!quit'): ").strip()
        if word == "!quit":
            break

        if can_form_word(board, word):
            remove_word(board, word)
            apply_gravity(board)
        else:
            print("word cannot be formed\n")


game()
