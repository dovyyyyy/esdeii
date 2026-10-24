"""Smooth vector glyphs for esdeii system icons.

Each glyph is a list of drawing operations in a 100x100 box:
    ("add", shape) paints the shape, ("cut", shape) erases it.
Shapes: SVG-style path strings (absolute M/L/C/Q/Z), rounded rects,
circles and capsules (thick lines with round ends). They are flattened to
polygons and drawn with heavy supersampling so curves come out smooth.
"""
import math
import re
from PIL import Image, ImageDraw


# ------------------------------------------------------------------ path flattening
def _bez3(p0, p1, p2, p3, n=24):
    out = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def _bez2(p0, p1, p2, n=18):
    out = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                    mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))
    return out


def parse_path(d):
    toks = re.findall(r"[MLCQZ]|-?\d*\.?\d+", d)
    polys, cur, i, cmd, pos = [], [], 0, None, (0, 0)
    while i < len(toks):
        t = toks[i]
        if t in "MLCQZ":
            cmd = t
            i += 1
            if cmd == "Z":
                if cur:
                    polys.append(cur)
                cur = []
            continue
        nums = lambda k: [float(x) for x in toks[i:i + k]]
        if cmd == "M":
            if cur:
                polys.append(cur)
            x, y = nums(2)
            cur = [(x, y)]
            pos = (x, y)
            i += 2
            cmd = "L"
        elif cmd == "L":
            x, y = nums(2)
            cur.append((x, y))
            pos = (x, y)
            i += 2
        elif cmd == "C":
            a = nums(6)
            pts = _bez3(pos, (a[0], a[1]), (a[2], a[3]), (a[4], a[5]))
            cur += pts
            pos = (a[4], a[5])
            i += 6
        elif cmd == "Q":
            a = nums(4)
            cur += _bez2(pos, (a[0], a[1]), (a[2], a[3]))
            pos = (a[2], a[3])
            i += 4
    if cur:
        polys.append(cur)
    return polys


# ------------------------------------------------------------------ shape helpers
def P(d):
    return ("path", d)


def RR(x0, y0, x1, y1, r=0):
    return ("rrect", (x0, y0, x1, y1, r))


def CI(cx, cy, r):
    return ("circle", (cx, cy, r))


def CAP(x0, y0, x1, y1, w):
    return ("capsule", (x0, y0, x1, y1, w))


def ELL(x0, y0, x1, y1):
    return ("ellipse", (x0, y0, x1, y1))


def plus(cx, cy, arm, w, op="cut"):
    r = w * 0.28
    return [(op, RR(cx - w / 2, cy - arm, cx + w / 2, cy + arm, r)),
            (op, RR(cx - arm, cy - w / 2, cx + arm, cy + w / 2, r))]


def diamond(cx, cy, off, r, op="cut"):
    return [(op, CI(cx + dx, cy + dy, r)) for dx, dy in ((0, -off), (off, 0), (0, off), (-off, 0))]


def ring(cx, cy, r_out, r_in):
    return [("cut", CI(cx, cy, r_out)), ("add", CI(cx, cy, r_in))]


def render(ops, G, ss=6):
    S = G * ss
    k = S / 100.0
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    for op, (kind, a) in ops:
        fill = 255 if op == "add" else 0
        if kind == "path":
            for poly in parse_path(a):
                d.polygon([(x * k, y * k) for x, y in poly], fill=fill)
        elif kind == "rrect":
            x0, y0, x1, y1, r = a
            d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k, fill=fill)
        elif kind == "circle":
            cx, cy, r = a
            d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=fill)
        elif kind == "ellipse":
            x0, y0, x1, y1 = a
            d.ellipse([x0 * k, y0 * k, x1 * k, y1 * k], fill=fill)
        elif kind == "capsule":
            x0, y0, x1, y1, w = a
            h = w / 2
            ang = math.atan2(y1 - y0, x1 - x0)
            nx, ny = -math.sin(ang) * h, math.cos(ang) * h
            d.polygon([((x0 + nx) * k, (y0 + ny) * k), ((x1 + nx) * k, (y1 + ny) * k),
                       ((x1 - nx) * k, (y1 - ny) * k), ((x0 - nx) * k, (y0 - ny) * k)], fill=fill)
            for cx, cy in ((x0, y0), (x1, y1)):
                d.ellipse([(cx - h) * k, (cy - h) * k, (cx + h) * k, (cy + h) * k], fill=fill)
    return m.resize((G, G), Image.LANCZOS)


