class Config:

    # HP formula:  max_hp = base_hp + factor_hp * (level - 1)
    player_base_hp = 5
    player_factor_hp = 2.4

    # HP  formula:  max_hp  = base_hp  + factor_hp  * (level - 1)
    # DMG formula:  atk_dmg = base_dmg + factor_dmg * (level - 1)
    enemy_base_hp = 10
    enemy_factor_hp = 5
    enemy_base_dmg = 2
    enemy_factor_dmg = 0.3

    log_filename = "log_1.csv"  # saved under lib/stats/

    # Player lunges when damage multiplier > 1 (orange/red/gray tile).
    # Enemy  lunges when it uses any special ability (g / b / p).
    entity_walking_speed = 8
    entity_lunge_speed = 0.25

    max_vowel = 4

    # Base chance weights (higher = more common).
    # Each level beyond 1 adds +1 to every non-'n' key (capped at max).
    player_ability_weights_base = {
        "n": 300, "g": 5, "o": 3, "r": 2, "w": 1, "b": 3, "p": 2
    }
    player_ability_max = 10

    enemy_ability_weights_base = {
        "n": 50, "g": 5, "b": 1, "p": 2
    }
    enemy_ability_max = 10

    letter_weights = {
        "a": 8,  "b": 3,  "c": 5,  "d": 4,  "e": 9,
        "f": 2,  "g": 3,  "h": 4,  "i": 9,  "j": 1,
        "k": 2,  "l": 6,  "m": 4,  "n": 7,  "o": 8,
        "p": 4,  "q": 1,  "r": 7,  "s": 7,  "t": 7,
        "u": 7,  "v": 1,  "w": 2,  "x": 2,  "y": 3,
        "z": 2,
    }

    max_reroll = 3   # rerolls granted at level start (+ 1 every 5 lvls)

    # ── 13. Hint penalty ─────────────────────────────────────
    hint_penalty = 2   # turns of 0-damage after using a hint

    # Final mult = base + sum of tile bonuses
    # orange (+0.25), red (+0.5), gray/white (+1.0)
    base_dmg_multiplier = 1.0

    click_volume = 100   # minecraft_click.mp3 only
    ambient_volume = 100   # forest_ambient.mp3 only
    sfx_volume = 100   # all other sound effects
