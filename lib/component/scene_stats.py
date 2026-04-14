import os
import csv
import gc
import pygame
from collections import defaultdict, Counter
from datetime import datetime
from lib.component.scene_base import BaseScene
from lib.component.button import Button
from lib.component.config import Config

LOG_PATH = os.path.join("lib", "stats", Config.log_filename)


def _load_log():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _ts_to_epoch(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y%m%d_%H%M%S").timestamp()
    except Exception:
        return 0.0


def _split_sessions(rows):
    """
    Split the full log into individual play-sessions.
    A session ends when a 'program_closed == True' row is encountered.
    """
    sessions, current = [], []
    for r in rows:
        current.append(r)
        if r.get("program_closed") == "True":
            sessions.append(current)
            current = []
    if current:
        sessions.append(current)
    return sessions


def _bucket_by_interval(pairs, interval_secs):
    """
    Group (timestamp, value) pairs into fixed-size time buckets.

    Time is measured from the FIRST timestamp in each session (not absolute
    wall-clock time), so gaps between sessions are ignored.  Pairs from
    multiple sessions are concatenated, with each session's clock reset.

    Returns an ordered list of (bucket_index, [values]) tuples.
    """
    if not pairs:
        return {}

    # Split pairs at session boundaries (pairs is already session-aware)
    buckets: dict[int, list] = defaultdict(list)
    offset = 0          # cumulative offset keeps bucket indices monotonically increasing
    session_pairs = []  # pairs inside current session

    for is_new_session, t, v in pairs:
        if is_new_session:
            # Finalise previous session: advance offset past its last bucket
            if session_pairs:
                last_t0, _ = session_pairs[0][1], session_pairs[0][2]
                last_t     = session_pairs[-1][1]
                last_bkt   = int((last_t - last_t0) // interval_secs) + 1
                offset    += last_bkt
            session_pairs = []
        session_pairs.append((is_new_session, t, v))

    # Process all sessions
    offset = 0
    cur_session: list = []
    all_sessions: list[list] = []

    for triple in pairs:
        is_new, t, v = triple
        if is_new and cur_session:
            all_sessions.append(cur_session)
            cur_session = []
        cur_session.append((t, v))
    if cur_session:
        all_sessions.append(cur_session)

    bucket_offset = 0
    for session in all_sessions:
        t0 = session[0][0]
        for t, v in session:
            bkt = int((t - t0) // interval_secs) + bucket_offset
            buckets[bkt].append(v)
        last_t = session[-1][0]
        bucket_offset += int((last_t - t0) // interval_secs) + 1

    return buckets


def _gather_pairs(data, value_key, interval_secs):
    """
    Walk through the log row-by-row, tag the start of each session,
    and return triples (is_new_session, epoch, value).
    """
    triples = []
    new_session = True
    for r in data:
        if r.get("program_closed") == "True":
            new_session = True
            continue
        val_str = r.get(value_key, "").strip()
        ts_str  = r.get("timestamp", "")
        if not val_str or not ts_str:
            continue
        try:
            triples.append((new_session, _ts_to_epoch(ts_str), int(val_str)))
        except Exception:
            continue
        new_session = False
    return triples


class StatsScene(BaseScene):
    PAGE_TITLES = [
        "Tile Clicks (every 20s)",
        "Words Created (by length)",
        "Damage Dealt (histogram)",
        "Damage Dealt (every 60s boxplot)",
        "Damage Received (scatter)",
        "Time to Complete Level (bar graph)",
    ]
    NUM_PAGES = 6

    def __init__(self, screen, switch_scene_callback, click_sound):
        super().__init__(screen, switch_scene_callback)
        self.click_sound = click_sound
        self.page        = 0

        # Base font sizes; individual pages may scale these down
        self.font       = pygame.font.Font("lib/font/minercraftory.regular.ttf", 24)
        self.big_font   = pygame.font.Font("lib/font/minercraftory.regular.ttf", 34)
        self.small_font = pygame.font.Font("lib/font/minercraftory.regular.ttf", 18)

        # Smaller variants for dense charts (20 % smaller than base 24 → 19)
        self.small_chart_font  = pygame.font.Font("lib/font/minercraftory.regular.ttf", 19)
        self.small_tick_font   = pygame.font.Font("lib/font/minercraftory.regular.ttf", 14)

        self.buttons = [
            Button(
                1430, 730, 150, 50, "Back",
                lambda: self.switch_scene_callback("menu"),
                click_sound, color=(200, 50, 50)
            ),
            Button(
                20, 730, 200, 50, "Reset game",
                self._reset, click_sound, color=(160, 30, 30)
            ),
        ]
        self._data = []
        self._refresh()

    def _reset(self):
        self._data = []
        gc.collect()
        if os.path.exists(LOG_PATH):
            try:
                os.remove(LOG_PATH)
            except PermissionError:
                open(LOG_PATH, "w").close()
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "w", newline="") as f:
            csv.writer(f).writerow([
                "timestamp", "tile_clicked", "damage_received",
                "created_word", "damage_dealt", "current_level", "program_closed"
            ])
        with open("game_save.json", "w") as f:
            f.write("{}")
        self._refresh()

    def _refresh(self):
        self._data = _load_log()

    # ── Navigation ────────────────────────────────────────────────────────────

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.page = (self.page + (1 if event.key == pygame.K_RIGHT else -1)) % self.NUM_PAGES
            if self.click_sound:
                self.click_sound.play()
            self._refresh()

    def update(self):
        pass

    def draw(self):
        self.draw_background()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 191))
        self.screen.blit(overlay, (0, 0))
        for b in self.buttons:
            b.draw(self.screen)
        self._draw_nav()
        [
            self._p0_clicks,
            self._p1_words,
            self._p2_histogram,
            self._p3_boxplot,
            self._p4_scatter,
            self._p5_level_time,
        ][self.page]()

    def _draw_nav(self):
        lbl  = self.big_font.render(self.PAGE_TITLES[self.page], True, (255, 220, 100))
        hint = self.small_font.render("use arrow keys to navigate", True, (200, 200, 200))
        cx   = self.width // 2
        self.screen.blit(lbl,  lbl.get_rect(centerx=cx, top=20))
        self.screen.blit(hint, hint.get_rect(centerx=cx, top=70))

        # Page indicator dots
        rect_w, rect_h = 36, 12
        gap     = 10
        total_w = self.NUM_PAGES * rect_w + (self.NUM_PAGES - 1) * gap
        start_x = self.width // 2 - total_w // 2
        for i in range(self.NUM_PAGES):
            color = (255, 200, 80) if i == self.page else (70, 70, 70)
            pygame.draw.rect(
                self.screen, color,
                (start_x + i * (rect_w + gap), 703, rect_w, rect_h),
                border_radius=3
            )

    # ── Axis helper ───────────────────────────────────────────────────────────

    def _draw_axes(self, area, x_label, y_label, x_ticks, y_ticks,
                   rotate_x=False, tick_font=None):
        """
        Draw chart axes with optional 90-degree rotation of x-tick labels.
        rotate_x=True renders x labels vertically (for crowded axes).
        """
        tf = tick_font or self.small_font
        ax, ay, aw, ah = area

        # Axes lines
        pygame.draw.line(self.screen, (200, 200, 200), (ax, ay), (ax, ay + ah), 2)
        pygame.draw.line(self.screen, (200, 200, 200), (ax, ay + ah), (ax + aw, ay + ah), 2)

        # X ticks
        n_x = max(len(x_ticks) - 1, 1)
        for i, xt in enumerate(x_ticks):
            px  = ax + int(i / n_x * aw)
            lbl = tf.render(str(xt), True, (200, 200, 200))
            if rotate_x:
                # Rotate 90 degrees so text reads bottom-to-top
                lbl = pygame.transform.rotate(lbl, 90)
                self.screen.blit(lbl, lbl.get_rect(centerx=px, bottom=ay + ah + 5 + lbl.get_height()))
            else:
                self.screen.blit(lbl, lbl.get_rect(centerx=px, top=ay + ah + 5))

        # Y ticks
        n_y = max(len(y_ticks) - 1, 1)
        for i, yt in enumerate(y_ticks):
            py  = ay + ah - int(i / n_y * ah)
            lbl = tf.render(str(yt), True, (200, 200, 200))
            self.screen.blit(lbl, lbl.get_rect(right=ax - 5, centery=py))

        # Axis labels
        xl = self.small_chart_font.render(x_label, True, (220, 220, 220))
        self.screen.blit(xl, xl.get_rect(centerx=ax + aw // 2, top=ay + ah + (80 if rotate_x else 32)))

        yl = pygame.transform.rotate(
            self.small_chart_font.render(y_label, True, (220, 220, 220)), 90
        )
        self.screen.blit(yl, yl.get_rect(right=ax - 40, centery=ay + ah // 2))

    # ── Page 0: Tile clicks ───────────────────────────────────────────────────

    def _p0_clicks(self):
        """Line chart – clicks bucketed into 20-second windows per session."""
        triples = []
        new_session = True
        for r in self._data:
            if r.get("program_closed") == "True":
                new_session = True
                continue
            ts = r.get("timestamp", "")
            if r.get("tile_clicked") == "True" and ts:
                triples.append((new_session, _ts_to_epoch(ts), 1))
                new_session = False

        bkts = _bucket_by_interval(triples, 20)
        if not bkts:
            self._no_data()
            return

        area = (120, 110, 1300, 480)
        ax, ay, aw, ah = area
        keys   = sorted(bkts)
        counts = [len(bkts[k]) for k in keys]
        max_c  = max(counts) or 1

        x_ticks = [f"{k * 20}s" for k in keys]
        y_ticks = list(range(0, max_c + 2, max(1, (max_c + 1) // 5)))

        self._draw_axes(
            area, "Time (20s intervals)", "Clicks",
            x_ticks, y_ticks,
            rotate_x=True, tick_font=self.small_tick_font
        )

        n   = max(len(keys) - 1, 1)
        pts = [(ax + int(i / n * aw), ay + ah - int(c / max_c * ah))
               for i, c in enumerate(counts)]
        if len(pts) >= 2:
            pygame.draw.lines(self.screen, (80, 200, 255), False, pts, 3)
        for p in pts:
            pygame.draw.circle(self.screen, (255, 200, 80), p, 5)

    # ── Page 1: Words created ─────────────────────────────────────────────────

    def _p1_words(self):
        ctr = Counter()
        for r in self._data:
            w = r.get("created_word", "").strip()
            if w:
                ctr[len(w)] += 1
        if not ctr:
            self._no_data()
            return
        col_w = [220, 220]
        x0, y0 = self.width // 2 - sum(col_w) // 2, 110
        row_h  = 44
        headers = ["Word Length", "Number of Words"]
        for ci, h in enumerate(headers):
            self.screen.blit(
                self.font.render(h, True, (255, 220, 100)),
                (x0 + sum(col_w[:ci]) + 10, y0)
            )
        pygame.draw.line(
            self.screen, (200, 200, 200),
            (x0, y0 + row_h - 4), (x0 + sum(col_w), y0 + row_h - 4), 1
        )
        for ri, (length, cnt) in enumerate(sorted(ctr.items())):
            y = y0 + row_h + ri * row_h
            pygame.draw.rect(
                self.screen,
                (40, 40, 60) if ri % 2 == 0 else (30, 30, 50),
                (x0, y, sum(col_w), row_h - 2)
            )
            self.screen.blit(
                self.font.render(str(length), True, (220, 220, 220)),
                (x0 + 10, y + 8)
            )
            self.screen.blit(
                self.font.render(str(cnt), True, (220, 220, 220)),
                (x0 + col_w[0] + 10, y + 8)
            )

    # ── Page 2: Damage dealt histogram ───────────────────────────────────────

    def _p2_histogram(self):
        vals = []
        for r in self._data:
            d = r.get("damage_dealt", "").strip()
            if d:
                try:
                    vals.append(int(d))
                except Exception:
                    pass
        if not vals:
            self._no_data()
            return

        area = (120, 110, 1300, 480)
        ax, ay, aw, ah = area
        mn, mx = min(vals), max(vals)
        bins   = 10
        bw_val = max(1, (mx - mn) / bins)
        counts = [0] * bins
        for d in vals:
            b = min(int((d - mn) / bw_val), bins - 1)
            counts[b] += 1
        max_c = max(counts) or 1
        bar_w = aw // bins - 2
        x_lbl = [str(int(mn + i * bw_val)) for i in range(bins)]
        y_lbl = list(range(0, max_c + 2, max(1, (max_c + 1) // 5)))

        self._draw_axes(
            area, "Damage dealt", "Frequency",
            x_lbl, y_lbl,
            tick_font=self.small_tick_font
        )
        for i, c in enumerate(counts):
            bx = ax + i * (aw // bins) + 1
            bh = int(c / max_c * ah)
            pygame.draw.rect(self.screen, (200, 80, 80), (bx, ay + ah - bh, bar_w, bh))

    # ── Page 3: Damage dealt box-plot (60s buckets) ───────────────────────────

    def _p3_boxplot(self):
        """Box-plot of damage dealt, bucketed every 60 seconds per session."""
        triples = _gather_pairs(self._data, "damage_dealt", 60)
        bkts    = _bucket_by_interval(triples, 60)
        if not bkts:
            self._no_data()
            return

        area = (120, 110, 1300, 480)
        ax, ay, aw, ah = area
        keys    = sorted(bkts)
        all_vals = [v for vs in bkts.values() for v in vs]
        max_v   = max(all_vals) or 1
        bw      = min(60, aw // max(len(keys), 1) - 10)

        x_ticks = [f"{k * 60}s" for k in keys]
        y_ticks = list(range(0, max_v + 2, max(1, (max_v + 1) // 5)))

        self._draw_axes(
            area, "Time (60s intervals)", "Damage dealt",
            x_ticks, y_ticks,
            rotate_x=True, tick_font=self.small_tick_font
        )

        n = max(len(keys) - 1, 1)
        for i, k in enumerate(keys):
            vs = sorted(bkts[k])
            if not vs:
                continue
            sz = len(vs)
            q1, q2, q3 = vs[sz // 4], vs[sz // 2], vs[3 * sz // 4]
            lo, hi      = vs[0], vs[-1]
            px          = ax + int(i / n * aw)

            def ty(v):
                return ay + ah - int(v / max_v * ah)

            pygame.draw.line(self.screen, (200, 200, 200), (px, ty(lo)), (px, ty(hi)), 2)
            pygame.draw.rect(
                self.screen, (80, 160, 220),
                (px - bw // 2, ty(q3), bw, ty(q1) - ty(q3))
            )
            pygame.draw.line(
                self.screen, (255, 200, 80),
                (px - bw // 2, ty(q2)), (px + bw // 2, ty(q2)), 3
            )

    # ── Page 4: Damage received scatter ──────────────────────────────────────

    def _p4_scatter(self):
        """Scatter plot of damage received; x-axis is session-relative time."""
        triples = _gather_pairs(self._data, "damage_received", 20)
        if not triples:
            self._no_data()
            return

        # Convert triples into (relative_time, value) pairs
        rel_pairs: list[tuple[float, int]] = []
        cur_t0   = None
        time_off = 0.0
        prev_t   = None

        for is_new, t, v in triples:
            if is_new or cur_t0 is None:
                if prev_t is not None:
                    time_off += (prev_t - cur_t0) if cur_t0 is not None else 0
                cur_t0 = t
            rel_pairs.append((time_off + (t - cur_t0), v))
            prev_t = t

        if not rel_pairs:
            self._no_data()
            return

        area  = (120, 110, 1300, 480)
        ax, ay, aw, ah = area
        max_t = max(p[0] for p in rel_pairs) or 1
        max_d = max(p[1] for p in rel_pairs) or 1

        n_buckets = max(1, int(max_t // 20) + 1)
        x_ticks   = [f"{i * 20}s" for i in range(0, n_buckets + 1, max(1, n_buckets // 4))]
        y_ticks   = list(range(0, int(max_d) + 2, max(1, (int(max_d) + 1) // 5)))

        self._draw_axes(
            area, "Time (20s intervals)", "Damage received",
            x_ticks, y_ticks
        )
        for rt, d in rel_pairs:
            px = ax + int(rt / max_t * aw)
            py = ay + ah - int(d / max_d * ah)
            pygame.draw.circle(self.screen, (255, 100, 80), (px, py), 6)

    # ── Page 5: Time to complete level ───────────────────────────────────────

    def _p5_level_time(self):
        """
        Bar chart showing how long each level took to complete.
        Categories: 'less than 1 min', '1 to 3 min', 'more than 3 min'
        X-axis labels appear centred under their bars (not at the axis origin).
        """
        sessions = _split_sessions(self._data)
        cats     = {"less than 1 min": 0, "1 to 3 min": 0, "more than 3 min": 0}

        for session in sessions:
            lvl_first: dict[str, float] = {}
            for r in session:
                ts  = r.get("timestamp", "")
                lvl = r.get("current_level", "").strip()
                if ts and lvl and lvl not in lvl_first:
                    lvl_first[lvl] = _ts_to_epoch(ts)

            sorted_lvls = sorted(
                lvl_first.keys(), key=lambda x: int(x) if x.isdigit() else 0
            )
            for i in range(len(sorted_lvls) - 1):
                duration = lvl_first[sorted_lvls[i + 1]] - lvl_first[sorted_lvls[i]]
                if duration < 60:
                    cats["less than 1 min"] += 1
                elif duration <= 180:
                    cats["1 to 3 min"] += 1
                else:
                    cats["more than 3 min"] += 1

        if sum(cats.values()) == 0:
            self._no_data()
            return

        area = (120, 110, 1300, 480)
        ax, ay, aw, ah = area
        labels  = list(cats.keys())
        values  = list(cats.values())
        max_v   = max(values) or 1
        n_bars  = len(labels)
        bar_w   = aw // (n_bars * 2)

        y_ticks = list(range(0, max_v + 2, max(1, (max_v + 1) // 5)))

        # Draw axes WITHOUT x tick labels (we'll place them manually under bars)
        self._draw_axes(
            area, "Time category", "Number of levels",
            [], y_ticks          # Empty x_ticks → no default x labels
        )

        colors = [(100, 200, 100), (100, 120, 220), (200, 80, 80)]
        for i, (label, val) in enumerate(zip(labels, values)):
            # Centre each bar within its third of the x-axis
            bx = ax + int((i + 0.5) / n_bars * aw) - bar_w // 2
            bh = int(val / max_v * ah)
            by = ay + ah - bh
            pygame.draw.rect(self.screen, colors[i], (bx, by, bar_w, bh))

            # Value label on top of bar
            if bh > 20:
                vl = self.small_font.render(str(val), True, (255, 255, 255))
                self.screen.blit(vl, vl.get_rect(centerx=bx + bar_w // 2, top=by + 4))

            # Category label centred under bar
            cat_lbl = self.small_font.render(label, True, (200, 200, 200))
            self.screen.blit(
                cat_lbl,
                cat_lbl.get_rect(centerx=bx + bar_w // 2, top=ay + ah + 8)
            )

    # ── Utility ───────────────────────────────────────────────────────────────

    def _no_data(self):
        msg = self.font.render(
            "No data yet  play a game first!", True, (200, 200, 200)
        )
        self.screen.blit(
            msg, msg.get_rect(centerx=self.width // 2, centery=self.height // 2)
        )