# ------------------------------------------------------------------ glyph designs
G = {}

# PlayStation-style pad: wide top, two long handles angled outwards
G["pad_ps"] = [
    ("add", P("M 30 25 C 40 23.5 60 23.5 70 25 C 82 26.5 90 31 93 41 C 96 52 97.5 67 95.5 79 "
              "C 94 88 86 92.5 79.5 88.5 C 74.5 85 72 75.5 66.5 68 C 62.5 63 56.5 61.5 50 61.5 "
              "C 43.5 61.5 37.5 63 33.5 68 C 28 75.5 25.5 85 20.5 88.5 C 14 92.5 6 88 4.5 79 "
              "C 2.5 67 4 52 7 41 C 10 31 18 26.5 30 25 Z")),
    *plus(21.5, 43, 9, 6),
    *diamond(78.5, 43, 8.6, 4.1),
    ("cut", RR(39.5, 37.5, 45.5, 40.5, 1.5)), ("cut", RR(54.5, 37.5, 60.5, 40.5, 1.5)),
    *ring(36, 56, 8.6, 5.6), *ring(64, 56, 8.6, 5.6),
]

# Xbox-style pad: chunky body, short fat grips, offset sticks
G["pad_xbox"] = [
    ("add", P("M 24 27 C 36 22.5 64 22.5 76 27 C 87 31 93.5 41 95.5 55 C 97.5 70 96.5 83 88.5 86.5 "
              "C 80.5 89.5 74.5 81 68.5 73 C 63 67 37 67 31.5 73 C 25.5 81 19.5 89.5 11.5 86.5 "
              "C 3.5 83 2.5 70 4.5 55 C 6.5 41 13 31 24 27 Z")),
    *ring(25, 43, 9, 6),
    *plus(37.5, 59, 6.5, 4.6),
    *diamond(75, 43, 7.2, 3.7),
    *ring(63, 59, 8, 5.2),
    ("cut", CI(50, 34.5, 4.2)),
]

# N64-style trident
G["pad_n64"] = [
    ("add", P("M 5 38 C 5 22 27 15 50 17 C 73 15 95 22 95 38 C 95 49 88 55 78 55 L 22 55 "
              "C 12 55 5 49 5 38 Z")),
    ("add", CAP(17, 44, 13, 85, 20)),
    ("add", CAP(83, 44, 87, 85, 20)),
    ("add", CAP(50, 48, 50, 77, 18)),
    *plus(19, 35, 7, 4.8),
    *ring(50, 54, 6.8, 4),
    *diamond(80, 30, 5, 2.6),
    ("cut", CI(69, 43, 3.9)), ("cut", CI(62.5, 36, 3.9)),
    ("cut", CI(50, 33, 3)),
]

# GameCube-style pad: rounded body, big round grips, big A button
G["pad_gc"] = [
    ("add", P("M 22 27 C 34 21 66 21 78 27 C 88.5 32 94.5 41 95 53 C 95.5 67 91.5 80.5 82 84.5 "
              "C 74 88 68.5 80.5 64.5 73 C 61 67 39 67 35.5 73 C 31.5 80.5 26 88 18 84.5 "
              "C 8.5 80.5 4.5 67 5 53 C 5.5 41 11.5 32 22 27 Z")),
    *ring(25, 43.5, 10, 6.4),
    *plus(36, 62, 5.2, 3.8),
    *ring(64, 62, 6.6, 4),
    ("cut", CI(74, 44.5, 7)),
    ("cut", CI(62.5, 52, 3.6)),
    ("cut", CAP(85.5, 37, 85.5, 50, 5.4)),
    ("cut", CAP(66, 33.5, 78, 31, 5)),
]

