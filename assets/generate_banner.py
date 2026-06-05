#!/usr/bin/env python3
"""Generate assets/feeding-the-robots.gif — retro pixel banner for the README.

Hand-placed pixel art, 320x96 native, upscaled 3x nearest-neighbor with
scanlines. 120-frame seamless loop: every animated element runs on a period
that divides 120 (belt treads 12px @2px/f, items spawn every 30f, chomp
cycle 30f, LED blink buckets of 6, star twinkle 24f, antenna 15f, drip 40f,
steam vent 60f, shooting star 1x/loop).

Four food types ride the belt — SKILL.md doc, floppy disk, cartridge,
coffee mug — and the robot reacts to each differently.
"""
import math
from PIL import Image, ImageDraw

W, H = 320, 96
SCALE = 3
FRAMES = 120
DURATION = 80  # ms/frame -> 9.6s loop

# ---- CRT terminal palette ----
BG_TOP   = (6, 8, 7)
BG_BOT   = (15, 21, 16)
GREEN_D  = (22, 56, 33)
GREEN_M  = (52, 130, 74)
GREEN_B  = (104, 228, 134)
GREEN_X  = (188, 255, 206)
AMBER    = (255, 178, 44)
AMBER_D  = (148, 96, 26)
RED      = (228, 84, 58)
METAL_D  = (30, 38, 35)
METAL_M  = (55, 68, 62)
METAL_L  = (88, 106, 98)
PAPER    = (198, 240, 208)
DARK     = (10, 14, 11)
RACK_BG  = (16, 22, 18)
SLATE    = (62, 86, 108)
SLATE_D  = (40, 58, 76)
SLATE_L  = (110, 140, 170)
COFFEE   = (140, 80, 30)
HAZ_A    = (96, 64, 18)
HAZ_B    = (26, 22, 12)

# ---- timing ----
SPEED = 2            # belt px/frame
SPAWN_EVERY = 30     # one item every chomp cycle
HOP_FRAMES = 12
BELT_END_X = 224     # item x where it leaves the belt
MOUTH = (276, 46)
LAND_MOD = 11        # land when t % 30 == 11
KINDS = 4            # doc, floppy, cartridge, mug


def h32(*args):
    """Deterministic hash -> stable pseudo-random 0..1 per coordinate."""
    x = 2166136261
    for v in args:
        x = ((x ^ (int(v) & 0xffffffff)) * 16777619) & 0xffffffff
    return (x % 1024) / 1024.0


def chomp_phase(t):
    """0 at the moment an item lands in the mouth, wraps every 30."""
    return (t - LAND_MOD) % 30


