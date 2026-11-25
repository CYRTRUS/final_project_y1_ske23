"""Tkinter + matplotlib window showing charts built from the gameplay log."""
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib.ticker as mticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from lib.component.stats_data import (
    FILE_PATH, TIME_INTERVAL,
    get_beat_time, get_damage_dealt, get_tile_clicked, get_word_created, get_word_length,
)


def _silence_runtime_error(cls):
    """Tk objects garbage-collected from a non-Tk thread raise RuntimeError in __del__."""
    original = cls.__del__

    def safe_del(self):
        try:
            original(self)
        except RuntimeError:
            pass

    cls.__del__ = safe_del


_silence_runtime_error(tk.Variable)
_silence_runtime_error(tk.Image)

# palette
BG = "#1a1a2e"
PANEL = "#16213e"
ACCENT = "#e94560"
ACCENT2 = "#0f3460"
TEXT = "#eaeaea"
TEXT_DIM = "#8888aa"
GOLD = "#f5c518"
TEAL = "#4ec9b0"
GRID_COLOR = "#2a2a4a"
CHART_BG = "#16213e"
FONT_BODY = ("Consolas", 11)
FONT_SMALL = ("Consolas", 9)
FIGSIZE = (9, 5)
DPI = 96
ROW_LIMIT = 100
TABLE_SAMPLE = 8


def _style_axes(ax):
    ax.set_facecolor(CHART_BG)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)
    ax.xaxis.label.set_color(TEXT_DIM)
    ax.yaxis.label.set_color(TEXT_DIM)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)
    ax.grid(color=GRID_COLOR, linewidth=0.6)


def _no_data(ax, message):
    ax.text(0.5, 0.5, message, transform=ax.transAxes,
            ha="center", va="center", color=TEXT_DIM, fontsize=12)


def _new_axes(styled=True):
    # A bare Figure (not pyplot) is safe to build on the stats window's own thread
    fig = Figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_subplot()
    if styled:
        _style_axes(ax)
    return fig, ax


# Chart builders: each takes `limit` and returns a matplotlib Figure

def chart_tile_clicks(limit):
    data = get_tile_clicked(limit)
    fig, ax = _new_axes()
    if not data:
        _no_data(ax, "No tile-click data yet.")
    else:
        xs = list(range(1, len(data) + 1))
        ax.plot(xs, data, color=ACCENT, linewidth=2, marker="o", markersize=4, markerfacecolor=GOLD)
        ax.fill_between(xs, data, alpha=0.15, color=ACCENT)
        ax.set_xlabel(f"Time bucket (each = {TIME_INTERVAL}s)")
        ax.set_ylabel("Tile clicks")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_title("Tile Clicks Over Time")
    return fig


def chart_words_table(limit):
    data = get_word_created(limit)
    fig, ax = _new_axes(styled=False)
    ax.set_facecolor(CHART_BG)
    ax.axis("off")
    ax.set_title("Words Created by Length", color=TEXT, pad=14, fontsize=13, fontweight="bold")
    if not data:
        _no_data(ax, "No word data yet.")
        return fig

    rows = []
    for length, words in data.items():
        unique = sorted(set(words))
        sample = ", ".join(unique[:TABLE_SAMPLE])
        if len(unique) > TABLE_SAMPLE:
            sample += f"  (+{len(unique) - TABLE_SAMPLE} more)"
        rows.append([str(length), sample])

    tbl = ax.table(cellText=rows, colLabels=["Length", "Example words"], loc="center", cellLoc="left")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.auto_set_column_width([0, 1])
    for (r, _), cell in tbl.get_celld().items():
        cell.set_edgecolor(GRID_COLOR)
        if r == 0:
            cell.set_facecolor(ACCENT2)
            cell.set_text_props(color=GOLD, fontweight="bold")
        else:
            cell.set_facecolor(PANEL if r % 2 == 0 else BG)
            cell.set_text_props(color=TEXT)
    return fig


def chart_damage_boxplot(limit):
    data = get_damage_dealt(limit)
    fig, ax = _new_axes()
    if not data:
        _no_data(ax, "No damage data yet.")
        ax.set_title("Damage Dealt Distribution")
        return fig

    ax.boxplot(
        data, patch_artist=True, widths=0.55,
        medianprops=dict(color=GOLD, linewidth=2),
        boxprops=dict(facecolor=ACCENT2, color=ACCENT),
        whiskerprops=dict(color=TEXT_DIM),
        capprops=dict(color=TEXT_DIM),
        flierprops=dict(marker="o", color=ACCENT, markersize=4, alpha=0.5),
    )
    ax.set_xlim(0.4, 1.6)
    ax.set_ylabel("Damage dealt")
    ax.set_xticks([1])
    ax.set_xticklabels(["All attacks"])
    med = sorted(data)[len(data) // 2]
    ax.set_title(f"Damage Dealt Distribution  (n={len(data)}, min={min(data):.0f}, "
                 f"med={med:.0f}, max={max(data):.0f})")
    return fig


def chart_word_length_hist(limit):
    data = get_word_length(limit)
    fig, ax = _new_axes()
    if not data:
        _no_data(ax, "No word-length data yet.")
    else:
        ax.hist(data, bins=range(min(data), max(data) + 2), color=ACCENT,
                edgecolor=BG, linewidth=0.6, alpha=0.9, align="left")
        ax.set_xlabel("Word length (letters)")
        ax.set_ylabel("Frequency")
        mean = sum(data) / len(data)
        ax.axvline(mean, color=GOLD, linestyle="--", linewidth=1.4, label=f"Mean: {mean:.1f}")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.legend(facecolor=PANEL, edgecolor=GRID_COLOR, labelcolor=TEXT, fontsize=9)
    ax.set_title("Word Length Spread")
    return fig


def chart_beat_time_bar(limit):
    data = get_beat_time(limit)
    fig, ax = _new_axes()
    labels = ["< 1 min", "1 - 3 min", "> 3 min"]
    values = [data["less_than_1"], data["1_to_3"], data["more_than_3"]]
    if sum(values) == 0:
        _no_data(ax, "No level-completion data yet.")
    else:
        bars = ax.bar(labels, values, color=[ACCENT, GOLD, TEAL], edgecolor=BG, linewidth=0.8, width=0.5)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                    str(val), ha="center", va="bottom", color=TEXT, fontsize=10)
        ax.set_ylabel("Level completions")
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.set_title("Time to Beat a Level")
    return fig


