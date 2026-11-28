import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import shutil

WORKSPACE_DIR = r"C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK"
DOWNLOADS_DIR = r"C:\Users\<user>\Downloads"
ARTIFACT_DIR = r"C:\Users\<user>\.gemini\antigravity-cli\brain\96252013-4633-45e8-b6a2-59b18be9e68c"

BG_COLOR = "#33363b"       # Matches GTAVI_MISSION_FLOW1.jpg dark-slate gray

def draw_mission(ax, x, y, w, h, title, subtitle="", is_climax=False, is_gate=False, font_size=8.5):
    bg = "#fef08a" if not is_climax else "#ffedd5"
    border = "#ca8a04" if not is_climax else "#ea580c"
    lw = 2.0 if (is_climax or is_gate) else 1.2
    
    rect = patches.Rectangle((x, y), w, h, linewidth=lw, edgecolor=border, facecolor=bg, zorder=3)
    ax.add_patch(rect)
    
    ty = y + h/2 + 0.12 if subtitle else y + h/2
    ax.text(x + w/2, ty, title, ha="center", va="center", fontsize=font_size, fontweight="bold", color="#1c1917", zorder=4)
    if subtitle:
        ax.text(x + w/2, y + 0.18, subtitle, ha="center", va="center", fontsize=font_size-1.8, color="#44403c", zorder=4)

def draw_callout(ax, x, y, w, h, text, icon_type="text", font_size=7.2):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.0, edgecolor="#71717a", facecolor="#ffffff", zorder=3)
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
        
    ax.text(x + w/2, y + h/2, prefix + text, ha="center", va="center", fontsize=font_size, fontweight="bold" if icon_type=="phone" else "normal", color="#09090b", zorder=4)

def draw_heart(ax, x, y, w, h, text, skip_label="[ANY% SKIP]", font_size=7.0):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.2, edgecolor="#f43f5e", facecolor="#ffe4e6", zorder=3)
    ax.add_patch(rect)
    t = "♥ " + text
    if skip_label:
        t += "\n" + skip_label
    ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=font_size, fontweight="bold", color="#9f1239", zorder=4)

def draw_side(ax, x, y, w, h, text, font_size=7.0):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.2, edgecolor="#a855f7", facecolor="#f3e8ff", zorder=3)
    ax.add_patch(rect)
    t = text + "\n[OPTIONAL / SKIP]"
    ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=font_size, color="#581c87", zorder=4)

def draw_diamond(ax, cx, cy, rx, ry, text, font_size=6.8):
    pts = [[cx, cy + ry], [cx + rx, cy], [cx, cy - ry], [cx - rx, cy]]
    poly = patches.Polygon(pts, closed=True, linewidth=1.4, edgecolor="#cbd5e1", facecolor="#ffffff", zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=font_size, fontweight="bold", color="#0f172a", zorder=4)

def draw_speedrun_badge(ax, x, y, w, h, title, note, font_size=6.8):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.4, edgecolor="#10b981", facecolor="#064e3b", zorder=3)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 0.22, "⚡ " + title, ha="center", va="center", fontsize=font_size+0.6, fontweight="bold", color="#34d399", zorder=4)
    ax.text(x + w/2, y + h/2 - 0.1, note, ha="center", va="center", fontsize=font_size, color="#ecfdf5", zorder=4)

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

