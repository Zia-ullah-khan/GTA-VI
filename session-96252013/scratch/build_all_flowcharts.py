import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import shutil

WORKSPACE_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
DOWNLOADS_DIR = r"C:\Users\<user>\Downloads"
ARTIFACT_DIR = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c"

BG_COLOR = "#0c1017"
TEXT_COLOR = "#f8fafc"
SUBTEXT_COLOR = "#94a3b8"

STYLES = {
    "normal": {
        "bg": "#161d2b",
        "border": "#00d4ff",
        "title": "#38bdf8",
        "badge_bg": "#083344",
        "badge_fg": "#38bdf8"
    },
    "milestone": {
        "bg": "#231528",
        "border": "#ff007f",
        "title": "#fb7185",
        "badge_bg": "#4c0519",
        "badge_fg": "#ff007f"
    },
    "heist": {
        "bg": "#281e10",
        "border": "#f59e0b",
        "title": "#fde047",
        "badge_bg": "#451a03",
        "badge_fg": "#fbbf24"
    },
    "point_of_no_return": {
        "bg": "#300e18",
        "border": "#ef4444",
        "title": "#fca5a5",
        "badge_bg": "#7f1d1d",
        "badge_fg": "#fca5a5"
    },
    "ending": {
        "bg": "#0c2820",
        "border": "#10b981",
        "title": "#34d399",
        "badge_bg": "#064e3b",
        "badge_fg": "#34d399"
    }
}

def draw_card(ax, x, y, w, h, title, subtitle="", badge="", card_type="normal", fontsize=9):
    st = STYLES.get(card_type, STYLES["normal"])
    
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.15",
        linewidth=1.6,
        edgecolor=st["border"],
        facecolor=st["bg"],
        zorder=3
    )
    ax.add_patch(rect)
    
    if badge:
        ax.text(
            x + w/2, y + h - 0.16,
            badge.upper(),
            ha="center", va="center",
            fontsize=fontsize - 2.5,
            fontweight="bold",
            color=st["badge_fg"],
            bbox=dict(boxstyle="round,pad=0.22", facecolor=st["badge_bg"], edgecolor=st["border"], lw=0.8),
            zorder=4
        )
        title_y = y + h/2 + 0.04
        sub_y = y + 0.22
    else:
        title_y = y + h/2 + 0.14 if subtitle else y + h/2
        sub_y = y + h/2 - 0.20

    ax.text(
        x + w/2, title_y,
        title,
        ha="center", va="center",
        fontsize=fontsize,
        fontweight="bold",
        color=st["title"],
        zorder=4
    )
    
    if subtitle:
        ax.text(
            x + w/2, sub_y,
            subtitle,
            ha="center", va="center",
            fontsize=fontsize - 2.2,
            color=SUBTEXT_COLOR,
            zorder=4
        )

def draw_diamond(ax, cx, cy, rx, ry, text, fontsize=7.2):
    pts = [[cx, cy + ry], [cx + rx, cy], [cx, cy - ry], [cx - rx, cy]]
    poly = patches.Polygon(pts, closed=True, linewidth=1.5, edgecolor="#f59e0b", facecolor="#281e10", zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize, fontweight="bold", color="#fde047", zorder=4)

def draw_arrow(ax, p1, p2, color="#38bdf8", lw=1.6, rad=0.0):
    conn = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
    ax.annotate(
        "",
        xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle="->,head_width=0.32,head_length=0.42",
            color=color,
            lw=lw,
            shrinkA=4,
            shrinkB=4,
            connectionstyle=conn
        ),
        zorder=2
    )

def draw_stage_bridge(ax, x_start, y_start, x_end, y_end, gutter_x, badge_text="", color="#f59e0b", lw=1.8):
    y_turn = y_start - 0.7
    ax.plot(
        [x_start, x_start, gutter_x, gutter_x, x_end],
        [y_start, y_turn, y_turn, y_end, y_end],
        color=color, lw=lw, zorder=2
    )
    ax.annotate(
        "",
        xy=(x_end, y_end), xytext=(x_end - 0.35, y_end),
        arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.42", color=color, lw=lw),
        zorder=2
    )
    if badge_text:
        badge_y = (y_turn + y_end) / 2
        ax.text(
            gutter_x, badge_y,
            badge_text,
            ha="center", va="center",
            fontsize=7.2, fontweight="bold",
            color="#fde047",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#281e10", edgecolor=color, lw=1.0),
            zorder=4
        )

def draw_column_bridge(ax, x_start, y_start, x_end, y_end, gutter_x, badge_text="", color="#f43f5e", lw=1.8):
    ax.plot([x_start, gutter_x, gutter_x, x_end], [y_start, y_start, y_end, y_end], color=color, lw=lw, zorder=3)
    ax.annotate(
        "",
        xy=(x_end, y_end), xytext=(x_end - 0.35, y_end),
        arrowprops=dict(arrowstyle="->,head_width=0.32,head_length=0.42", color=color, lw=lw),
        zorder=3
    )
    if badge_text:
        badge_y = (y_start + y_end) / 2
        ax.text(
            gutter_x, badge_y, badge_text,
            ha="center", va="center", fontsize=6.8, fontweight="bold",
            color="#fde047",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="#18140f", edgecolor=color, lw=1.0),
            zorder=4
        )

def setup_header(ax, title, subtitle, w_total, y_top=11.5):
    ax.text(
        w_total / 2, y_top,
        title,
        ha="center", va="center",
        fontsize=16,
        fontweight="bold",
        color="#ffffff",
        zorder=5
    )
    ax.text(
        w_total / 2, y_top - 0.45,
        subtitle,
        ha="center", va="center",
        fontsize=10.5,
        color="#38bdf8",
        zorder=5
    )

def copy_to_all(src_filename):
    art_path = os.path.join(ARTIFACT_DIR, src_filename)
    ws_path = os.path.join(WORKSPACE_DIR, src_filename)
    dl_path = os.path.join(DOWNLOADS_DIR, src_filename)
    if os.path.exists(art_path):
        shutil.copyfile(art_path, ws_path)
        shutil.copyfile(art_path, dl_path)
        print(f"Synced {src_filename} to workspace and Downloads.")