CHARTS = {
    "Tile Clicks Over Time (Line)": chart_tile_clicks,
    "Words Created by Length (Table)": chart_words_table,
    "Damage Dealt Distribution (Boxplot)": chart_damage_boxplot,
    "Word Length Spread (Histogram)": chart_word_length_hist,
    "Time to Beat Level (Bar)": chart_beat_time_bar,
}
STAT_CHOICES = list(CHARTS)


class StatsWindow:
    """Singleton Tk window, run on its own daemon thread next to the pygame loop."""

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def launch(cls):
        """Open the window, or bring it to the front if it is already open."""
        with cls._lock:
            inst = cls._instance
            if inst and inst._alive:
                try:
                    inst.root.lift()
                    inst.root.focus_force()
                    return
                except tk.TclError:
                    pass
            threading.Thread(target=cls._run, daemon=True).start()

    @classmethod
    def _run(cls):
        win = cls()
        cls._instance = win
        win.root.mainloop()
        win._alive = False

    @classmethod
    def shutdown(cls):
        """Ask the Tk thread to close the window (safe to call from any thread)."""
        with cls._lock:
            inst = cls._instance
        if inst is None or not inst._alive:
            return
        try:
            inst.root.after(0, inst._on_close)
        except (tk.TclError, RuntimeError):
            pass

    def __init__(self):
        self._alive = True
        self._canvas = None
        self._fig = None

        self.root = tk.Tk()
        self.root.title("WordForge - Stats")
        self.root.configure(bg=BG)
        self.root.geometry("1000x700")
        self.root.minsize(800, 560)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_toolbar()
        self._build_infobar()
        self._frame = tk.Frame(self.root, bg=BG)
        self._frame.pack(fill="both", expand=True, padx=16, pady=(12, 4))
        tk.Frame(self.root, bg=ACCENT2, height=6).pack(fill="x", side="bottom")

        self.root.after(100, self._refresh)

    # Layout

    def _build_toolbar(self):
        bar = tk.Frame(self.root, bg=ACCENT2, pady=6, padx=10)
        bar.pack(fill="x", side="top")
        tk.Label(bar, text="WordForge Stats", bg=ACCENT2, fg=GOLD,
                 font=("Consolas", 14, "bold")).pack(side="left")

        tk.Button(
            bar, text="Refresh", command=self._refresh,
            bg=ACCENT, fg=TEXT, font=FONT_BODY, relief="flat", padx=10, pady=2,
            activebackground="#c73650", activeforeground=TEXT, cursor="hand2",
        ).pack(side="right", padx=(6, 0))

        self._stat_var = tk.StringVar(value=STAT_CHOICES[0])
        combo = ttk.Combobox(bar, textvariable=self._stat_var, values=STAT_CHOICES,
                             state="readonly", font=FONT_BODY, width=38)
        combo.pack(side="right", padx=(0, 12))
        combo.bind("<<ComboboxSelected>>", lambda _: self._refresh())

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=TEXT,
                        selectbackground=ACCENT2, selectforeground=TEXT, arrowcolor=TEXT)

    def _build_infobar(self):
        info = tk.Frame(self.root, bg=PANEL, pady=5, padx=12)
        info.pack(fill="x")
        tk.Label(info, text=f"Data source: {FILE_PATH}", bg=PANEL, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(side="left")

        self._limit_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            info, text=f"Limit to first {ROW_LIMIT} rows", variable=self._limit_var,
            bg=PANEL, fg=TEXT, selectcolor=ACCENT2, activebackground=PANEL, activeforeground=TEXT,
            font=FONT_BODY, cursor="hand2", command=self._refresh,
        ).pack(side="right")

    # Charts

    def _clear_chart(self):
        if self._canvas:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        self._fig = None

    def _refresh(self):
        self._clear_chart()
        limit = ROW_LIMIT if self._limit_var.get() else None
        try:
            fig = CHARTS[self._stat_var.get()](limit)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")
            return

        self._fig = fig
        fig.patch.set_facecolor(BG)
        self._canvas = FigureCanvasTkAgg(fig, master=self._frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)

    def _on_close(self):
        self._alive = False
        self._clear_chart()
        self.root.destroy()
