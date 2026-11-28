import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

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

def setup_header(ax, title, subtitle, max_x, y_top):
    ax.text(max_x / 2, y_top, title, ha="center", va="center", fontsize=16, fontweight="bold", color="#ffffff")
    ax.text(max_x / 2, y_top - 0.5, subtitle, ha="center", va="center", fontsize=9.2, color="#fde047")

def test_chapter_1():
    fig, ax = plt.subplots(figsize=(26, 36), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 36)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 1: LEONIDA KEYS MISSION FLOW",
        "Ground Truth Directed Acyclic Graph (Build 1.0.2.1) | Missions 1 - 21 | All 7 Verified Any% Auto-Flag Skips",
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
    
    # Split bar below Gone Fishing (splits into 3 parallel tracks)
    split_y = 30.9
    ax.plot([2.5, 6.5, 13.3], [split_y, split_y, split_y], color="#ffffff", lw=1.5, zorder=2)
    draw_arrow(ax, (center_x + mw/2, 31.8), (center_x + mw/2, split_y))
    
    # -------------------------------------------------------------
    # TRACK 1: UNWANTED ATTENTION & PIPEWORK (Left Track: x = 0.6, w = 3.8)
    # -------------------------------------------------------------
    b1_x = 0.6
    mw1 = 3.8
    draw_arrow(ax, (2.5, split_y), (b1_x + mw1/2, 29.85))
    draw_mission(ax, b1_x, 28.8, mw1, mh, "3. UNWANTED ATTENTION [COM_KBOS_COLAT]", "Cal & Jason Drive to Hamlet\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True)
    
    draw_callout(ax, b1_x, 27.65, mw1, 0.75, "CAL TEXT\n($200 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (b1_x + mw1/2, 28.8), (b1_x + mw1/2, 28.4))
    
    draw_callout(ax, b1_x, 26.55, mw1, 0.65, "BRIAN CALL", "phone")
    draw_arrow(ax, (b1_x + mw1/2, 27.65), (b1_x + mw1/2, 27.2))
    
    draw_mission(ax, b1_x, 25.1, mw1, mh, "4. PIPEWORK [COM_KBOS_NEIGHB]", "Marina Maintenance Jobs\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True)
    draw_arrow(ax, (b1_x + mw1/2, 26.55), (b1_x + mw1/2, 26.15))
    
    draw_callout(ax, b1_x, 23.95, mw1, 0.65, "BRIAN TEXT", "text")
    draw_arrow(ax, (b1_x + mw1/2, 25.1), (b1_x + mw1/2, 24.6))
    
    draw_callout(ax, b1_x, 22.75, mw1, 0.75, "CHUCK'S GUN SHOP TEXT\n(Cooldown / After Pipework)", "text", font_size=6.2)
    draw_arrow(ax, (b1_x + mw1/2, 23.95), (b1_x + mw1/2, 23.5))
    
    draw_speedrun_badge(ax, b1_x - 0.1, 20.6, mw1 + 0.2, 1.7, "DOWNTIME PARALLEL ROUTING", "Clear Unwanted Attention & Pipework\nduring Feng Shui's 24h wait!\nGrab $200 mailbox immediately.")
    draw_arrow(ax, (b1_x + mw1/2, 22.75), (b1_x + mw1/2, 22.3))
    
    # -------------------------------------------------------------
    # TRACK 2: GEAR UP & JUST A SCRATCH (Middle-Left Track: x = 4.8, w = 3.6)
    # -------------------------------------------------------------
    b2_x = 4.8
    mw2 = 3.6
    draw_arrow(ax, (6.5, split_y), (b2_x + mw2/2, 29.85))
    draw_mission(ax, b2_x, 28.8, mw2, mh, "5. GEAR UP [FT_AMUCO]", "Pick up Longarm for Brian\nProtagonist: Jason")
    
    draw_callout(ax, b2_x, 27.65, mw2, 0.75, "POST-MISSION FORCED CALL\nFROM DONNIE", "phone")
    draw_arrow(ax, (b2_x + mw2/2, 28.8), (b2_x + mw2/2, 28.4))
    
    draw_callout(ax, b2_x, 26.55, mw2, 0.65, "JOEY TEXT", "text")
    draw_arrow(ax, (b2_x + mw2/2, 27.65), (b2_x + mw2/2, 27.2))
    
    draw_heart(ax, b2_x, 25.1, mw2, mh, "6. JUST A SCRATCH [FT_KMODSHP]\n(Ganado Repair & Respray)", skip_label="[MANDATORY STORY GATE!]")
    draw_arrow(ax, (b2_x + mw2/2, 26.55), (b2_x + mw2/2, 26.15))
    
    scratch_line_x = b2_x + mw2/2   # x = 6.6
    
    # -------------------------------------------------------------
    # SUB-BRANCH: ISLAND DREAMS (Keys Diving: x = 8.8, w = 3.0)
    # -------------------------------------------------------------
    isl_x = 8.8
    isl_w = 3.0
    draw_mission(ax, isl_x, 26.2, isl_w, mh, "ISLAND DREAMS [CSC_TRH_CHART]", "Shipwreck Treasure Dive\n[ANY% SKIP / OPTIONAL]", is_skip=True)
    draw_callout(ax, isl_x, 25.0, isl_w, 0.75, "KENTON CALL\n(Treasure Search)", "phone")
    draw_arrow(ax, (isl_x + isl_w/2, 26.2), (isl_x + isl_w/2, 25.75))
    
    # -------------------------------------------------------------
    # TRACK 3: LAB FEES -> HEY ARNOLD! -> FENG SHUI -> COMING HOME (x = 12.2, w = 4.2)
    # -------------------------------------------------------------
    b3_x = 12.2
    mw3 = 4.2
    draw_arrow(ax, (13.3, split_y), (b3_x + mw3/2, 29.85))
    draw_mission(ax, b3_x, 28.8, mw3, mh, "7. LAB FEES [COM_KBOS_SHOP]", "Brian's Rent Collection\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True)
    
    draw_side(ax, b3_x + mw3 + 0.4, 28.85, 3.8, 0.85, "GRAB ANY DRUG, CASH\nOR DIAMOND ON MAP\n(Unlocks Brian's Drop Off)")
    draw_arrow(ax, (b3_x + mw3, 29.25), (b3_x + mw3 + 0.4, 29.25))
    
    draw_callout(ax, b3_x, 27.65, mw3, 0.65, "BRIAN'S CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, 28.8), (b3_x + mw3/2, 28.3))
    
    draw_mission(ax, b3_x, 26.2, mw3, mh, "8. HEY ARNOLD! [COM_KBOS_RADR]", "Track Down Cargo Broker\n[08:00–16:00] [ANY% SKIP]", is_skip=True)
    draw_arrow(ax, (b3_x + mw3/2, 27.65), (b3_x + mw3/2, 27.25))
    
    # Arrow to Island Dreams
    draw_arrow(ax, (b3_x, 26.7), (isl_x + isl_w, 26.7))
    
    # Right offshoots from Hey Arnold!
    draw_callout(ax, b3_x + mw3 + 0.4, 26.3, 2.4, 0.65, "CAL'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3, 26.6), (b3_x + mw3 + 0.4, 26.6))
    
    draw_callout(ax, b3_x + mw3 + 3.1, 26.3, 2.8, 0.65, "BRIAN'S TEXT\n($600 MAILBOX)", "mailbox")
    draw_arrow(ax, (b3_x + mw3 + 2.8, 26.6), (b3_x + mw3 + 3.1, 26.6))
    
    draw_side(ax, b3_x + mw3 + 6.2, 26.2, 2.8, 0.85, "DONNIE TEXT\nKingfishers Robbery")
    draw_arrow(ax, (b3_x + mw3 + 5.9, 26.6), (b3_x + mw3 + 6.2, 26.6))
    
    # FENG SHUI
    draw_mission(ax, b3_x, 23.6, mw3, mh, "9. FENG SHUI [COM_SFH_MVFN]", "Move Furniture for Brian | Protagonist: Jason")
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
    draw_mission(ax, b3_x, 20.8, mw3, mh, "10. COMING HOME [INT_PRISO]", "Lucia Released from Prison | Jason & Lucia", is_climax=True)
    draw_arrow(ax, (b3_x + mw3/2, 22.35), (b3_x + mw3/2, 21.85))
    
    # Side tasks post Coming Home
    draw_callout(ax, b3_x + mw3 + 0.4, 20.95, 2.6, 0.65, "ANDY CALL", "phone")
    draw_heart(ax, b3_x + mw3 + 3.2, 20.95, 2.6, 0.65, "LUCIA'S CLOTHES", skip_label="[HOT METER]")
    draw_arrow(ax, (b3_x + mw3, 21.3), (b3_x + mw3 + 0.4, 21.3))
    draw_arrow(ax, (b3_x + mw3 + 3.0, 21.3), (b3_x + mw3 + 3.2, 21.3))
    
    draw_callout(ax, b3_x - 3.4, 20.95, 3.0, 0.65, "UNLOCK DONNIE DROP OFF", "text", font_size=6.2)
    draw_arrow(ax, (b3_x, 21.3), (b3_x - 0.4, 21.3))
    
    # FIND DONNIE'S PACKAGE
    draw_mission(ax, b3_x, 19.3, mw3, mh, "11. FIND DONNIE'S PACKAGE [CTI_PIL_RD_SH]", "Clean Up After Donnie | Protagonist: Jason")
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
    draw_mission(ax, b3_x, 14.8, mw3, mh, "12. BUCK ME [INT_BANK]", "Setup Banking App & Deposit | Jason & Lucia")
    draw_arrow(ax, (b3_x + mw3/2, 16.35), (b3_x + mw3/2, 15.85))
    
    draw_callout(ax, b3_x - 3.9, 14.9, 3.4, 0.75, "DEPOSIT CASH\nINTO BUCK ME", "cash")
    draw_arrow(ax, (b3_x, 15.3), (b3_x - 0.5, 15.3))
    
    draw_callout(ax, b3_x + mw3 + 0.4, 14.9, 3.4, 0.75, "BRIAN'S TEXT\nSAVE FOR THE FUTURE", "text")
    draw_arrow(ax, (b3_x + mw3, 15.3), (b3_x + mw3 + 0.4, 15.3))
    
    # DOWN TO EARTH
    draw_mission(ax, b3_x, 13.2, mw3, mh, "13. DOWN TO EARTH [COM_KBOS_PLNDATE]", "Marina Smuggling Run | Jason & Lucia")
    draw_arrow(ax, (b3_x + mw3/2, 14.8), (b3_x + mw3/2, 14.25))
    
    draw_callout(ax, b3_x - 3.9, 13.3, 3.4, 0.75, "DONNIE TEXT\n($600 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (b3_x, 13.7), (b3_x - 0.5, 13.7))
    
    draw_side(ax, b3_x + mw3 + 0.4, 13.25, 3.4, 0.85, "CAL TEXT\nFind Lost Drugs x4")
    draw_arrow(ax, (b3_x + mw3, 13.7), (b3_x + mw3 + 0.4, 13.7))
    
    # CLEAR SKIES
    draw_callout(ax, b3_x, 11.95, mw3, 0.65, "DONNIE'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3/2, 13.2), (b3_x + mw3/2, 12.6))
    
    draw_mission(ax, b3_x, 10.4, mw3, mh, "14. CLEAR SKIES [INT_PLNSH]", "Deal with Southwind Bikers\n[07:00–23:00 Window] | Protagonist: Jason")
    draw_arrow(ax, (b3_x + mw3/2, 11.95), (b3_x + mw3/2, 11.45))
    
    # DAY RELEASE
    draw_callout(ax, b3_x, 9.15, mw3, 0.65, "LUCIA'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3/2, 10.4), (b3_x + mw3/2, 9.8))
    
    draw_mission(ax, b3_x, 7.6, mw3, mh, "15. DAY RELEASE [BIL_FUN]", "Rusty Anchor & Yacht Party\n[07:00–17:00 Window] | Jason & Lucia")
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
    draw_mission(ax, dia2_x - mw2/2, 5.0, mw2, mh, "16. SWAMPED [INT_AIR]", "Kingfishers Ambush | Donnie Killed!\nBrian Retires | Protagonist: Jason")
    draw_arrow(ax, (dia2_x, 6.5), (dia2_x, 6.05))
    
    # Split below Swamped: Left to Don Gone (Skip) / Down to Tourist Trap (Main Story)
    sw_exit_y = 5.0
    
    # -------------------------------------------------------------
    # OPTIONAL / ANY% SKIP BRANCH OFF DONNIE'S DEATH:
    # 17. DON GONE & 18. RECALIBRATION
    # -------------------------------------------------------------
    sk_x = 0.6
    sk_w = 4.0
    
    # Line to Don Gone
    ax.plot([dia2_x - mw2/2, sk_x + sk_w/2, sk_x + sk_w/2], [sw_exit_y + mh/2, sw_exit_y + mh/2, 4.45], color="#a855f7", lw=1.4, zorder=2)
    draw_arrow(ax, (sk_x + sk_w/2, 4.45), (sk_x + sk_w/2, 4.15), color="#a855f7")
    
    draw_mission(ax, sk_x, 3.1, sk_w, mh, "17. DON GONE [COM_KBOS_CLEAN]", "Clean Donnie's Trailer | Jason\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True)
    
    draw_mission(ax, sk_x, 1.4, sk_w, mh, "18. RECALIBRATION [HO_PAR_KEYCO]", "Cal Grief Fishing | Jason & Lucia\n[ANY% SKIP / AUTO-FLAGGED]", is_skip=True)
    draw_arrow(ax, (sk_x + sk_w/2, 3.1), (sk_x + sk_w/2, 2.45), color="#a855f7")
    
    # -------------------------------------------------------------
    # MAIN STORY MANDATORY GAUNTLET:
    # 19. TOURIST TRAP -> 20. HOME SWEET HOME -> 21. DISCHARGE TIME
    # -------------------------------------------------------------
    sp_x = 5.0
    sp_w = 4.8
    
    # Arrow from Swamped to Tourist Trap
    draw_arrow(ax, (dia2_x, sw_exit_y), (sp_x + sp_w/2, 4.25))
    
    draw_mission(ax, sp_x, 3.1, sp_w, mh, "19. TOURIST TRAP [BIL_PICK]", "Grassrivers Visitor Center Locker Pickup\n[10:00–17:00 / 17:00–10:00] | Jason Shot!")
    
    draw_mission(ax, sp_x, 1.4, sp_w, mh, "20. HOME SWEET HOME [BIL_HOUSE]", "Lucia Hamlet Stash Retrieval | Lucia Solo\nCartel Hitmen Ambush — House Torched!")
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
        "Hard cut to Starlet Motel (Port Gellhorn)!\nfunc_10AA55 sweeps & auto-flags all 7 uncompleted side missions:\n• Lab Fees [0x2D7D2164] • Unwanted Attention [0x5AE70594]\n• Pipework [0xC8513199] • Hey Arnold! [0x21D03E4F]\n• Don Gone [0x10BE4C94] • Recalibration [0x420623AF] • Island Dreams",
        font_size=6.6
    )
    draw_arrow(ax, (clim_x + clim_w, 1.9), (trans_x, 1.9), color="#f43f5e", lw=2.2)
    
    out_file = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c\test_ch1.png"
    plt.savefig(out_file, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print("Rendered test Chapter 1.")

if __name__ == "__main__":
    test_chapter_1()
