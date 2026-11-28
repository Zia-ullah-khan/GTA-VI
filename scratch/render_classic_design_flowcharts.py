import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import shutil
import sys

# Charts render into ARTIFACT_DIR and are mirrored to MIRROR_DIRS. Both stay inside the workspace.
WORKSPACE_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
ARTIFACT_DIR = os.environ.get("FLOWCHART_OUTPUT_DIR", WORKSPACE_DIR)
MIRROR_DIRS = [os.path.join(WORKSPACE_DIR, "output", "antigravity_version")]

# Classic Ground-Truth Theme Colors (Matching image_1188e9.jpg & GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.jpg)
BG_COLOR = "#33363b"          # Slate-gray background
CARD_BG_NORMAL = "#fef08a"    # Warm cream / yellow
CARD_BORDER_NORMAL = "#ca8a04"# Golden yellow border
CARD_BG_CLIMAX = "#ffedd5"    # Warm peach / orange
CARD_BORDER_CLIMAX = "#ea580c"# Deep orange border
CARD_BG_SKIP = "#f3e8ff"      # Light purple for skippable side missions
CARD_BORDER_SKIP = "#a855f7"  # Purple border
TEXT_COLOR = "#1c1917"        # Dark charcoal / black text
SUBTEXT_COLOR = "#44403c"     # Muted charcoal subtext

def draw_mission(ax, x, y, w, h, title, subtitle="", is_climax=False, is_gate=False, is_skip=False, font_size=8.2):
    if is_climax:
        bg = CARD_BG_CLIMAX
        border = CARD_BORDER_CLIMAX
    elif is_skip:
        bg = CARD_BG_SKIP
        border = CARD_BORDER_SKIP
    else:
        bg = CARD_BG_NORMAL
        border = CARD_BORDER_NORMAL
        
    lw = 2.0 if (is_climax or is_gate) else 1.2
    
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.10",
        linewidth=lw,
        edgecolor=border,
        facecolor=bg,
        zorder=3
    )
    ax.add_patch(rect)
    
    ty = y + h/2 + 0.14 if subtitle else y + h/2
    c_title = "#581c87" if is_skip else TEXT_COLOR
    c_sub = "#6b21a8" if is_skip else SUBTEXT_COLOR
    
    ax.text(x + w/2, ty, title, ha="center", va="center", fontsize=font_size, fontweight="bold", color=c_title, zorder=4)
    if subtitle:
        ax.text(x + w/2, y + 0.22, subtitle, ha="center", va="center", fontsize=font_size-1.8, color=c_sub, zorder=4)

def draw_callout(ax, x, y, w, h, text, icon_type="text", font_size=7.0):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.0,
        edgecolor="#71717a",
        facecolor="#ffffff",
        zorder=3
    )
    ax.add_patch(rect)
    
    prefix = ""
    if icon_type == "phone":
        prefix = "[CALL] "
    elif icon_type == "text":
        prefix = "[MSG] "
    elif icon_type == "mailbox":
        prefix = "[MAILBOX] "
    elif icon_type == "cash":
        prefix = "[$] "
        
    ax.text(x + w/2, y + h/2, prefix + text, ha="center", va="center", fontsize=font_size, fontweight="bold" if icon_type in ["phone", "cash"] else "normal", color="#09090b", zorder=4)

def draw_heart(ax, x, y, w, h, text, skip_label="[ANY% SKIP]", font_size=7.0):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        edgecolor="#f43f5e",
        facecolor="#ffe4e6",
        zorder=3
    )
    ax.add_patch(rect)
    t = "♥ " + text
    if skip_label:
        t += "\n" + skip_label
    ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=font_size, fontweight="bold", color="#9f1239", zorder=4)

def draw_side(ax, x, y, w, h, text, font_size=7.0):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        edgecolor="#a855f7",
        facecolor="#f3e8ff",
        zorder=3
    )
    ax.add_patch(rect)
    t = text + "\n[OPTIONAL / SKIP]"
    ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=font_size, color="#581c87", zorder=4)

def draw_diamond(ax, cx, cy, rx, ry, text, font_size=6.8):
    pts = [[cx, cy + ry], [cx + rx, cy], [cx, cy - ry], [cx - rx, cy]]
    poly = patches.Polygon(pts, closed=True, linewidth=1.4, edgecolor="#cbd5e1", facecolor="#ffffff", zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=font_size, fontweight="bold", color="#0f172a", zorder=4)

def draw_speedrun_badge(ax, x, y, w, h, title, note, font_size=6.8):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.4,
        edgecolor="#10b981",
        facecolor="#064e3b",
        zorder=3
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.24, "⚡ " + title, ha="center", va="center", fontsize=font_size+0.6, fontweight="bold", color="#34d399", zorder=4)
    ax.text(x + w/2, y + h/2 - 0.12, note, ha="center", va="center", fontsize=font_size, color="#ecfdf5", zorder=4)

def draw_arrow(ax, p1, p2, color="#ffffff", lw=1.2, rad=0.0):
    conn = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    ax.annotate(
        "",
        xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle="->,head_width=0.28,head_length=0.38",
            color=color,
            lw=lw,
            shrinkA=3,
            shrinkB=3,
            connectionstyle=conn
        ),
        zorder=2
    )

def draw_stage_bridge(ax, x1, y1, x2, y2, gx, label):
    ax.plot([x1, gx, gx, x2], [y1, y1, y2, y2], color="#ffffff", lw=1.6, zorder=2)
    draw_arrow(ax, (gx, y2), (x2, y2), color="#ffffff", lw=1.6)
    
    badge = patches.FancyBboxPatch(
        (gx - 0.9, (y1 + y2)/2 - 0.35), 1.8, 0.7,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.0,
        edgecolor="#cbd5e1",
        facecolor="#26292e",
        zorder=4
    )
    ax.add_patch(badge)
    ax.text(gx, (y1 + y2)/2, label, ha="center", va="center", fontsize=6.5, fontweight="bold", color="#fde047", zorder=5)

def copy_to_all(filename):
    # A redirected render (FLOWCHART_OUTPUT_DIR) is a preview and must not touch the mirrors.
    if os.path.normcase(ARTIFACT_DIR) != os.path.normcase(WORKSPACE_DIR):
        print(f"Preview render of {filename}, mirrors skipped")
        return

    src = os.path.join(ARTIFACT_DIR, filename)
    for mirror_dir in MIRROR_DIRS:
        shutil.copyfile(src, os.path.join(mirror_dir, filename))

    print(f"Mirrored {filename}")

def setup_header(ax, title, subtitle, max_x, y_top):
    ax.text(max_x / 2, y_top, title, ha="center", va="center", fontsize=16, fontweight="bold", color="#ffffff")
    ax.text(max_x / 2, y_top - 0.5, subtitle, ha="center", va="center", fontsize=9.2, color="#fde047")

