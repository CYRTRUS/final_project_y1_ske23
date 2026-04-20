import tkinter as _tk_mod
from lib.component.stats_data import (
    get_tile_clicked,
    get_word_created,
    get_damage_dealt,
    get_word_length,
    get_beat_time,
)
import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

import matplotlib
matplotlib.use("TkAgg")

# local data reader
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress tkinter Variable.__del__ RuntimeError on non-main-thread teardown
_orig_var_del = _tk_mod.Variable.__del__


def _safe_var_del(self):
    try:
        _orig_var_del(self)
    except RuntimeError:
        pass


_tk_mod.Variable.__del__ = _safe_var_del

# palette
BG = "#1a1a2e"
PANEL = "#16213e"
ACCENT = "#e94560"
ACCENT2 = "#0f3460"
TEXT = "#eaeaea"
TEXT_DIM = "#8888aa"
GOLD = "#f5c518"
GRID_COLOR = "#2a2a4a"
CHART_BG = "#16213e"
FONT_TITLE = ("Consolas", 13, "bold")
FONT_BODY = ("Consolas", 11)
FONT_SMALL = ("Consolas", 9)

STAT_CHOICES = [
    "Tile Clicks Over Time (Line)",
    "Words Created by Length (Table)",
    "Damage Dealt Distribution (Boxplot)",
    "Word Length Spread (Histogram)",
    "Time to Beat Level (Bar)",
]


# helpers

def _style_axes(ax):
    ax.set_facecolor(CHART_BG)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)
    ax.xaxis.label.set_color(TEXT_DIM)
    ax.yaxis.label.set_color(TEXT_DIM)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.grid(color=GRID_COLOR, linewidth=0.6)


# main window

