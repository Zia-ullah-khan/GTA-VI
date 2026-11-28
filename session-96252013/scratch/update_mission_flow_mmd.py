import shutil, os

new_c1 = '''    subgraph Chapter_1["Chapter 1: Just Like Paradise (Leonida Keys) — 21 Missions"]
        direction TB
        m_INT_PROLO["<b>Prologue</b><br/><code>INT_PROLO</code> • <i>Campaign Opening Prologue Gate</i>"]:::bottleneck
        m_INT_CHASE["<b>Gone Fishing</b><br/><code>INT_CHASE</code> • <i>Main Story Core (Boat Drop)</i>"]:::coreStory
        m_COM_KBOS_COLAT["<b>Unwanted Attention</b><br/><code>COM_KBOS_COLAT</code> • <i>Side Strand (Cal / $200 Mailbox) [ANY% SKIP]</i>"]:::sideStrand
        m_COM_KBOS_NEIGHB["<b>Pipework</b><br/><code>COM_KBOS_NEIGHB</code> • <i>Side Strand (Mandy Maintenance) [ANY% SKIP]</i>"]:::sideStrand
        m_FT_AMUCO["<b>Gear Up</b><br/><code>FT_AMUCO</code> • <i>Main Story Core (Longarm Pickup)</i>"]:::coreStory
        m_FT_KMODSHP["<b>Just a Scratch</b><br/><code>FT_KMODSHP</code> • <i>★ MANDATORY STORY GATE ★ (Ganado Repair)</i>"]:::bottleneck
        m_COM_KBOS_SHOP["<b>Lab Fees</b><br/><code>COM_KBOS_SHOP</code> • <i>Side Strand (Rent Collection) [ANY% SKIP]</i>"]:::sideStrand
        m_COM_KBOS_RADR["<b>Hey Arnold!</b><br/><code>COM_KBOS_RADR</code> • <i>Side Strand [08:00–16:00] [ANY% SKIP]</i>"]:::sideStrand
        m_CSC_TRH_CHART["<b>Island Dreams</b><br/><code>CSC_TRH_CHART</code> • <i>Side Strand (Kenton Diving) [ANY% SKIP]</i>"]:::sideStrand
        m_COM_SFH_MVFN["<b>Feng Shui</b><br/><code>COM_SFH_MVFN</code> • <i>Main Story Core (Furniture Move / 24h Wait)</i>"]:::coreStory
        m_INT_PRISO["<b>Coming Home</b><br/><code>INT_PRISO</code> • <i>Main Story Core (Lucia Prison Release)</i>"]:::coreStory
        m_CTI_PIL_RD_SH["<b>Find Donnie's Package</b><br/><code>CTI_PIL_RD_SH</code> • <i>Main Story Core (Swamp Drug Retrieval)</i>"]:::coreStory
        m_INT_BANK["<b>Buck Me</b><br/><code>INT_BANK</code> • <i>Mandatory Banking Setup Gate</i>"]:::bottleneck
        m_COM_KBOS_PLNDATE["<b>Down to Earth</b><br/><code>COM_KBOS_PLNDATE</code> • <i>Main Story Core (Seaplane Smuggling)</i>"]:::coreStory
        m_INT_PLNSH["<b>Clear Skies</b><br/><code>INT_PLNSH</code> • <i>Main Story Core [07:00–23:00] (Southwind Bikers)</i>"]:::coreStory
        m_BIL_FUN["<b>Day Release</b><br/><code>BIL_FUN</code> • <i>Main Story Core [07:00–17:00] (Rusty Anchor & Club)</i>"]:::coreStory
        m_INT_AIR["<b>Swamped</b><br/><code>INT_AIR</code> • <i>Main Story Core (Kingfishers Ambush / Donnie Killed)</i>"]:::coreStory
        m_COM_KBOS_CLEAN["<b>Don Gone</b><br/><code>COM_KBOS_CLEAN</code> • <i>Side Strand (Donnie Trailer Evidence) [ANY% SKIP]</i>"]:::sideStrand
        m_HO_PAR_KEYCO["<b>Recalibration</b><br/><code>HO_PAR_KEYCO</code> • <i>Side Strand (Cal Grief Fishing) [ANY% SKIP]</i>"]:::sideStrand
        m_BIL_PICK["<b>Tourist Trap</b><br/><code>BIL_PICK</code> • <i>Main Story Core [10:00–17:00 / 17:00–10:00] (Locker Ambush)</i>"]:::coreStory
        m_BIL_HOUSE["<b>Home Sweet Home</b><br/><code>BIL_HOUSE</code> • <i>Main Story Core (Lucia Solo / House Torched)</i>"]:::coreStory
        m_BIL_WHEEL["<b>Discharge Time</b><br/><code>BIL_WHEEL</code> • <i>★ CHAPTER 1 FINALE CLIMAX ★ (Hospital Shootout Escape)</i>"]:::bottleneck
    end'''

path = r'C:\Users\<user>\Downloads\antigravity_version\mission_flow.mmd'
content = open(path, 'r', encoding='utf-8').read()
idx1 = content.find('    subgraph Chapter_1[')
idx2 = content.find('    subgraph Chapter_2[')
new_content = content[:idx1] + new_c1 + '\n\n' + content[idx2:]
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Updated mission_flow.mmd')

dsts = [
    r'C:\Users\<user>\Downloads\GTA6.Xbox.v1.0.2.1-CYBERLEEK\output\antigravity_version\mission_flow.mmd',
    r'C:\Users\<user>\Downloads\mission_flow_antigravity.mmd'
]
for d in dsts:
    os.makedirs(os.path.dirname(d), exist_ok=True)
    shutil.copyfile(path, d)
    print('Copied to', d)