# Genesis-style crescent pad with round d-pad and 3 diagonal buttons
G["pad_genesis"] = [
    ("add", P("M 5 47 C 5 31 25 22 50 22 C 75 22 95 31 95 47 C 95 63 87 77 75 80.5 "
              "C 66 83 60 74.5 50 74.5 C 40 74.5 34 83 25 80.5 C 13 77 5 63 5 47 Z")),
    ("cut", CI(26, 48, 12.5)), ("add", CI(26, 48, 10.5)),
    *plus(26, 48, 8.4, 4.4),
    ("cut", CI(61.5, 56.5, 4.7)), ("cut", CI(72, 50.5, 4.7)), ("cut", CI(82.5, 44.5, 4.7)),
    ("cut", RR(46, 35.5, 54, 39, 1.7)),
]

# SNES-style dog-bone pad
G["pad_snes"] = [
    ("add", P("M 27 27 C 37 27 42 31 50 31 C 58 31 63 27 73 27 C 86 27 96 37 96 50 "
              "C 96 63 86 73 73 73 C 63 73 58 69 50 69 C 42 69 37 73 27 73 C 14 73 4 63 4 50 "
              "C 4 37 14 27 27 27 Z")),
    *plus(26, 50, 10.5, 6.2),
    *diamond(74, 50, 9.2, 4.5),
    ("cut", CAP(40.5, 57.5, 45, 53, 3.8)), ("cut", CAP(51.5, 57.5, 56, 53, 3.8)),
]

# NES-style rectangle pad
G["pad_nes"] = [
    ("add", RR(3, 30, 97, 70, 4.5)),
    ("cut", RR(7.5, 34.5, 92.5, 65.5, 2.5)), ("add", RR(9, 36, 91, 64, 2)),
    *plus(21, 50, 9.5, 6),
    ("cut", RR(36, 47, 64, 61, 2)), ("add", RR(38.5, 54, 45.5, 58, 2)), ("add", RR(54.5, 54, 61.5, 58, 2)),
    ("cut", CI(72, 54, 5.6)), ("cut", CI(86, 54, 5.6)),
]

# Wii Remote
G["remote"] = [
    ("add", RR(36.5, 3, 63.5, 97, 11)),
    ("cut", CI(44, 9.5, 2)),
    *plus(50, 21, 7, 4.6),
    ("cut", RR(44, 33, 56, 45, 4.5)),
    ("cut", CI(42.5, 56, 2.4)), ("cut", CI(50, 56, 2.6)), ("cut", CI(57.5, 56, 2.4)),
    ("cut", CI(50, 75, 4)), ("cut", CI(50, 85.5, 4)),
]

# Wii U GamePad-style tablet controller
G["tablet_pad"] = [
    ("add", P("M 12 25 L 88 25 C 94 25 97.5 29 97.5 35 L 97.5 66 C 97.5 72 94 76 88 76 L 74 76 "
              "C 70 76 68 79 62 79 L 38 79 C 32 79 30 76 26 76 L 12 76 C 6 76 2.5 72 2.5 66 "
              "L 2.5 35 C 2.5 29 6 25 12 25 Z")),
    ("cut", RR(20, 31, 80, 70, 2)),
    *ring(11, 36.5, 5.2, 3.2), *plus(11, 56, 5, 3.4),
    *ring(89, 36.5, 5.2, 3.2), *diamond(89, 56, 4.6, 2.2),
]

# Switch-style hybrid with detached-looking side controllers
G["switch"] = [
    ("add", P("M 15 25 L 18.2 25 L 18.2 75 L 15 75 C 7.5 75 3 70 3 62 L 3 38 C 3 30 7.5 25 15 25 Z")),
    ("add", RR(19.8, 25, 80.2, 75, 2.5)),
    ("add", P("M 85 25 C 92.5 25 97 30 97 38 L 97 62 C 97 70 92.5 75 85 75 L 81.8 75 L 81.8 25 Z")),
    ("cut", RR(23.5, 29, 76.5, 71, 1.5)),
    *ring(10.6, 36, 4.4, 2.7), *diamond(10.6, 55, 3.9, 1.9),
    *diamond(89.4, 40, 3.9, 1.9), *ring(89.4, 58, 4.4, 2.7),
]