# =========================================================================
# 1. RENDER EXACT CHAPTER 1 MATCHING image_1188e9.jpg GROUND TRUTH + SPEEDRUN
# =========================================================================
def render_speedrun_chapter_1():
    fig, ax = plt.subplots(figsize=(25, 28), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 28)
    ax.axis("off")
    
    # Title Banner
    ax.text(12.5, 27.4, "GRAND THEFT AUTO VI — CHAPTER 1 MISSION FLOW (GROUND TRUTH)", ha="center", va="center", fontsize=17, fontweight="bold", color="#ffffff")
    ax.text(12.5, 26.9, "Exact 3-Branch Parallel Structure, Decision Diamonds, Mailboxes & Corrected Mission Flow (Missions 1 - 18)", ha="center", va="center", fontsize=10, color="#fde047")
    
    # Top: PROLOGUE -> GONE FISHING
    mw, mh = 3.6, 0.95
    center_x = 10.8
    
    draw_mission(ax, center_x, 25.5, mw, mh, "PROLOGUE", "Lucia Prison Counselor Interview")
    draw_mission(ax, center_x, 24.0, mw, mh, "GONE FISHING", "Jason & Donnie Boat Drop")
    draw_arrow(ax, (center_x + mw/2, 25.5), (center_x + mw/2, 24.95))
    
    # Donnie Text Mailbox
    draw_callout(ax, center_x + mw + 0.4, 24.05, 3.4, 0.75, "DONNIE TEXT\n($140 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (center_x + mw, 24.45), (center_x + mw + 0.4, 24.45))
    
    # Split bar below Gone Fishing (splits into 3 parallel tracks)
    split_y = 23.2
    ax.plot([2.2, 5.7, 12.6], [split_y, split_y, split_y], color="#ffffff", lw=1.5, zorder=2)
    draw_arrow(ax, (center_x + mw/2, 24.0), (center_x + mw/2, split_y))
    
    # -------------------------------------------------------------
    # BRANCH 1: UNWANTED ATTENTION & PIPEWORK (Left Track: x = 0.7)
    # -------------------------------------------------------------
    b1_x = 0.7
    mw1 = 3.0
    draw_arrow(ax, (2.2, split_y), (b1_x + mw1/2, 22.2))
    draw_mission(ax, b1_x, 21.2, mw1, mh, "UNWANTED ATTENTION", "Cal & Jason Drive to Hamlet")
    
    draw_callout(ax, b1_x, 20.1, mw1, 0.75, "CAL TEXT\n($200 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (b1_x + mw1/2, 21.2), (b1_x + mw1/2, 20.85))
    
    draw_callout(ax, b1_x, 19.0, mw1, 0.65, "BRIAN CALL", "phone")
    draw_arrow(ax, (b1_x + mw1/2, 20.1), (b1_x + mw1/2, 19.65))
    
    draw_mission(ax, b1_x, 17.7, mw1, mh, "PIPEWORK", "Marina Maintenance Jobs")
    draw_arrow(ax, (b1_x + mw1/2, 19.0), (b1_x + mw1/2, 18.65))
    
    draw_callout(ax, b1_x, 16.6, mw1, 0.65, "BRIAN TEXT", "text")
    draw_arrow(ax, (b1_x + mw1/2, 17.7), (b1_x + mw1/2, 17.25))
    
    # Chuck Gun shop text offshoot (placed directly in Branch 1 below Brian text)
    draw_callout(ax, b1_x, 15.4, mw1, 0.75, "CHUCK'S GUN SHOP TEXT\n(Cooldown / After Pipework)", "text", font_size=6.2)
    draw_arrow(ax, (b1_x + mw1/2, 16.6), (b1_x + mw1/2, 16.15))
    
    # Speedrun routing tip for Branch 1
    draw_speedrun_badge(ax, b1_x - 0.2, 13.3, mw1 + 0.4, 1.7, "DOWNTIME PARALLEL ROUTING", "Clear Unwanted Attention & Pipework\nduring Feng Shui's 24h wait!\nGrab $200 mailbox immediately.")
    draw_arrow(ax, (b1_x + mw1/2, 15.4), (b1_x + mw1/2, 15.0))
    
    # -------------------------------------------------------------
    # BRANCH 2: GEAR UP & JUST A SCRATCH (Middle-Left Track: x = 4.2)
    # -------------------------------------------------------------
    b2_x = 4.2
    mw2 = 3.0
    draw_arrow(ax, (5.7, split_y), (b2_x + mw2/2, 22.2))
    draw_mission(ax, b2_x, 21.2, mw2, mh, "GEAR UP", "Pick up Longarm for Brian")
    
    draw_callout(ax, b2_x, 20.0, mw2, 0.75, "POST-MISSION FORCED CALL\nFROM DONNIE", "phone")
    draw_arrow(ax, (b2_x + mw2/2, 21.2), (b2_x + mw2/2, 20.75))
    
    draw_callout(ax, b2_x, 18.9, mw2, 0.65, "JOEY TEXT", "text")
    draw_arrow(ax, (b2_x + mw2/2, 20.0), (b2_x + mw2/2, 19.55))
    
    draw_heart(ax, b2_x, 17.6, mw2, mh, "JUST A SCRATCH\n(Ganado Repair & Respray)", skip_label="[MANDATORY STORY GATE!]")
    draw_arrow(ax, (b2_x + mw2/2, 18.9), (b2_x + mw2/2, 18.55))
    
    scratch_line_x = b2_x + mw2/2   # x = 5.7
    
    # -------------------------------------------------------------
    # SUB-BRANCH: ISLAND DREAMS (Keys Diving: x = 7.6)
    # -------------------------------------------------------------
    isl_x = 7.6
    isl_w = 2.8
    draw_mission(ax, isl_x, 18.7, isl_w, mh, "ISLAND DREAMS", "Keys Diving")
    draw_callout(ax, isl_x, 17.5, isl_w, 0.75, "KENTON CALL\n(Treasure Search)", "phone")
    draw_arrow(ax, (isl_x + isl_w/2, 18.7), (isl_x + isl_w/2, 18.25))
    
    # -------------------------------------------------------------
    # BRANCH 3: LAB FEES -> HEY ARNOLD! -> FENG SHUI -> COMING HOME (x = 10.8)
    # -------------------------------------------------------------
    b3_x = 10.8
    mw3 = 3.6
    draw_arrow(ax, (12.6, split_y), (b3_x + mw3/2, 22.2))
    draw_mission(ax, b3_x, 21.2, mw3, mh, "LAB FEES", "Brian's Rent Collection")
    
    # Side task: Drug/diamond drop off
    draw_side(ax, b3_x + mw3 + 0.4, 21.25, 3.6, 0.85, "GRAB ANY DRUG, CASH\nOR DIAMOND ON MAP\n(Unlocks Brian's Drop Off)")
    draw_arrow(ax, (b3_x + mw3, 21.65), (b3_x + mw3 + 0.4, 21.65))
    
    draw_callout(ax, b3_x, 20.0, mw3, 0.65, "BRIAN'S CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, 21.2), (b3_x + mw3/2, 20.65))
    
    draw_mission(ax, b3_x, 18.7, mw3, mh, "HEY ARNOLD!", "Track Down Cargo Broker")
    draw_arrow(ax, (b3_x + mw3/2, 20.0), (b3_x + mw3/2, 19.65))
    
    # Arrow to Island Dreams (left from Hey Arnold)
    draw_arrow(ax, (b3_x, 19.15), (isl_x + isl_w, 19.15))
    
    # Right offshoots from Hey Arnold!
    draw_callout(ax, b3_x + 4.0, 18.8, 2.2, 0.65, "CAL'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3, 19.1), (b3_x + 4.0, 19.1))
    
    draw_callout(ax, b3_x + 6.5, 18.8, 2.8, 0.65, "BRIAN'S TEXT\n($600 MAILBOX)", "mailbox")
    draw_arrow(ax, (b3_x + 6.2, 19.1), (b3_x + 6.5, 19.1))
    
    draw_side(ax, b3_x + 9.6, 18.7, 2.8, 0.85, "DONNIE TEXT\nKingfishers Robbery")
    draw_arrow(ax, (b3_x + 9.3, 19.1), (b3_x + 9.6, 19.1))
    
    # FENG SHUI
    draw_mission(ax, b3_x, 16.0, mw3, mh, "FENG SHUI", "Move Furniture for Brian")
    draw_arrow(ax, (b3_x + mw3/2, 18.7), (b3_x + mw3/2, 16.95))
    
    # 24H Cooldown Note
    draw_callout(ax, b3_x, 14.8, mw3, 0.75, "24 IN-GAME HOURS LATER\n→ LUCIA CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, 16.0), (b3_x + mw3/2, 15.55))
    
    # 4 Heart Activities (ALL ANY% SKIPS!)
    h_y = 14.8
    draw_heart(ax, b3_x + 4.0, h_y, 2.2, 0.75, "GET HAIRCUT")
    draw_heart(ax, b3_x + 6.4, h_y, 2.2, 0.75, "BUY NECKLACE")
    draw_heart(ax, b3_x + 8.8, h_y, 2.2, 0.75, "BUY FLOWERS")
    draw_heart(ax, b3_x + 11.2, h_y, 2.2, 0.75, "BUY GROCERIES")
    draw_arrow(ax, (b3_x + mw3, 15.2), (b3_x + 4.0, 15.2), color="#f43f5e")
    
    # COMING HOME
    draw_mission(ax, b3_x, 13.4, mw3, mh, "COMING HOME", "Lucia Released from Prison", is_climax=True)
    draw_arrow(ax, (b3_x + mw3/2, 14.8), (b3_x + mw3/2, 14.35))
    
    # Side tasks post Coming Home (Right side)
    draw_callout(ax, b3_x + mw3 + 0.4, 13.5, 2.6, 0.65, "ANDY CALL", "phone")
    draw_heart(ax, b3_x + mw3 + 3.2, 13.5, 2.6, 0.65, "LUCIA'S CLOTHES", skip_label="[HOT METER]")
    draw_arrow(ax, (b3_x + mw3, 13.85), (b3_x + mw3 + 0.4, 13.85))
    draw_arrow(ax, (b3_x + mw3 + 3.0, 13.85), (b3_x + mw3 + 3.2, 13.85))
    
    # Side tasks post Coming Home (Left side)
    draw_callout(ax, b3_x - 3.4, 13.5, 3.0, 0.65, "UNLOCK DONNIE DROP OFF", "text", font_size=6.2)
    draw_arrow(ax, (b3_x, 13.85), (b3_x - 0.4, 13.85))
    
    # FIND DONNIE'S PACKAGE (RESTORED!)
    draw_mission(ax, b3_x, 12.0, mw3, mh, "FIND DONNIE'S PACKAGE", "Clean Up After Donnie")
    draw_arrow(ax, (b3_x + mw3/2, 13.4), (b3_x + mw3/2, 12.95))
    
    # Decision Diamond 1: Did player finish Just a Scratch?
    dia1_y = 10.6
    draw_diamond(ax, b3_x + mw3/2, dia1_y, 2.0, 0.75, "Did the player finish:\nJUST A SCRATCH?")
    draw_arrow(ax, (b3_x + mw3/2, 12.0), (b3_x + mw3/2, dia1_y + 0.75))
    
    # Left No branch from Diamond 1
    draw_callout(ax, b3_x - 3.7, dia1_y - 0.35, 3.2, 0.7, "NO → JOEY CALL\nReminds to clear Scratch", "phone")
    draw_arrow(ax, (b3_x + mw3/2 - 2.0, dia1_y), (b3_x - 0.5, dia1_y))
    # Reconnects to Just a Scratch
    draw_arrow(ax, (b3_x - 2.1, dia1_y + 0.35), (b2_x + mw2, 17.8), rad=0.25, color="#f43f5e")
    
    # Yes -> Lucia Call
    draw_callout(ax, b3_x, 9.2, mw3, 0.65, "LUCIA'S CALL", "phone")
    draw_arrow(ax, (b3_x + mw3/2, dia1_y - 0.75), (b3_x + mw3/2, 9.85))
    
    # BUCK ME
    draw_mission(ax, b3_x, 7.8, mw3, mh, "BUCK ME", "Setup Banking App & Deposit")
    draw_arrow(ax, (b3_x + mw3/2, 9.2), (b3_x + mw3/2, 8.75))
    
    draw_callout(ax, b3_x - 3.9, 7.9, 3.4, 0.75, "DEPOSIT CASH\nINTO BUCK ME", "cash")
    draw_arrow(ax, (b3_x, 8.3), (b3_x - 0.5, 8.3))
    
    draw_callout(ax, b3_x + mw3 + 0.4, 7.9, 3.4, 0.75, "BRIAN'S TEXT\nSAVE FOR THE FUTURE", "text")
    draw_arrow(ax, (b3_x + mw3, 8.3), (b3_x + mw3 + 0.4, 8.3))
    
    # DOWN TO EARTH
    draw_mission(ax, b3_x, 6.3, mw3, mh, "DOWN TO EARTH", "Marina Smuggling Run")
    draw_arrow(ax, (b3_x + mw3/2, 7.8), (b3_x + mw3/2, 7.25))
    
    # Side tasks of Down to Earth
    draw_callout(ax, b3_x - 3.9, 6.35, 3.4, 0.75, "DONNIE TEXT\n($600 IN MAILBOX)", "mailbox")
    draw_arrow(ax, (b3_x, 6.75), (b3_x - 0.5, 6.75))
    
    draw_side(ax, b3_x + mw3 + 0.4, 6.35, 3.4, 0.85, "CAL TEXT\nFind Lost Drugs x4")
    draw_arrow(ax, (b3_x + mw3, 6.75), (b3_x + mw3 + 0.4, 6.75))
    
    # CLEAR SKIES / BUILDING A LIFE
    draw_callout(ax, b3_x, 5.0, mw3, 0.65, "DONNIE'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3/2, 6.3), (b3_x + mw3/2, 5.65))
    
    draw_mission(ax, b3_x, 3.7, mw3, mh, "CLEAR SKIES\n(BUILDING A LIFE)", "Deal with Southwind Bikers")
    draw_arrow(ax, (b3_x + mw3/2, 5.0), (b3_x + mw3/2, 4.65))
    
    # DAY RELEASE
    draw_callout(ax, b3_x, 2.5, mw3, 0.65, "LUCIA'S TEXT", "text")
    draw_arrow(ax, (b3_x + mw3/2, 3.7), (b3_x + mw3/2, 3.15))
    
    draw_mission(ax, b3_x, 1.2, mw3, mh, "DAY RELEASE", "Rusty Anchor Bar Night Out")
    draw_arrow(ax, (b3_x + mw3/2, 2.5), (b3_x + mw3/2, 2.15))
    
    draw_callout(ax, b3_x + mw3 + 0.4, 1.25, 3.2, 0.75, "BUCK ME TEXT\n(Interest Earned)", "cash")
    draw_arrow(ax, (b3_x + mw3, 1.65), (b3_x + mw3 + 0.4, 1.65))
    
    # Right of Day Release: Lucia Clock Out side activity
    draw_heart(ax, b3_x + mw3 + 4.0, 1.25, 3.2, 0.85, "LUCIA 'PICK ME UP'\nCLOCK OUT", skip_label="[HOT METER]")
    draw_arrow(ax, (b3_x + mw3 + 3.6, 1.65), (b3_x + mw3 + 4.0, 1.65))
    
    # -------------------------------------------------------------
    # DECISION DIAMOND 2 & BOTTOM CLIMAX (Matches image_1188e9.jpg)
    # -------------------------------------------------------------
    dia2_x = 5.7
    dia2_y = 5.2
    draw_diamond(ax, dia2_x, dia2_y, 2.2, 0.85, "Is DAY RELEASE &\nJUST A SCRATCH\ndone?")
    
    # Arrow from Day Release (pointing left to Diamond 2)
    draw_arrow(ax, (b3_x, 1.65), (dia2_x, dia2_y - 0.85), rad=-0.25)
    
    # Long vertical line from JUST A SCRATCH straight down into top of Diamond 2
    ax.plot([scratch_line_x, dia2_x], [17.6, dia2_y + 0.85], color="#ffffff", lw=1.4, zorder=2)
    draw_arrow(ax, (scratch_line_x, 17.6), (dia2_x, dia2_y + 0.85))
    
    # Below Diamond 2: YES -> Brian's Call -> SWAMPED -> Brian's Call -> DOIN' GONE
    draw_callout(ax, dia2_x - mw2/2, 3.8, mw2, 0.65, "YES → BRIAN'S CALL", "phone")
    draw_arrow(ax, (dia2_x, dia2_y - 0.85), (dia2_x, 4.45))
    
    draw_mission(ax, dia2_x - mw2/2, 2.5, mw2, mh, "SWAMPED", "Kingfishers Smugglers Meet")
    draw_arrow(ax, (dia2_x, 3.8), (dia2_x, 3.45))
    
    draw_callout(ax, dia2_x - mw2/2, 1.35, mw2, 0.65, "BRIAN'S CALL", "phone")
    draw_arrow(ax, (dia2_x, 2.5), (dia2_x, 2.0))
    
    # DOIN' GONE (CORRECTED NAME & GROUND TRUTH CLIMAX!)
    draw_mission(ax, dia2_x - mw2/2, 0.1, mw2, mh, "DOIN' GONE", "Clear Donnie's Trailer (Ch. 1 Climax)", is_climax=True, is_gate=True)
    draw_arrow(ax, (dia2_x, 1.35), (dia2_x, 1.05))
    
    # Transition to Chapter 2
    trans_w = 4.2
    draw_speedrun_badge(ax, dia2_x + mw2/2 + 0.6, 0.1, trans_w, 1.1, "CHAPTER 2 TRANSITION", "Hard cut to Port Gellhorn!\nStarlet Motel arrival & Lucia solo recovery.")
    draw_arrow(ax, (dia2_x + mw2/2, 0.55), (dia2_x + mw2/2 + 0.6, 0.55), color="#f43f5e", lw=1.8)
    
    # Save artifacts
    out_artifact = os.path.join(ARTIFACT_DIR, "GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.png")
    out_workspace = os.path.join(WORKSPACE_DIR, "GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.png")
    out_downloads = os.path.join(DOWNLOADS_DIR, "GTAVI_SPEEDRUN_CHAPTER1_COMPLETE.png")
    
    plt.savefig(out_artifact, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    
    shutil.copyfile(out_artifact, out_workspace)
    shutil.copyfile(out_artifact, out_downloads)
    print("Saved Chapter 1 complete speedrun chart to:", out_artifact)

# =========================================================================
# 2. RENDER FULL CAMPAIGN SPEEDRUN MASTER FLOWCHART (ALL 5 CHAPTERS)
# =========================================================================
def render_speedrun_master_campaign():
    fig, ax = plt.subplots(figsize=(32, 20), dpi=200)
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 32)
    ax.set_ylim(0, 20)
    ax.axis("off")
    
    ax.text(16, 19.3, "GRAND THEFT AUTO VI — ANY% SPEEDRUN ROUTING MASTER MAP", ha="center", va="center", fontsize=20, fontweight="bold", color="#ffffff")
    ax.text(16, 18.7, "All 5 Story Chapters | Optimal Route, Parallel Strands, Heist Prep Concurrency, Cash Gates & Ending Routing", ha="center", va="center", fontsize=11, color="#fde047")
    
    col_w = 5.8
    cols_x = [0.8, 7.0, 13.2, 19.4, 25.6]
    
    chapter_headers = [
        ("CHAPTER 1: LEONIDA KEYS", "Missions 1-18 | Parallel Downtime Route", "#22d3ee"),
        ("CHAPTER 2: PORT GELLHORN", "Missions 23-44 | Character Switch Rush", "#f43f5e"),
        ("CHAPTER 3: VICE CITY HEIST", "Missions 45-70 | 3 Strands -> Sinfrontera Heist", "#fbbf24"),
        ("CHAPTER 4: AIRPORT TAKEDOWN", "Missions 71-95 | $75k Gate & VCIA Cargo Heist", "#a855f7"),
        ("CHAPTER 5: THE FINALE", "Missions 96-102 | Fast 'The Deal' Ending B", "#ef4444"),
    ]
    
    for idx, (title, sub, color) in enumerate(chapter_headers):
        cx = cols_x[idx]
        panel = patches.Rectangle((cx, 0.6), col_w, 17.6, linewidth=1.8, edgecolor=color, facecolor="#26292e", zorder=1)
        ax.add_patch(panel)
        ax.text(cx + col_w/2, 17.8, title, ha="center", va="center", fontsize=11, fontweight="bold", color=color, zorder=2)
        ax.text(cx + col_w/2, 17.4, sub, ha="center", va="center", fontsize=7.8, color="#cbd5e1", zorder=2)
        
    mw = 5.2
    
    # ---------------- CHAPTER 1 COLUMN (EXACT MATCHING GROUND TRUTH) ----------------
    c1_x = cols_x[0] + 0.3
    c1_items = [
        ("1. Prologue -> 2. Gone Fishing", "Grab $140 Mailbox | Splits to 3 Branches", "normal", 16.2),
        ("BRANCH A: Unwanted Attention -> Pipework", "Grab $200 Mailbox | Clear in Downtime", "normal", 14.8),
        ("BRANCH B: Gear Up -> Just a Scratch", "MANDATORY: Joey will block later if skipped!", "heart", 13.4),
        ("BRANCH C: Lab Fees -> Hey Arnold! -> Feng Shui", "Grab $600 Mailbox | 24h Cooldown Trigger", "normal", 12.0),
        ("SKIP: Haircut / Gifts / Lost Drugs / Clock Out", "Bypass all non-essential activities (Saves ~8m)", "badge", 10.6),
        ("Coming Home -> Find Donnie's Package", "Reunite Lucia -> Hamlet package pickup", "normal", 9.2),
        ("DIAMOND 1: Is Just a Scratch Done?", "Joey reminder call triggers if ignored", "badge", 7.8),
        ("Buck Me -> Down to Earth -> Clear Skies", "Setup banking app -> Grab $600 Mailbox", "normal", 6.4),
        ("Day Release -> DIAMOND 2 GATE", "Requires both Day Release & Just a Scratch", "normal", 5.0),
        ("Swamped -> Doin' Gone (Ch. 1 Climax)", "Clear Donnie's trailer -> Ready for PG cut", "climax", 3.4),
        ("TRANSITION TO PORT GELLHORN", "Hard cut to Starlet Motel (Chapter 2)", "badge", 1.8),
    ]
    for t, s, ct, cy in c1_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c1_x, cy, mw, 1.15, t, s, font_size=7.2)
        elif ct == "heart":
            draw_heart(ax, c1_x, cy, mw, 1.15, t + "\n" + s, skip_label="[CRITICAL GATE]")
        else:
            draw_mission(ax, c1_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c1_x + mw, 1.8 + 0.55), (cols_x[1] + 0.3, 16.5), color="#f43f5e", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 2 COLUMN ----------------
    c2_x = cols_x[1] + 0.3
    c2_items = [
        ("23. What's in the Bag? -> 26. Just Moved In", "Starlet Motel Setup & Lucia Solo Recovery", "normal", 16.2),
        ("28. Moses (Vehicle Fencing)", "Register required getaway car with Moses", "normal", 14.8),
        ("29-37. Port Gellhorn Hustle", "Beeline through debt tasks (Ambulance/Daily Driver)", "normal", 13.4),
        ("38. COFFEE BREAK", "★ DUAL CHARACTER SWITCHING UNLOCKED ★\nEnables Fast Character Warping!", "badge", 11.6),
        ("39. Hit Avery Pawn", "Store Robbery System Active", "normal", 10.0),
        ("SKIP: Hit Kingpin Bowling", "Bypass secondary non-essential robberies", "badge", 8.6),
        ("40-42. Kelly County Operations", "Impounded Vehicle recovery & Afternoon Delight", "normal", 7.2),
        ("43. Prepare for Vice City", "Packing & Asset Liquidation", "normal", 5.8),
        ("44. CHECKING OUT", "Port Gellhorn Climax -> Move to VC Safehouse", "climax", 4.0),
        ("SPEEDRUN NOTE: CASH ROUTING", "Maintain $10,000+ for early VC equipment", "badge", 2.2),
    ]
    for t, s, ct, cy in c2_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c2_x, cy, mw, 1.3 if "SWITCHING" in t else 1.15, t, s, font_size=7.2)
        else:
            draw_mission(ax, c2_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c2_x + mw, 4.5), (cols_x[2] + 0.3, 16.5), color="#fbbf24", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 3 COLUMN (3 PARALLEL STRANDS + 3-TRACK PREP) ----------------
    c3_x = cols_x[2] + 0.3
    c3_items = [
        ("45. Welcome to VC -> 50. Real Estate", "Arrival & First VC Safehouse Unlocked", "normal", 16.2),
        ("STRAND 1: Tyrone Muscle (51-52)", "Here, Kitty Kitty & Street Muscle", "normal", 14.8),
        ("STRAND 2: Boobie & Dre (54-56)", "Nightclub / Port Everglades / Introductions", "normal", 13.5),
        ("STRAND 3: Raul & Randy (53,57-60)", "Car Service -> Zorrusso Supercar Boost", "normal", 12.2),
        ("3-WAY STRAND JUGGLING", "Cooldowns trigger alternating calls:\nZigzag Tyrone ↔ Boobie ↔ Raul (Zero idle time).", "badge", 10.4),
        ("61. Sinfrontera Bank Scope Out", "All 3 Strands Converge Into Heist Board!", "normal", 8.9),
        ("3 PARALLEL PREP TRACKS (62-69)", "Track 1: Safecracker (62,65,68)\nTrack 2: Explosives (63,66,69) | Track 3: Codes (64,67)", "badge", 7.1),
        ("PREP SKIP: Hidden Charges", "BLOW 2 CELL TOWERS ONLY (Saves ~3m in Any%)", "badge", 5.4),
        ("70. THE CARTEL HEIST", "Sinfrontera Vault Score ($10.5M Take)", "climax", 4.0),
        ("BANK $75,000 FOR ABE IMMEDIATELY", "CRITICAL: Do not spend the heist cut!\n$75k needed for Chapter 4 gate.", "badge", 2.2),
    ]
    for t, s, ct, cy in c3_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c3_x, cy, mw, 1.5 if "TRACKS" in t else (1.3 if "BANK" in t else 1.15), t, s, font_size=7.2)
        else:
            draw_mission(ax, c3_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c3_x + mw, 4.5), (cols_x[3] + 0.3, 16.5), color="#a855f7", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 4 COLUMN ----------------
    c4_x = cols_x[3] + 0.3
    c4_items = [
        ("71. Ocean Beach (Y Hotel Safehouse)", "Establish South Beach Headquarters", "normal", 16.2),
        ("74. Lawyer Up -> 75. PARTY HARD", "INSTANT WIRE: Send $75,000 via BuckMe\nNo grinding needed if Ch. 3 cut was kept!", "badge", 14.5),
        ("76-82. Syndicate & Corporate Ops", "Heavy Lifting, Making Gainz, Dirty Work", "normal", 12.8),
        ("83. Too Much Baggage -> 84. Babysitting", "Airport Recon -> Celebrity VIP Escort", "normal", 11.4),
        ("85-88. Dre'Quan Storyline", "Fresh Evidence -> Power Play -> Headliners", "normal", 10.0),
        ("89-91. VCIA Perimeter Recon", "Close Surveillance -> Delivery -> Team Building", "normal", 8.6),
        ("92. Fully Catered", "Infiltrate Airport via Catering Van Vector", "normal", 7.2),
        ("93. VCIA TAKEDOWN", "Major Airport Cargo Heist", "climax", 5.8),
        ("94. SUNSET (POINT OF NO RETURN)", "Locks open-world roaming and saves!", "badge", 4.2),
        ("95. Starting From Zero", "Chapter 4 Climax / Evacuation Sequence", "climax", 2.6),
    ]
    for t, s, ct, cy in c4_items:
        if ct == "badge":
            draw_speedrun_badge(ax, c4_x, cy, mw, 1.3 if "INSTANT" in t else 1.15, t, s, font_size=7.2)
        else:
            draw_mission(ax, c4_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    draw_arrow(ax, (c4_x + mw, 3.1), (cols_x[4] + 0.3, 16.5), color="#ef4444", rad=-0.3, lw=2.0)
    
    # ---------------- CHAPTER 5 COLUMN (ENDING A vs B CLARIFICATION) ----------------
    c5_x = cols_x[4] + 0.3
    c5_items = [
        ("96. Top of the World -> 98. Scorched Earth", "Federal Raid Defense & Cartel Standoff", "normal", 16.2),
        ("99. Two Hundred Percent", "Joint Assault on Mendez Compound", "normal", 14.8),
        ("100. FINAL DECISION STANDOFF", "Choose Loyalty (Ending A) or Immunity (Ending B)", "badge", 13.0),
        ("★ ENDING B: THE DEAL (ANY% ROUTE) ★", "Accept Mendez Deal -> Skip Boat Chase!\nSAVES 8-12 MINUTES OVER ENDING A!", "badge", 10.8),
        ("Ending A: Bonnie & Clyde", "Loyalty Choice: Fight through Coast Guard.\nAwards $2,000,000 Payout (NOT a requirement!)", "normal", 8.8),
        ("Ending C: The Sacrifice", "Partner Betrayal -> Solo Escort", "normal", 7.4),
        ("101. Final Evacuation", "Airstrip extraction or border run", "climax", 6.0),
        ("102. Epilogue & Credits", "Credits Roll -> Final IGT Split Time!", "badge", 4.2),
        ("TARGET ANY% TIME: ~10h 45m", "Assuming optimal dialogue skips and routing", "badge", 2.2),
    ]
    for t, s, ct, cy in c5_items:
        if "ANY% ROUTE" in t:
            draw_speedrun_badge(ax, c5_x, cy, mw, 1.6, t, s, font_size=7.2)
        elif ct == "badge":
            draw_speedrun_badge(ax, c5_x, cy, mw, 1.3 if "TARGET" in t else 1.15, t, s, font_size=7.2)
        else:
            draw_mission(ax, c5_x, cy, mw, 1.15, t, s, is_climax=(ct=="climax"))
            
    # Save artifacts
    out_artifact = os.path.join(ARTIFACT_DIR, "GTAVI_SPEEDRUN_CAMPAIGN_MASTER.png")
    out_workspace = os.path.join(WORKSPACE_DIR, "GTAVI_SPEEDRUN_CAMPAIGN_MASTER.png")
    out_downloads = os.path.join(DOWNLOADS_DIR, "GTAVI_SPEEDRUN_CAMPAIGN_MASTER.png")
    
    plt.savefig(out_artifact, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    
    shutil.copyfile(out_artifact, out_workspace)
    shutil.copyfile(out_artifact, out_downloads)
    print("Saved Campaign Master speedrun chart to:", out_artifact)

if __name__ == "__main__":
    render_speedrun_chapter_1()
    render_speedrun_master_campaign()