# =========================================================================
# 1. CHAPTER 1: EXACT MATCH TO BUILD 1.0.2.1 GROUND TRUTH (MISSIONS 1 - 21)
# =========================================================================
def render_chapter_1():
    fig, ax = plt.subplots(figsize=(26, 36), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 36)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 1: LEONIDA KEYS MISSION FLOW",
        "Ground Truth Directed Acyclic Graph (Build 1.0.2.1) | Missions 1 - 21 | 6 Verified Any% Auto-Flag Skips",
        26,
        y_top=35.2
    )
    
    mw, mh = 4.2, 1.05
    center_x = 11.2
    
    # 1. PROLOGUE
    draw_mission(ax, center_x, 33.4, mw, mh, "1. PROLOGUE [INT_PROLO]", "Lucia Prison Counselor Interview | Protagonist: Lucia")
    # 2. GONE FISHING
    draw_mission(ax, center_x, 31.8, mw, mh, "2. GONE FISHING [INT_CHASE]", "Jason & Donnie Boat Drop | Protagonist: Jason")
    draw_arrow(ax, (center_x + mw/2, 33.4), (center_x + mw/2, 32.85))
    
    # Donnie Text Mailbox
    draw_callout(ax, center_x + mw + 0.4, 31.85, 3.6, 0.75, "DONNIE TEXT\n($140 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (center_x + mw, 32.3), (center_x + mw + 0.4, 32.3))
    
    # Split bar below Gone Fishing (splits into parallel tracks)
    split_y = 30.9
    ax.plot([2.55, 14.3], [split_y, split_y], color="#ffffff", lw=1.5, zorder=2)
    draw_arrow(ax, (center_x + mw/2, 31.8), (center_x + mw/2, split_y))
    
    # -------------------------------------------------------------
    # TRACK 1: UNWANTED ATTENTION & PIPEWORK (Left Track: x = 0.6, w = 3.9)
    # -------------------------------------------------------------
    b1_x = 0.6
    mw1 = 3.9
    draw_arrow(ax, (b1_x + mw1/2, split_y), (b1_x + mw1/2, 29.85))
    draw_mission(ax, b1_x, 28.8, mw1, mh, "3. UNWANTED ATTENTION [COM_KBOS_COLAT]", "Cal & Jason Drive to Hamlet\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True, font_size=7.6)
    
    draw_callout(ax, b1_x, 27.65, mw1, 0.75, "CAL TEXT\n($200 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (b1_x + mw1/2, 28.8), (b1_x + mw1/2, 28.4))
    
    draw_callout(ax, b1_x, 26.55, mw1, 0.65, "BRIAN CALL", "phone")
    draw_arrow(ax, (b1_x + mw1/2, 27.65), (b1_x + mw1/2, 27.2))
    
    draw_mission(ax, b1_x, 25.1, mw1, mh, "4. PIPEWORK [COM_KBOS_NEIGHB]", "Marina Maintenance Jobs\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True, font_size=7.8)
    draw_arrow(ax, (b1_x + mw1/2, 26.55), (b1_x + mw1/2, 26.15))
    
    draw_callout(ax, b1_x, 23.95, mw1, 0.65, "BRIAN TEXT", "text")
    draw_arrow(ax, (b1_x + mw1/2, 25.1), (b1_x + mw1/2, 24.6))
    
    draw_callout(ax, b1_x, 22.75, mw1, 0.75, "CHUCK'S GUN SHOP TEXT\n(Cooldown / After Pipework)", "text", font_size=6.2)
    draw_arrow(ax, (b1_x + mw1/2, 23.95), (b1_x + mw1/2, 23.5))
    
    draw_speedrun_badge(ax, b1_x - 0.1, 20.6, mw1 + 0.2, 1.7, "DOWNTIME PARALLEL ROUTING", "Clear Unwanted Attention & Pipework\nduring Feng Shui's 24h wait!\nGrab $200 mailbox immediately.")
    draw_arrow(ax, (b1_x + mw1/2, 22.75), (b1_x + mw1/2, 22.3))
    
    # -------------------------------------------------------------
    # TRACK 2A: JUST A SCRATCH
    # Joey's text arrives after Gone Fishing without Gear Up (in-game report). The game files hold no
    # link between FT_AMUCO and FT_KMODSHP, and the text itself (c1cf23c9) credits Cal, not Brian.
    # -------------------------------------------------------------
    b2_x = 4.8
    mw2 = 3.5
    draw_arrow(ax, (b2_x + mw2/2, split_y), (b2_x + mw2/2, 29.75))
    draw_callout(ax, b2_x, 28.75, mw2, 1.0, "JOEY TEXT (Coastal Auto Care)\n\"Cal mentioned your car might need some work\"\nArrives after Gone Fishing - Gear Up NOT needed", "text", font_size=6.0)
    
    draw_heart(ax, b2_x, 25.1, mw2, mh, "6. JUST A SCRATCH [FT_KMODSHP]\n(Ganado Repair & Respray)", skip_label="[MANDATORY STORY GATE!]")
    draw_arrow(ax, (b2_x + mw2/2, 28.75), (b2_x + mw2/2, 26.15))
    
    scratch_line_x = b2_x + mw2/2   # x = 6.55
    
    # -------------------------------------------------------------
    # TRACK 2B: GEAR UP (parallel off Gone Fishing, does not lead to Just a Scratch)
    # -------------------------------------------------------------
    g_x = 8.65
    g_w = 3.25
    draw_arrow(ax, (g_x + g_w/2, split_y), (g_x + g_w/2, 29.85))
    draw_mission(ax, g_x, 28.8, g_w, mh, "5. GEAR UP [FT_AMUCO]", "Pick up Longarm at Ammu-Nation | Jason\nSeparate branch - does not unlock Scratch", font_size=7.6)
    
    draw_callout(ax, g_x, 27.65, g_w, 0.72, "POST-MISSION CALL\nFROM DONNIE", "phone", font_size=6.4)
    draw_arrow(ax, (g_x + g_w/2, 28.8), (g_x + g_w/2, 28.37))
    
    # -------------------------------------------------------------
    # SUB-BRANCH: ISLAND DREAMS (Keys Diving: x = 8.8, w = 3.0)
    # -------------------------------------------------------------
    isl_x = 8.8
    isl_w = 3.0
    draw_mission(ax, isl_x, 25.85, isl_w, mh, "ISLAND DREAMS [CSC_TRH_CHART]", "Shipwreck Treasure Dive\n[ANY% SKIP / OPTIONAL]", is_skip=True, font_size=7.4)
    draw_callout(ax, isl_x, 24.65, isl_w, 0.75, "KENTON CALL\n(Treasure Search)", "phone")
    draw_arrow(ax, (isl_x + isl_w/2, 25.85), (isl_x + isl_w/2, 25.4))
    
    # -------------------------------------------------------------
    # TRACK 3: LAB FEES -> HEY ARNOLD! -> FENG SHUI -> COMING HOME (x = 12.2, w = 4.2)
    # -------------------------------------------------------------
    b3_x = 12.2
    mw3 = 4.2
    draw_arrow(ax, (b3_x + mw3/2, split_y), (b3_x + mw3/2, 29.85))
    draw_mission(ax, b3_x, 28.8, mw3, mh, "7. LAB FEES [COM_KBOS_SHOP]", "Brian's Rent Collection\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True, font_size=7.8)
    
    draw_side(ax, b3_x + mw3 + 0.4, 28.85, 3.8, 0.85, "GRAB ANY DRUG, CASH\nOR DIAMOND ON MAP\n(Unlocks Brian's Drop Off)")
    draw_arrow(ax, (b3_x + mw3, 29.25), (b3_x + mw3 + 0.4, 29.25))
    
    draw_callout(ax, b3_x, 27.65, mw3, 0.65, "BRIAN'S CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, 28.8), (b3_x + mw3/2, 28.3))
    
    draw_mission(ax, b3_x, 26.2, mw3, mh, "8. HEY ARNOLD! [COM_KBOS_RADR]", "Track Down Cargo Broker\n[08:00–16:00] [ANY% SKIP]", is_skip=True, font_size=7.8)
    draw_arrow(ax, (b3_x + mw3/2, 27.65), (b3_x + mw3/2, 27.25))
    
    # Arrow to Island Dreams
    draw_arrow(ax, (b3_x, 26.4), (isl_x + isl_w, 26.4))
    
    # Right offshoots from Hey Arnold!
    draw_callout(ax, b3_x + mw3 + 0.4, 26.3, 2.4, 0.65, "CAL'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3, 26.6), (b3_x + mw3 + 0.4, 26.6))
    
    draw_callout(ax, b3_x + mw3 + 3.1, 26.3, 2.8, 0.65, "BRIAN'S TEXT\n($600 MAILBOX)", "mailbox")
    draw_arrow(ax, (b3_x + mw3 + 2.8, 26.6), (b3_x + mw3 + 3.1, 26.6))
    
    draw_side(ax, b3_x + mw3 + 6.2, 26.2, 2.8, 0.85, "DONNIE TEXT\nKingfishers Robbery")
    draw_arrow(ax, (b3_x + mw3 + 5.9, 26.6), (b3_x + mw3 + 6.2, 26.6))
    
    # FENG SHUI
    draw_mission(ax, b3_x, 23.6, mw3, mh, "9. FENG SHUI [COM_SFH_MVFN]", "Move Furniture for Brian | Protagonist: Jason", font_size=8.0)
    draw_arrow(ax, (b3_x + mw3/2, 26.2), (b3_x + mw3/2, 24.65))
    
    # 24H Cooldown Note
    draw_callout(ax, b3_x, 22.35, mw3, 0.75, "24 IN-GAME HOURS LATER\n→ LUCIA CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, 23.6), (b3_x + mw3/2, 23.1))
    
    # 4 Heart Activities
    h_y = 22.35
    draw_heart(ax, b3_x + 4.5, h_y, 2.0, 0.75, "GET HAIRCUT")
    draw_heart(ax, b3_x + 6.7, h_y, 2.0, 0.75, "BUY NECKLACE")
    draw_heart(ax, b3_x + 8.9, h_y, 2.0, 0.75, "BUY FLOWERS")
    draw_heart(ax, b3_x + 11.1, h_y, 2.0, 0.75, "BUY GROCERIES")
    draw_arrow(ax, (b3_x + mw3, 22.72), (b3_x + 4.5, 22.72), color="#f43f5e")
    
    # COMING HOME
    draw_mission(ax, b3_x, 20.8, mw3, mh, "10. COMING HOME [INT_PRISO]", "Lucia Released from Prison | Jason & Lucia", is_climax=True, font_size=8.2)
    draw_arrow(ax, (b3_x + mw3/2, 22.35), (b3_x + mw3/2, 21.85))
    
    # Side tasks post Coming Home
    draw_callout(ax, b3_x + mw3 + 0.4, 20.95, 2.6, 0.65, "ANDY CALL", "phone")
    draw_heart(ax, b3_x + mw3 + 3.2, 20.95, 2.6, 0.65, "LUCIA'S CLOTHES", skip_label="[HOT METER]")
    draw_arrow(ax, (b3_x + mw3, 21.3), (b3_x + mw3 + 0.4, 21.3))
    draw_arrow(ax, (b3_x + mw3 + 3.0, 21.3), (b3_x + mw3 + 3.2, 21.3))
    
    draw_callout(ax, b3_x - 3.4, 20.95, 3.0, 0.65, "UNLOCK DONNIE DROP OFF", "text", font_size=6.2)
    draw_arrow(ax, (b3_x, 21.3), (b3_x - 0.4, 21.3))
    
    # FIND DONNIE'S PACKAGE
    draw_mission(ax, b3_x, 19.3, mw3, mh, "11. FIND DONNIE'S PACKAGE [CTI_PIL_RD_SH]", "Clean Up After Donnie | Protagonist: Jason", font_size=8.0)
    draw_arrow(ax, (b3_x + mw3/2, 20.8), (b3_x + mw3/2, 20.35))
    
    # Decision Diamond 1: Did player finish Just a Scratch?
    dia1_y = 17.8
    draw_diamond(ax, b3_x + mw3/2, dia1_y, 2.2, 0.75, "Did the player finish:\nJUST A SCRATCH?")
    draw_arrow(ax, (b3_x + mw3/2, 19.3), (b3_x + mw3/2, dia1_y + 0.75))
    
    draw_callout(ax, b3_x - 3.7, dia1_y - 0.35, 3.2, 0.7, "NO → JOEY CALL\nReminds to clear Scratch", "phone")
    draw_arrow(ax, (b3_x + mw3/2 - 2.2, dia1_y), (b3_x - 0.5, dia1_y))
    draw_arrow(ax, (b3_x - 2.1, dia1_y + 0.35), (b2_x + mw2, 25.3), rad=0.25, color="#f43f5e")
    
    draw_callout(ax, b3_x, 16.35, mw3, 0.65, "YES → LUCIA'S CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, dia1_y - 0.75), (b3_x + mw3/2, 17.0))
    
    # BUCK ME
    draw_mission(ax, b3_x, 14.8, mw3, mh, "12. BUCK ME [INT_BANK]", "Setup Banking App & Deposit | Jason & Lucia", font_size=8.0)
    draw_arrow(ax, (b3_x + mw3/2, 16.35), (b3_x + mw3/2, 15.85))
    
    draw_callout(ax, b3_x - 3.9, 14.9, 3.4, 0.75, "DEPOSIT CASH\nINTO BUCK ME", "cash")
    draw_arrow(ax, (b3_x, 15.3), (b3_x - 0.5, 15.3))
    
    draw_callout(ax, b3_x + mw3 + 0.4, 14.9, 3.4, 0.75, "BRIAN'S TEXT\nSAVE FOR THE FUTURE", "text")
    draw_arrow(ax, (b3_x + mw3, 15.3), (b3_x + mw3 + 0.4, 15.3))
    
    # DOWN TO EARTH
    draw_mission(ax, b3_x, 13.2, mw3, mh, "13. DOWN TO EARTH [COM_KBOS_PLNDATE]", "Marina Smuggling Run | Jason & Lucia", font_size=8.0)
    draw_arrow(ax, (b3_x + mw3/2, 14.8), (b3_x + mw3/2, 14.25))
    
    draw_callout(ax, b3_x - 3.9, 13.3, 3.4, 0.75, "DONNIE TEXT\n($600 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (b3_x, 13.7), (b3_x - 0.5, 13.7))
    
    draw_side(ax, b3_x + mw3 + 0.4, 13.25, 3.4, 0.85, "CAL TEXT\nFind Lost Drugs x4")
    draw_arrow(ax, (b3_x + mw3, 13.7), (b3_x + mw3 + 0.4, 13.7))
    
    # CLEAR SKIES
    draw_callout(ax, b3_x, 11.95, mw3, 0.65, "DONNIE'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3/2, 13.2), (b3_x + mw3/2, 12.6))
    
    draw_mission(ax, b3_x, 10.4, mw3, mh, "14. CLEAR SKIES [INT_PLNSH]", "Deal with Southwind Bikers\n[07:00–23:00 Window] | Protagonist: Jason", font_size=7.8)
    draw_arrow(ax, (b3_x + mw3/2, 11.95), (b3_x + mw3/2, 11.45))
    
    # DAY RELEASE
    draw_callout(ax, b3_x, 9.15, mw3, 0.65, "LUCIA'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3/2, 10.4), (b3_x + mw3/2, 9.8))
    
    draw_mission(ax, b3_x, 7.6, mw3, mh, "15. DAY RELEASE [BIL_FUN]", "Rusty Anchor & Yacht Party\n[07:00–17:00 Window] | Jason & Lucia", font_size=7.8)
    draw_arrow(ax, (b3_x + mw3/2, 9.15), (b3_x + mw3/2, 8.65))
    
    draw_callout(ax, b3_x + mw3 + 0.4, 7.7, 3.4, 0.75, "BUCK ME TEXT\n(Interest Earned)", "cash")
    draw_arrow(ax, (b3_x + mw3, 8.1), (b3_x + mw3 + 0.4, 8.1))
    
    draw_heart(ax, b3_x + mw3 + 4.2, 7.7, 3.4, 0.85, "LUCIA 'PICK ME UP'\nCLOCK OUT", skip_label="[HOT METER]")
    draw_arrow(ax, (b3_x + mw3 + 3.8, 8.1), (b3_x + mw3 + 4.2, 8.1))
    
    # -------------------------------------------------------------
    # DECISION DIAMOND 2 & BOTTOM CLIMAX (Missions 16 - 21)
    # -------------------------------------------------------------
    dia2_x = 6.6
    dia2_y = 8.1
    draw_diamond(ax, dia2_x, dia2_y, 2.4, 0.85, "Is DAY RELEASE &\nJUST A SCRATCH\nboth completed?")
    
    draw_arrow(ax, (b3_x, 8.1), (dia2_x + 2.4, dia2_y))
    
    ax.plot([scratch_line_x, dia2_x], [25.1, dia2_y + 0.85], color="#ffffff", lw=1.4, zorder=2)
    draw_arrow(ax, (scratch_line_x, 25.1), (dia2_x, dia2_y + 0.85))
    
    draw_callout(ax, dia2_x - mw2/2, 6.5, mw2, 0.65, "YES → BRIAN'S CALL", "phone")
    draw_arrow(ax, (dia2_x, dia2_y - 0.85), (dia2_x, 7.15))
    
    # 16. SWAMPED
    draw_mission(ax, dia2_x - mw2/2, 5.0, mw2, mh, "16. SWAMPED [INT_AIR]", "Kingfishers Ambush | Donnie Killed!\nBrian Retires | Protagonist: Jason", font_size=8.0)
    draw_arrow(ax, (dia2_x, 6.5), (dia2_x, 6.05))
    
    # Split below Swamped: Left to Don Gone (Skip) / Down to Tourist Trap (Main Story)
    sw_exit_y = 5.0
    
    # -------------------------------------------------------------
    # OPTIONAL / ANY% SKIP BRANCH OFF DONNIE'S DEATH:
    # 17. DON GONE & 18. RECALIBRATION
    # -------------------------------------------------------------
    sk_x = 0.6
    sk_w = 4.1
    
    # Line to Don Gone
    ax.plot([dia2_x - mw2/2, sk_x + sk_w/2, sk_x + sk_w/2], [sw_exit_y + mh/2, sw_exit_y + mh/2, 4.45], color="#a855f7", lw=1.4, zorder=2)
    draw_arrow(ax, (sk_x + sk_w/2, 4.45), (sk_x + sk_w/2, 4.15), color="#a855f7")
    
    draw_mission(ax, sk_x, 3.1, sk_w, mh, "17. DON GONE [COM_KBOS_CLEAN]", "Clean Donnie's Trailer | Jason\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True, font_size=7.6)
    
    draw_mission(ax, sk_x, 1.4, sk_w, mh, "18. RECALIBRATION [HO_PAR_KEYCO]", "Cal Grief Fishing | Jason & Lucia\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True, font_size=7.6)
    draw_arrow(ax, (sk_x + sk_w/2, 3.1), (sk_x + sk_w/2, 2.45), color="#a855f7")
    
    # -------------------------------------------------------------
    # MAIN STORY MANDATORY GAUNTLET:
    # 19. TOURIST TRAP -> 20. HOME SWEET HOME -> 21. DISCHARGE TIME
    # -------------------------------------------------------------
    sp_x = 5.0
    sp_w = 4.8
    
    # Arrow from Swamped to Tourist Trap
    draw_arrow(ax, (dia2_x, sw_exit_y), (sp_x + sp_w/2, 4.25))
    
    draw_mission(ax, sp_x, 3.1, sp_w, mh, "19. TOURIST TRAP [BIL_PICK]", "Grassrivers Visitor Center Locker Pickup\n[10:00–17:00 / 17:00–10:00] | Jason Shot!", font_size=7.8)
    
    draw_mission(ax, sp_x, 1.4, sp_w, mh, "20. HOME SWEET HOME [BIL_HOUSE]", "Lucia Hamlet Stash Retrieval | Lucia Solo\nCartel Hitmen Ambush — House Torched!", font_size=7.8)
    draw_arrow(ax, (sp_x + sp_w/2, 3.1), (sp_x + sp_w/2, 2.45))
    
    # 21. DISCHARGE TIME (Chapter 1 Finale Climax)
    clim_x = 10.4
    clim_w = 5.2
    clim_h = 1.35
    draw_mission(ax, clim_x, 1.25, clim_w, clim_h, "21. DISCHARGE TIME [BIL_WHEEL]", "★ CHAPTER 1 FINALE CLIMAX ★\nVice City Hospital Shootout & Ambulance Escape!\nLucia Rescues Jason — Flee West to Kelly County!", is_climax=True, is_gate=True, font_size=8.0)
    
    draw_arrow(ax, (sp_x + sp_w, 1.9), (clim_x, 1.9), color="#ea580c", lw=1.8)
    
    # CHAPTER 2 TRANSITION BADGE
    trans_x = 16.2
    trans_w = 9.2
    trans_h = 2.1
    draw_speedrun_badge(
        ax, trans_x, 0.9, trans_w, trans_h,
        "CHAPTER 2 TRANSITION: WHAT'S IN THE BAG? [MTL_WAKE]",
        "Hard cut to Starlet Motel (Port Gellhorn)!\nfunc_10AA55 sets these completion flags when MTL_WAKE starts:\n• Lab Fees [0x2D7D2164] • Unwanted Attention [0x5AE70594]\n• Pipework [0xC8513199] • Hey Arnold! [0x21D03E4F]\n• Don Gone [0x10BE4C94] • Recalibration [0x420623AF]\n• Just a Scratch [FT_KMODSHP_SECOND 0xE48C934A] • Donnie's Drop x2\nIsland Dreams is optional but is NOT part of this sweep",
        font_size=6.6
    )
    draw_arrow(ax, (clim_x + clim_w, 1.9), (trans_x, 1.9), color="#f43f5e", lw=2.2)
    
    out_file1 = os.path.join(ARTIFACT_DIR, "flowchart_chapter_1.png")
    plt.savefig(out_file1, bbox_inches="tight", facecolor=BG_COLOR)
    
    out_file2 = os.path.join(ARTIFACT_DIR, "GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.png")
    plt.savefig(out_file2, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    
    copy_to_all("flowchart_chapter_1.png")
    copy_to_all("GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.png")
    print("Rendered Chapter 1 (flowchart_chapter_1.png & GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.png).")

# =========================================================================
# 2. CHAPTER 2: PORT GELLHORN & KELLY COUNTY (CLASSIC DESIGN)
# =========================================================================
def render_chapter_2():
    fig, ax = plt.subplots(figsize=(25, 13), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 25)
    ax.set_ylim(3.2, 16.0)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 2: PARADISE LOST",
        "Setting: Port Gellhorn & Kelly County | Missions 23 - 44 | Dual Character Switching Unlocked",
        25,
        y_top=15.4
    )
    
    w, h = 4.6, 1.0
    cols_x = [1.0, 7.2, 13.4, 19.4]
    gap = 1.32
    
    # STAGE 1: MOTEL ARRIVAL & MEDICAL (Missions 23 - 28)
    s1_cards = [
        ("23. What's in the Bag?", "Starlet Motel Arrival & Safehouse", False),
        ("24. Overnight Charges", "Paying Motel Upkeep & Debts", False),
        ("25. Take Care of Jason", "Lucia Solo Medical Supply Run", False),
        ("26. Just Moved In", "Setting Up Port Gellhorn Base", False),
        ("27. Girls' Trip", "Local Contact Introduction", False),
        ("28. Moses", "Vehicle Fencing & Chop Shop Access", False),
    ]
    
    # STAGE 2: DEBT HUSTLE & GUN RUNS (Missions 29 - 37)
    s2_cards = [
        ("29. New Look -> 30. How Do I Look?", "Disguise and Wardrobe Setup", False),
        ("31. Behind on Payments", "Collecting Local Debt", False),
        ("32. Ambulance Chaser", "Medical Fraud Operation", False),
        ("33. Painkiller Supplier", "Securing Prescription Drugs", False),
        ("34. Daily Driver -> 35. Pick Up A Gun", "Securing Getaway Wheels & Firearm", False),
        ("36. Slam Dunk -> 37. Breakfast Run", "Local Corner Job & Meetup", False),
    ]
    
    # STAGE 3: COFFEE BREAK & PAWN SHOP ROBBERIES (Missions 38 - 40)
    s3_cards = [
        ("38. Coffee Break", "★ DUAL CHARACTER SWITCHING UNLOCKED ★\nEnables Fast Character Warping!", True), # milestone
        ("39. Hit Avery Pawn", "Store Robbery System Active", False),
        ("40. Hit Kingpin Bowling", "Kelly County Robbery Operation\n[Optional / Any% Skip]", False),
    ]
    
    # STAGE 4: HIGHWAY ESCAPE & MOVE TO VICE CITY (Missions 41 - 44)
    s4_cards = [
        ("41. Impounded Vehicle", "Retrieving Confiscated Ride", False),
        ("42. Afternoon Delight", "Kelly County Smugglers Meet", False),
        ("43. Prepare for Vice City", "Liquidating Local Assets & Packing", False),
        ("44. Checking Out", "Port Gellhorn Climax & Motel Shootout", True), # climax
    ]
    
    stages = [
        ("STAGE 1: MOTEL ARRIVAL (M23-28)", s1_cards, cols_x[0]),
        ("STAGE 2: DEBT HUSTLE (M29-37)", s2_cards, cols_x[1]),
        ("STAGE 3: DUAL SWITCHING (M38-40)", s3_cards, cols_x[2]),
        ("STAGE 4: MOVE TO VC (M41-44)", s4_cards, cols_x[3]),
    ]
    
    for s_idx, (stitle, card_list, cx) in enumerate(stages):
        hdr_rect = patches.FancyBboxPatch(
            (cx, 14.0), w, 0.65,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2,
            edgecolor="#ca8a04",
            facecolor="#26292e",
            zorder=3
        )
        ax.add_patch(hdr_rect)
        ax.text(cx + w/2, 14.32, stitle, ha="center", va="center", fontsize=8.8, fontweight="bold", color="#fde047", zorder=4)
        
        y_start = 12.5
        for r_idx, (t, sub, is_spec) in enumerate(card_list):
            cy = y_start - r_idx * gap
            if "SWITCHING" in sub:
                draw_speedrun_badge(ax, cx, cy, w, h + 0.25, t, sub, font_size=7.5)
            elif "Optional" in sub:
                draw_side(ax, cx, cy, w, h, t, font_size=7.5)
            else:
                draw_mission(ax, cx, cy, w, h, t, sub, is_climax=is_spec, font_size=8.2)
                
            if r_idx < len(card_list) - 1:
                draw_arrow(ax, (cx + w/2, cy), (cx + w/2, cy - (gap - h)))
                
    # Gutter Bridges connecting sequential stages
    gx1 = (cols_x[0] + w + cols_x[1]) / 2
    draw_stage_bridge(ax, cols_x[0] + w/2, 12.5 - 5*gap, cols_x[1], 12.5 + h/2, gx1, "STAGE 2 ▲\nNEXT")
    
    gx2 = (cols_x[1] + w + cols_x[2]) / 2
    draw_stage_bridge(ax, cols_x[1] + w/2, 12.5 - 5*gap, cols_x[2], 12.5 + h/2, gx2, "STAGE 3 ▲\nNEXT")
    
    gx3 = (cols_x[2] + w + cols_x[3]) / 2
    draw_stage_bridge(ax, cols_x[2] + w/2, 12.5 - 2*gap, cols_x[3], 12.5 + h/2, gx3, "STAGE 4 ▲\nNEXT")
    
    # Transition to Chapter 3 Badge
    ch3_y = 12.5 - 4.5*gap
    draw_speedrun_badge(ax, cols_x[3], ch3_y, w, 1.25, "CHAPTER 3 TRANSITION", "Hard cut to Vice City!\nMove to First South Leonida Safehouse.")
    draw_arrow(ax, (cols_x[3] + w/2, 12.5 - 3*gap), (cols_x[3] + w/2, ch3_y + 1.25), color="#f43f5e", lw=2.0)
    
    out_file = os.path.join(ARTIFACT_DIR, "flowchart_chapter_2.png")
    plt.savefig(out_file, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_2.png")
    print("Rendered Chapter 2 (Classic Design).")

# =========================================================================
# 3. CHAPTER 3: VICE CITY SYNDICATE EXPANSION (CLASSIC DESIGN)
# =========================================================================
def render_chapter_3():
    fig, ax = plt.subplots(figsize=(26, 16), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 16)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 3: VICE CITY SYNDICATE EXPANSION",
        "Setting: Vice City Metro | Missions 45 - 70 | 3 Parallel Strands -> Sinfrontera Heist Preps",
        26,
        y_top=15.3
    )
    
    w, h = 3.6, 1.05
    
    # Column 1: Missions 45 - 50 (Linear Safehouse Spine)
    col1 = [
        ("45. Welcome to Vice City", "Arrival in the Metropolis"),
        ("46. Dealer's Choice", "Underground Casino Meeting"),
        ("47. Meet the Heders", "Local Smuggler Syndicate"),
        ("48. Dubious Provenance", "Handling Hot Merchandise"),
        ("49. Mami Knows Best", "Vice City Cartel Liaison"),
        ("50. Real Estate", "Safehouse Unlocked -> 3 Strands Open"),
    ]
    
    for r, (t, sub) in enumerate(col1):
        cy = 13.0 - r * 1.5
        draw_mission(ax, 0.7, cy, w, h, t, sub, is_climax=(r==5), font_size=8.0)
        if r < len(col1) - 1:
            draw_arrow(ax, (0.7 + w/2, cy), (0.7 + w/2, cy - 0.45))
            
    m50_pt = (0.7 + w, 13.0 - 5 * 1.5 + h/2)
    
    # ---------------- STRANDS (Columns 2 & 3) ----------------
    s1_x1, s1_x2 = 4.8, 8.8
    
    # STRAND 1: TYRONE (Street Muscle)
    draw_mission(ax, s1_x1, 13.0, w, h, "51. Tyrone", "Street Muscle Contract", font_size=8.0)
    draw_mission(ax, s1_x2, 13.0, w, h, "52. Here, Kitty Kitty", "Vice Strip Club Contract", font_size=8.0)
    draw_arrow(ax, (s1_x1 + w, 13.52), (s1_x2, 13.52))
    draw_arrow(ax, m50_pt, (s1_x1, 13.52), rad=-0.25)
    
    # STRAND 2: BOOBIE & DRE'QUAN (Syndicate)
    s2_y = 11.2
    draw_mission(ax, s1_x1, s2_y, w, h, "54. Top Billing", "High-End Nightclub Job", font_size=8.0)
    draw_mission(ax, s1_x2, s2_y, w, h, "55. Boobie Time", "Boobie Ike Alliance Formed", is_climax=True, font_size=8.0)
    draw_mission(ax, s1_x2, 9.5, w, h, "56. First Impressions", "Syndicate Introductions", font_size=8.0)
    draw_arrow(ax, (s1_x1 + w, s2_y + h/2), (s1_x2, s2_y + h/2))
    draw_arrow(ax, (s1_x2 + w/2, s2_y), (s1_x2 + w/2, 9.5 + h))
    draw_arrow(ax, m50_pt, (s1_x1, s2_y + h/2), rad=-0.15)
    
    # STRAND 3: RAUL & RANDY (Cartel & Cars)
    draw_mission(ax, s1_x1, 7.8, w, h, "53. Car Service", "Luxury Vehicle Interception", font_size=8.0)
    draw_mission(ax, s1_x1, 6.2, w, h, "57. Caught Slipping", "Surviving Competitor Ambush", font_size=8.0)
    draw_mission(ax, s1_x1, 4.6, w, h, "58. Crosstown Traffic", "Highway Pursuit & Escape", font_size=8.0)
    draw_mission(ax, s1_x1, 3.0, w, h, "59. Credit Check", "Background Probe on Raul", font_size=8.0)
    draw_mission(ax, s1_x2, 3.0, w, h, "60. Steal Zorrusso", "Exotic Supercar Booster", font_size=8.0)
    
    draw_arrow(ax, m50_pt, (s1_x1, 7.8 + h/2), rad=0.15)
    draw_arrow(ax, (s1_x1 + w/2, 7.8), (s1_x1 + w/2, 7.25))
    draw_arrow(ax, (s1_x1 + w/2, 6.2), (s1_x1 + w/2, 5.65))
    draw_arrow(ax, (s1_x1 + w/2, 4.6), (s1_x1 + w/2, 4.05))
    draw_arrow(ax, (s1_x1 + w, 3.0 + h/2), (s1_x2, 3.0 + h/2))
    
    # HEIST SCOPE OUT CONVERGENCE (Mission 61)
    heist_scope_y = 6.2
    draw_diamond(ax, s1_x2 + w/2, heist_scope_y + h/2, 2.2, 0.95, "61. SINFRONTERA BANK\nSCOPE OUT & HEIST BOARD\n(All 3 Strands Converge!)", font_size=7.2)
    
    draw_arrow(ax, (s1_x2 + w/2, 13.0), (s1_x2 + w/2, heist_scope_y + h/2 + 0.95), rad=-0.2)
    draw_arrow(ax, (s1_x2 + w/2, 9.5), (s1_x2 + w/2, heist_scope_y + h/2 + 0.95))
    draw_arrow(ax, (s1_x2 + w/2, 4.05), (s1_x2 + w/2, heist_scope_y + h/2 - 0.95))
    
    # ---------------- 3 CONCURRENT PREP TRACKS ----------------
    prep_box = patches.FancyBboxPatch(
        (13.2, 1.2), 12.2, 12.8,
        boxstyle="round,pad=0.03,rounding_size=0.15",
        linewidth=1.4,
        edgecolor="#ca8a04",
        facecolor="#26292e",
        zorder=1
    )
    ax.add_patch(prep_box)
    ax.text(19.3, 13.5, "SINFRONTERA BANK HEIST PREPARATION PIPELINE (3 CONCURRENT TRACKS)", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#fde047")
    
    pw = 3.6
    t1_x = 13.6   # Track 1: Safecracker
    t2_x = 17.5   # Track 2: Explosives
    t3_x = 21.4   # Track 3: Codes & Van
    
    # Track 1: Safecracker (62 -> 65 -> 68)
    draw_mission(ax, t1_x, 11.5, pw, 1.05, "62. Security Expert", "Retrieve Nicole Park", font_size=7.8)
    draw_mission(ax, t1_x, 9.7, pw, 1.05, "65. Safe Word", "Safe-Cracking Drill", font_size=7.8)
    draw_mission(ax, t1_x, 7.9, pw, 1.05, "68. Cooties", "Disinfecting Evidence", font_size=7.8)
    draw_arrow(ax, (t1_x + pw/2, 11.5), (t1_x + pw/2, 10.75))
    draw_arrow(ax, (t1_x + pw/2, 9.7), (t1_x + pw/2, 8.95))
    
    # Track 2: Explosives (63 -> 66 -> 69)
    draw_mission(ax, t2_x, 11.5, pw, 1.05, "63. Company Property", "Steal Vault Charges", font_size=7.8)
    draw_mission(ax, t2_x, 9.7, pw, 1.05, "66. Hidden Charges", "Rig 3 Regional Towers", font_size=7.8)
    draw_mission(ax, t2_x, 7.9, pw, 1.05, "69. Bricked Up", "Reinforce Extraction Route", font_size=7.8)
    draw_arrow(ax, (t2_x + pw/2, 11.5), (t2_x + pw/2, 10.75))
    draw_arrow(ax, (t2_x + pw/2, 9.7), (t2_x + pw/2, 8.95))
    
    # Track 3: Codes & Van (64 -> 67)
    draw_mission(ax, t3_x, 11.5, pw, 1.05, "64. The Missing Link", "Interrogate Monty for Codes", font_size=7.8)
    draw_mission(ax, t3_x, 9.7, pw, 1.05, "67. Ride or Die", "Armored Extraction Van", font_size=7.8)
    draw_arrow(ax, (t3_x + pw/2, 11.5), (t3_x + pw/2, 10.75))
    
    # Bus bar from Scope Out to Preps
    y_bus = 12.8
    gx_bus = 12.8
    m61_exit_y = heist_scope_y + h/2
    ax.plot([s1_x2 + w, gx_bus, gx_bus, t3_x + pw/2], [m61_exit_y, m61_exit_y, y_bus, y_bus], color="#ffffff", lw=1.8, zorder=2)
    draw_arrow(ax, (t1_x + pw/2, y_bus), (t1_x + pw/2, 12.55))
    draw_arrow(ax, (t2_x + pw/2, y_bus), (t2_x + pw/2, 12.55))
    draw_arrow(ax, (t3_x + pw/2, y_bus), (t3_x + pw/2, 12.55))
    
    # 70. THE CARTEL HEIST
    heist_fin_y = 4.2
    draw_mission(ax, 14.5, heist_fin_y, 9.6, 1.45, "70. THE CARTEL HEIST", "Sinfrontera National Bank Vault Raid ($10.5M Take)\n★ Keep $75,000 for Chapter 4 Abe Gate! ★", is_climax=True, font_size=9.2)
    
    draw_arrow(ax, (t1_x + pw/2, 7.9), (t1_x + pw/2, heist_fin_y + 1.45), color="#ea580c", lw=1.8)
    draw_arrow(ax, (t2_x + pw/2, 7.9), (t2_x + pw/2, heist_fin_y + 1.45), color="#ea580c", lw=1.8)
    ax.plot([t3_x + pw/2, t3_x + pw/2, 22.8], [9.7, 6.5, 6.5], color="#ea580c", lw=1.8, zorder=2)
    draw_arrow(ax, (22.8, 6.5), (22.8, heist_fin_y + 1.45), color="#ea580c", lw=1.8)
    
    # Transition to Chapter 4
    trans_x = 14.5 + 4.8 - w/2
    draw_speedrun_badge(ax, trans_x, 1.8, w, 1.15, "CHAPTER 4 TRANSITION", "Hard cut to Ocean Beach (VC)!\nMaintain $75k balance.")
    draw_arrow(ax, (trans_x + w/2, heist_fin_y), (trans_x + w/2, 1.8 + 1.15), color="#f43f5e", lw=2.0)
    
    out_file = os.path.join(ARTIFACT_DIR, "flowchart_chapter_3.png")
    plt.savefig(out_file, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_3.png")
    print("Rendered Chapter 3 (Classic Design).")

# =========================================================================
# 4. CHAPTER 4: VICE CITY METRO & AIRPORT HEIST (CLASSIC DESIGN)
# =========================================================================
def render_chapter_4():
    fig, ax = plt.subplots(figsize=(25, 14), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 25)
    ax.set_ylim(2.5, 16.0)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 4: VICE CITY METRO & AIRPORT HEIST",
        "Setting: Ocean Beach, Downtown VC & VCIA Airport | Missions 71 - 95 | Sequential Timeline",
        25,
        y_top=15.4
    )
    
    w, h = 4.6, 0.95
    cols_x = [1.0, 7.2, 13.4, 19.4]
    gap = 1.25
    
    # STAGE 1: BEACHHEAD & ABE'S $75k GATE (Missions 71 - 75)
    s1_cards = [
        ("71. Ocean Beach", "Establish Y Hotel Safehouse", False),
        ("72. Another Life", "High-End Lifestyle Setup", False),
        ("73. Company Cars", "Fleet Acquisition for Syndicate", False),
        ("74. Lawyer Up", "Abe Gonzalez Legal Consultation", False),
        ("75. Party Hard", "Nightclub Meet & $75k Wire to Abe", True), # Gate
    ]
    
    # STAGE 2: SYNDICATE & CORPORATE OPERATIONS (Missions 76 - 82)
    s2_cards = [
        ("76. Heavy Lifting", "Smuggling Port Cargo Containers", False),
        ("77. Photo/Shoot", "Paparazzi Blackmail & Intel", False),
        ("78. Making Gainz", "Fitness Syndicate Interception", False),
        ("79. Watch It", "Executive Surveillance Job", False),
        ("80. Cash Injections", "Laundering Syndicate Profits", False),
        ("81. Amateur Hour", "Rival Gang Ambush Defense", False),
        ("82. Dirty Work", "Sanitizing High-Profile Murder", False),
    ]
    
    # STAGE 3: DRE'QUAN CLIMAX & AIRPORT RECON (Missions 83 - 91)
    s3_cards = [
        ("83. Too Much Baggage", "Airport Courier Reconnaissance", False),
        ("84. Adventures in Babysitting", "Protecting Celebrity VIP", False),
        ("85. Fresh Evidence", "Stealing Prosecutor Files", False),
        ("86. Power Play", "Corporate Extortion Meeting", False),
        ("87. Child's Play", "Kidnapping High-Value Target", False),
        ("88. Headliners", "Dre'Quan Climax Performance", False),
        ("89. Close Surveillance -> 91. Team Building", "VCIA Perimeter Intel & Crew Rally", False),
    ]
    
    # STAGE 4: VCIA HEIST & POINT OF NO RETURN (Missions 92 - 95)
    s4_cards = [
        ("92. Fully Catered", "Infiltrating Catering Trucks", False),
        ("93. VCIA TAKEDOWN", "Major Airport Cargo Heist", True),
        ("94. Sunset", "★ POINT OF NO RETURN ★ Locks Saves!", True),
        ("95. Starting From Zero", "Chapter 4 Climax / Evacuation Sequence", True),
    ]
    
    stages = [
        ("STAGE 1: BEACHHEAD & $75k (M71-75)", s1_cards, cols_x[0]),
        ("STAGE 2: SYNDICATE OPS (M76-82)", s2_cards, cols_x[1]),
        ("STAGE 3: DRE & RECON (M83-91)", s3_cards, cols_x[2]),
        ("STAGE 4: VCIA HEIST (M92-95)", s4_cards, cols_x[3]),
    ]
    
    for s_idx, (stitle, card_list, cx) in enumerate(stages):
        hdr_rect = patches.FancyBboxPatch(
            (cx, 14.0), w, 0.65,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2,
            edgecolor="#ca8a04",
            facecolor="#26292e",
            zorder=3
        )
        ax.add_patch(hdr_rect)
        ax.text(cx + w/2, 14.32, stitle, ha="center", va="center", fontsize=8.8, fontweight="bold", color="#fde047", zorder=4)
        
        y_start = 12.5
        for r_idx, (t, sub, is_spec) in enumerate(card_list):
            cy = y_start - r_idx * gap
            if "POINT OF NO RETURN" in sub:
                draw_speedrun_badge(ax, cx, cy, w, h + 0.1, t, sub, font_size=7.5)
            elif "$75k Wire" in sub:
                draw_speedrun_badge(ax, cx, cy, w, h + 0.1, t, sub, font_size=7.5)
            else:
                draw_mission(ax, cx, cy, w, h, t, sub, is_climax=is_spec, font_size=8.2)
                
            if r_idx < len(card_list) - 1:
                draw_arrow(ax, (cx + w/2, cy), (cx + w/2, cy - (gap - h)))
                
    # Gutter Bridges
    gx1 = (cols_x[0] + w + cols_x[1]) / 2
    draw_stage_bridge(ax, cols_x[0] + w/2, 12.5 - 4*gap, cols_x[1], 12.5 + h/2, gx1, "STAGE 2 ▲\nNEXT")
    
    gx2 = (cols_x[1] + w + cols_x[2]) / 2
    draw_stage_bridge(ax, cols_x[1] + w/2, 12.5 - 6*gap, cols_x[2], 12.5 + h/2, gx2, "STAGE 3 ▲\nNEXT")
    
    gx3 = (cols_x[2] + w + cols_x[3]) / 2
    draw_stage_bridge(ax, cols_x[2] + w/2, 12.5 - 6*gap, cols_x[3], 12.5 + h/2, gx3, "STAGE 4 ▲\nNEXT")
    
    # Transition to Chapter 5 Badge
    ch5_y = 12.5 - 5.0*gap
    draw_speedrun_badge(ax, cols_x[3], ch5_y, w, 1.25, "CHAPTER 5 TRANSITION", "Hard cut to Endgame Standoff!\nImmediate point of no return.")
    draw_arrow(ax, (cols_x[3] + w/2, 12.5 - 3*gap), (cols_x[3] + w/2, ch5_y + 1.25), color="#f43f5e", lw=2.0)
    
    out_file = os.path.join(ARTIFACT_DIR, "flowchart_chapter_4.png")
    plt.savefig(out_file, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_4.png")
    print("Rendered Chapter 4 (Classic Design).")

# =========================================================================
# 5. CHAPTER 5: THE FINALE & ENDINGS (CLASSIC DESIGN)
# =========================================================================
def render_chapter_5():
    fig, ax = plt.subplots(figsize=(20, 14), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 20)
    ax.set_ylim(1.8, 16.0)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 5: TOP OF THE WORLD, MA!",
        "The Climax, Tactical Assaults, Betrayal, and Branching Endings | Missions 96 - 102",
        20,
        y_top=15.4
    )
    
    w, h = 4.8, 1.1
    cx = 7.6
    
    spine = [
        ("96. Top of the World", "Leonida Keys Sanctuary Infiltration", False),
        ("97. Bait and Switch", "Luring Federal Strike Teams", False),
        ("98. Scorched Earth", "Asset Destruction & Evacuation", False),
        ("99. Two Hundred Percent", "Joint Assault on Mendez Compound", True),
    ]
    
    y_start = 13.5
    gap = 1.45
    for idx, (t, sub, is_spec) in enumerate(spine):
        cy = y_start - idx * gap
        draw_mission(ax, cx, cy, w, h, t, sub, is_climax=is_spec, font_size=8.5)
        if idx < len(spine) - 1:
            draw_arrow(ax, (cx + w/2, cy), (cx + w/2, cy - (gap - h)))
            
    # Standoff Decision Diamond (Mission 100)
    dia_y = y_start - 4 * gap + 0.2
    draw_diamond(ax, cx + w/2, dia_y, 2.8, 0.95, "100. FINAL DECISION STANDOFF\nAgent Mendez Ambush at Key West Motel\nChoose Jason & Lucia's Fate", font_size=7.5)
    draw_arrow(ax, (cx + w/2, y_start - 3 * gap), (cx + w/2, dia_y + 0.95))
    
    # 3 Branching Endings
    end_w = 5.2
    end_y = dia_y - 2.5
    
    # Ending A (Left)
    draw_mission(ax, 0.8, end_y, end_w, 1.55, "ENDING A: BONNIE & CLYDE", "Outlaws Together | Reject Federal Deal\nFight through Coast Guard to Airstrip.\n★ AWARDS $2,000,000 Payout (Not required!) ★", is_climax=True, font_size=8.0)
    draw_arrow(ax, (cx + w/2 - 2.8, dia_y), (0.8 + end_w/2, end_y + 1.55), color="#ffffff", rad=-0.2)
    
    # Ending B (Center - Speedrun Route)
    draw_speedrun_badge(ax, 7.4, end_y, end_w, 1.55, "ENDING B: THE DEAL (ANY% ROUTE)", "Accept Mendez Deal & Enter Immunity\nSkips Multi-Stage Offshore Boat Chase!\n★ SAVES 8-12 MINUTES IN ANY% SPEEDRUN ★", font_size=7.5)
    draw_arrow(ax, (cx + w/2, dia_y - 0.95), (7.4 + end_w/2, end_y + 1.55), color="#10b981", lw=2.2)
    
    # Ending C (Right)
    draw_side(ax, 14.0, end_y, end_w, 1.55, "ENDING C: THE SACRIFICE\nOne Partner Escapes, One Stays Behind\nSolo Evacuation Flight to South America\nUnique Melancholy Radio Broadcasts", font_size=7.5)
    draw_arrow(ax, (cx + w/2 + 2.8, dia_y), (14.0 + end_w/2, end_y + 1.55), color="#ffffff", rad=0.2)
    
    # Final Epilogue & Credits
    epi_y = end_y - 2.2
    draw_mission(ax, 5.8, epi_y, 8.4, 1.35, "101. Final Evacuation  →  102. Epilogue & Credits", "Story Campaign Concluded | Free Roam Restored\nFull Leonida Map Unlocked for Post-Game Activities", is_climax=True, font_size=9.2)
    
    draw_arrow(ax, (0.8 + end_w/2, end_y), (5.8 + 1.2, epi_y + 1.35))
    draw_arrow(ax, (7.4 + end_w/2, end_y), (5.8 + 4.2, epi_y + 1.35), color="#10b981")
    draw_arrow(ax, (14.0 + end_w/2, end_y), (5.8 + 7.2, epi_y + 1.35))
    
    out_file = os.path.join(ARTIFACT_DIR, "flowchart_chapter_5.png")
    plt.savefig(out_file, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_5.png")
    print("Rendered Chapter 5 (Classic Design).")

# =========================================================================
# 6. COMBINED FLOWCHART: ALL 5 CHAPTERS UNIFIED (CLASSIC DESIGN)
# =========================================================================
def render_all_combined():
    fig, ax = plt.subplots(figsize=(32, 22), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 22)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — ANY% SPEEDRUN ROUTING MASTER MAP",
        "All 5 Story Chapters | Optimal Route, Parallel Strands, Heist Prep Concurrency, Cash Gates & Ending Routing",
        32,
        y_top=21.2
    )
    
    col_w = 5.8
    cols_x = [0.8, 7.0, 13.2, 19.4, 25.6]
    
    chapter_headers = [
        ("CHAPTER 1: LEONIDA KEYS", "Missions 1-21 | Parallel Branches & Any% Skips", "#22d3ee"),
        ("CHAPTER 2: PORT GELLHORN", "Missions 23-44 | Character Switch Rush", "#f43f5e"),
        ("CHAPTER 3: VICE CITY HEIST", "Missions 45-70 | 3 Strands -> Sinfrontera Heist", "#fbbf24"),
        ("CHAPTER 4: AIRPORT TAKEDOWN", "Missions 71-95 | $75k Gate & VCIA Cargo Heist", "#a855f7"),
        ("CHAPTER 5: THE FINALE", "Missions 96-102 | Fast 'The Deal' Ending B", "#ef4444"),
    ]
    
    for idx, (title, sub, color) in enumerate(chapter_headers):
        cx = cols_x[idx]
        panel = patches.Rectangle((cx, 0.6), col_w, 19.5, linewidth=1.8, edgecolor=color, facecolor="#26292e", zorder=1)
        ax.add_patch(panel)
        ax.text(cx + col_w/2, 19.5, title, ha="center", va="center", fontsize=11, fontweight="bold", color=color, zorder=2)
        ax.text(cx + col_w/2, 19.0, sub, ha="center", va="center", fontsize=7.8, color="#cbd5e1", zorder=2)
        
    mw = 5.2
    
    # ---------------- CHAPTER 1 COLUMN (UPDATED TO 21 MISSIONS) ----------------
    c1_x = cols_x[0] + 0.3
    c1_items = [
        ("1. Prologue -> 2. Gone Fishing", "Grab $140 Mailbox | Splits into Parallel Branches", "normal", 17.5),
        ("BRANCH A: Unwanted Attention -> Pipework", "ANY% SKIP: Auto-flagged by MTL_WAKE", "badge", 15.9),
        ("BRANCH B: Just a Scratch  |  Gear Up (separate)", "Scratch gates Swamped | Gear Up NOT needed for it", "heart", 14.3),
        ("BRANCH C: Lab Fees -> Hey Arnold! -> Feng Shui", "Grab $600 Mailbox | 24h Cooldown Trigger", "normal", 12.7),
        ("Coming Home -> Find Donnie's Package", "Lucia Released -> Diamond 1 Gate Check", "normal", 11.2),
        ("Buck Me -> Down to Earth -> Clear Skies", "Banking App Setup -> 07:00-23:00 Window", "normal", 9.7),
        ("Day Release -> DIAMOND 2 GATE", "07:00-17:00 Window | Evaluates Just a Scratch", "normal", 8.2),
        ("16. Swamped [INT_AIR]", "Donnie Killed in Ambush | Kingfishers Meet", "normal", 6.7),
        ("SKIP: Don Gone -> Recalibration", "ANY% SKIP: Trailer & Fishing auto-flagged", "badge", 5.2),
        ("19. Tourist Trap -> 20. Home Sweet Home", "10:00-17:00 | Grassrivers Ambush & Torched House", "normal", 3.6),
        ("21. DISCHARGE TIME [BIL_WHEEL]", "★ CH. 1 HOSPITAL CLIMAX ★ -> Starlet Motel", "climax", 1.8),
    ]
    for t, s, ct, cy in c1_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c1_x, cy, mw, 1.15, t, s, font_size=7.0)
        elif ct == "heart":
            draw_heart(ax, c1_x, cy, mw, 1.15, t + "\n" + s, skip_label="[CRITICAL GATE]")
        else:
            draw_mission(ax, c1_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"), font_size=7.8)
            
    draw_arrow(ax, (c1_x + mw, 1.8 + 0.55), (cols_x[1] + 0.3, 17.5), color="#f43f5e", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 2 COLUMN ----------------
    c2_x = cols_x[1] + 0.3
    c2_items = [
        ("23. What's in the Bag? -> 26. Just Moved In", "Starlet Motel Setup & Lucia Solo Recovery", "normal", 17.2),
        ("28. Moses (Vehicle Fencing)", "Register required getaway car with Moses", "normal", 15.6),
        ("29-37. Port Gellhorn Hustle", "Beeline through debt tasks (Ambulance/Daily Driver)", "normal", 14.1),
        ("38. COFFEE BREAK", "★ DUAL CHARACTER SWITCHING UNLOCKED ★\nEnables Fast Character Warping!", "badge", 12.3),
        ("39. Hit Avery Pawn", "Store Robbery System Active", "normal", 10.6),
        ("SKIP: Hit Kingpin Bowling", "Bypass secondary non-essential robberies", "badge", 9.1),
        ("40-42. Kelly County Operations", "Impounded Vehicle recovery & Afternoon Delight", "normal", 7.6),
        ("43. Prepare for Vice City", "Packing & Asset Liquidation", "normal", 6.0),
        ("44. CHECKING OUT", "Port Gellhorn Climax -> Move to VC Safehouse", "climax", 4.0),
        ("SPEEDRUN NOTE: CASH ROUTING", "Maintain $10,000+ for early VC equipment", "badge", 2.2),
    ]
    for t, s, ct, cy in c2_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c2_x, cy, mw, 1.35 if "SWITCHING" in t else 1.15, t, s, font_size=7.2)
        else:
            draw_mission(ax, c2_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c2_x + mw, 4.5), (cols_x[2] + 0.3, 17.5), color="#fbbf24", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 3 COLUMN ----------------
    c3_x = cols_x[2] + 0.3
    c3_items = [
        ("45. Welcome to VC -> 50. Real Estate", "Arrival & First VC Safehouse Unlocked", "normal", 17.2),
        ("STRAND 1: Tyrone Muscle (51-52)", "Here, Kitty Kitty & Street Muscle", "normal", 15.6),
        ("STRAND 2: Boobie & Dre (54-56)", "Nightclub / Port Everglades / Introductions", "normal", 14.2),
        ("STRAND 3: Raul & Randy (53,57-60)", "Car Service -> Zorrusso Supercar Boost", "normal", 12.8),
        ("3-WAY STRAND JUGGLING", "Cooldowns trigger alternating calls:\nZigzag Tyrone ↔ Boobie ↔ Raul (Zero idle time).", "badge", 10.9),
        ("61. Sinfrontera Bank Scope Out", "All 3 Strands Converge Into Heist Board!", "normal", 9.2),
        ("3 PARALLEL PREP TRACKS (62-69)", "Track 1: Safecracker (62,65,68)\nTrack 2: Explosives (63,66,69) | Track 3: Codes (64,67)", "badge", 7.3),
        ("PREP SKIP: Hidden Charges", "BLOW 2 CELL TOWERS ONLY (Saves ~3m in Any%)", "badge", 5.5),
        ("70. THE CARTEL HEIST", "Sinfrontera Vault Score ($10.5M Take)", "climax", 3.9),
        ("BANK $75,000 FOR ABE IMMEDIATELY", "CRITICAL: Do not spend the heist cut!\n$75k needed for Chapter 4 gate.", "badge", 2.0),
    ]
    for t, s, ct, cy in c3_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c3_x, cy, mw, 1.5 if "TRACKS" in t else (1.3 if "BANK" in t else 1.15), t, s, font_size=7.2)
        else:
            draw_mission(ax, c3_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c3_x + mw, 4.5), (cols_x[3] + 0.3, 17.5), color="#a855f7", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 4 COLUMN ----------------
    c4_x = cols_x[3] + 0.3
    c4_items = [
        ("71. Ocean Beach (Y Hotel Safehouse)", "Establish South Beach Headquarters", "normal", 17.2),
        ("74. Lawyer Up -> 75. PARTY HARD", "INSTANT WIRE: Send $75,000 via BuckMe\nNo grinding needed if Ch. 3 cut was kept!", "badge", 15.4),
        ("76-82. Syndicate & Corporate Ops", "Heavy Lifting, Making Gainz, Dirty Work", "normal", 13.6),
        ("83. Too Much Baggage -> 84. Babysitting", "Airport Recon -> Celebrity VIP Escort", "normal", 12.1),
        ("85-88. Dre'Quan Storyline", "Fresh Evidence -> Power Play -> Headliners", "normal", 10.6),
        ("89-91. VCIA Perimeter Recon", "Close Surveillance -> Delivery -> Team Building", "normal", 9.1),
        ("92. Fully Catered", "Infiltrate Airport via Catering Van Vector", "normal", 7.6),
        ("93. VCIA TAKEDOWN", "Major Airport Cargo Heist", "climax", 6.0),
        ("94. SUNSET (POINT OF NO RETURN)", "Locks open-world roaming and saves!", "badge", 4.3),
        ("95. Starting From Zero", "Chapter 4 Climax / Evacuation Sequence", "climax", 2.6),
    ]
    for t, s, ct, cy in c4_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c4_x, cy, mw, 1.3 if "INSTANT" in t else 1.15, t, s, font_size=7.2)
        else:
            draw_mission(ax, c4_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c4_x + mw, 3.1), (cols_x[4] + 0.3, 17.5), color="#ef4444", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 5 COLUMN ----------------
    c5_x = cols_x[4] + 0.3
    c5_items = [
        ("96. Top of the World -> 98. Scorched Earth", "Federal Raid Defense & Cartel Standoff", "normal", 17.2),
        ("99. Two Hundred Percent", "Joint Assault on Mendez Compound", "normal", 15.6),
        ("100. FINAL DECISION STANDOFF", "Choose Loyalty (Ending A) or Immunity (Ending B)", "badge", 13.8),
        ("★ ENDING B: THE DEAL (ANY% ROUTE) ★", "Accept Mendez Deal -> Skip Boat Chase!\nSAVES 8-12 MINUTES OVER ENDING A!", "badge", 11.4),
        ("Ending A: Bonnie & Clyde", "Loyalty Choice: Fight through Coast Guard.\nAwards $2,000,000 Payout (NOT a requirement!)", "normal", 9.2),
        ("Ending C: The Sacrifice", "Partner Betrayal -> Solo Escort", "normal", 7.6),
        ("101. Final Evacuation", "Airstrip extraction or border run", "climax", 6.0),
        ("102. Epilogue & Credits", "Credits Roll -> Final IGT Split Time!", "badge", 4.2),
        ("TARGET ANY% TIME: ~10h 45m", "Assuming optimal dialogue skips and routing", "badge", 2.2),
    ]
    for t, s, ct, cy in c5_items:
        if "ANY% ROUTE" in t:
            draw_speedrun_badge(ax, c5_x, cy, mw, 1.7, t, s, font_size=7.2)
        elif ct == "badge":
            draw_speedrun_badge(ax, c5_x, cy, mw, 1.3 if "TARGET" in t else 1.15, t, s, font_size=7.2)
        else:
            draw_mission(ax, c5_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    out_file = os.path.join(ARTIFACT_DIR, "flowchart_all_chapters_combined.png")
    plt.savefig(out_file, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_all_chapters_combined.png")
    print("Rendered All Chapters Combined (Classic Design).")

RENDERERS = {
    "ch1": render_chapter_1,
    "ch2": render_chapter_2,
    "ch3": render_chapter_3,
    "ch4": render_chapter_4,
    "ch5": render_chapter_5,
    "combined": render_all_combined,
}


def main(chart_names):
    unknown = [name for name in chart_names if name not in RENDERERS]
    if unknown:
        print(f"Unknown chart(s): {', '.join(unknown)}. Choose from: {', '.join(RENDERERS)}")
        return 2

    for name in chart_names or list(RENDERERS):
        RENDERERS[name]()

    print("Render complete")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