# Game Boy-style vertical handheld (big bottom-right corner)
G["handheld"] = [
    ("add", P("M 27 3 L 73 3 C 76.5 3 78.5 5 78.5 8.5 L 78.5 80 C 78.5 90 71 97 61 97 L 27 97 "
              "C 23.5 97 21.5 95 21.5 91.5 L 21.5 8.5 C 21.5 5 23.5 3 27 3 Z")),
    ("cut", P("M 29 9 L 71 9 C 72.5 9 73 9.5 73 11 L 73 43 C 73 47 70 49.5 66 49.5 L 29 49.5 "
              "C 27.5 49.5 27 49 27 47.5 L 27 11 C 27 9.5 27.5 9 29 9 Z")),
    ("add", RR(34, 14.5, 66, 43.5, 1)),
    *plus(34.5, 66, 7.4, 4.8),
    ("cut", CI(67, 62, 4.3)), ("cut", CI(58, 67, 4.3)),
    ("cut", CAP(40, 85, 44, 82, 3.2)), ("cut", CAP(49, 85, 53, 82, 3.2)),
    ("cut", CAP(62, 90, 68, 84, 1.8)), ("cut", CAP(66, 91, 72, 85, 1.8)),
]

# GBA-style horizontal handheld
G["wide_handheld"] = [
    ("add", P("M 15 27 C 26 25.5 74 25.5 85 27 C 93.5 28.5 98 39 98 50 C 98 62 94 72.5 84 74.5 "
              "L 16 74.5 C 6 72.5 2 62 2 50 C 2 39 6.5 28.5 15 27 Z")),
    ("cut", RR(28.5, 31.5, 71.5, 68.5, 2.5)), ("add", RR(32, 35, 68, 65, 1)),
    *plus(15, 47, 6.8, 4.4),
    ("cut", CI(86.5, 44, 3.9)), ("cut", CI(79, 52, 3.9)),
    ("cut", CI(15, 63, 1.6)), ("cut", CI(15, 67.5, 1.6)),
]

# PSP-style long handheld
G["psp"] = [
    ("add", RR(2, 32, 98, 68, 17)),
    ("cut", RR(21, 35.5, 79, 64.5, 1.5)),
    *plus(11, 46, 4.8, 3.2),
    *diamond(89, 46, 4.3, 2.1),
    ("cut", CI(11, 59.5, 2.6)),
]

# DS-style clamshell
G["dual"] = [
    ("add", RR(10, 3, 90, 46.5, 6)), ("cut", RR(23, 9, 77, 40.5, 1.5)),
    ("cut", CI(16.5, 24, 1.3)), ("cut", CI(16.5, 28, 1.3)), ("cut", CI(83.5, 24, 1.3)), ("cut", CI(83.5, 28, 1.3)),
    ("add", RR(12, 46, 20, 54, 2)), ("add", RR(80, 46, 88, 54, 2)),
    ("add", RR(10, 53.5, 90, 97, 6)), ("cut", RR(29.5, 59.5, 70.5, 91, 1.5)),
    *plus(19.5, 73, 5.2, 3.4), *diamond(80.5, 73, 4.6, 2.1),
]

# 3DS-style clamshell (wider top screen, circle pad above the d-pad)
G["dual3d"] = [
    ("add", RR(8, 3, 92, 46.5, 6)), ("cut", RR(17, 8.5, 83, 41, 1.5)),
    ("add", RR(12, 46, 20, 54, 2)), ("add", RR(80, 46, 88, 54, 2)),
    ("add", RR(8, 53.5, 92, 97, 6)), ("cut", RR(29.5, 58.5, 70.5, 90, 1.5)),
    *ring(18.5, 65, 5.4, 3.4), *plus(18.5, 83.5, 4.6, 3), *diamond(81.5, 70, 4.4, 2),
]