def swallow_kind(t):
    """Which item kind was most recently swallowed."""
    return ((t - LAND_MOD) // 30) % KINDS


# ---- tiny 3x5 font (variable width) ----
FONT = {
    'S': ["###", "#..", "###", "..#", "###"],
    'K': ["#.#", "#.#", "##.", "#.#", "#.#"],
    'I': ["###", ".#.", ".#.", ".#.", "###"],
    'L': ["#..", "#..", "#..", "#..", "###"],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
    'T': ["###", ".#.", ".#.", ".#.", ".#."],
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'E': ["###", "#..", "##.", "#..", "###"],
    '1': [".#.", "##.", ".#.", ".#.", "###"],
    '+': ["...", ".#.", "###", ".#.", "..."],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
    'C': ["###", "#..", "#..", "#..", "###"],
    'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'F': ["###", "#..", "##.", "#..", "#.."],
    'G': ["###", "#..", "#.#", "#.#", "###"],
    'O': ["###", "#.#", "#.#", "#.#", "###"],
    '/': ["..#", "..#", ".#.", "#..", "#.."],
    ' ': ["..", "..", "..", "..", ".."],
}


def text_width(s):
    return sum(len(FONT[ch][0]) for ch in s) + (len(s) - 1)


def draw_text(d, x, y, s, color):
    cx = x
    for ch in s:
        glyph = FONT[ch]
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c == '#':
                    d.point((cx + gx, y + gy), fill=color)
        cx += len(glyph[0]) + 1


# ====================================================================
# background
# ====================================================================
STARS = [
    (14, 6, 0), (38, 12, 5), (61, 4, 9), (88, 9, 13), (107, 15, 2),
    (131, 5, 7), (158, 11, 11), (183, 7, 4), (207, 14, 16), (236, 5, 8),
    (259, 10, 1), (282, 16, 12), (303, 6, 6), (47, 19, 15), (172, 19, 3),
    (227, 20, 10), (312, 18, 14), (25, 16, 7), (74, 14, 19), (120, 9, 21),
    (148, 16, 1), (197, 11, 18), (250, 17, 4), (270, 5, 23), (295, 13, 9),
]
# slow dust motes hanging in the air (fade in/out, period 24)
MOTES = [
    (70, 36, 2), (150, 32, 9), (235, 40, 15), (310, 34, 5),
    (40, 50, 20), (200, 46, 12), (314, 58, 7), (243, 60, 18),
]


def draw_background(d, t):
    for y in range(H):
        f = y / (H - 1)
        c = tuple(int(a + (b - a) * f) for a, b in zip(BG_TOP, BG_BOT))
        d.line([(0, y), (W - 1, y)], fill=c)
    # twinkling stars
    for sx, sy, ph in STARS:
        k = (t + ph * 3) % 24
        if k < 8:
            col = GREEN_D
        elif k < 16:
            col = GREEN_M
        else:
            col = GREEN_B
        d.point((sx, sy), fill=col)
        if 16 <= k < 20:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                d.point((sx + dx, sy + dy), fill=GREEN_D)
    # shooting star, once per loop
    if 70 <= t < 82:
        a = t - 70
        hx, hy = 30 + a * 8, 5 + a
        for tr in range(4):
            col = (GREEN_X, GREEN_B, GREEN_M, GREEN_D)[tr]
            d.point((hx - tr * 3, hy - tr // 2), fill=col)
    # dust motes
    for mx, my, ph in MOTES:
        k = (t + ph) % 24
        if k < 12:
            d.point((mx, my), fill=GREEN_D if k < 4 or k > 8 else (38, 70, 48))


def draw_wall(d, t):
    # panel seams behind the racks
    d.line([(0, 50), (W - 1, 50)], fill=(17, 23, 18))
    for sx in (61, 114, 171, 232):
        d.line([(sx, 26), (sx, 70)], fill=(17, 23, 18))
    # hazard stripe wall base (peeks through gaps under the belt),
    # chipped and scuffed in places
    for x in range(0, 240):
        for y in range(83, 88):
            if h32(x * 7, y * 3) < 0.05:  # chipped paint
                continue
            col = HAZ_A if ((x - y) // 3) % 3 == 0 else HAZ_B
            if h32(x, y, 9) < 0.04:  # scuff
                col = (col[0] // 2, col[1] // 2, col[2] // 2)
            d.point((x, y), fill=col)
    # steam vent on the left wall
    d.rectangle([0, 56, 5, 64], fill=METAL_D, outline=METAL_M)
    for vy in range(58, 64, 2):
        d.line([(1, vy), (4, vy)], fill=DARK)
    a = t % 60
    if a < 16:  # hisss
        for pi, (off, lift) in enumerate(((0, 0), (3, 2), (6, 1))):
            px = 7 + a + off
            py = 58 - a // 3 - lift
            if px < 60:
                col = METAL_L if a < 8 else METAL_M
                d.point((px, py), fill=col)


# uneven brackets: (x, width, shade 0=dark 1=normal 2=light, rusty, missing_bolt)
BRACKETS = [
    (16, 2, 1, False, False), (50, 3, 2, False, False), (88, 2, 1, False, True),
    (127, 3, 0, True, False), (163, 2, 1, False, False), (199, 3, 1, False, False),
    (240, 2, 0, False, False), (278, 3, 2, True, False), (306, 2, 1, False, False),
]


def draw_pipes(d, t):
    # twin ceiling pipes
    d.rectangle([0, 0, W - 1, 2], fill=METAL_M)
    d.line([(0, 2), (W - 1, 2)], fill=METAL_D)
    d.line([(0, 0), (W - 1, 0)], fill=METAL_L)
    d.rectangle([0, 5, W - 1, 6], fill=METAL_D)
    d.line([(0, 5), (W - 1, 5)], fill=METAL_M)
    # weld patches + a dent
    for wx0, wx1 in ((73, 76), (218, 222), (292, 294)):
        d.rectangle([wx0, 0, wx1, 2], fill=METAL_L)
        d.point((wx0, 1), fill=METAL_D)
    d.point((142, 1), fill=METAL_D)  # dent
    d.line([(101, 5), (103, 5)], fill=(70, 84, 78))  # discolored segment
    # brackets, no two quite alike
    for bx, bw, shade, rusty, missing in BRACKETS:
        col = (METAL_D, METAL_L, (110, 130, 120))[shade] if shade != 1 else METAL_L
        d.rectangle([bx, 0, bx + bw, 7], fill=col)
        if not missing:
            d.point((bx + bw // 2, 3), fill=METAL_D)
        if rusty:
            d.point((bx + bw, 6), fill=AMBER_D)
            d.point((bx, 4), fill=(100, 70, 24))
    # valve over the rack gap, wheel turns
    d.rectangle([168, 7, 172, 11], fill=METAL_M, outline=METAL_D)
    slot = (t // 6) % 4
    wx, wy = [(0, -2), (2, 0), (0, 2), (-2, 0)][slot]
    d.ellipse([167, 8, 173, 14], outline=METAL_L)
    d.point((170 + wx, 11 + wy), fill=GREEN_B)
    # drip falls through the gap every 40 frames
    a = t % 40
    if a < 11:
        dy = 14 + a * 7
        if dy <= 87:
            d.point((170, dy), fill=SLATE_L)
            d.point((170, dy - 2), fill=SLATE_D)
    elif a < 13:
        d.point((168, 87), fill=SLATE_L)
        d.point((172, 87), fill=SLATE_L)


# racks at slightly different heights/widths: (x, top_y, width)
RACKS = [(8, 26, 50), (64, 28, 44), (120, 27, 46), (176, 29, 42)]
CABLE_GAPS = ((58, 64), (108, 120), (166, 176))
# special units per rack: which unit index is a screen / EQ meter / dead panel
SPECIALS = {0: ('screen', 2), 1: ('eq', 3), 2: ('screen', 1), 3: ('eq', 2)}
DEAD_PANEL = (1, 5)      # rack 1, unit 5 is dark
BROKEN_LED = (2, 4)      # rack 2, unit 4's first LED flickers erratically


def draw_racks(d, t):
    bucket = (t // 6) % 20
    # cables draped between rack tops, with a light pulse running along them
    for gi, (gx0, gx1) in enumerate(CABLE_GAPS):
        glen = gx1 - gx0
        a = (t + gi * 13) % 40
        for i in range(glen + 1):
            x = gx0 + i
            sag = int(3 * math.sin(math.pi * i / glen))
            col = METAL_M
            if a <= glen:
                if i == a:
                    col = GREEN_B
                elif i == a - 1:
                    col = GREEN_M
            d.point((x, 30 + sag), fill=col)
    for ri, (rx, ry, rw) in enumerate(RACKS):
        x0, y0, x1, y1 = rx, ry, rx + rw, 76
        d.rectangle([x0, y0, x1, y1], fill=RACK_BG, outline=METAL_D)
        d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=METAL_M)
        d.line([(x0 + 1, y0 + 2), (x0 + 1, y1 - 1)], fill=(22, 30, 25))
        d.rectangle([x0 + 2, y1, x0 + 5, y1 + 2], fill=METAL_D)  # feet
        d.rectangle([x1 - 5, y1, x1 - 2, y1 + 2], fill=METAL_D)
        for ui, uy in enumerate(range(y0 + 4, y1 - 4, 7)):
            d.line([(x0 + 2, uy + 5), (x1 - 2, uy + 5)], fill=METAL_D)
            special = SPECIALS.get(ri) if SPECIALS.get(ri, (None, -1))[1] == ui else None
            if (ri, ui) == DEAD_PANEL:
                # dark dead unit, hanging loose cable
                d.rectangle([x0 + 3, uy, x1 - 3, uy + 4], fill=(12, 16, 13))
                d.line([(x0 + 6, uy + 4), (x0 + 7, uy + 7)], fill=METAL_M)
                continue
            if special and special[0] == 'screen':
                # mini terminal with scrolling readout
                sx0 = x0 + 4
                d.rectangle([sx0, uy, sx0 + 14, uy + 4], fill=DARK, outline=(28, 40, 32))
                for row, ry2 in enumerate((uy + 1, uy + 3)):
                    for xi in range(12):
                        if ((xi + (t // 2) + row * 3) % 5) < 2:
                            d.point((sx0 + 1 + xi, ry2), fill=GREEN_M if row else GREEN_B)
            elif special and special[0] == 'eq':
                # bouncing EQ bars
                for b in range(5):
                    bh = 1 + int(h32(ri, ui, b, (t // 4) % 30) * 4)
                    bx = x0 + 5 + b * 3
                    col = GREEN_B if bh > 3 else GREEN_M
                    d.line([(bx, uy + 4 - bh), (bx, uy + 4)], fill=col)
            else:
                # vent slits (one rack has a slightly crooked row)
                tilt = 1 if (ri == 3 and ui == 1) else 0
                for vi, vx in enumerate(range(x0 + 4, x1 - 19, 3)):
                    vy = uy + 1 + (tilt if vi > 3 else 0)
                    d.line([(vx, vy), (vx, vy + 2)], fill=(22, 30, 25))
                d.point((x0 + 3, uy + 2), fill=METAL_M)
            # four status LEDs, deterministic blink
            for li in range(4):
                if (ri, ui) == BROKEN_LED and li == 0:
                    col = GREEN_B if (t * 7 + t // 3) % 13 < 4 else (18, 26, 20)
                else:
                    hh = (ri * 7 + ui * 13 + li * 5 + bucket * 3) % 11
                    if hh < 3:
                        col = GREEN_B
                    elif hh < 5:
                        col = AMBER
                    elif hh == 5:
                        col = RED
                    else:
                        col = GREEN_D
                d.point((x1 - 4 - li * 3, uy + 2), fill=col)
            # fast network-activity LED
            net = h32(ri, ui, (t // 2) % 60)
            d.point((x1 - 4 - 4 * 3, uy + 2), fill=GREEN_X if net < 0.45 else (18, 26, 20))


def draw_floor(d, t):
    d.rectangle([0, 88, W - 1, H - 1], fill=(11, 15, 12))
    d.line([(0, 88), (W - 1, 88)], fill=(38, 48, 42))
    # worn edge: a few chipped pixels in the floor line
    for cx in (57, 141, 226, 289):
        d.point((cx, 88), fill=(24, 31, 27))
    # grating texture
    for y in range(90, H, 3):
        for x in range((y * 5) % 6, W, 12):
            d.point((x, y), fill=(20, 27, 22))
    # old stain under the drip gap
    for sx, sy in ((168, 91), (169, 91), (170, 92), (171, 91), (167, 92), (172, 92)):
        d.point((sx, sy), fill=(15, 20, 18))
    # cracks
    for crack in (((44, 90), (46, 91), (47, 93)), ((261, 91), (263, 92), (264, 94), (266, 95))):
        for px, py in crack:
            d.point((px, py), fill=(6, 9, 7))
    # scattered bolts / debris
    for bx, by in ((28, 92), (118, 94), (205, 91), (243, 93), (310, 92), (87, 93)):
        d.point((bx, by), fill=(30, 40, 33))
    # grounding shadows
    d.line([(9, 89), (227, 89)], fill=(7, 10, 8))
    d.rectangle([248, 89, 304, 90], fill=(7, 10, 8))


def draw_critter(d, t):
    """Tiny maintenance bot scuttling across the floor once per loop."""
    x = 335 - 3 * t
    if not -6 < x < W + 6:
        return
    bob = 1 if (t // 2) % 2 else 0
    y = 92 - bob
    d.rectangle([x, y, x + 4, y + 1], fill=METAL_M)
    d.point((x + 1, y - 1), fill=METAL_L)              # little dome
    d.point((x, y), fill=GREEN_B)                      # eye (faces direction of travel)
    leg = (t // 2) % 2
    d.point((x + 1 + leg, y + 2), fill=METAL_D)        # scuttling legs
    d.point((x + 3 - leg, y + 2), fill=METAL_D)
    if t % 4 < 2:
        d.point((x + 4, y - 1), fill=AMBER)            # blinking tail light


def draw_sign(d, t):
    msg = "BCANFIELD/DOTAGENTS"
    tw = text_width(msg)
    bx0, by0 = 150, 10
    bx1, by1 = bx0 + tw + 7, by0 + 11
    # chains: left one hangs straight, right one is a link longer and kinked
    for cy in range(7, by0, 2):
        d.point((bx0 + 6, cy), fill=METAL_L)
    for cy in range(7, by0 + 1, 2):
        d.point((bx1 - 6 + (1 if cy == 9 else 0), cy), fill=METAL_L)
    d.rectangle([bx0, by0, bx1, by1], fill=DARK, outline=AMBER_D)
    d.point((bx0, by0), fill=AMBER)
    d.point((bx1, by1), fill=AMBER)
    d.point((bx1 - 1, by0), fill=(60, 40, 12))  # dented corner
    flick = (t % 40) in (28, 29, 33)
    draw_text(d, bx0 + 4, by0 + 3, msg, AMBER_D if flick else AMBER)
    # one tired letter flickers on its own
    if (t % 40) in (10, 11, 14):
        bad = 8  # the first 'D'
        bx = bx0 + 4 + sum(len(FONT[ch][0]) + 1 for ch in msg[:bad])
        glyph = FONT[msg[bad]]
        for gy, row in enumerate(glyph):
            for gx, c in enumerate(row):
                if c == '#':
                    d.point((bx + gx, by0 + 3 + gy), fill=(70, 46, 14))


# ====================================================================
# conveyor
# ====================================================================
def draw_belt(d, t):
    x0, x1 = 7, 229
    for lx in (34, 94, 154, 208):  # support legs
        d.rectangle([lx, 80, lx + 3, 87], fill=METAL_D)
        d.point((lx + 1, 81), fill=METAL_M)
    d.rectangle([x0, 72, x1, 80], fill=METAL_D)
    d.line([(x0, 72), (x1, 72)], fill=METAL_L)
    d.line([(x0, 80), (x1, 80)], fill=(20, 26, 23))
    d.line([(x0, 75), (x1, 75)], fill=(24, 31, 27))  # band seam
    # moving tread dashes, two rows
    off = (t * SPEED) % 12
    for x in range(x0 - 12 + off, x1, 12):
        for dx in range(5):
            px = x + dx
            if x0 + 1 <= px <= x1 - 1:
                d.point((px, 77), fill=METAL_M)
        if x0 + 1 <= x + 6 <= x1 - 1:
            d.point((x + 6, 73), fill=(34, 43, 38))
    # end rollers with rotating notch
    for cx in (12, 224):
        d.ellipse([cx - 5, 71, cx + 5, 81], fill=METAL_M, outline=METAL_D)
        slot = ((t * SPEED) // 3) % 4
        nx, ny = [(0, -3), (3, 0), (0, 3), (-3, 0)][slot]
        d.point((cx + nx, 76 + ny), fill=METAL_L)
        d.point((cx, 76), fill=METAL_D)
    # hazard-striped end guard
    for y in range(70, 80):
        for x in range(231, 236):
            d.point((x, y), fill=HAZ_A if ((x + y) // 2) % 2 == 0 else HAZ_B)
    d.rectangle([231, 80, 235, 87], fill=METAL_D)


# ====================================================================
# the food
# ====================================================================
def item_positions(t):
    """Yield (x, bottom_y, scale, phase, kind) for every visible item."""
    out = []
    for i in range(-8, 4):
        spawn = i * SPAWN_EVERY
        age = t - spawn
        if age < 0:
            continue
        kind = i % KINDS
        x = -14 + SPEED * age
        if x <= BELT_END_X:
            if x > -16:
                bob = 1 if (age // 5) % 2 else 0  # belt vibration
                out.append((x, 72 - bob, 1.0, 'belt', kind))
        else:
            hop_age = age - (BELT_END_X + 14) // SPEED
            if 0 <= hop_age <= HOP_FRAMES:
                p = hop_age / HOP_FRAMES
                hx = BELT_END_X + (273 - BELT_END_X) * p
                # low arc straight through the open jaw
                hy = 72 + (48 - 72) * p - 6 * math.sin(math.pi * p)
                s = 1.0 if p < 0.5 else max(0.5, 1.0 - (p - 0.5) * 1.0)
                out.append((hx, hy, s, 'hop' if p <= 0.7 else 'swallow', kind))
    return out


def draw_doc(d, t, x0, y0, x1, y1, s):
    d.rectangle([x0, y0, x1, y1], fill=PAPER)
    fc = max(2, int(3 * s))
    flap = 1 if (t // 4) % 2 else 0  # corner flutter
    d.polygon([(x1 - fc - flap, y0), (x1, y0), (x1, y0 + fc + flap)], fill=GREEN_M)
    if s > 0.6:
        for i, ly in enumerate(range(y0 + 4, y1 - 2, 3)):
            d.line([(x0 + 2, ly), (x1 - 3 + (1 if i % 2 else 0), ly)], fill=GREEN_M)
        d.line([(x0 + 2, y0 + 2), (x1 - fc - 1, y0 + 2)], fill=GREEN_B)


def draw_floppy(d, t, x0, y0, x1, y1, s):
    d.rectangle([x0, y0, x1, y1], fill=SLATE)
    d.line([(x0, y1), (x1, y1)], fill=SLATE_D)
    d.line([(x1, y0), (x1, y1)], fill=SLATE_D)
    if s > 0.6:
        # metal shutter with a moving glint
        sx0 = x0 + 3
        d.rectangle([sx0, y0 + 1, sx0 + 6, y0 + 5], fill=METAL_L)
        d.line([(sx0 + 2, y0 + 2), (sx0 + 2, y0 + 4)], fill=METAL_M)
        g = (t // 3) % 8
        if g < 3:
            d.point((sx0 + 1 + g * 2, y0 + 1), fill=GREEN_X)
        # label
        d.rectangle([x0 + 2, y1 - 6, x1 - 2, y1 - 1], fill=PAPER)
        d.line([(x0 + 3, y1 - 4), (x1 - 4, y1 - 4)], fill=GREEN_M)
        d.point((x0 + 1, y1 - 1), fill=SLATE_D)  # write-protect notch


def draw_cart(d, t, x0, y0, x1, y1, s):
    d.rectangle([x0, y0, x1, y1], fill=METAL_M)
    d.line([(x0, y0), (x1, y0)], fill=METAL_L)
    d.line([(x0, y1), (x1, y1)], fill=METAL_D)
    if s > 0.6:
        for gy in range(y0 + 2, y0 + 5):  # grip ridges
            d.line([(x0 + 1, gy), (x0 + 3, gy)], fill=METAL_D)
            d.line([(x1 - 3, gy), (x1 - 1, gy)], fill=METAL_D)
        # label with shimmer
        d.rectangle([x0 + 2, y0 + 5, x1 - 2, y1 - 2], fill=AMBER_D)
        shim = (t // 5) % 6
        if shim < 2:
            d.line([(x0 + 3 + shim * 3, y0 + 6), (x0 + 3 + shim * 3, y1 - 3)], fill=AMBER)
        d.line([(x0 + 3, y0 + 7), (x1 - 4, y0 + 7)], fill=DARK)
        d.line([(x0 + 3, y0 + 9), (x1 - 5, y0 + 9)], fill=DARK)


def draw_mug(d, t, x0, y0, x1, y1, s):
    mx1 = x1 - 3  # leave room for the handle
    d.rectangle([x0, y0 + 3, mx1, y1], fill=PAPER)
    d.line([(x0, y1), (mx1, y1)], fill=GREEN_M)
    # handle
    d.line([(mx1 + 1, y0 + 5), (mx1 + 2, y0 + 5)], fill=PAPER)
    d.line([(mx1 + 2, y0 + 5), (mx1 + 2, y1 - 3)], fill=PAPER)
    d.line([(mx1 + 1, y1 - 3), (mx1 + 2, y1 - 3)], fill=PAPER)
    # coffee surface
    d.line([(x0 + 1, y0 + 3), (mx1 - 1, y0 + 3)], fill=COFFEE)
    if s > 0.6:
        d.line([(x0 + 2, y0 + 6), (x0 + 2, y1 - 2)], fill=GREEN_M)  # logo stripe
        # steam wisps
        for wi, wx in enumerate((x0 + 2, x0 + 5, x0 + 8)):
            k = (t + wi * 5) % 12
            if k < 8:
                d.point((wx + (k // 3) % 2, y0 - k // 2), fill=METAL_L if k < 4 else METAL_M)


ITEM_PAINTERS = (draw_doc, draw_floppy, draw_cart, draw_mug)
ITEM_GLOWS = (GREEN_D, (26, 38, 52), (40, 34, 16), None)  # mug: no boxy halo
ITEM_SIZES = ((12, 14), (12, 12), (12, 12), (11, 11))
ITEM_BASE = (PAPER, SLATE_L, AMBER_D, PAPER)


def draw_item(d, t, x, bottom, s, kind, phase='belt'):
    if phase == 'swallow':
        # simplified chunk disappearing into the open jaw
        w = max(2, int(8 * s))
        h = max(2, int(5 * s))
        x0 = max(266, int(x - w / 2))
        y0 = max(43, int(bottom - h))
        d.rectangle([x0, y0, min(286, x0 + w), min(47, y0 + h)], fill=ITEM_BASE[kind])
        return
    bw, bh = ITEM_SIZES[kind]
    w = max(3, int(bw * s))
    h = max(4, int(bh * s))
    x0 = int(x - w / 2)
    y0 = int(bottom - h)
    x1, y1 = x0 + w, y0 + h
    if phase == 'belt' and ITEM_GLOWS[kind]:
        d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=ITEM_GLOWS[kind])
    ITEM_PAINTERS[kind](d, t, x0, y0, x1, y1, s)


# ====================================================================
# the robot
# ====================================================================
def draw_robot(d, t):
    c = chomp_phase(t)
    chomping = 0 <= c < 12
    gulping = 12 <= c < 18
    excited = c >= 24 or c < 1
    if excited:
        mouth_open = 6
    elif chomping:
        mouth_open = 5 if (c // 2) % 2 == 0 else 0
    else:
        mouth_open = 0

    # treads
    d.rectangle([250, 80, 302, 88], fill=METAL_D, outline=(20, 26, 23))
    for wx in (257, 276, 295):
        d.ellipse([wx - 3, 81, wx + 3, 87], fill=METAL_M, outline=METAL_D)
        d.point((wx, 84), fill=METAL_D)
    for tx in range(252, 301, 4):  # tread lugs (one has fallen off)
        if tx != 272:
            d.point((tx, 80), fill=METAL_M)

    # body
    d.rectangle([246, 50, 306, 80], fill=METAL_M, outline=METAL_D)
    d.line([(247, 51), (305, 51)], fill=METAL_L)
    d.line([(247, 79), (305, 79)], fill=(40, 50, 45))
    d.line([(288, 52), (288, 78)], fill=(45, 56, 51))  # panel seam
    for rx, ry in ((249, 53), (303, 53), (249, 77), (303, 77)):
        d.point((rx, ry), fill=METAL_L)
    # vent slits lower-right
    for vy in (72, 74, 76):
        d.line([(292, vy), (302, vy)], fill=METAL_D)
    # weld patch lower-left + scratches: this robot has eaten a lot
    d.rectangle([250, 71, 256, 75], fill=(48, 60, 54), outline=(40, 50, 45))
    d.point((251, 72), fill=METAL_L)
    d.line([(258, 54), (260, 56)], fill=(45, 56, 51))   # scratch
    d.point((300, 62), fill=(45, 56, 51))
    # status LED beside the panel seam
    d.point((290, 54), fill=GREEN_B if (t // 12) % 2 else AMBER_D)

    # chest screen + meter (4 segments, one per item kind)
    d.rectangle([254, 56, 284, 70], fill=DARK, outline=GREEN_D)
    k = (t - LAND_MOD) % FRAMES
    segs = min(4, k // 30 + 1)
    full_flash = k >= 114 and (t // 2) % 2 == 0
    for i in range(4):
        x0 = 256 + i * 7
        lit = i < segs
        col = GREEN_B if (lit and not (segs == 4 and k >= 114 and not full_flash)) else (20, 32, 24)
        d.rectangle([x0, 62, x0 + 5, 67], fill=col)
    draw_text(d, 257, 57, "EAT", GREEN_M)
    # screen scan sweep
    sy = 57 + (t % 30) // 2
    if sy <= 69:
        for sx in range(255, 284, 2):
            r, g, b = d._image.getpixel((sx, sy))
            d.point((sx, sy), fill=(min(255, r + 14), min(255, g + 22), min(255, b + 16)))

    # exhaust chimney
    d.rectangle([296, 42, 301, 50], fill=METAL_D)
    d.line([(296, 42), (301, 42)], fill=METAL_L)

    # head
    d.rectangle([252, 26, 300, 50], fill=METAL_M, outline=METAL_D)
    d.line([(253, 27), (299, 27)], fill=METAL_L)
    d.rectangle([256, 30, 296, 47], fill=(24, 32, 28))
    d.rectangle([249, 33, 252, 41], fill=METAL_L, outline=METAL_D)  # ear caps
    d.rectangle([300, 33, 303, 41], fill=METAL_L, outline=METAL_D)
    d.point((301, 34), fill=METAL_D)                    # dinged right ear
    d.line([(286, 28), (288, 28)], fill=(45, 56, 51))   # head scratch

    # antenna
    d.line([(275, 16), (275, 26)], fill=METAL_L)
    tip = AMBER if (t % 15) < 8 else RED
    d.ellipse([273, 12, 277, 16], fill=tip)
    if (t % 15) in (0, 1):  # signal ring
        for dx, dy in ((-3, 0), (3, 0), (0, -3)):
            d.point((275 + dx, 14 + dy), fill=AMBER_D)

    # eyes
    nearest = None
    hop_now = False
    for x, _, _, ph, _ in item_positions(t):
        if ph == 'belt' and (nearest is None or x > nearest):
            nearest = x
        if ph in ('hop', 'swallow'):
            hop_now = True
    blink = c in (21, 22)
    for ex in (262, 280):
        d.rectangle([ex, 32, ex + 10, 40], fill=DARK, outline=GREEN_D)
        brow_y = 29 if excited else 30
        d.line([(ex + 1, brow_y), (ex + 9, brow_y)], fill=METAL_L)  # brow
        if gulping or blink:
            d.line([(ex + 2, 36), (ex + 8, 36)], fill=GREEN_B)  # happy-closed
        else:
            px, py = ex + 4, 35
            if hop_now:
                px, py = ex + 2, 36
            elif nearest is not None and nearest > 120:
                px = ex + 2
            col = AMBER if (chomping and t % 2 == 0) else GREEN_B
            d.rectangle([px, py, px + 3, py + 3], fill=col)
            d.point((px, py), fill=GREEN_X if col == GREEN_B else (255, 220, 120))

    # mouth
    if mouth_open > 0:
        d.rectangle([264, 42, 288, 42 + mouth_open], fill=DARK, outline=GREEN_D)
        for tx in range(266, 288, 4):
            d.point((tx, 43), fill=PAPER)
        if mouth_open >= 5:
            for tx in range(268, 287, 4):
                d.point((tx, 42 + mouth_open - 1), fill=PAPER)
    else:
        d.line([(264, 44), (288, 44)], fill=DARK)
        d.line([(264, 45), (288, 45)], fill=(18, 24, 20))

    # arms + utensils (fork left, knife right), raised while chomping
    lift = 3 if chomping else 0
    wig = 1 if (chomping and (t // 3) % 2 == 0) else 0
    d.line([(246, 58), (240, 54 - lift)], fill=METAL_M)
    d.line([(246, 59), (240, 55 - lift)], fill=METAL_L)
    fx, fy = 239, 53 - lift - wig
    d.line([(fx, fy), (fx, fy - 8)], fill=PAPER)
    for px in (fx - 2, fx, fx + 2):
        d.line([(px, fy - 11), (px, fy - 8)], fill=PAPER)
    d.line([(306, 58), (311, 55 - lift)], fill=METAL_M)
    d.line([(306, 59), (311, 56 - lift)], fill=METAL_L)
    kx, ky = 311, 55 - lift + wig          # knife gripped at the arm tip
    d.rectangle([kx, ky - 3, kx + 1, ky], fill=AMBER_D)       # handle
    d.rectangle([kx, ky - 10, kx + 1, ky - 4], fill=PAPER)    # blade
    d.point((kx + 1, ky - 10), fill=METAL_L)                  # tip bevel


# ====================================================================
# particles
# ====================================================================
HEART = [
    ".#.#.",
    "#####",
    "#####",
    ".###.",
    "..#..",
]
STARBURST = [
    "..#..",
    ".###.",
    "##.##",
    ".###.",
    "..#..",
]
CRUMB_COLS = (GREEN_B, SLATE_L, AMBER, COFFEE)


def draw_particles(d, t):
    c = chomp_phase(t)
    kind = swallow_kind(t)

    # impact sparks the moment food lands
    if c < 2:
        for dx, dy in ((-3, -2), (3, -2), (-4, 2), (4, 2), (0, -4), (-1, 3)):
            d.point((276 + dx * (c + 1), 45 + dy * (c + 1)), fill=GREEN_X if c == 0 else GREEN_M)

    # reaction particle after the gulp — varies by what was eaten
    if 16 <= c < 28:
        a = c - 16
        hy = 28 - a
        hx = 290 + (1 if (a // 3) % 2 else 0)
        fade = a >= 7
        if kind == 0:  # doc -> heart
            col = AMBER_D if fade else AMBER
            for gy, row in enumerate(HEART):
                for gx, ch in enumerate(row):
                    if ch == '#':
                        d.point((hx + gx, hy + gy), fill=col)
        elif kind == 1:  # floppy -> sparkle
            col = GREEN_M if fade else GREEN_X
            for gy, row in enumerate(STARBURST):
                for gx, ch in enumerate(row):
                    if ch == '#':
                        d.point((hx + gx, hy + gy), fill=col)
        elif kind == 2:  # cartridge -> +1
            draw_text(d, hx, hy, "+1", AMBER_D if fade else AMBER)
        else:  # mug -> steam puffs
            col = METAL_M if fade else METAL_L
            for pi, (ox, oy) in enumerate(((0, 0), (3, -3), (-2, -5))):
                d.point((hx + ox + (a // 4) % 2, hy + oy), fill=col)

    # crumbs falling while chomping, colored by the meal
    if 2 <= c < 12:
        a = c - 2
        for ci, (cx, drift) in enumerate(((268, 0), (276, 1), (283, -1))):
            cy = 50 + a * 2 + ci * 2
            if cy < 79:
                col = CRUMB_COLS[kind] if a < 4 else GREEN_M
                d.point((cx + drift * (a // 3), cy), fill=col)

    # exhaust puffs
    if 14 <= c < 26:
        a = c - 14
        py = 40 - a
        col = METAL_L if a < 6 else METAL_M
        d.point((298 + (a % 2), py), fill=col)
        if a > 3:
            d.point((297, py + 4), fill=METAL_M)


# ====================================================================
def render_frame(t):
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    draw_background(d, t)
    draw_wall(d, t)
    draw_pipes(d, t)
    draw_racks(d, t)
    draw_floor(d, t)
    draw_sign(d, t)
    draw_belt(d, t)
    for x, by, s, ph, kind in item_positions(t):
        if ph == 'belt':
            draw_item(d, t, x, by, s, kind)
    draw_robot(d, t)
    for x, by, s, ph, kind in item_positions(t):
        if ph in ('hop', 'swallow'):
            draw_item(d, t, x, by, s, kind, ph)
    draw_particles(d, t)
    draw_critter(d, t)

    big = img.resize((W * SCALE, H * SCALE), Image.NEAREST)
    pix = big.load()
    for y in range(2, H * SCALE, 3):
        for x in range(W * SCALE):
            r, g, b = pix[x, y]
            pix[x, y] = (int(r * 0.86), int(g * 0.86), int(b * 0.86))
    return big


def main():
    frames = [render_frame(t) for t in range(FRAMES)]
    for t in (0, 8, 16, 24, 38, 68, 98):
        frames[t].save(f"assets/_frame_{t:03d}.png")
    frames[0].save(
        "assets/feeding-the-robots.gif",
        save_all=True,
        append_images=frames[1:],
        duration=DURATION,
        loop=0,
        optimize=True,
    )
    print("wrote assets/feeding-the-robots.gif")


if __name__ == '__main__':
    main()
