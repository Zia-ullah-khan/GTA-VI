import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import shutil

WORKSPACE_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
ARTIFACT_DIR = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c"

BG_COLOR = "#2e3035"       # Similar to reference dark gray
TEXT_COLOR = "#000000"

def draw_mission(ax, x, y, w, h, title, subtitle="", is_climax=False, is_gate=False):
    bg = "#fef08a" if not is_climax else "#fed7aa"
    border = "#ca8a04" if not is_climax else "#ea580c"
    lw = 2.0 if (is_climax or is_gate) else 1.2
    
    rect = patches.Rectangle(
        (x, y), w, h,
        linewidth=lw,
        edgecolor=border,
        facecolor=bg,
        zorder=3
    )
    ax.add_patch(rect)
    
    ty = y + h/2 + 0.12 if subtitle else y + h/2
    ax.text(x + w/2, ty, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1c1917", zorder=4)
    if subtitle:
        ax.text(x + w/2, y + 0.2, subtitle, ha="center", va="center", fontsize=7.0, color="#44403c", zorder=4)

def draw_callout(ax, x, y, w, h, text, icon_type="text", badge=""):
    # icon_type: "phone", "text", "mailbox", "cash"
    rect = patches.Rectangle(
        (x, y), w, h,
        linewidth=1.0,
        edgecolor="#71717a",
        facecolor="#ffffff",
        zorder=3
    )
    ax.add_patch(rect)
    
    icon_str = ""
    if icon_type == "phone":
        icon_str = "[CALL] "
    elif icon_type == "text":
        icon_str = "[MSG] "
    elif icon_type == "mailbox":
        icon_str = "[MAILBOX] "
    elif icon_type == "cash":
        icon_str = "[$ CASH] "
        
    full_text = icon_str + text
    ax.text(x + w/2, y + h/2, full_text, ha="center", va="center", fontsize=7.2, fontweight="bold" if icon_type=="phone" else "normal", color="#09090b", zorder=4)

def draw_heart(ax, x, y, w, h, text, skip_tag=True):
    # Relationship / Domestic Task
    rect = patches.Rectangle(
        (x, y), w, h,
        linewidth=1.2,
        edgecolor="#f43f5e",
        facecolor="#ffe4e6",
        zorder=3
    )
    ax.add_patch(rect)
    heart_text = "♥ " + text
    if skip_tag:
        heart_text += "\n[ANY% SKIP]"
    ax.text(x + w/2, y + h/2, heart_text, ha="center", va="center", fontsize=6.8, fontweight="bold", color="#9f1239", zorder=4)

def draw_side(ax, x, y, w, h, text, skip_tag=True):
    # Purple side activity
    rect = patches.Rectangle(
        (x, y), w, h,
        linewidth=1.2,
        edgecolor="#a855f7",
        facecolor="#f3e8ff",
        zorder=3
    )
    ax.add_patch(rect)
    side_text = text
    if skip_tag:
        side_text += "\n[OPTIONAL / SKIP]"
    ax.text(x + w/2, y + h/2, side_text, ha="center", va="center", fontsize=6.8, color="#581c87", zorder=4)

def draw_diamond(ax, cx, cy, r, text):
    pts = [[cx, cy + r], [cx + r*1.6, cy], [cx, cy - r], [cx - r*1.6, cy]]
    poly = patches.Polygon(pts, closed=True, linewidth=1.5, edgecolor="#cbd5e1", facecolor="#ffffff", zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=6.8, fontweight="bold", color="#0f172a", zorder=4)

def draw_speedrun_note(ax, x, y, w, h, title, note):
    rect = patches.Rectangle(
        (x, y), w, h,
        linewidth=1.5,
        edgecolor="#10b981",
        facecolor="#064e3b",
        zorder=3
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.22, "⚡ SPEEDRUN OPTIMIZATION", ha="center", va="center", fontsize=7.5, fontweight="bold", color="#34d399", zorder=4)
    ax.text(x + w/2, y + h/2 - 0.1, note, ha="center", va="center", fontsize=6.8, color="#ecfdf5", zorder=4)

def draw_arrow(ax, p1, p2, color="#ffffff", lw=1.2, rad=0.0):
    conn = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    ax.annotate(
        "",
        xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle="->,head_width=0.25,head_length=0.35",
            color=color,
            lw=lw,
            shrinkA=3,
            shrinkB=3,
            connectionstyle=conn
        ),
        zorder=2
    )

print("Speedrun flowchart primitives initialized.")