# Virtual Boy-style goggles on a stand
G["goggles"] = [
    ("add", P("M 9 37 C 9 26 22 21 50 21 C 78 21 91 26 91 37 L 91 52 C 91 60 85 64 77 64 L 23 64 "
              "C 15 64 9 60 9 52 Z")),
    ("cut", RR(19, 31, 45, 54, 7)), ("cut", RR(55, 31, 81, 54, 7)),
    ("add", CAP(50, 62, 50, 85, 9)),
    ("add", CAP(32, 90, 68, 90, 7)),
]

# Atari-style joystick
G["joystick"] = [
    ("add", P("M 20 54 L 80 54 C 85 54 88 57 88 62 L 88 86 C 88 91 85 94 80 94 L 20 94 "
              "C 15 94 12 91 12 86 L 12 62 C 12 57 15 54 20 54 Z")),
    ("cut", RR(16.5, 58.5, 83.5, 89.5, 4)), ("add", RR(18.5, 60.5, 81.5, 87.5, 3)),
    ("cut", CI(29, 69, 6.5)), ("add", CI(29, 69, 4.4)),
    ("cut", CI(54, 64, 6.5)),
    ("add", CAP(54, 18, 54, 64, 8.5)),
    ("add", CI(54, 15, 7)),
]

# Arcade cabinet
G["arcade"] = [
    ("add", P("M 27 4 L 73 4 C 75.5 4 77 5.5 77 8 L 77 41 L 85 53 L 85 93 C 85 95 84 96 82 96 "
              "L 18 96 C 16 96 15 95 15 93 L 15 53 L 23 41 L 23 8 C 23 5.5 24.5 4 27 4 Z")),
    ("cut", RR(28, 9, 72, 17, 1.5)),
    ("cut", RR(28, 21, 72, 41, 2)),
    ("cut", P("M 24 48 L 76 48 L 80 54 L 20 54 Z")),
    ("add", CI(34, 51, 2.2)), ("add", CI(58, 51, 1.8)), ("add", CI(65, 51, 1.8)),
    ("cut", RR(44, 66, 56, 71, 1)),
    ("cut", RR(40, 78, 60, 88, 2)),
]

# Pinball table
G["pinball"] = [
    ("add", RR(22, 3, 78, 97, 10)),
    ("cut", RR(28, 9, 72, 91, 6)),
    ("add", CI(50, 34, 7.5)), ("add", CI(36, 21, 5)), ("add", CI(64, 21, 5)),
    ("add", CAP(34, 74, 46, 81, 5)), ("add", CAP(66, 74, 54, 81, 5)),
    ("add", CI(57, 59, 3.4)),
]

# Desktop computer
G["computer"] = [
    ("add", RR(5, 7, 95, 67, 6)), ("cut", RR(12, 14, 88, 59, 2.5)),
    ("add", P("M 43 66 L 57 66 L 60 80 L 40 80 Z")),
    ("add", RR(25, 79, 75, 88, 4)),
]

# 8-bit home computer (wedge keyboard)
_kb = [("add", P("M 7 72 L 14 37 C 15 33 18 31 22 31 L 78 31 C 82 31 85 33 86 37 L 93 72 "
                 "C 94 76 91.5 79 87.5 79 L 12.5 79 C 8.5 79 6 76 7 72 Z"))]
for row, (y, x0, n, w) in enumerate(((38, 19, 9, 6.2), (47, 17, 9, 6.6), (56, 15, 9, 7.0))):
    step = (100 - 2 * x0) / n
    for i in range(n):
        x = x0 + i * step
        _kb.append(("cut", RR(x + 0.6, y, x + step - 0.6, y + 6.4, 1.2)))
_kb.append(("cut", RR(30, 66, 70, 72.5, 1.5)))
G["keyboard"] = _kb

# Optical disc
G["disc"] = [
    ("add", CI(50, 50, 46)), ("cut", CI(50, 50, 16)), ("add", CI(50, 50, 13)), ("cut", CI(50, 50, 5.5)),
    ("cut", P("M 50 12 C 66 12 79 21 85 34 L 80 36.5 C 75 25.5 63.5 17.5 50 17.5 Z")),
]

