#!/usr/bin/env python3
"""Draw the v3 front page for Friday 20 November 2026.

Renders entry.png (1024x1024) with Pillow from the Lexend variable font
shipped in fonts/.  All story text lives in the tables below; every fact
was checked against Reuters / AP / WSJ / The Hindu / IMD reporting of
20 November 2026 (see the research notes in the repo README).
Run:  python3 draw.py   ->  writes entry.png and entry-300.png
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "Lexend-Variable.ttf")
OUT = os.path.join(HERE, "entry.png")
THUMB = os.path.join(HERE, "entry-300.png")
W, H = 1024, 1024

PAPER = (246, 241, 229)
INK = (25, 25, 25)
RED = (158, 27, 27)
NAVY = (20, 50, 78)
TEAL = (15, 91, 77)
GOLD = (176, 124, 22)
GREY = (107, 107, 96)
LINE = (201, 191, 165)
CREAM = (232, 220, 188)
SKY = (126, 178, 214)
SEA = (38, 96, 122)

_fonts = {}


def font(size, weight=400):
    key = (size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(FONT_PATH, size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        _fonts[key] = f
    return _fonts[key]


def wrap(text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, width, max_lines):
    """Wrap and clip to max_lines, adding an ellipsis when clipped."""
    lines = wrap(text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and fnt.getlength(lines[-1] + " ...") > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + " ..."
    return lines


def text_block(d, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def rule(d, x, y, w, fill=INK, width=2):
    d.line([(x, y), (x + w, y)], fill=fill, width=width)


# ---------------------------------------------------------------- data
# (number, place, beat, headline, deck, source, kind)
HEROES = [
    (1, "ODISHA", "STORM",
     "Akvan comes ashore in India",
     "Crosses the coast near Gopalpur on Friday morning; winds 70-80 "
     "km/h, gusting to 90.",
     "IMD / The Hindu", "cyclone"),
    (2, "ANTALYA", "CLIMATE",
     "COP31 reaches its final day",
     "Draft cut to 80 paragraphs, fossil-fuel mentions gone; the $120bn "
     "adaptation target is dropped.",
     "AP", "climate"),
    (3, "NEW YORK", "MARKETS",
     "Anthropic ends first day up 17%",
     "Opens at $111.50, closes at $97.17 on an $83 offer; raises $81.3bn, "
     "a record IPO.",
     "WSJ / Reuters", "ipo"),
]

CARDS = [
    (4, "KYIV", "WAR",
     "Missiles strike Kyiv overnight",
     "Overnight ballistic attack; fires, explosions, three bridges hit.",
     "Reuters", "kyiv"),
    (5, "BERLIN", "EUROPE",
     "Europe answers with its own summit",
     "Berlin backs binding security guarantees for Kyiv; presses for an "
     "energy truce.",
     "Reuters", "berlin"),
    (6, "WASHINGTON", "POLITICS",
     "Senate rejects Iran war-powers bid",
     "The measure fails 48-51, with three Republicans voting in favour.",
     "Reuters", "senate"),
    (7, "CALIFORNIA", "TECH",
     "California subpoenas Nvidia",
     "AG asks if advanced chips or secrets reached China; Huang testifies "
     "1 Dec.",
     "CA Attorney General", "nvidia"),
    (8, "WELLINGTON", "SPORT",
     "Nicholls 175* carries New Zealand to 368",
     "Phillips makes 118 in a 216-run stand; India reach 16/0 at tea.",
     "Reuters", "cricket"),
    (9, "TONGA", "PACIFIC",
     "Tonga declares drought emergency",
     "A 28-day state of emergency; schools shut on Friday as drought bites.",
     "PINA", "tonga"),
    (10, "WORLD", "GAMES",
     "GTA VI's first full day on sale",
     "Metacritic 99, joint-highest ever; Sensor Tower estimates 19m "
     "copies and $1.84bn.",
     "Sensor Tower", "gta"),
    (11, "THE GULF", "ENERGY",
     "Tanker attacks mount in Hormuz",
     "Four attacks on tankers in 96 hours; the maritime centre calls "
     "the threat severe.",
     "JMIC", "hormuz"),
    (12, "GAZA", "MIDDLE EAST",
     "Gaza truce under strain",
     "The Board of Peace reports to the UN Security Council; the "
     "ceasefire risks collapse.",
     "AP", "gaza"),
    (13, "COPENHAGEN", "EUROPE",
     "Denmark backs Greenland pact",
     "The Folketing ratifies the Greenland defence pact, 109-0.",
     "Al Jazeera", "denmark"),
]

# (number, place, text) -- kept short on purpose: one line each at 11pt
BRIEFS = [
    (14, "ODISHA", "69 trains cancelled."),
    (15, "ODISHA", "1,012 emergency teams, 60 ODRAF."),
    (16, "ODISHA", "9,341 shelters hold evacuees."),
    (17, "ANTALYA", "Draft cut from 144 to 80 paragraphs."),
    (18, "ANTALYA", "$120bn adaptation target dropped."),
    (19, "NEW YORK", "Anthropic opens $111.50; high $115."),
    (20, "NEW YORK", "S&P 500 -2.02%, sixth straight fall."),
    (21, "NEW YORK", "Dow closes 49,097, below 50,000."),
    (22, "NEW YORK", "Filing lists $895bn in commitments."),
    (23, "WASHINGTON", "Collins, Murkowski, Paul back the bid."),
    (24, "KYIV", "Kushner: Russia open to NATO guarantees."),
    (25, "KYIV", "Putin rules out energy or sea truce."),
    (26, "SENEGAL", "Navy rescues 1,400+ in 48 hours."),
    (27, "CANARY IS.", "24,364 arrivals, up two-thirds."),
    (28, "SENEGAL", "Four bodies found after capsize."),
    (29, "GAZA", "1,600+ killed since the ceasefire."),
    (30, "HORMUZ", "Fourteen attacks in November."),
    (31, "HORMUZ", "227 ships wait east of the strait."),
    (32, "CALIFORNIA", "Huang testifies before Congress 1 Dec."),
    (33, "WORLD", "One in five US workers plan GTA time off."),
    (34, "WORLD", "GTA VI at 30fps; no PC version yet."),
    (35, "WORLD", "UN marks World Children's Day."),
    (36, "TONGA", "TOP$1.8m for farmers; El Nino to June."),
]

STATS = [
    ("300,000+", "evacuated ahead of Akvan"),
    ("$97.17", "Anthropic first close, +17%"),
    ("-1,101", "Dow falls to 49,097"),
    ("175*", "Nicholls not out"),
    ("48-51", "Senate rejects Iran bid"),
    ("99", "GTA VI Metacritic score"),
]

REGIONS = [
    ("EUROPE", 9, (31, 78, 121)),
    ("THE AMERICAS", 11, RED),
    ("ASIA-PACIFIC", 4, TEAL),
    ("MIDEAST", 5, (122, 74, 18)),
    ("AFRICA", 2, (91, 122, 31)),
    ("OCEANIA", 3, (47, 111, 143)),
    ("WORLD", 2, (85, 85, 85)),
]

DATE_CHECK = (
    "First reported before Friday 20 November, so NOT on this page as "
    "today's news: the Trump-Xi-Putin trilateral and 'peace declaration' "
    "in Shenzhen \u00b7 the World Court's Myanmar genocide ruling \u00b7 the "
    "daytime drone attack on Kyiv \u00b7 the EU's proposed \u20ac45bn loan "
    "for Ukraine \u00b7 the record Van Gogh sale \u00b7 the third strike on "
    "the Crimean Bridge \u00b7 Voyager 1 crossing one light-day."
)

# lat, lon, number, nudge (dx, dy) for the map dots
DOTS = [
    (19.3, 84.9, 1, 0, 0), (36.9, 30.7, 2, 24, 22),
    (40.7, -74.0, 3, 0, 0), (50.4, 30.5, 4, 30, -18),
    (52.5, 13.4, 5, -26, -14), (38.9, -77.0, 6, 0, 10),
    (37.4, -122.0, 7, 0, 0), (-41.3, 174.8, 8, 0, 0),
    (-21.1, -175.2, 9, 0, 0), (25.8, -80.2, 10, 10, 8),
    (26.5, 56.3, 11, 0, 0), (31.5, 34.5, 12, -16, 24),
    (55.7, 12.6, 13, 26, -26),
]


# ---------------------------------------------------------------- art
def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx, cy = x + w * 0.38, y + h * 0.52
    for r in (52, 40, 28, 16):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(240, 244, 248), width=3)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(250, 226, 150))
    for i in range(5):
        rx = x + w * 0.78 + i * 3
        d.line([(rx, y + 8 + i * 4), (rx - 8, y + 26 + i * 4)], fill=SKY, width=2)
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(10, 28, 48))
    d.text((x + 10, y + h - 18), "LANDFALL: FRIDAY MORNING", font=font(11, 700), fill=(255, 255, 255))


def art_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w - 62, y + 10, x + w - 22, y + 50], fill=(250, 178, 60))
    d.polygon([(x, y + h), (x, y + h - 26), (x + w * 0.45, y + h - 44),
               (x + w * 0.7, y + h - 18), (x + w, y + h - 30), (x + w, y + h)],
              fill=(46, 125, 62))
    d.polygon([(x, y + h), (x, y + h - 12), (x + w * 0.5, y + h - 26),
               (x + w, y + h - 8), (x + w, y + h)], fill=(28, 92, 46))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(20, 60, 40))
    d.text((x + 10, y + h - 18), "ANTALYA  \u00b7  9-20 NOV", font=font(11, 700), fill=(255, 255, 255))


def art_ipo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 58, 40))
    base = y + h - 14
    bars = [(18, 26, 1), (34, 20, 0), (50, 30, 1), (66, 16, 0),
            (82, 24, 1), (98, 14, 0), (114, 28, 1)]
    for bx, bh, up in bars:
        col = (74, 222, 128) if up else (248, 113, 113)
        d.rectangle([x + bx, base - bh, x + bx + 9, base], fill=col)
        d.line([(x + bx + 4, base - bh - 6), (x + bx + 4, base + 4)], fill=col, width=2)
    d.text((x + w - 118, y + 8), "$97.17", font=font(26, 700), fill=(250, 200, 80))
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(8, 36, 26))
    d.text((x + 10, y + h - 18), "NASDAQ  \u00b7  FIRST CLOSE  +17%", font=font(11, 700), fill=(255, 255, 255))


def art_small(d, x, y, w, h, kind):
    if kind == "kyiv":
        d.rectangle([x, y, x + w, y + h], fill=(52, 62, 78))
        for i, bh in enumerate((26, 34, 22)):
            d.rectangle([x + 14 + i * 20, y + h - bh, x + 28 + i * 20, y + h], fill=(140, 148, 165))
        d.ellipse([x + w - 42, y + 6, x + w - 14, y + 34], fill=(250, 160, 40))
        d.line([(x + w - 28, y + 20), (x + w - 52, y + 8)], fill=(250, 200, 90), width=3)
        d.line([(x + w - 28, y + 20), (x + w - 54, y + 30)], fill=(250, 200, 90), width=3)
    elif kind == "berlin":
        d.rectangle([x, y, x + w, y + h], fill=(228, 220, 200))
        d.rectangle([x + 18, y + 12, x + w - 18, y + 18], fill=(90, 80, 70))
        for i in range(5):
            d.rectangle([x + 22 + i * 26, y + 18, x + 28 + i * 26, y + h - 8], fill=(120, 110, 98))
        for i, c in enumerate(((0, 0, 0), (221, 0, 0), (255, 206, 0))):
            d.rectangle([x + w - 34, y + 8 + i * 7, x + w - 12, y + 14 + i * 7], fill=c)
    elif kind == "senate":
        d.rectangle([x, y, x + w, y + h], fill=NAVY)
        d.pieslice([x + w // 2 - 26, y + 2, x + w // 2 + 26, y + 34], 180, 360, fill=(240, 240, 235))
        d.rectangle([x + 16, y + h - 14, x + w - 16, y + h - 8], fill=(240, 240, 235))
        for i in range(4):
            d.rectangle([x + 24 + i * 30, y + h - 26, x + 30 + i * 30, y + h - 14], fill=(200, 205, 215))
    elif kind == "nvidia":
        d.rectangle([x, y, x + w, y + h], fill=(16, 40, 26))
        d.rectangle([x + w // 2 - 20, y + 8, x + w // 2 + 20, y + h - 10], fill=(34, 197, 94))
        d.rectangle([x + w // 2 - 11, y + 17, x + w // 2 + 11, y + h - 19], fill=(16, 40, 26))
        for i in range(4):
            d.line([(x + w // 2 - 20 + i * 13, y + 2), (x + w // 2 - 20 + i * 13, y + 8)], fill=(34, 197, 94), width=3)
            d.line([(x + w // 2 - 20 + i * 13, y + h - 10), (x + w // 2 - 20 + i * 13, y + h - 4)], fill=(34, 197, 94), width=3)
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(46, 125, 62))
        d.rectangle([x + w // 2 - 8, y, x + w // 2 + 8, y + h], fill=(232, 220, 188))
        d.ellipse([x + w - 30, y + h - 24, x + w - 16, y + h - 10], fill=(200, 40, 40))
        d.line([(x + 16, y + 12), (x + 44, y + h - 14)], fill=(232, 220, 188), width=4)
    elif kind == "tonga":
        d.rectangle([x, y, x + w, y + h], fill=(240, 214, 150))
        d.ellipse([x + w - 44, y + 6, x + w - 12, y + 38], fill=(250, 178, 60))
        for i in range(3):
            d.line([(x + 10, y + h - 10 - i * 8), (x + w - 10, y + h - 14 - i * 8)], fill=(176, 124, 22), width=2)
    elif kind == "gta":
        for i, c in enumerate(((124, 58, 160), (220, 90, 120), (250, 160, 60), (250, 210, 110))):
            d.rectangle([x, y + i * h // 4, x + w, y + (i + 1) * h // 4], fill=c)
        d.ellipse([x + w // 2 - 14, y + h // 2 - 14, x + w // 2 + 14, y + h // 2 + 14], fill=(255, 240, 180))
        d.text((x + 8, y + h - 22), "VI", font=font(20, 700), fill=(255, 255, 255))
    elif kind == "hormuz":
        d.rectangle([x, y, x + w, y + h], fill=SEA)
        d.rectangle([x + 14, y + 14, x + w - 14, y + 28], fill=(40, 40, 40))
        d.polygon([(x + 14, y + 28), (x + w - 14, y + 28), (x + w - 26, y + 40), (x + 26, y + 40)], fill=(25, 25, 25))
        for i in range(3):
            d.arc([x + 10 + i * 8, y + h - 16, x + 40 + i * 8, y + h - 2], 0, 180, fill=(255, 255, 255), width=2)
    elif kind == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(178, 205, 228))
        d.rectangle([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + h - 8], fill=(255, 255, 255))
        for i in range(3):
            d.line([(x + w // 2 - 18, y + 16 + i * 10), (x + w // 2 + 18, y + 16 + i * 10)], fill=(90, 130, 180), width=2)
    elif kind == "denmark":
        d.rectangle([x, y, x + w, y + h], fill=(200, 16, 46))
        d.rectangle([x + w // 2 - 7, y, x + w // 2 + 7, y + h], fill=(255, 255, 255))
        d.rectangle([x, y + h // 2 - 7, x + w, y + h // 2 + 7], fill=(255, 255, 255))


ART = {"cyclone": art_cyclone, "climate": art_climate, "ipo": art_ipo}


# ---------------------------------------------------------------- page
def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 28
    cw = W - 2 * mx

    # kicker row
    d.text((mx, 14), "T H E   W O R L D   I N   O N E   D A Y", font=font(13, 700), fill=RED)
    right = "FRIDAY'S NEWS  \u00b7  ONE PAGE  \u00b7  36 STORIES"
    d.text((W - mx - font(12, 700).getlength(right), 15), right, font=font(12, 700), fill=INK)
    rule(d, mx, 36, cw, width=2)

    # giant date headline
    d.text((mx, 44), "Friday 20 November 2026", font=font(60, 700), fill=INK)
    d.text((mx, 112), "A cyclone comes ashore in India  \u00b7  Climate talks reach their final day  \u00b7  A record IPO's first close",
           font=font(16, 500), fill=RED)
    rule(d, mx, 140, cw, width=1)

    # stat strip: one short label line each, no wrap into the strip below
    y = 148
    colw = cw // 6
    for i, (num, label) in enumerate(STATS):
        x = mx + i * colw
        if i:
            d.line([(x - 7, y), (x - 7, y + 40)], fill=LINE, width=1)
        d.text((x, y), num, font=font(26, 700), fill=RED if i % 2 == 0 else INK)
        d.text((x, y + 31), label, font=font(11, 400), fill=GREY)
    rule(d, mx, 196, cw, width=1)

    # region strip
    y = 204
    x = mx
    for name, n, col in REGIONS:
        label = f"{name} {n}"
        fw = font(12, 700).getlength(label) + 16
        d.rectangle([x, y, x + fw, y + 20], fill=col)
        d.text((x + 8, y + 3), label, font=font(12, 700), fill=(255, 255, 255))
        x += fw + 6
    d.text((x + 2, y + 4), "36 stories, six continents", font=font(12, 400), fill=GREY)

    # heroes
    y0 = 232
    hh = 178
    hw = (cw - 2 * 12) // 3
    art_fn = {"cyclone": art_cyclone, "climate": art_climate, "ipo": art_ipo}
    for i, (num, place, beat, head, deck, src, kind) in enumerate(HEROES):
        x = mx + i * (hw + 12)
        d.rectangle([x, y0, x + hw, y0 + hh], outline=INK, width=1)
        art_fn[kind](d, x + 1, y0 + 1, hw - 2, 70)
        ty = y0 + 74
        d.text((x + 8, ty), f"{num}  \u00b7  {place}  \u00b7  {beat}", font=font(11, 700), fill=RED)
        ty += 15
        ty = text_block(d, x + 8, ty, fit_lines(head, font(21, 700), hw - 16, 2), font(21, 700), leading=22)
        ty = text_block(d, x + 8, ty + 2, fit_lines(deck, font(12, 400), hw - 16, 2), font(12, 400), fill=(60, 60, 60), leading=14)
        d.text((x + 8, y0 + hh - 13), f"Source: {src}", font=font(9, 400), fill=GREY)

    # small cards, two rows of five (no per-card source line: sources are
    # listed in the footer, which keeps the cards readable at 300px)
    y0 = 420
    ch = 138
    sw = (cw - 4 * 10) // 5
    for row in range(2):
        for col in range(5):
            idx = row * 5 + col
            num, place, beat, head, deck, src, kind = CARDS[idx]
            x = mx + col * (sw + 10)
            y = y0 + row * (ch + 10)
            d.rectangle([x, y, x + sw, y + ch], outline=INK, width=1)
            art_small(d, x + 1, y + 1, sw - 2, 42, kind)
            ty = y + 47
            d.text((x + 7, ty), f"{num}  \u00b7  {place}", font=font(10, 700), fill=RED)
            ty += 14
            ty = text_block(d, x + 7, ty, fit_lines(head, font(16, 700), sw - 14, 2), font(16, 700), leading=18)
            ty = text_block(d, x + 7, ty + 1, fit_lines(deck, font(11, 400), sw - 14, 3), font(11, 400), fill=(60, 60, 60), leading=13)

    # bottom: map + briefs
    y0 = 714
    d.text((mx, y0), "WHERE IT HAPPENED", font=font(14, 700), fill=RED)
    d.text((mx + 300, y0), "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES", font=font(14, 700), fill=RED)
    rule(d, mx, y0 + 20, cw, width=1)
    my = y0 + 26
    mh = 180
    mapw = 272
    d.rectangle([mx, my, mx + mapw, my + mh], fill=(24, 48, 74))
    # rough continents
    land = (232, 220, 188)
    d.polygon([(mx + 18, my + 52), (mx + 52, my + 34), (mx + 78, my + 40), (mx + 70, my + 66),
               (mx + 44, my + 78), (mx + 22, my + 70)], fill=land)  # N America
    d.polygon([(mx + 58, my + 96), (mx + 78, my + 92), (mx + 82, my + 118), (mx + 66, my + 140),
               (mx + 56, my + 118)], fill=land)  # S America
    d.polygon([(mx + 128, my + 44), (mx + 150, my + 40), (mx + 158, my + 56), (mx + 146, my + 72),
               (mx + 132, my + 66)], fill=land)  # Europe
    d.polygon([(mx + 138, my + 84), (mx + 162, my + 78), (mx + 172, my + 100), (mx + 158, my + 128),
               (mx + 142, my + 112)], fill=land)  # Africa
    d.polygon([(mx + 168, my + 40), (mx + 210, my + 30), (mx + 248, my + 42), (mx + 252, my + 66),
               (mx + 220, my + 84), (mx + 186, my + 76), (mx + 168, my + 58)], fill=land)  # Asia
    d.polygon([(mx + 226, my + 128), (mx + 250, my + 124), (mx + 254, my + 142), (mx + 232, my + 148),
               (mx + 222, my + 138)], fill=land)  # Australia
    for lat, lon, n, dx, dy in DOTS:
        px = mx + (lon + 180) / 360 * mapw + dx
        py = my + (90 - lat) / 180 * mh + dy
        px = max(mx + 10, min(mx + mapw - 10, px))
        py = max(my + 10, min(my + mh - 10, py))
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        t = str(n)
        d.text((px - font(9, 700).getlength(t) / 2, py - 6), t, font=font(9, 700), fill=(255, 255, 255))
    d.text((mx + 4, my + mh - 16), "Red numbers mark stories 1-13.", font=font(10, 400), fill=(220, 225, 235))

    # briefs, two columns
    bx = mx + 300
    bw = (cw - 300 - 12) // 2
    half = 12
    for ci in range(2):
        x = bx + ci * (bw + 12)
        yy = my
        for num, place, txt in BRIEFS[ci * half:(ci + 1) * half]:
            head_f, body_f = font(11, 700), font(11, 400)
            lead = f"{num} {place} \u2014 "
            lines = wrap(lead + txt, body_f, bw)
            # bold the lead part of the first line
            first = lines[0]
            d.text((x, yy), first[:len(lead)] if first.startswith(lead) else lead, font=head_f, fill=RED)
            rest_first = first[len(lead):] if first.startswith(lead) else first
            d.text((x + head_f.getlength(lead), yy), rest_first, font=body_f, fill=INK)
            yy += 14
            for ln in lines[1:]:
                d.text((x, yy), ln, font=body_f, fill=INK)
                yy += 14
    # date check
    y0 = 928
    d.rectangle([mx, y0, W - mx, y0 + 64], outline=RED, width=2)
    d.text((mx + 10, y0 + 6), "DATE CHECK", font=font(12, 700), fill=RED)
    dc_lines = fit_lines(DATE_CHECK, font(12, 400), cw - 20, 3)
    text_block(d, mx + 10, y0 + 21, dc_lines, font(12, 400), leading=13)
    # footer
    fy = 998
    d.text((mx, fy), "Every story here happened, or was first reported, on Friday 20 November 2026. Disputed claims are attributed, not stated as fact.",
           font=font(10, 400), fill=GREY)
    d.text((mx, fy + 12), "Sources: Reuters, AP, WSJ, BBC, The Hindu, IMD, Al Jazeera, Sensor Tower, Metacritic. Original drawings.",
           font=font(10, 400), fill=GREY)
    return img


def main():
    img = draw_page()
    img.save(OUT, format="PNG", optimize=True)
    img.resize((300, 300), Image.LANCZOS).save(THUMB, format="PNG", optimize=True)
    data = open(OUT, "rb").read()
    print(f"entry.png: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"size ok (<=1048576): {len(data) <= 1048576}")


if __name__ == "__main__":
    main()
