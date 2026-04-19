import random


class Config:

    # HP formula: max_hp = base_hp + factor_hp * (level - 1)
    player_base_dmg = 3
    player_base_hp = 8
    player_factor_hp = 2.5

    # HP  formula: max_hp  = base_hp  + factor_hp  * (level - 1)
    # DMG formula: atk_dmg = base_dmg + factor_dmg * (level - 1)
    enemy_base_hp = 20
    enemy_factor_hp = 5
    enemy_base_dmg = 2
    enemy_factor_dmg = 0.3
    enemy_threshold_dmg = 15

    log_filename = "log_1.csv"

    # Player lunges when any boosted ability is present (orange/red/gray).
    # Enemy lunges when it uses any special ability (green/blue/purple).
    entity_walking_speed = 12
    entity_lunge_speed = 0.5

    avg_vowel = 4
    max_vowel = min(random.randint(avg_vowel, int(avg_vowel*1.5)), 16)

    heal_amount = 0.1
    orange_boost = 1.25
    red_boost = 1.50
    gray_boost = 2.00
    weaken_amount = 0.5

    num_frozen_turn = 1
    num_weaken_turn = 1

    base_dmg_multiplier = 1

    # Ability keys: "n" = normal, "green", "orange", "red", "gray", "blue", "purple"
    player_ability_weights_base = {
        "n": 225, "green": 5, "orange": 3, "red": 2, "gray": 1, "blue": 3, "purple": 2
    }
    player_ability_max = 15

    enemy_ability_weights_base = {
        "n": 70, "green": 5, "blue": 1, "purple": 2
    }
    enemy_ability_max = 10

    letter_weights = {
        "a": 8,  "b": 3,  "c": 5,  "d": 4,  "e": 9,
        "f": 2,  "g": 3,  "h": 4,  "i": 8,  "j": 1,
        "k": 2,  "l": 6,  "m": 4,  "n": 7,  "o": 8,
        "p": 4,  "q": 1,  "r": 7,  "s": 7,  "t": 7,
        "u": 6,  "v": 1,  "w": 2,  "x": 1,  "y": 3,
        "z": 1,
    }

    max_reroll = 3

    hint_penalty = 2

    # Sound filenames - call as f"{name}_{random.randint(1, var)}.mp3"
    ambient = "ambient"
    ambient_var = 1
    btn_click = "btn_click"
    btn_click_var = 1
    btn_hovering = "btn_hovering"
    btn_hovering_var = 1
    fail_sound = "fail_sound"
    fail_sound_var = 1
    level_up = "level_up"
    level_up_var = 1
    notify = "notify"
    notify_var = 1

    blood_sound = "blood_sound"
    blood_sound_var = 1

    enemy_attack = "enemy_attack"
    enemy_attack_var = 1
    enemy_die = "enemy_die"
    enemy_die_var = 3
    enemy_hurt = "enemy_hurt"
    enemy_hurt_var = 3
    enemy_idle = "enemy_idle"
    enemy_idle_var = 3

    player_attack = "player_attack"
    player_attack_var = 2
    player_die = "player_die"
    player_die_var = 1

    boosted = "boosted"
    boosted_var = 1
    freeze = "freeze"
    freeze_var = 1
    heal = "heal"
    heal_var = 1
    weaken = "weaken"
    weaken_var = 1

    hover_brightness = 30
    click_volume = 100
    hover_volume = 10
    noti_volume = 50
    ambient_volume = 100
    sfx_volume = 100