# =========================================================================
# 1. CHAPTER 1: TRUE PARALLEL BRANCHING (MATCHING image_1188e9.jpg GROUND TRUTH)
# =========================================================================
def render_chapter_1():
    fig, ax = plt.subplots(figsize=(24, 18), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 18)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 1: JUST LIKE PARADISE",
        "Setting: Leonida Keys (Key Lento & Southwind Marina) | Missions 1 - 18 (Ends at Doin' Gone) | 3 Parallel Branches & Gates",
        24,
        y_top=17.4
    )
    
    w, h = 3.6, 1.05
    center_x = 10.2
    
    # Top: 1. Prologue -> 2. Gone Fishing
    draw_card(ax, center_x, 15.6, w, h, "1. Prologue", "Lucia Prison Counselor Interview", "Intro", "normal")
    draw_card(ax, center_x, 14.1, w, h, "2. Gone Fishing", "Jason & Donnie Boat Drop ($140 Mailbox)", "", "normal")
    draw_arrow(ax, (center_x + w/2, 15.6), (center_x + w/2, 15.15))
    
    # 3-Track Horizontal Split Bar
    split_y = 13.3
    ax.plot([2.5, 6.2, 12.0], [split_y, split_y, split_y], color="#38bdf8", lw=1.8, zorder=2)
    draw_arrow(ax, (center_x + w/2, 14.1), (center_x + w/2, split_y))
    
    # -------------------------------------------------------------
    # BRANCH 1: UNWANTED ATTENTION & PIPEWORK (Left Track: x = 0.8)
    # -------------------------------------------------------------
    b1_x = 0.8
    draw_arrow(ax, (2.5, split_y), (b1_x + w/2, 12.35))
    draw_card(ax, b1_x, 11.3, w, h, "6. Unwanted Attention", "Cal Trip to Hamlet ($200 Mailbox)", "Branch 1", "normal")
    draw_card(ax, b1_x, 9.7, w, h, "7. Pipework", "Marina Maintenance Jobs", "Branch 1", "normal")
    draw_arrow(ax, (b1_x + w/2, 11.3), (b1_x + w/2, 10.75))
    
    # Downtime tip box
    p1 = patches.FancyBboxPatch((b1_x, 7.8), w, 1.4, boxstyle="round,pad=0.03,rounding_size=0.15", linewidth=1.2, edgecolor="#10b981", facecolor="#064e3b", zorder=3)
    ax.add_patch(p1)
    ax.text(b1_x + w/2, 8.8, "⚡ PARALLEL DOWNTIME ROUTE", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#34d399", zorder=4)
    ax.text(b1_x + w/2, 8.2, "Clear Missions 6 & 7 during Feng Shui's\n24-hour waiting window for optimal routing.", ha="center", va="center", fontsize=6.8, color="#ecfdf5", zorder=4)
    draw_arrow(ax, (b1_x + w/2, 9.7), (b1_x + w/2, 9.2))
    
    # -------------------------------------------------------------
    # BRANCH 2: GEAR UP & JUST A SCRATCH (Middle Track: x = 4.8)
    # -------------------------------------------------------------
    b2_x = 4.8
    draw_arrow(ax, (6.2, split_y), (b2_x + w/2, 12.35))
    draw_card(ax, b2_x, 11.3, w, h, "3. Gear Up", "Pick up Longarm for Brian", "Branch 2", "normal")
    draw_card(ax, b2_x, 9.7, w, h, "4. Just a Scratch", "Ganado Repair & Respray", "MANDATORY GATE", "milestone")
    draw_arrow(ax, (b2_x + w/2, 11.3), (b2_x + w/2, 10.75))
    
    # Scratch line runs down to Diamond 2
    scratch_line_x = b2_x + w/2
    
    # -------------------------------------------------------------
    # SUB-BRANCH: ISLAND DREAMS (Keys Diving: x = 8.6)
    # -------------------------------------------------------------
    isl_x = 8.6
    draw_card(ax, isl_x - 3.4, 8.2, 3.0, h, "9. Island Dreams", "Keys Diving (Kenton Treasure)", "Side Activity", "normal", fontsize=8.2)
    
    # -------------------------------------------------------------
    # BRANCH 3: LAB FEES -> HEY ARNOLD! -> FENG SHUI -> COMING HOME (x = 10.2)
    # -------------------------------------------------------------
    b3_x = 10.2
    draw_arrow(ax, (12.0, split_y), (b3_x + w/2, 12.35))
    draw_card(ax, b3_x, 11.3, w, h, "5. Lab Fees", "Brian's Rent Collection", "Branch 3", "normal")
    draw_card(ax, b3_x, 9.7, w, h, "8. Hey Arnold!", "Track Down Cargo Broker", "Branch 3", "normal")
    draw_arrow(ax, (b3_x + w/2, 11.3), (b3_x + w/2, 10.75))
    
    # Offshoot arrow to Island Dreams
    draw_arrow(ax, (b3_x, 10.2), (isl_x - 0.4, 8.7), rad=0.15)
    
    # FENG SHUI
    draw_card(ax, b3_x, 8.1, w, h, "10. Feng Shui", "Move Furniture for Brian (24h Wait)", "", "normal")
    draw_arrow(ax, (b3_x + w/2, 9.7), (b3_x + w/2, 9.15))
    
    # COMING HOME
    draw_card(ax, b3_x, 6.5, w, h, "11. Coming Home", "Lucia Released from Prison", "LUCIA REUNION", "milestone")
    draw_arrow(ax, (b3_x + w/2, 8.1), (b3_x + w/2, 7.55))
    
    # FIND DONNIE'S PACKAGE (RESTORED GROUND TRUTH!)
    draw_card(ax, b3_x, 4.9, w, h, "12. Find Donnie's Package", "Retrieve Hamlet Drop Package", "", "normal")
    draw_arrow(ax, (b3_x + w/2, 6.5), (b3_x + w/2, 5.95))
    
    # DECISION DIAMOND 1: Did player finish Just a Scratch?
    dia1_y = 3.6
    draw_diamond(ax, b3_x + w/2, dia1_y, 2.2, 0.65, "Did player finish\nJUST A SCRATCH?")
    draw_arrow(ax, (b3_x + w/2, 4.9), (b3_x + w/2, dia1_y + 0.65))
    
    # Diamond 1 No Branch (Joey Reminder Call -> Points back to Just a Scratch)
    p_joey = patches.FancyBboxPatch((b3_x - 4.2, dia1_y - 0.45), 3.4, 0.9, boxstyle="round,pad=0.03,rounding_size=0.15", linewidth=1.0, edgecolor="#f43f5e", facecolor="#300e18", zorder=3)
    ax.add_patch(p_joey)
    ax.text(b3_x - 2.5, dia1_y, "NO: Joey Reminder Call\n(Redirects to Just a Scratch)", ha="center", va="center", fontsize=7.2, color="#fca5a5", zorder=4)
    draw_arrow(ax, (b3_x + w/2 - 2.2, dia1_y), (b3_x - 0.8, dia1_y), color="#f43f5e")
    draw_arrow(ax, (b3_x - 2.5, dia1_y + 0.45), (b2_x + w, 10.0), color="#f43f5e", rad=0.25)
    
    # -------------------------------------------------------------
    # MAIN COLUMN LOWER HALF: BUCK ME -> DOWN TO EARTH -> CLEAR SKIES -> DAY RELEASE
    # -------------------------------------------------------------
    draw_card(ax, b3_x, 2.0, w, h, "13. Buck Me", "Setup Banking App & Deposit", "Banking Setup", "milestone")
    draw_arrow(ax, (b3_x + w/2, dia1_y - 0.65), (b3_x + w/2, 3.05))
    
    col_r_x = 15.6
    draw_card(ax, col_r_x, 11.3, w, h, "14. Down to Earth", "Marina Smuggling Run ($600 Mailbox)", "", "normal")
    draw_arrow(ax, (b3_x + w, 2.5), (col_r_x + w/2, 12.35), rad=-0.25, color="#38bdf8")
    
    draw_card(ax, col_r_x, 9.7, w, h, "15. Clear Skies", "Deal with Southwind Bikers", "", "normal")
    draw_arrow(ax, (col_r_x + w/2, 11.3), (col_r_x + w/2, 10.75))
    
    draw_card(ax, col_r_x, 8.1, w, h, "16. Day Release", "Rusty Anchor Bar Night Out", "", "normal")
    draw_arrow(ax, (col_r_x + w/2, 9.7), (col_r_x + w/2, 9.15))
    
    # DECISION DIAMOND 2: Are Day Release and Just a Scratch both done?
    dia2_x = col_r_x + w/2
    dia2_y = 6.4
    draw_diamond(ax, dia2_x, dia2_y, 2.4, 0.75, "Are DAY RELEASE &\nJUST A SCRATCH done?")
    draw_arrow(ax, (col_r_x + w/2, 8.1), (dia2_x, dia2_y + 0.75))
    
    # Line from Just a Scratch into Diamond 2
    ax.plot([scratch_line_x, scratch_line_x, dia2_x - 2.4], [9.7, 7.3, dia2_y], color="#ff007f", lw=1.6, zorder=2)
    draw_arrow(ax, (dia2_x - 2.8, dia2_y), (dia2_x - 2.4, dia2_y), color="#ff007f")
    
    # YES -> 17. Swamped -> 18. Doin' Gone
    draw_card(ax, col_r_x, 4.6, w, h, "17. Swamped", "Kingfishers Smugglers Meet", "", "normal")
    draw_arrow(ax, (dia2_x, dia2_y - 0.75), (dia2_x, 5.65))
    
    # 18. DOIN' GONE (GROUND TRUTH CLIMAX!)
    draw_card(ax, col_r_x, 3.0, w, h, "18. Doin' Gone", "Clear Donnie's Trailer", "CHAPTER 1 CLIMAX", "point_of_no_return")
    draw_arrow(ax, (dia2_x, 4.6), (dia2_x, 4.05))
    
    # Transition to Chapter 2
    draw_card(ax, col_r_x, 1.2, w, 1.1, "→ TRANSITION TO CHAPTER 2", "Destination: Port Gellhorn & Starlet Motel", "Next Chapter", "point_of_no_return")
    draw_arrow(ax, (dia2_x, 3.0), (dia2_x, 2.3), color="#ef4444", lw=2.0)
    
    out_path = os.path.join(ARTIFACT_DIR, "flowchart_chapter_1.png")
    plt.savefig(out_path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_1.png")

# =========================================================================
# 2. CHAPTER 2: STRICT SEQUENTIAL PHASES (NO MISLEADING WRAP-AROUND ARROWS)
# =========================================================================
def render_chapter_2():
    fig, ax = plt.subplots(figsize=(24, 15), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 15)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 2: PARADISE LOST",
        "Setting: Port Gellhorn & Kelly County | Missions 23 - 44 | Dual Character Switching Unlocked",
        24,
        y_top=14.4
    )
    
    # Disclaimer Banner
    banner = patches.FancyBboxPatch((2.0, 13.1), 20.0, 0.7, boxstyle="round,pad=0.03,rounding_size=0.15", linewidth=1.2, edgecolor="#38bdf8", facecolor="#083344", zorder=3)
    ax.add_patch(banner)
    ax.text(12.0, 13.45, "⚠️ STRICT CHRONOLOGICAL SEQUENCE — Stages must be completed 1 → 2 → 3 → 4 in order (Not parallel branches)", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#38bdf8", zorder=4)
    
    w, h = 4.4, 0.95
    cols_x = [1.0, 6.8, 12.6, 18.4]
    gap = 1.3
    
    # STAGE 1: MOTEL ARRIVAL & MEDICAL (Missions 23 - 28)
    s1_cards = [
        ("23. What's in the Bag?", "Starlet Motel Arrival", "", "normal"),
        ("24. Overnight Charges", "Paying Motel Upkeep", "", "normal"),
        ("25. Take Care of Jason", "Lucia Solo Medical Run", "Lucia Solo", "milestone"),
        ("26. Just Moved In", "Setting Up Port Gellhorn Base", "", "normal"),
        ("27. Girls' Trip", "Local Contact Introduction", "", "normal"),
        ("28. Moses", "Vehicle Fencing & Garage Reg", "Fencing Unlocked", "milestone"),
    ]
    
    # STAGE 2: DEBT HUSTLE & GUN RUNS (Missions 29 - 37)
    s2_cards = [
        ("29. New Look -> 30. How Do I Look?", "Disguise and Wardrobe Setup", "", "normal"),
        ("31. Behind on Payments", "Collecting Local Debt", "", "normal"),
        ("32. Ambulance Chaser", "Medical Fraud Operation", "", "normal"),
        ("33. Painkiller Supplier", "Securing Prescription Drugs", "", "normal"),
        ("34. Daily Driver -> 35. Pick Up A Gun", "Securing Wheels & Firearm", "", "normal"),
        ("36. Slam Dunk -> 37. Breakfast Run", "Local Corner Job & Meetup", "", "normal"),
    ]
    
    # STAGE 3: COFFEE BREAK & PAWN SHOP ROBBERIES (Missions 38 - 40)
    s3_cards = [
        ("38. Coffee Break", "★ DUAL CHARACTER SWITCHING UNLOCKED ★", "MAJOR MILESTONE", "milestone"),
        ("39. Hit Avery Pawn", "Store Robbery Mechanic Active", "Robbery Active", "normal"),
        ("40. Hit Kingpin Bowling", "Kelly County Robbery Operation", "Optional / Skip", "normal"),
    ]
    
    # STAGE 4: HIGHWAY ESCAPE & MOVE TO VICE CITY (Missions 41 - 44)
    s4_cards = [
        ("41. Impounded Vehicle", "Retrieving Confiscated Ride", "", "normal"),
        ("42. Afternoon Delight", "Kelly County Smugglers", "", "normal"),
        ("43. Prepare for Vice City", "Liquidating Local Assets", "", "normal"),
        ("44. Checking Out", "Port Gellhorn Climax & Relocation", "Ch. 2 Climax", "point_of_no_return"),
    ]
    
    stages = [
        ("STAGE 1: MOTEL ARRIVAL (M23-28)", s1_cards, cols_x[0]),
        ("STAGE 2: DEBT HUSTLE (M29-37)", s2_cards, cols_x[1]),
        ("STAGE 3: DUAL SWITCHING (M38-40)", s3_cards, cols_x[2]),
        ("STAGE 4: MOVE TO VC (M41-44)", s4_cards, cols_x[3]),
    ]
    
    for s_idx, (stitle, card_list, cx) in enumerate(stages):
        # Stage container header
        ax.text(cx + w/2, 12.5, stitle, ha="center", va="center", fontsize=9.2, fontweight="bold", color="#fde047", zorder=4)
        ax.plot([cx, cx + w], [12.2, 12.2], color="#f59e0b", lw=1.2, zorder=3)
        
        y_start = 11.0
        for r_idx, (t, sub, badge, ctype) in enumerate(card_list):
            cy = y_start - r_idx * gap
            draw_card(ax, cx, cy, w, h, t, sub, badge, ctype, fontsize=8.2)
            if r_idx < len(card_list) - 1:
                draw_arrow(ax, (cx + w/2, cy), (cx + w/2, cy - (gap - h)), color="#38bdf8")
                
    # Sequential Bridge Connectors (Orthogonal perimeter / gutter routing)
    # Stage 1 bottom -> Stage 2 top
    gx1 = (cols_x[0] + w + cols_x[1]) / 2
    draw_stage_bridge(ax, cols_x[0] + w/2, 11.0 - 5*gap, cols_x[1], 11.0 + h/2, gx1, "STAGE 2 ▲\nNEXT")
    
    # Stage 2 bottom -> Stage 3 top
    gx2 = (cols_x[1] + w + cols_x[2]) / 2
    draw_stage_bridge(ax, cols_x[1] + w/2, 11.0 - 5*gap, cols_x[2], 11.0 + h/2, gx2, "STAGE 3 ▲\nNEXT")
    
    # Stage 3 bottom -> Stage 4 top
    gx3 = (cols_x[2] + w + cols_x[3]) / 2
    draw_stage_bridge(ax, cols_x[2] + w/2, 11.0 - 2*gap, cols_x[3], 11.0 + h/2, gx3, "STAGE 4 ▲\nNEXT")
    
    # Transition to Chapter 3
    ch3_x, ch3_y = cols_x[3], 11.0 - 4.5*gap
    draw_card(ax, ch3_x, ch3_y, w, 1.1, "→ TRANSITION TO CHAPTER 3", "Destination: Vice City (South Leonida)", "Next Chapter", "point_of_no_return")
    draw_arrow(ax, (cols_x[3] + w/2, 11.0 - 3*gap), (cols_x[3] + w/2, ch3_y + 1.1), color="#ef4444", lw=2.0)
    
    out_path = os.path.join(ARTIFACT_DIR, "flowchart_chapter_2.png")
    plt.savefig(out_path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_2.png")

# =========================================================================
# 3. CHAPTER 3: 3 PARALLEL STRANDS + 3-TRACK CONCURRENT HEIST PREP
# =========================================================================
def render_chapter_3():
    fig, ax = plt.subplots(figsize=(24, 14), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 14)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 3: VICE CITY SYNDICATE EXPANSION",
        "Setting: Vice City Metro & Outskirts | Missions 45 - 70 | 3 Parallel Strands -> Sinfrontera Heist Preps",
        24,
        y_top=13.4
    )
    
    w, h = 3.2, 1.05
    
    # Column 1: Missions 45 - 50 (Linear Safehouse Spine)
    col1 = [
        ("45. Welcome to Vice City", "Arrival in the Metropolis", "", "normal"),
        ("46. Dealer's Choice", "Underground Casino Meeting", "", "normal"),
        ("47. Meet the Heders", "Local Smuggler Syndicate", "", "normal"),
        ("48. Dubious Provenance", "Handling Hot Merchandise", "", "normal"),
        ("49. Mami Knows Best", "Vice City Cartel Liaison", "", "normal"),
        ("50. South Leonida Real Estate", "Safehouse Unlocked -> 3 Strands Open", "Safehouse", "milestone"),
    ]
    
    for r, (t, sub, b, ct) in enumerate(col1):
        cy = 11.8 - r * 1.5
        draw_card(ax, 0.6, cy, w, h, t, sub, b, ct)
        if r < len(col1) - 1:
            draw_arrow(ax, (0.6 + w/2, cy), (0.6 + w/2, cy - 0.45))
            
    # From Mission 50 -> Fan out to 3 Strands
    m50_pt = (0.6 + w, 11.8 - 5 * 1.5 + h/2)
    
    # STRAND 1: TYRONE (Street Muscle)
    s1_x1, s1_x2 = 4.3, 7.8
    draw_card(ax, s1_x1, 11.8, w, h, "51. Tyrone", "Street Level Muscle Contract", "Strand 1", "normal")
    draw_card(ax, s1_x2, 11.8, w, h, "52. Here, Kitty Kitty", "Vice Strip Club Contract", "Strand 1", "normal")
    draw_arrow(ax, (s1_x1 + w, 12.32), (s1_x2, 12.32))
    draw_arrow(ax, m50_pt, (s1_x1, 12.32), color="#38bdf8", rad=-0.25)
    
    # STRAND 2: BOOBIE & DRE'QUAN (Syndicate)
    s2_y = 10.2
    draw_card(ax, s1_x1, s2_y, w, h, "54. Top Billing", "High-End Nightclub Job", "Strand 2", "normal")
    draw_card(ax, s1_x2, s2_y, w, h, "55. Boobie Time", "Boobie Ike Alliance Formed", "Key Contact", "milestone")
    draw_card(ax, s1_x2, 8.6, w, h, "56. First Impressions", "Syndicate Introductions", "Strand 2", "normal")
    draw_arrow(ax, (s1_x1 + w, s2_y + h/2), (s1_x2, s2_y + h/2))
    draw_arrow(ax, (s1_x2 + w/2, s2_y), (s1_x2 + w/2, 8.6 + h))
    draw_arrow(ax, m50_pt, (s1_x1, s2_y + h/2), color="#a855f7", rad=-0.15)
    
    # STRAND 3: RAUL & RANDY (Cartel & Cars)
    draw_card(ax, s1_x1, 6.9, w, h, "53. Car Service", "Luxury Vehicle Interception", "Strand 3", "normal")
    draw_card(ax, s1_x1, 5.4, w, h, "57. Caught Slipping", "Surviving Competitor Ambush", "Strand 3", "normal")
    draw_card(ax, s1_x1, 3.9, w, h, "58. Crosstown Traffic", "Highway Pursuit & Escape", "Strand 3", "normal")
    draw_card(ax, s1_x1, 2.4, w, h, "59. Credit Check", "Background Probe on Raul", "Strand 3", "normal")
    draw_card(ax, s1_x2, 2.4, w, h, "60. Steal Zorrusso for Randy", "Exotic Supercar Booster", "Strand 3", "normal")
    
    draw_arrow(ax, m50_pt, (s1_x1, 6.9 + h/2), color="#f59e0b", rad=0.15)
    draw_arrow(ax, (s1_x1 + w/2, 6.9), (s1_x1 + w/2, 6.45))
    draw_arrow(ax, (s1_x1 + w/2, 5.4), (s1_x1 + w/2, 4.95))
    draw_arrow(ax, (s1_x1 + w/2, 3.9), (s1_x1 + w/2, 3.45))
    draw_arrow(ax, (s1_x1 + w, 2.4 + h/2), (s1_x2, 2.4 + h/2))
    
    # HEIST SCOPE OUT CONVERGENCE (Mission 61)
    heist_scope_y = 5.2
    draw_card(ax, s1_x2, heist_scope_y, w, 1.4, "61. Sinfrontera National Bank", "HEIST SCOPE OUT & PLANNING BOARD\nAll 3 Strands Converge Here!", "CONVERGENCE", "heist")
    
    # Arrows from Strand 1, 2, 3 into Mission 61
    draw_arrow(ax, (s1_x2 + w/2, 11.8), (s1_x2 + w/2, heist_scope_y + 1.4), color="#fbbf24", rad=-0.2)
    draw_arrow(ax, (s1_x2 + w/2, 8.6), (s1_x2 + w/2, heist_scope_y + 1.4), color="#fbbf24")
    draw_arrow(ax, (s1_x2 + w/2, 3.45), (s1_x2 + w/2, heist_scope_y), color="#fbbf24")
    
    # -------------------------------------------------------------
    # HEIST PREPARATION PIPELINE: 3 CONCURRENT PARALLEL TRACKS
    # -------------------------------------------------------------
    prep_box = patches.FancyBboxPatch(
        (11.8, 1.2), 11.6, 11.2,
        boxstyle="round,pad=0.03,rounding_size=0.2",
        linewidth=1.4,
        edgecolor="#f59e0b",
        facecolor="#18140f",
        zorder=1
    )
    ax.add_patch(prep_box)
    ax.text(17.6, 12.0, "SINFRONTERA BANK HEIST PREPARATION PIPELINE (3 CONCURRENT TRACKS)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#fde047")
    
    pw = 3.6
    t1_x = 12.2   # Track 1: Safecracker
    t2_x = 16.0   # Track 2: Explosives
    t3_x = 19.8   # Track 3: Codes & Van
    
    # Track 1: Safecracker (62 -> 65 -> 68)
    draw_card(ax, t1_x, 10.3, pw, 1.05, "62. Security Expert", "Retrieve Nicole Park", "Track 1", "heist", fontsize=8.2)
    draw_card(ax, t1_x, 8.6, pw, 1.05, "65. Safe Word", "Safe-Cracking Drill", "Track 1", "heist", fontsize=8.2)
    draw_card(ax, t1_x, 6.9, pw, 1.05, "68. Cooties", "Disinfecting Evidence", "Track 1", "heist", fontsize=8.2)
    draw_arrow(ax, (t1_x + pw/2, 10.3), (t1_x + pw/2, 9.65), color="#fde047")
    draw_arrow(ax, (t1_x + pw/2, 8.6), (t1_x + pw/2, 7.95), color="#fde047")
    
    # Track 2: Explosives (63 -> 66 -> 69)
    draw_card(ax, t2_x, 10.3, pw, 1.05, "63. Company Property", "Steal Vault Charges", "Track 2", "heist", fontsize=8.2)
    draw_card(ax, t2_x, 8.6, pw, 1.05, "66. Hidden Charges", "Rig 3 Regional Towers", "Track 2", "heist", fontsize=8.2)
    draw_card(ax, t2_x, 6.9, pw, 1.05, "69. Bricked Up", "Reinforce Extraction Route", "Track 2", "heist", fontsize=8.2)
    draw_arrow(ax, (t2_x + pw/2, 10.3), (t2_x + pw/2, 9.65), color="#fde047")
    draw_arrow(ax, (t2_x + pw/2, 8.6), (t2_x + pw/2, 7.95), color="#fde047")
    
    # Track 3: Codes & Van (64 -> 67)
    draw_card(ax, t3_x, 10.3, pw, 1.05, "64. The Missing Link", "Interrogate Monty for Codes", "Track 3", "heist", fontsize=8.2)
    draw_card(ax, t3_x, 8.6, pw, 1.05, "67. Ride or Die", "Armored Extraction Van", "Track 3", "heist", fontsize=8.2)
    draw_arrow(ax, (t3_x + pw/2, 10.3), (t3_x + pw/2, 9.65), color="#fde047")
    
    # Top Distribution Bus Bar from 61. Sinfrontera Scope Out to Tracks 1, 2, 3
    y_bus = 11.65
    gx_bus = 11.4
    m61_exit_y = heist_scope_y + 0.7
    ax.plot([s1_x2 + w, gx_bus, gx_bus, t3_x + pw/2], [m61_exit_y, m61_exit_y, y_bus, y_bus], color="#fbbf24", lw=2.0, zorder=2)
    
    # Drop vertical arrows into tops of 62, 63, and 64
    top_card_y = 10.3 + 1.05
    draw_arrow(ax, (t1_x + pw/2, y_bus), (t1_x + pw/2, top_card_y), color="#fbbf24")
    draw_arrow(ax, (t2_x + pw/2, y_bus), (t2_x + pw/2, top_card_y), color="#fbbf24")
    draw_arrow(ax, (t3_x + pw/2, y_bus), (t3_x + pw/2, top_card_y), color="#fbbf24")
    
    # 70. THE CARTEL HEIST CLIMAX
    heist_fin_y = 3.6
    draw_card(ax, 13.5, heist_fin_y, 8.2, 1.35, "70. THE CARTEL HEIST", "Sinfrontera National Bank Vault Raid ($10.5M Take)\n★ Keep $75,000 for Chapter 4 Abe Gate! ★", "MAJOR HEIST CLIMAX", "point_of_no_return", fontsize=9.5)
    
    # Clean non-crossing convergence into 70
    draw_arrow(ax, (t1_x + pw/2, 6.9), (t1_x + pw/2, heist_fin_y + 1.35), color="#ef4444", lw=1.8)
    draw_arrow(ax, (t2_x + pw/2, 6.9), (t2_x + pw/2, heist_fin_y + 1.35), color="#ef4444", lw=1.8)
    ax.plot([t3_x + pw/2, t3_x + pw/2, 21.0], [8.6, 5.8, 5.8], color="#ef4444", lw=1.8, zorder=2)
    draw_arrow(ax, (21.0, 5.8), (21.0, heist_fin_y + 1.35), color="#ef4444", lw=1.8)
    
    # Transition to Chapter 4
    trans_x = 13.5 + 4.1 - w/2
    draw_card(ax, trans_x, 1.8, w, 1.05, "→ TRANSITION TO CH. 4", "Destination: Ocean Beach (VC)", "Next Chapter", "point_of_no_return")
    draw_arrow(ax, (trans_x + w/2, heist_fin_y), (trans_x + w/2, 1.8 + 1.05), color="#ef4444", lw=2.0)
    
    out_path = os.path.join(ARTIFACT_DIR, "flowchart_chapter_3.png")
    plt.savefig(out_path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_3.png")

# =========================================================================
# 4. CHAPTER 4: STRICT SEQUENTIAL PHASES (NO MISLEADING WRAP-AROUND ARROWS)
# =========================================================================
def render_chapter_4():
    fig, ax = plt.subplots(figsize=(24, 16), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 16)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 4: VICE CITY METRO & AIRPORT HEIST",
        "Setting: Ocean Beach, Downtown VC & VCIA Airport | Missions 71 - 95 | Sequential Timeline",
        24,
        y_top=15.4
    )
    
    # Disclaimer Banner
    banner = patches.FancyBboxPatch((2.0, 14.1), 20.0, 0.7, boxstyle="round,pad=0.03,rounding_size=0.15", linewidth=1.2, edgecolor="#38bdf8", facecolor="#083344", zorder=3)
    ax.add_patch(banner)
    ax.text(12.0, 14.45, "⚠️ STRICT CHRONOLOGICAL SEQUENCE — Stages must be completed 1 → 2 → 3 → 4 in order (Not parallel branches)", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#38bdf8", zorder=4)
    
    w, h = 4.4, 0.95
    cols_x = [1.0, 6.8, 12.6, 18.4]
    gap = 1.25
    
    # STAGE 1: BEACHHEAD & ABE'S $75k GATE (Missions 71 - 75)
    s1_cards = [
        ("71. Ocean Beach", "Establish Y Hotel Safehouse", "Safehouse", "milestone"),
        ("72. Another Life", "High-End Lifestyle Setup", "", "normal"),
        ("73. Company Cars", "Fleet Acquisition for Syndicate", "", "normal"),
        ("74. Lawyer Up", "Abe Gonzalez Legal Consultation", "Legal Contact", "milestone"),
        ("75. Party Hard", "Nightclub Meet & $75k Wire to Abe", "$75k BuckMe Wire", "point_of_no_return"),
    ]
    
    # STAGE 2: SYNDICATE & CORPORATE OPERATIONS (Missions 76 - 82)
    s2_cards = [
        ("76. Heavy Lifting", "Smuggling Port Cargo Containers", "", "normal"),
        ("77. Photo/Shoot", "Paparazzi Blackmail & Intel", "", "normal"),
        ("78. Making Gainz", "Fitness Syndicate Interception", "", "normal"),
        ("79. Watch It", "Executive Surveillance Job", "", "normal"),
        ("80. Cash Injections", "Laundering Syndicate Profits", "", "normal"),
        ("81. Amateur Hour", "Rival Gang Ambush Defense", "", "normal"),
        ("82. Dirty Work", "Sanitizing High-Profile Murder", "", "normal"),
    ]
    
    # STAGE 3: DRE'QUAN CLIMAX & AIRPORT RECON (Missions 83 - 91)
    s3_cards = [
        ("83. Too Much Baggage", "Airport Courier Reconnaissance", "Airport Recon", "milestone"),
        ("84. Adventures in Babysitting", "Protecting Celebrity VIP", "", "normal"),
        ("85. Fresh Evidence", "Stealing Prosecutor Files", "", "normal"),
        ("86. Power Play", "Corporate Extortion Meeting", "", "normal"),
        ("87. Child's Play", "Kidnapping High-Value Target", "", "normal"),
        ("88. Headliners", "Dre'Quan Climax Performance", "Dre'Quan End", "milestone"),
        ("89. Close Surveillance -> 91. Team Building", "VCIA Perimeter Intel & Crew Rally", "", "normal"),
    ]
    
    # STAGE 4: VCIA HEIST & POINT OF NO RETURN (Missions 92 - 95)
    s4_cards = [
        ("92. Fully Catered", "Infiltrating Catering Trucks", "Smuggling Vector", "heist"),
        ("93. VCIA TAKEDOWN", "Major Airport Cargo Heist", "MAJOR AIRPORT HEIST", "heist"),
        ("94. Sunset", "Open-World Closure & Transition", "★ POINT OF NO RETURN ★", "point_of_no_return"),
        ("95. Starting From Zero", "Chapter 4 Climax / Evacuation", "Ch. 4 Climax", "point_of_no_return"),
    ]
    
    stages = [
        ("STAGE 1: BEACHHEAD & $75k (M71-75)", s1_cards, cols_x[0]),
        ("STAGE 2: SYNDICATE OPS (M76-82)", s2_cards, cols_x[1]),
        ("STAGE 3: DRE & RECON (M83-91)", s3_cards, cols_x[2]),
        ("STAGE 4: VCIA HEIST (M92-95)", s4_cards, cols_x[3]),
    ]
    
    for s_idx, (stitle, card_list, cx) in enumerate(stages):
        ax.text(cx + w/2, 13.5, stitle, ha="center", va="center", fontsize=9.2, fontweight="bold", color="#fde047", zorder=4)
        ax.plot([cx, cx + w], [13.2, 13.2], color="#f59e0b", lw=1.2, zorder=3)
        
        y_start = 12.0
        for r_idx, (t, sub, badge, ctype) in enumerate(card_list):
            cy = y_start - r_idx * gap
            draw_card(ax, cx, cy, w, h, t, sub, badge, ctype, fontsize=8.2)
            if r_idx < len(card_list) - 1:
                draw_arrow(ax, (cx + w/2, cy), (cx + w/2, cy - (gap - h)), color="#38bdf8")
                
    # Sequential Bridge Connectors (Orthogonal perimeter / gutter routing)
    # Stage 1 bottom -> Stage 2 top
    gx1 = (cols_x[0] + w + cols_x[1]) / 2
    draw_stage_bridge(ax, cols_x[0] + w/2, 12.0 - 4*gap, cols_x[1], 12.0 + h/2, gx1, "STAGE 2 ▲\nNEXT")
    
    # Stage 2 bottom -> Stage 3 top
    gx2 = (cols_x[1] + w + cols_x[2]) / 2
    draw_stage_bridge(ax, cols_x[1] + w/2, 12.0 - 6*gap, cols_x[2], 12.0 + h/2, gx2, "STAGE 3 ▲\nNEXT")
    
    # Stage 3 bottom -> Stage 4 top
    gx3 = (cols_x[2] + w + cols_x[3]) / 2
    draw_stage_bridge(ax, cols_x[2] + w/2, 12.0 - 6*gap, cols_x[3], 12.0 + h/2, gx3, "STAGE 4 ▲\nNEXT")
    
    # Transition to Chapter 5
    ch5_x, ch5_y = cols_x[3], 12.0 - 5.0*gap
    draw_card(ax, ch5_x, ch5_y, w, 1.1, "→ TRANSITION TO CHAPTER 5", "Destination: Endgame Standoff", "Final Chapter", "point_of_no_return")
    draw_arrow(ax, (cols_x[3] + w/2, 12.0 - 3*gap), (cols_x[3] + w/2, ch5_y + 1.1), color="#ef4444", lw=2.0)
    
    out_path = os.path.join(ARTIFACT_DIR, "flowchart_chapter_4.png")
    plt.savefig(out_path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_4.png")

# =========================================================================
# 5. CHAPTER 5: THE FINALE & ENDING A/B PAYOUT CLARIFICATION
# =========================================================================
def render_chapter_5():
    fig, ax = plt.subplots(figsize=(18, 15), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 15)
    ax.axis("off")
    
    setup_header(
        ax,
        "GRAND THEFT AUTO VI — CHAPTER 5: TOP OF THE WORLD, MA!",
        "The Climax, Tactical Assaults, Betrayal, and Branching Endings | Missions 96 - 102",
        18,
        y_top=14.4
    )
    
    w, h = 4.2, 1.1
    cx = 6.9
    
    # Spine missions: 96 -> 97 -> 98 -> 99
    spine = [
        ("96. Top of the World", "Leonida Keys Sanctuary Infiltration", "", "milestone"),
        ("97. Bait and Switch", "Luring Federal Strike Teams", "", "normal"),
        ("98. Scorched Earth", "Asset Destruction & Evacuation", "", "normal"),
        ("99. Two Hundred Percent", "Joint Assault on Mendez Compound", "Joint Assault", "heist"),
    ]
    
    y_start = 13.0
    gap = 1.45
    for idx, (t, sub, badge, ctype) in enumerate(spine):
        cy = y_start - idx * gap
        draw_card(ax, cx, cy, w, h, t, sub, badge, ctype)
        if idx < len(spine) - 1:
            draw_arrow(ax, (cx + w/2, cy), (cx + w/2, cy - (gap - h)))
            
    # Standoff Decision Card (Mission 100)
    dia_y = y_start - 4 * gap
    draw_card(ax, cx - 0.5, dia_y, w + 1.0, 1.35, "100. FINAL DECISION STANDOFF", "Agent Mendez Federal Ambush at Key West Motel\nChoose Jason & Lucia's Ultimate Fate", "DECISION FORK", "point_of_no_return")
    draw_arrow(ax, (cx + w/2, y_start - 3 * gap), (cx + w/2, dia_y + 1.35), color="#ef4444", lw=2.0)
    
    # 3 Branching Endings
    end_w = 4.8
    end_y = dia_y - 2.2
    
    # Ending A (Left)
    draw_card(ax, 0.8, end_y, end_w, 1.45, "ENDING A: BONNIE & CLYDE", "Outlaws Together | Reject Federal Deal\nFight through Coast Guard to Airstrip.\n★ AWARDS $2,000,000 Payout (Not required!) ★", "LOYALTY PATH", "ending", fontsize=8.5)
    draw_arrow(ax, (cx - 0.5, dia_y + 0.65), (0.8 + end_w/2, end_y + 1.45), color="#10b981", rad=-0.2)
    
    # Ending B (Center)
    draw_card(ax, 6.6, end_y, end_w, 1.45, "ENDING B: THE DEAL (ANY% ROUTE)", "Accept Mendez Deal & Enter Immunity\nSkips Multi-Stage Offshore Boat Chase!\n★ SAVES 8-12 MINUTES IN ANY% SPEEDRUN ★", "SPEEDRUN ROUTE", "ending", fontsize=8.5)
    draw_arrow(ax, (cx + w/2, dia_y), (6.6 + end_w/2, end_y + 1.45), color="#38bdf8", lw=2.2)
    
    # Ending C (Right)
    draw_card(ax, 12.4, end_y, end_w, 1.45, "ENDING C: THE SACRIFICE", "One Partner Escapes, One Stays Behind\nSolo Evacuation Flight to South America\nUnique Melancholy Radio Broadcasts", "TRAGIC PATH", "ending", fontsize=8.5)
    draw_arrow(ax, (cx + w + 0.5, dia_y + 0.65), (12.4 + end_w/2, end_y + 1.45), color="#f59e0b", rad=0.2)
    
    # Final Epilogue & Credits
    epi_y = end_y - 2.0
    draw_card(ax, 5.5, epi_y, 7.0, 1.25, "101. Final Evacuation  →  102. Epilogue & Credits", "Story Campaign Concluded | Free Roam Restored\nFull Leonida Map Unlocked for Post-Game Activities", "CAMPAIGN FINALE", "point_of_no_return", fontsize=9.2)
    
    draw_arrow(ax, (0.8 + end_w/2, end_y), (5.5 + 1.0, epi_y + 1.25), color="#10b981")
    draw_arrow(ax, (6.6 + end_w/2, end_y), (5.5 + 3.5, epi_y + 1.25), color="#38bdf8")
    draw_arrow(ax, (12.4 + end_w/2, end_y), (5.5 + 6.0, epi_y + 1.25), color="#f59e0b")
    
    out_path = os.path.join(ARTIFACT_DIR, "flowchart_chapter_5.png")
    plt.savefig(out_path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_chapter_5.png")

# =========================================================================
# 6. COMBINED FLOWCHART: ALL 5 CHAPTERS UNIFIED
# =========================================================================
def render_all_combined():
    fig, ax = plt.subplots(figsize=(26, 36), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 26)
    ax.set_ylim(0, 36)
    ax.axis("off")
    
    ax.text(13, 35.4, "GRAND THEFT AUTO VI — COMPLETE CAMPAIGN MISSION FLOW (ALL 5 CHAPTERS)", ha="center", va="center", fontsize=18, fontweight="bold", color="#ffffff")
    ax.text(13, 34.9, "Ground Truth Dependency Graph | Verified Parallel Branches, Decision Diamonds, Heist Preps & Branching Endings", ha="center", va="center", fontsize=10.5, color="#38bdf8")
    
    col_w = 4.6
    cols_x = [0.8, 5.8, 10.8, 15.8, 20.8]
    
    chapter_panels = [
        ("CHAPTER 1: LEONIDA KEYS", "Missions 1-18 | Parallel Downtime Route", "#22d3ee"),
        ("CHAPTER 2: PORT GELLHORN", "Missions 23-44 | 4 Sequential Stages", "#f43f5e"),
        ("CHAPTER 3: VICE CITY HEIST", "Missions 45-70 | 3 Strands & Heist Board", "#fbbf24"),
        ("CHAPTER 4: AIRPORT TAKEDOWN", "Missions 71-95 | 4 Sequential Stages", "#a855f7"),
        ("CHAPTER 5: THE FINALE", "Missions 96-102 | Decision & Endings", "#ef4444"),
    ]
    
    for idx, (title, sub, color) in enumerate(chapter_panels):
        cx = cols_x[idx]
        panel = patches.Rectangle((cx, 1.0), col_w, 33.2, linewidth=1.6, edgecolor=color, facecolor="#101520", zorder=1)
        ax.add_patch(panel)
        ax.text(cx + col_w/2, 33.7, title, ha="center", va="center", fontsize=9.8, fontweight="bold", color=color, zorder=2)
        ax.text(cx + col_w/2, 33.3, sub, ha="center", va="center", fontsize=7.2, color="#94a3b8", zorder=2)
        
    pw = 4.2
    
    # Col 1: Chapter 1
    c1_x = cols_x[0] + 0.2
    c1_cards = [
        ("1. Prologue -> 2. Gone Fishing", "Boat Drop ($140 Mailbox)", "normal", 31.8),
        ("BRANCH A: Unwanted Attention -> Pipework", "Hamlet Trip ($200 Mailbox)", "normal", 29.8),
        ("BRANCH B: Gear Up -> Just a Scratch", "Ganado Respray (MANDATORY GATE)", "milestone", 27.8),
        ("BRANCH C: Lab Fees -> Hey Arnold!", "Rent Collection & Broker Recon", "normal", 25.8),
        ("10. Feng Shui (24h Cooldown Window)", "Clear Branch A during this downtime!", "normal", 23.8),
        ("11. Coming Home -> 12. Donnie's Package", "Lucia Reunion & Hamlet Pickup", "milestone", 21.8),
        ("DIAMOND 1: Just a Scratch Done?", "Joey reminder call if skipped", "heist", 19.8),
        ("13. Buck Me -> 14. Down to Earth", "Banking App & $600 Mailbox", "normal", 17.8),
        ("15. Clear Skies -> 16. Day Release", "Southwind Bikers & Rusty Anchor", "normal", 15.8),
        ("DIAMOND 2: Day Release & Scratch Done?", "Gate for Smuggler Ambush", "heist", 13.8),
        ("17. Swamped -> 18. Doin' Gone", "Chapter 1 Climax at Trailer", "point_of_no_return", 11.8),
        ("TRANSITION TO PORT GELLHORN", "Starlet Motel Arrival", "point_of_no_return", 9.8),
    ]
    for t, s, ct, cy in c1_cards:
        draw_card(ax, c1_x, cy, pw, 1.25, t, s, card_type=ct, fontsize=7.6)
    draw_column_bridge(ax, c1_x + pw, 10.4, cols_x[1] + 0.2, 32.4, 5.6, "CH. 2 NEXT ▲", color="#f43f5e")
    
    # Col 2: Chapter 2
    c2_x = cols_x[1] + 0.2
    c2_cards = [
        ("STAGE 1: Motel Arrival (M23-28)", "Take Care of Jason & Moses Fencing", "normal", 31.8),
        ("STAGE 2: Debt Hustle (M29-37)", "Ambulance Chaser & Gun Runs", "normal", 28.5),
        ("38. Coffee Break (Dual Switching)", "★ DUAL SWITCHING UNLOCKED ★", "milestone", 25.2),
        ("STAGE 3: Robberies (M39-40)", "Hit Avery Pawn System Demo", "normal", 22.2),
        ("STAGE 4: Move to VC (M41-44)", "Impounded Vehicle -> Checking Out", "normal", 19.2),
        ("44. Checking Out (Ch. 2 Climax)", "Relocate to Vice City Safehouse", "point_of_no_return", 16.2),
        ("TRANSITION TO VICE CITY", "South Leonida Real Estate", "point_of_no_return", 13.2),
    ]
    for t, s, ct, cy in c2_cards:
        draw_card(ax, c2_x, cy, pw, 1.35, t, s, card_type=ct, fontsize=7.6)
    draw_column_bridge(ax, c2_x + pw, 13.8, cols_x[2] + 0.2, 32.4, 10.6, "CH. 3 NEXT ▲", color="#fbbf24")
    
    # Col 3: Chapter 3
    c3_x = cols_x[2] + 0.2
    c3_cards = [
        ("45. Welcome to VC -> 50. Real Estate", "Safehouse Unlocked -> 3 Strands", "normal", 31.8),
        ("STRAND 1: Tyrone (M51-52)", "Street Muscle & Here Kitty Kitty", "normal", 29.2),
        ("STRAND 2: Boobie & Dre (M54-56)", "Nightclub & Port Introductions", "normal", 26.8),
        ("STRAND 3: Raul & Randy (M53,57-60)", "Car Service -> Zorrusso Supercar", "normal", 24.4),
        ("61. Sinfrontera Bank Scope Out", "All 3 Strands Converge Here!", "heist", 21.8),
        ("3 PARALLEL HEIST PREP TRACKS", "Track 1: Safecracker (62,65,68)\nTrack 2: Explosives (63,66,69)\nTrack 3: Codes & Van (64,67)", "heist", 18.8),
        ("70. THE CARTEL HEIST", "Vault Raid Score ($10.5M Take)\nKeep $75k for Ch. 4 Abe Gate!", "point_of_no_return", 15.6),
        ("TRANSITION TO OCEAN BEACH", "Y Hotel Headquarters", "point_of_no_return", 13.0),
    ]
    for t, s, ct, cy in c3_cards:
        draw_card(ax, c3_x, cy, pw, 1.45 if "TRACKS" in t else 1.3, t, s, card_type=ct, fontsize=7.5)
    draw_column_bridge(ax, c3_x + pw, 13.6, cols_x[3] + 0.2, 32.4, 15.6, "CH. 4 NEXT ▲", color="#a855f7")
    
    # Col 4: Chapter 4
    c4_x = cols_x[3] + 0.2
    c4_cards = [
        ("STAGE 1: Beachhead & $75k Gate", "71. Ocean Beach -> 75. Party Hard", "normal", 31.8),
        ("STAGE 2: Syndicate Ops (M76-82)", "Heavy Lifting, Making Gainz, Dirty Work", "normal", 28.5),
        ("STAGE 3: Dre'Quan Climax (M83-88)", "Too Much Baggage -> Headliners", "normal", 25.2),
        ("STAGE 4: VCIA Recon (M89-91)", "Close Surveillance & Team Building", "normal", 22.0),
        ("92. Fully Catered -> 93. VCIA TAKEDOWN", "Major Airport Cargo Heist", "heist", 18.8),
        ("94. Sunset (Point of No Return)", "Locks open-world roaming and saves!", "point_of_no_return", 15.6),
        ("95. Starting From Zero", "Chapter 4 Climax Evacuation", "point_of_no_return", 13.0),
    ]
    for t, s, ct, cy in c4_cards:
        draw_card(ax, c4_x, cy, pw, 1.3, t, s, card_type=ct, fontsize=7.5)
    draw_column_bridge(ax, c4_x + pw, 13.6, cols_x[4] + 0.2, 32.4, 20.6, "CH. 5 NEXT ▲", color="#ef4444")
    
    # Col 5: Chapter 5
    c5_x = cols_x[4] + 0.2
    c5_cards = [
        ("96. Top of the World -> 98. Scorched Earth", "Federal Raid & Asset Evacuation", "normal", 31.8),
        ("99. Two Hundred Percent", "Joint Assault on Mendez Compound", "heist", 28.5),
        ("100. FINAL DECISION STANDOFF", "Choose Loyalty or Immunity", "point_of_no_return", 25.2),
        ("★ ENDING B: THE DEAL (ANY% ROUTE) ★", "Accept Immunity -> Skips Boat Chase!\nSAVES 8-12 MINUTES IN ANY%", "ending", 21.6),
        ("Ending A: Bonnie & Clyde", "Loyalty: Awards $2,000,000 Payout\n(Reward payout, not requirement!)", "ending", 18.0),
        ("Ending C: The Sacrifice", "Partner Betrayal & Solo Escort", "ending", 15.0),
        ("101. Final Evacuation -> 102. Credits", "Full Leonida Map Unlocked for End Game", "point_of_no_return", 12.0),
    ]
    for t, s, ct, cy in c5_cards:
        draw_card(ax, c5_x, cy, pw, 1.45 if "ANY%" in t else 1.3, t, s, card_type=ct, fontsize=7.5)
        
    out_path = os.path.join(ARTIFACT_DIR, "flowchart_all_chapters_combined.png")
    plt.savefig(out_path, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    copy_to_all("flowchart_all_chapters_combined.png")

if __name__ == "__main__":
    render_chapter_1()
    render_chapter_2()
    render_chapter_3()
    render_chapter_4()
    render_chapter_5()
    render_all_combined()