class StatsWindow:

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def launch(cls):
        """Launch (or focus) the stats window in the main thread via a flag."""
        with cls._lock:
            if cls._instance and cls._instance._alive:
                try:
                    cls._instance.root.lift()
                    cls._instance.root.focus_force()
                    return
                except Exception:
                    pass
            t = threading.Thread(target=cls._run, daemon=True)
            t.start()

    @classmethod
    def _run(cls):
        win = cls()
        cls._instance = win
        win.root.mainloop()
        win._alive = False

    @classmethod
    def shutdown(cls):
        """Destroy the stats window from any thread, then wait for it to close."""
        with cls._lock:
            inst = cls._instance
        if inst is None or not inst._alive:
            return
        try:
            # Schedule destroy on the Tk thread; it runs on its next iteration
            inst.root.after(0, inst._on_close)
        except Exception:
            pass

    # init

    def __init__(self):
        self._alive = True
        self.root = tk.Tk()
        self.root.title("WordForge - Stats")
        self.root.configure(bg=BG)
        self.root.geometry("1000x700")
        self.root.minsize(800, 560)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_toolbar()
        self._build_infobar()
        self._build_canvas_area()
        self._build_strip()

        # force initial draw
        self.root.after(100, self._refresh)

    # decorative bottom strip

    def _build_strip(self):
        tk.Frame(self.root, bg=ACCENT2, height=6).pack(fill="x", side="bottom")

    # toolbar
    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=ACCENT2, pady=6, padx=10)
        bar.pack(fill="x", side="top")

        tk.Label(bar, text="WordForge Stats", bg=ACCENT2,
                 fg=GOLD, font=("Consolas", 14, "bold")).pack(side="left")

        # Refresh button (top-right)
        btn = tk.Button(
            bar, text="Refresh", command=self._refresh,
            bg=ACCENT, fg=TEXT, font=FONT_BODY,
            relief="flat", padx=10, pady=2,
            activebackground="#c73650", activeforeground=TEXT, cursor="hand2"
        )
        btn.pack(side="right", padx=(6, 0))

        # Dropdown
        self._stat_var = tk.StringVar(value=STAT_CHOICES[0])
        combo = ttk.Combobox(
            bar, textvariable=self._stat_var,
            values=STAT_CHOICES, state="readonly",
            font=FONT_BODY, width=38
        )
        combo.pack(side="right", padx=(0, 12))
        combo.bind("<<ComboboxSelected>>", lambda _: self._refresh())

        # Style the combobox
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=PANEL, background=PANEL,
                        foreground=TEXT, selectbackground=ACCENT2,
                        selectforeground=TEXT, arrowcolor=TEXT)

    # canvas area

    def _build_canvas_area(self):
        self._frame = tk.Frame(self.root, bg=BG)
        self._frame.pack(fill="both", expand=True, padx=16, pady=(12, 4))
        self._canvas_widget = None
        self._fig = None

    # info bar (between toolbar and chart)

    def _build_infobar(self):
        foot = tk.Frame(self.root, bg=PANEL, pady=5, padx=12)
        foot.pack(fill="x")

        tk.Label(foot, text="Data source: lib/stats/log_1.csv",
                 bg=PANEL, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left")

        self._limit_var = tk.BooleanVar(value=False)
        chk = tk.Checkbutton(
            foot, text="Limit to first 100 rows",
            variable=self._limit_var,
            bg=PANEL, fg=TEXT, selectcolor=ACCENT2,
            activebackground=PANEL, activeforeground=TEXT,
            font=FONT_BODY, cursor="hand2",
            command=self._refresh
        )
        chk.pack(side="right")

    # refresh

    def _refresh(self):
        limit = 100 if self._limit_var.get() else None
        choice = self._stat_var.get()

        # clear old chart
        if self._canvas_widget:
            self._canvas_widget.get_tk_widget().destroy()
            self._canvas_widget = None
        if self._fig:
            plt.close(self._fig)
            self._fig = None

        try:
            if choice == STAT_CHOICES[0]:
                self._draw_line(limit)
            elif choice == STAT_CHOICES[1]:
                self._draw_table(limit)
            elif choice == STAT_CHOICES[2]:
                self._draw_boxplot(limit)
            elif choice == STAT_CHOICES[3]:
                self._draw_histogram(limit)
            elif choice == STAT_CHOICES[4]:
                self._draw_bar(limit)
        except FileNotFoundError:
            messagebox.showerror("File Not Found",
                                 "lib/stats/log_1.csv not found.\nPlay the game first to generate data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")

    # chart builders

    def _embed(self, fig):
        self._fig = fig
        fig.patch.set_facecolor(BG)
        canvas = FigureCanvasTkAgg(fig, master=self._frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas_widget = canvas

    # 1. Line graph

    def _draw_line(self, limit):
        data = get_tile_clicked(limit)
        fig, ax = plt.subplots(figsize=(9, 5), dpi=96)
        _style_axes(ax)

        if not data:
            ax.text(0.5, 0.5, "No tile-click data yet.", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_DIM, fontsize=12)
        else:
            xs = list(range(1, len(data) + 1))
            ax.plot(xs, data, color=ACCENT, linewidth=2, marker="o",
                    markersize=4, markerfacecolor=GOLD)
            ax.fill_between(xs, data, alpha=0.15, color=ACCENT)
            ax.set_xlabel(f"Time bucket (each = {20}s)")
            ax.set_ylabel("Tile clicks")
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

        ax.set_title("Tile Clicks Over Time")
        self._embed(fig)

    # 2. Table

    def _draw_table(self, limit):
        data = get_word_created(limit)

        fig, ax = plt.subplots(figsize=(9, 5), dpi=96)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(CHART_BG)
        ax.axis("off")
        ax.set_title("Words Created by Length", color=TEXT, pad=14,
                     fontsize=13, fontweight="bold")

        if not data:
            ax.text(0.5, 0.5, "No word data yet.", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_DIM, fontsize=12)
            self._embed(fig)
            return

        col_labels = ["Length", "Example words"]
        rows = []
        for length, words in data.items():
            unique = sorted(set(words))
            sample = ", ".join(unique[:8])
            if len(unique) > 8:
                sample += f"  (+{len(unique)-8} more)"
            rows.append([str(length), sample])

        tbl = ax.table(
            cellText=rows,
            colLabels=col_labels,
            loc="center",
            cellLoc="left"
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        tbl.auto_set_column_width([0, 1])

        for (r, c), cell in tbl.get_celld().items():
            cell.set_edgecolor(GRID_COLOR)
            if r == 0:
                cell.set_facecolor(ACCENT2)
                cell.set_text_props(color=GOLD, fontweight="bold")
            else:
                cell.set_facecolor(PANEL if r % 2 == 0 else BG)
                cell.set_text_props(color=TEXT)

        self._embed(fig)

    # 3. Histogram (Word Length Spread)

    def _draw_histogram(self, limit):
        data = get_word_length(limit)
        fig, ax = plt.subplots(figsize=(9, 5), dpi=96)
        _style_axes(ax)

        if not data:
            ax.text(0.5, 0.5, "No word-length data yet.", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_DIM, fontsize=12)
        else:
            ax.hist(data, bins=range(min(data), max(data) + 2), color=ACCENT,
                    edgecolor=BG, linewidth=0.6, alpha=0.9, align="left")
            ax.set_xlabel("Word length (letters)")
            ax.set_ylabel("Frequency")
            mean_v = sum(data) / len(data)
            ax.axvline(mean_v, color=GOLD, linestyle="--", linewidth=1.4,
                       label=f"Mean: {mean_v:.1f}")
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            ax.legend(facecolor=PANEL, edgecolor=GRID_COLOR, labelcolor=TEXT, fontsize=9)

        ax.set_title("Word Length Spread")
        self._embed(fig)

    # 4. Boxplot (Damage Dealt Distribution)

    def _draw_boxplot(self, limit):
        data = get_damage_dealt(limit)
        fig, ax = plt.subplots(figsize=(9, 5), dpi=96)
        _style_axes(ax)

        if not data:
            ax.text(0.5, 0.5, "No damage data yet.", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_DIM, fontsize=12)
            ax.set_title("Damage Dealt Distribution")
        else:
            ax.boxplot(
                data, vert=True, patch_artist=True,
                widths=0.55,
                medianprops=dict(color=GOLD, linewidth=2),
                boxprops=dict(facecolor=ACCENT2, color=ACCENT),
                whiskerprops=dict(color=TEXT_DIM),
                capprops=dict(color=TEXT_DIM),
                flierprops=dict(marker="o", color=ACCENT, markersize=4, alpha=0.5)
            )
            ax.set_xlim(0.4, 1.6)
            ax.set_ylabel("Damage dealt")
            ax.set_xticks([1])
            ax.set_xticklabels(["All attacks"])
            n = len(data)
            mn = min(data)
            mx = max(data)
            med = sorted(data)[n // 2]
            ax.set_title(f"Damage Dealt Distribution  (n={n}, min={mn:.0f}, med={med:.0f}, max={mx:.0f})")

        self._embed(fig)

    # 5. Bar

    def _draw_bar(self, limit):
        data = get_beat_time(limit)
        fig, ax = plt.subplots(figsize=(9, 5), dpi=96)
        _style_axes(ax)

        labels = ["< 1 min", "1 - 3 min", "> 3 min"]
        values = [data["less_than_1"], data["1_to_3"], data["more_than_3"]]
        colors = [ACCENT, GOLD, "#4ec9b0"]

        if sum(values) == 0:
            ax.text(0.5, 0.5, "No level-completion data yet.", transform=ax.transAxes,
                    ha="center", va="center", color=TEXT_DIM, fontsize=12)
        else:
            bars = ax.bar(labels, values, color=colors, edgecolor=BG, linewidth=0.8, width=0.5)
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                        str(val), ha="center", va="bottom", color=TEXT, fontsize=10)
            ax.set_ylabel("Level completions")
            ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

        ax.set_title("Time to Beat a Level")
        self._embed(fig)

    # close

    def _on_close(self):
        self._alive = False
        if self._fig:
            plt.close(self._fig)
        self.root.destroy()
