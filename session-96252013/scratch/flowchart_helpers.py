import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import shutil

# Styling Constants
BG_COLOR = "#0b0e14"
TEXT_COLOR = "#ffffff"
SUBTEXT_COLOR = "#9ca3af"

# Card Types & Colors
STYLES = {
    "normal": {
        "bg": "#151922",
        "border": "#22d3ee",       # Cyan
        "title": "#38bdf8",
        "badge_bg": "#083344",
        "badge_fg": "#38bdf8"
    },
    "milestone": {
        "bg": "#1c1427",
        "border": "#f43f5e",       # Rose / Neon Pink
        "title": "#fb7185",
        "badge_bg": "#4c0519",
        "badge_fg": "#f43f5e"
    },
    "heist": {
        "bg": "#211a12",
        "border": "#fbbf24",       # Amber / Gold
        "title": "#fde047",
        "badge_bg": "#451a03",
        "badge_fg": "#fbbf24"
    },
    "point_of_no_return": {
        "bg": "#280d16",
        "border": "#ef4444",       # Crimson
        "title": "#fca5a5",
        "badge_bg": "#7f1d1d",
        "badge_fg": "#fca5a5"
    },
    "ending": {
        "bg": "#0c221a",
        "border": "#10b981",       # Emerald
        "title": "#34d399",
        "badge_bg": "#064e3b",
        "badge_fg": "#34d399"
    }
}

def draw_card(ax, x, y, w, h, title, subtitle="", badge="", card_type="normal", fontsize=9):
    st = STYLES.get(card_type, STYLES["normal"])
    
    # Outer box
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.15",
        linewidth=1.5,
        edgecolor=st["border"],
        facecolor=st["bg"],
        zorder=3
    )
    ax.add_patch(rect)
    
    # Badge (if any)
    if badge:
        bx = x + w - 0.1
        by = y + h - 0.08
        ax.text(
            x + w/2, y + h - 0.15,
            badge.upper(),
            ha="center", va="center",
            fontsize=fontsize - 2.5,
            fontweight="bold",
            color=st["badge_fg"],
            bbox=dict(boxstyle="round,pad=0.2", facecolor=st["badge_bg"], edgecolor=st["border"], lw=0.8),
            zorder=4
        )
        title_y = y + h/2 + 0.02
        sub_y = y + 0.22
    else:
        title_y = y + h/2 + 0.12 if subtitle else y + h/2
        sub_y = y + h/2 - 0.22

    # Title
    ax.text(
        x + w/2, title_y,
        title,
        ha="center", va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=st["title"],
        zorder=4
    )
    
    # Subtitle
    if subtitle:
        ax.text(
            x + w/2, sub_y,
            subtitle,
            ha="center", va="center",
            fontsize=fontsize - 2,
            color=SUBTEXT_COLOR,
            zorder=4
        )

def draw_arrow(ax, p1, p2, color="#38bdf8", lw=1.6, rad=0.0):
    connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    ax.annotate(
        "",
        xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle="->,head_width=0.35,head_length=0.45",
            color=color,
            lw=lw,
            shrinkA=4,
            shrinkB=4,
            connectionstyle=connectionstyle
        ),
        zorder=2
    )

print("Helper definitions loaded.")
