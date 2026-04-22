# WordForge

## Project Description

- Project by: Wassawin Swangjaeng
- Game Genre: Word puzzle

This project is a word-puzzle battle game inspired by Bookworm Adventures, in which players form words from a grid of letter tiles to attack enemies. The player connects adjacent letters to create valid words, which deal damage based on word length and tile effects. The game features an infinite-level system in which enemy difficulty increases via mathematical scaling. Special colored tiles provide additional effects such as bonus damage, healing, or weaken enemy to add strategic gameplay.

---

## Installation

To Clone this project:

```sh
git clone https://github.com/CYRTRUS/final_project_y1_ske23
```

To create and run Python Environment for This project:

Window:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Mac:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Running Guide

After activate Python Environment of this project, you can process to run the game by:

Window:

```bat
python main.py
```

Mac:

```sh
python3 main.py
```

---

## Tutorial / Usage

### Objective

Survive as many levels as possible by defeating enemies with words. Each level introduces a stronger enemy - stay alive by choosing your words wisely.

### How to Play

1. **Select tiles** - Click letter tiles on the 4×4 board to build a word. Selected tiles appear at the top of the screen. Click a tile again to deselect it (and all tiles selected after it).
2. **Form a valid word** - The Attack button turns green when your current selection forms a valid word. Words must be at least 2 letters or longer.
3. **Attack** - Click the green Attack button to send your word and deal damage to the enemy. Damage scales with word length and your current level.
4. **Enemy counterattack** - After your attack, the enemy strikes back. Survive their hit and keep building words until the enemy's HP reaches zero.
5. **Level up** - Defeating an enemy advances you to the next level. Your HP is fully restored, but the new enemy is stronger.
6. **Game over** - If your HP drops to zero, the run ends. Click anywhere on the game-over screen to return to the main menu.

### Extra Tools

- **Hint** - Reveals the longest possible word on the current board. Using it penalises you for 2 turns of zero damage, so use it only when truly stuck.
- **Reroll** - Discards the entire board and generates a new one. You start with 3 rerolls and earn 1 additional reroll every 5 levels completed.
- **How to Play** - Opens the in-game reference overlay. Click anywhere to close it.

### Damage Formula

Base damage is calculated as `(word length × ceil(level ^ 0.55)) + 3`, then multiplied by any tile ability bonuses. Longer words and boosted tiles hit much harder at higher levels.

---

## Game Features

### Tile Abilities (Player)

Colored tiles on your board grant special effects when included in a word:

| Tile Color | Effect |
| --- | --- |
| **White** (Normal) | No bonus |
| **Green** | Heals you for 10% of your max HP per green tile used |
| **Orange** | Adds a ×1.25 damage multiplier per tile |
| **Red** | Adds a ×1.50 damage multiplier per tile |
| **Gray** | Adds a ×2.00 damage multiplier per tile |
| **Blue** | Freezes the enemy for 1 turn, causing them to skip their next counterattack |
| **Purple** | Weakens the enemy for 1 turn, reducing their attack damage by 50% |

Multiple boosted tiles in one word stack their multipliers, and orange/red/gray tiles also trigger a special lunge animation when attacking.

### Enemy Abilities

Enemies can use special moves of their own when they counterattack:

- **Green** - The enemy heals itself for 10% of its max HP.
- **Blue** - The enemy attacks twice in the same turn.
- **Purple** - Weakens you for 1 turn, cutting your next attack's damage by 50%.

Enemy ability frequency and HP/damage both scale with level via a mathematical formula, ensuring an infinite and progressively challenging run.

### Word Scoring Bonuses

Certain word patterns deal extra damage on top of tile bonuses. Words that use rare letters (X, Y, Z) or end with strong suffixes (-r, -y, -es, or a consonant cluster -s) receive a 5% damage multiplier per qualifying pattern, stacking with each other.

### Save System

Your progress is automatically saved after every level and when you exit via the Back button. The next time you launch the game you can continue from exactly where you left off, including your current board state, HP, reroll count, and any active status effects.

### Statistics Window

The game logs your performance data throughout a run. A built-in statistics window lets you review charts on damage dealt, word length distribution, and time taken to complete each level.

---

## Known Bugs

- After leave a game, you might need to kill the terminal due to Matplotlib GUI warning

---

## Unfinished Works

- None

---

## External sources

Acknowledge to:

1. All Sound effects, <https://pixabay.com/sound-effects/> [SFX]
2. All Textures, <https://itch.io/game-assets/tag-pixel-art> [Texture]
3. Word library, <https://github.com/dwyl/english-words> [Word validation database]
