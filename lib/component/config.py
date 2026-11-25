import os
import random


class Config:
    """Central place for every tunable number, path and asset name."""

    # Window
    screen_width = 1600
    screen_height = 800
    fps = 60
    title = "WordForge"

    # Paths (relative to the project root, where main.py lives)
    lib_dir = "lib"
    asset_dir = os.path.join(lib_dir, "asset")
    sfx_dir = os.path.join(lib_dir, "sfx")
    stats_dir = os.path.join(lib_dir, "stats")
    font_path = os.path.join(lib_dir, "font", "minercraftory.regular.ttf")
    word_list_path = os.path.join(lib_dir, "word_list", "word_list.txt")
    log_filename = "log_1.csv"
    log_path = os.path.join(stats_dir, log_filename)
    save_path = "game_save.json"

    # Player   HP formula: max_hp = base_hp + factor_hp * (level - 1)
    player_base_dmg = 3
    player_base_hp = 8
    player_factor_hp = 2.5

    # Enemy    HP  formula: max_hp  = base_hp  + factor_hp  * (level - 1)
    #          DMG formula: atk_dmg = base_dmg + factor_dmg * (level - 1)  (+/- threshold %)
    enemy_base_hp = 15
    enemy_factor_hp = 5
    enemy_base_dmg = 2
    enemy_factor_dmg = 0.3
    enemy_threshold_dmg = 15

    # Movement. Player lunges when any boosted ability is present (orange/red/gray).
    # Enemy lunges when it uses any special ability (green/blue/purple).
    entity_walking_speed = 12
    entity_lunge_speed = 0.5
    entity_sprite_scale = 6

    # Board
    board_size = 4
    avg_vowel = 4
    max_vowel = min(random.randint(avg_vowel, int(avg_vowel * 1.5)), board_size ** 2)
    letter_weights = {
        "a": 8,  "b": 3,  "c": 5,  "d": 4,  "e": 9,
        "f": 2,  "g": 3,  "h": 4,  "i": 8,  "j": 1,
        "k": 2,  "l": 6,  "m": 4,  "n": 7,  "o": 8,
        "p": 4,  "q": 1,  "r": 7,  "s": 7,  "t": 7,
        "u": 6,  "v": 1,  "w": 2,  "x": 1,  "y": 3,
        "z": 1,
    }

    # Abilities
    heal_amount = 0.1
    orange_boost = 1.25
    red_boost = 1.50
    gray_boost = 2.00
    weaken_amount = 0.5
    num_frozen_turn = 1
    num_weaken_turn = 1
    base_dmg_multiplier = 1
    word_bonus_multiplier = 1.05

    # Ability keys: "n" = normal, "green", "orange", "red", "gray", "blue", "purple"
    player_ability_weights_base = {
        "n": 225, "green": 5, "orange": 3, "red": 2, "gray": 1, "blue": 3, "purple": 2
    }
    player_ability_max = 15

    enemy_ability_weights_base = {
        "n": 100, "green": 5, "blue": 1, "purple": 2
    }
    enemy_ability_max = 10

    # Words that instantly defeat the enemy (debug / easter egg)
    cheat_words = ("plummet",)
    cheat_damage = 1_000_000_000

    # Tools
    max_reroll = 3
    reroll_bonus_every = 5
    hint_penalty = 2

    # Sound effects: name -> number of variants, file is f"{name}_{n}.mp3" with n in 1..variants
    sfx_variants = {
        "ambient": 1,
        "btn_click": 1,
        "btn_hovering": 1,
        "fail_sound": 1,
        "level_up": 1,
        "notify": 1,
        "blood_sound": 1,
        "enemy_attack": 1,
        "enemy_die": 3,
        "enemy_hurt": 3,
        "enemy_idle": 3,
        "player_attack": 2,
        "player_die": 1,
        "boosted": 1,
        "freeze": 1,
        "heal": 1,
        "weaken": 1,
    }

    # Volumes (0 - 100)
    click_volume = 100
    hover_volume = 10
    noti_volume = 50
    ambient_volume = 100
    sfx_volume = 100

    hover_brightness = 30