# Cartridge
G["cart"] = [
    ("add", P("M 20 8 L 80 8 C 83 8 85 10 85 13 L 85 88 C 85 91 83 93 80 93 L 30 93 L 15 80 "
              "L 15 13 C 15 10 17 8 20 8 Z")),
    ("cut", RR(26, 18, 74, 56, 3)),
    *[("cut", RR(29 + i * 9, 72, 34 + i * 9, 93, 0.8)) for i in range(5)],
]

# Smartphone
G["phone"] = [
    ("add", RR(26, 3, 74, 97, 9)), ("cut", RR(30.5, 10, 69.5, 86, 2.5)),
    ("cut", RR(44, 5.5, 56, 7.5, 1)), ("cut", CI(50, 91.5, 3)),
]

# Gear (game engines / ports)
_gear = []
for i in range(8):
    a = i * math.pi / 4
    pts = [(50 + r * math.cos(a + da), 50 + r * math.sin(a + da))
           for da, r in ((-0.2, 32), (-0.13, 47), (0.13, 47), (0.2, 32))]
    _gear.append(("add", P("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z")))
_gear += [("add", CI(50, 50, 35)), ("cut", CI(50, 50, 14))]
G["gear"] = _gear

# TV
G["tv"] = [
    ("add", RR(5, 25, 95, 85, 8)), ("cut", RR(12, 32, 74, 78, 4)),
    ("cut", CI(84.5, 42, 4)), ("cut", CI(84.5, 56, 4)),
    ("add", CAP(33, 7, 50, 24, 4.5)), ("add", CAP(67, 7, 50, 24, 4.5)),
    ("add", RR(22, 85, 34, 93, 2)), ("add", RR(66, 85, 78, 93, 2)),
]

_star = []
for i in range(10):
    a = -math.pi / 2 + i * math.pi / 5
    r = 47 if i % 2 == 0 else 21
    _star.append((50 + r * math.cos(a), 53 + r * math.sin(a)))
G["star"] = [("add", P("M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in _star) + " Z"))]

G["clock"] = [("add", CI(50, 50, 46)), ("cut", CI(50, 50, 37)),
              ("add", CAP(50, 50, 50, 24, 7)), ("add", CAP(50, 50, 67, 60, 7)), ("add", CI(50, 50, 6))]

G["stack"] = [("add", RR(30, 6, 94, 70, 8)), ("cut", RR(35, 11, 89, 65, 5)),
              ("add", RR(18, 18, 82, 82, 8)), ("cut", RR(23, 23, 77, 77, 5)),
              ("add", RR(6, 30, 70, 94, 8))]

G["folder"] = [("add", P("M 6 22 C 6 18 9 15 13 15 L 38 15 C 41 15 43 16 45 18 L 51 24 L 87 24 "
                         "C 91 24 94 27 94 31 L 94 80 C 94 84 91 87 87 87 L 13 87 C 9 87 6 84 6 80 Z")),
               ("cut", RR(6, 33, 94, 36.5, 0))]

# generic pad (unknown consoles)
G["console"] = [
    ("add", P("M 24 29 C 36 24 64 24 76 29 C 87 33 94 43 95 56 C 96 70 92 82 84 84.5 "
              "C 76 87 71 80 66 73 C 61 67 39 67 34 73 C 29 80 24 87 16 84.5 C 8 82 4 70 5 56 "
              "C 6 43 13 33 24 29 Z")),
    *plus(26, 49, 9.5, 6), *diamond(74, 49, 8, 4),
]


def glyph(kind, size):
    return render(G.get(kind, G["console"]), size)

# envelope and house for decorative menu buttons
G["mail"] = [("add", RR(8, 22, 92, 78, 8)),
             ("cut", P("M 14 28 L 50 55 L 86 28 L 86 33 L 50 60 L 14 33 Z"))]
G["home"] = [("add", P("M 50 8 L 94 46 L 84 46 L 84 90 L 60 90 L 60 64 L 40 64 L 40 90 L 16 90 L 16 46 L 6 46 Z"))]
