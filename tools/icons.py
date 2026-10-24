"""System icon artwork for esdeii: glyph drawings + three tile styles.

Glyphs are simple original silhouettes (controllers, handhelds, computers...)
drawn as white-on-transparent masks. Tile styles:
  3ds  - glossy colour tile with white art (3DS HOME menu feel)
  wii  - white "channel" tile with coloured art (Wii menu feel)
  wiiu - bold flat colour tile with a white name band (Wii U menu feel)
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TILE = 360
PAD = 20          # transparent margin around the body (holds the shadow)
LIFT = 4          # body sits this many px above centre (shadow below)
RAD = 78          # body corner radius
BODY = (PAD, PAD - LIFT, TILE - PAD, TILE - PAD - LIFT)

# ---------------------------------------------------------------- glyphs
def glyph(kind, G):
    """White glyph mask (L mode, G x G)."""
    ss = 4
    S = G * ss
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    ON, OFF = 255, 0

    def R(x0, y0, x1, y1, r=0.0, f=ON):
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=f)

    def C(cx, cy, r, f=ON):
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=f)

    def E(x0, y0, x1, y1, f=ON):
        d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=f)

    def P(pts, f=ON):
        d.polygon([(x * S, y * S) for x, y in pts], fill=f)

    def plus(cx, cy, a, w, f=OFF):
        R(cx - w, cy - a, cx + w, cy + a, w * 0.35, f)
        R(cx - a, cy - w, cx + a, cy + w, w * 0.35, f)

    def diamond(cx, cy, off, r, f=OFF):
        for dx, dy in ((0, -off), (off, 0), (0, off), (-off, 0)):
            C(cx + dx, cy + dy, r, f)

    def L_(pts, w, f=ON):
        d.line([(x * S, y * S) for x, y in pts], fill=f, width=int(w * S), joint="curve")

    k = kind
    if k == "pad_nes":
        R(0.03, 0.30, 0.97, 0.70, 0.05)
        plus(0.20, 0.50, 0.10, 0.034)
        R(0.38, 0.52, 0.46, 0.56, 0.02, OFF)
        R(0.50, 0.52, 0.58, 0.56, 0.02, OFF)
        C(0.70, 0.54, 0.055, OFF)
        C(0.85, 0.54, 0.055, OFF)
    elif k == "pad_snes":
        R(0.18, 0.31, 0.82, 0.69, 0.0)
        C(0.25, 0.50, 0.22)
        C(0.75, 0.50, 0.22)
        plus(0.25, 0.50, 0.095, 0.032)
        diamond(0.75, 0.50, 0.085, 0.042)
        R(0.42, 0.52, 0.48, 0.555, 0.02, OFF)
        R(0.52, 0.52, 0.58, 0.555, 0.02, OFF)
    elif k == "pad_n64":
        R(0.14, 0.18, 0.86, 0.46, 0.13)
        R(0.10, 0.30, 0.30, 0.88, 0.10)
        R(0.40, 0.34, 0.60, 0.82, 0.10)
        R(0.70, 0.30, 0.90, 0.88, 0.10)
        plus(0.25, 0.34, 0.06, 0.022)
        C(0.50, 0.50, 0.055, OFF)
        C(0.73, 0.30, 0.035, OFF)
        C(0.81, 0.37, 0.035, OFF)
    elif k == "pad_gc":
        R(0.10, 0.24, 0.90, 0.62, 0.19)
        C(0.25, 0.64, 0.17)
        C(0.75, 0.64, 0.17)
        C(0.26, 0.41, 0.085, OFF)
        C(0.26, 0.41, 0.045)
        C(0.72, 0.44, 0.075, OFF)
        C(0.86, 0.38, 0.035, OFF)
        C(0.62, 0.55, 0.035, OFF)
        plus(0.37, 0.57, 0.045, 0.016)
    elif k == "pad_ps":
        R(0.10, 0.27, 0.90, 0.55, 0.14)
        for sx in (1, -1):
            a, b = (0.5 + sx * 0.25, 0.46), (0.5 + sx * 0.32, 0.80)
            L_([a, b], 0.17)
            C(*a, 0.085)
            C(*b, 0.085)
        plus(0.22, 0.42, 0.075, 0.026)
        diamond(0.78, 0.42, 0.065, 0.032)
        C(0.38, 0.58, 0.055, OFF)
        C(0.62, 0.58, 0.055, OFF)
    elif k == "pad_xbox":
        R(0.08, 0.26, 0.92, 0.62, 0.22)
        C(0.24, 0.66, 0.18)
        C(0.76, 0.66, 0.18)
        C(0.25, 0.42, 0.065, OFF)
        plus(0.38, 0.57, 0.05, 0.018)
        diamond(0.74, 0.42, 0.06, 0.03)
        C(0.62, 0.57, 0.055, OFF)
    elif k == "pad_genesis":
        E(0.04, 0.24, 0.96, 0.82)
        E(0.30, 0.66, 0.70, 1.10, OFF)
        plus(0.24, 0.47, 0.09, 0.03)
        for i in range(3):
            C(0.60 + i * 0.105, 0.52 - i * 0.04, 0.045, OFF)
    elif k == "remote":
        R(0.37, 0.03, 0.63, 0.97, 0.12)
        plus(0.50, 0.17, 0.06, 0.022)
        C(0.50, 0.34, 0.055, OFF)
        C(0.50, 0.53, 0.022, OFF)
        C(0.50, 0.61, 0.022, OFF)
        C(0.50, 0.79, 0.035, OFF)
        C(0.50, 0.88, 0.035, OFF)
    elif k == "tablet_pad":
        R(0.02, 0.22, 0.98, 0.78, 0.13)
        R(0.21, 0.30, 0.79, 0.70, 0.03, OFF)
        C(0.115, 0.37, 0.045, OFF)
        plus(0.115, 0.58, 0.045, 0.016)
        diamond(0.885, 0.40, 0.045, 0.022)
        C(0.885, 0.62, 0.045, OFF)
    elif k == "switch":
        R(0.03, 0.24, 0.185, 0.76, 0.08)
        R(0.205, 0.24, 0.795, 0.76, 0.02)
        R(0.815, 0.24, 0.97, 0.76, 0.08)
        R(0.25, 0.30, 0.75, 0.70, 0.02, OFF)
        C(0.11, 0.37, 0.04, OFF)
        C(0.89, 0.55, 0.04, OFF)
        diamond(0.89, 0.37, 0.04, 0.019)
        plus(0.11, 0.56, 0.04, 0.014)
    elif k == "handheld":  # vertical (Game Boy-like)
        R(0.22, 0.03, 0.78, 0.97, 0.10)
        R(0.29, 0.10, 0.71, 0.46, 0.03, OFF)
        plus(0.36, 0.68, 0.075, 0.027)
        C(0.62, 0.66, 0.045, OFF)
        C(0.71, 0.74, 0.045, OFF)
        R(0.43, 0.86, 0.48, 0.88, 0.01, OFF)
        R(0.52, 0.86, 0.57, 0.88, 0.01, OFF)
    elif k == "wide_handheld":  # horizontal (GBA-like)
        R(0.03, 0.25, 0.97, 0.75, 0.17)
        R(0.29, 0.32, 0.71, 0.68, 0.03, OFF)
        plus(0.16, 0.50, 0.07, 0.025)
        C(0.82, 0.47, 0.042, OFF)
        C(0.89, 0.56, 0.042, OFF)
    elif k == "psp":
        R(0.02, 0.31, 0.98, 0.69, 0.19)
        R(0.21, 0.36, 0.79, 0.64, 0.02, OFF)
        plus(0.11, 0.50, 0.05, 0.018)
        diamond(0.89, 0.50, 0.045, 0.022)
    elif k == "dual":
        R(0.12, 0.03, 0.88, 0.47, 0.08)
        R(0.22, 0.09, 0.78, 0.41, 0.025, OFF)
        R(0.10, 0.53, 0.90, 0.97, 0.08)
        R(0.30, 0.59, 0.70, 0.91, 0.025, OFF)
        C(0.20, 0.66, 0.035, OFF)
        plus(0.20, 0.82, 0.045, 0.016)
        diamond(0.80, 0.72, 0.042, 0.019)
    elif k == "goggles":
        R(0.06, 0.26, 0.94, 0.62, 0.15)
        C(0.32, 0.44, 0.10, OFF)
        C(0.68, 0.44, 0.10, OFF)
        R(0.44, 0.60, 0.56, 0.86)
        R(0.30, 0.84, 0.70, 0.92, 0.04)
    elif k == "joystick":
        R(0.18, 0.56, 0.82, 0.90, 0.07)
        R(0.455, 0.16, 0.545, 0.62, 0.03)
        C(0.50, 0.15, 0.065)
        C(0.30, 0.64, 0.055, OFF)
    elif k == "arcade":
        P([(0.10, 0.92), (0.16, 0.60), (0.84, 0.60), (0.90, 0.92)])
        R(0.455, 0.24, 0.545, 0.66, 0.03)
        C(0.50, 0.22, 0.15)
        C(0.68, 0.76, 0.045, OFF)
        C(0.80, 0.72, 0.045, OFF)
        C(0.32, 0.78, 0.035, OFF)
    elif k == "computer":
        R(0.06, 0.06, 0.94, 0.66, 0.07)
        R(0.14, 0.14, 0.86, 0.58, 0.03, OFF)
        R(0.43, 0.64, 0.57, 0.80)
        R(0.24, 0.79, 0.76, 0.89, 0.05)
    elif k == "keyboard":
        P([(0.04, 0.74), (0.12, 0.34), (0.88, 0.34), (0.96, 0.74)])
        R(0.04, 0.70, 0.96, 0.78, 0.03)
        for row, (y, x0, n) in enumerate(((0.42, 0.18, 8), (0.51, 0.16, 8), (0.60, 0.14, 8))):
            for i in range(n):
                x = x0 + i * 0.085
                R(x, y, x + 0.06, y + 0.06, 0.012, OFF)
    elif k == "disc":
        C(0.5, 0.5, 0.46)
        C(0.5, 0.5, 0.15, OFF)
        C(0.5, 0.5, 0.075)
        d.arc([0.17 * S, 0.17 * S, 0.83 * S, 0.83 * S], 200, 250, fill=OFF, width=int(0.045 * S))
        d.arc([0.25 * S, 0.25 * S, 0.75 * S, 0.75 * S], 20, 60, fill=OFF, width=int(0.035 * S))
    elif k == "cart":
        P([(0.18, 0.12), (0.82, 0.12), (0.82, 0.88), (0.30, 0.88), (0.18, 0.76)])
        R(0.28, 0.24, 0.72, 0.56, 0.03, OFF)
        for i in range(5):
            R(0.30 + i * 0.09, 0.74, 0.36 + i * 0.09, 0.88, 0.0, OFF)
    elif k == "phone":
        R(0.27, 0.03, 0.73, 0.97, 0.09)
        R(0.32, 0.12, 0.68, 0.82, 0.03, OFF)
        C(0.5, 0.895, 0.035, OFF)
    elif k == "gear":
        for i in range(8):
            a = i * math.pi / 4
            pts = [((0.5 + rr * math.cos(a + da)), (0.5 + rr * math.sin(a + da)))
                   for da, rr in ((-0.18, 0.30), (-0.12, 0.47), (0.12, 0.47), (0.18, 0.30))]
            P(pts)
        C(0.5, 0.5, 0.34)
        C(0.5, 0.5, 0.13, OFF)
    elif k == "tv":
        R(0.06, 0.24, 0.94, 0.84, 0.08)
        R(0.14, 0.32, 0.86, 0.76, 0.04, OFF)
        L_([(0.34, 0.06), (0.5, 0.24), (0.66, 0.06)], 0.05)
        R(0.28, 0.86, 0.40, 0.94, 0.02)
        R(0.60, 0.86, 0.72, 0.94, 0.02)
    elif k == "pinball":
        R(0.22, 0.04, 0.78, 0.96, 0.10)
        R(0.28, 0.10, 0.72, 0.90, 0.06, OFF)
        C(0.50, 0.36, 0.07)
        C(0.36, 0.22, 0.045)
        C(0.64, 0.22, 0.045)
        L_([(0.34, 0.74), (0.46, 0.80)], 0.045)
        L_([(0.66, 0.74), (0.54, 0.80)], 0.045)
    elif k == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 0.48 if i % 2 == 0 else 0.21
            pts.append((0.5 + r * math.cos(a), 0.53 + r * math.sin(a)))
        P(pts)
    elif k == "clock":
        C(0.5, 0.5, 0.46)
        C(0.5, 0.5, 0.36, OFF)
        L_([(0.5, 0.5), (0.5, 0.24)], 0.07)
        L_([(0.5, 0.5), (0.68, 0.6)], 0.07)
        C(0.5, 0.5, 0.06)
    elif k == "stack":
        for i, (x, y) in enumerate(((0.30, 0.06), (0.18, 0.18), (0.06, 0.30))):
            R(x, y, x + 0.64, y + 0.64, 0.08)
            if i < 2:
                R(x + 0.05, y + 0.05, x + 0.59, y + 0.59, 0.05, OFF)
    elif k == "folder":
        R(0.06, 0.16, 0.48, 0.34, 0.05)
        R(0.06, 0.24, 0.94, 0.86, 0.08)
    else:  # generic console pad
        R(0.06, 0.26, 0.94, 0.66, 0.20)
        C(0.25, 0.62, 0.17)
        C(0.75, 0.62, 0.17)
        plus(0.28, 0.47, 0.10, 0.036)
        C(0.68, 0.42, 0.05, OFF)
        C(0.79, 0.52, 0.05, OFF)
    return m.resize((G, G), Image.LANCZOS)


# Which drawing each system gets (anything missing uses its category glyph).
GLYPHS = {
    "nes": "pad_nes", "famicom": "pad_nes", "mastersystem": "pad_nes", "mark3": "pad_nes",
    "sg-1000": "pad_nes", "gx4000": "pad_nes", "pv1000": "pad_nes", "scv": "pad_nes",
    "snes": "pad_snes", "snesna": "pad_snes", "sfc": "pad_snes", "satellaview": "pad_snes",
    "sgb": "pad_snes", "sufami": "cart", "pcengine": "pad_nes", "tg16": "pad_nes",
    "supergrafx": "pad_nes", "supracan": "pad_snes",
    "n64": "pad_n64", "gc": "pad_gc", "wii": "remote", "wiiu": "tablet_pad",
    "switch": "switch", "gb": "handheld", "gbc": "handheld", "pokemini": "handheld",
    "gamate": "handheld", "gmaster": "handheld", "megaduck": "handheld", "supervision": "handheld",
    "lcdgames": "handheld", "gamecom": "handheld", "arduboy": "handheld",
    "gba": "wide_handheld", "atarilynx": "wide_handheld", "gamegear": "wide_handheld",
    "ngp": "wide_handheld", "ngpc": "wide_handheld", "wonderswan": "wide_handheld",
    "wonderswancolor": "wide_handheld",
    "psp": "psp", "psvita": "psp", "nds": "dual", "n3ds": "dual", "gameandwatch": "dual",
    "virtualboy": "goggles",
    "psx": "pad_ps", "ps2": "pad_ps", "ps3": "pad_ps", "ps4": "pad_ps",
    "xbox": "pad_xbox", "xbox360": "pad_xbox", "xboxone": "pad_xbox",
    "genesis": "pad_genesis", "megadrive": "pad_genesis", "megadrivejp": "pad_genesis",
    "sega32x": "pad_genesis", "sega32xjp": "pad_genesis", "sega32xna": "pad_genesis",
    "saturn": "pad_genesis", "saturnjp": "pad_genesis", "dreamcast": "pad_gc",
    "atari2600": "joystick", "atari5200": "joystick", "atari7800": "joystick",
    "atarijaguar": "pad_genesis", "channelf": "joystick", "astrocde": "joystick",
    "colecovision": "joystick", "intellivision": "joystick", "odyssey2": "joystick",
    "videopac": "joystick", "arcadia": "joystick", "crvision": "joystick", "vectrex": "joystick",
    "multivision": "joystick",
    "c64": "keyboard", "vic20": "keyboard", "plus4": "keyboard", "zxspectrum": "keyboard",
    "zx81": "keyboard", "zxnext": "keyboard", "atari800": "keyboard", "atarixe": "keyboard",
    "atarist": "keyboard", "amiga": "keyboard", "amiga600": "keyboard", "amiga1200": "keyboard",
    "amstradcpc": "keyboard", "bbcmicro": "keyboard", "electron": "keyboard", "msx": "keyboard",
    "msx1": "keyboard", "msx2": "keyboard", "msxturbor": "keyboard", "oric": "keyboard",
    "coco": "keyboard", "trs-80": "keyboard", "dragon32": "keyboard", "tanodragon": "keyboard",
    "ti99": "keyboard", "spectravideo": "keyboard", "samcoupe": "keyboard", "adam": "keyboard",
    "apple2": "keyboard", "archimedes": "keyboard", "moto": "keyboard", "to8": "keyboard",
    "fm7": "keyboard",
    "fpinball": "pinball", "vpinball": "pinball",
    "vsmile": "pad_snes",
}

CATEGORY_GLYPH = {"console": "console", "handheld": "handheld", "dual": "dual", "computer": "computer",
                  "arcade": "arcade", "disc": "disc", "phone": "phone", "gear": "gear", "tv": "tv",
                  "star": "star", "clock": "clock", "stack": "stack", "folder": "folder"}


# ---------------------------------------------------------------- helpers
def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c, d, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c, d))


def lum(c):
    r, g, b = (v / 255 for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def rr_mask(box, rad, size=TILE, ss=4, inset=0):
    m = Image.new("L", (size * ss, size * ss), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rounded_rectangle(
        [(x0 + inset) * ss, (y0 + inset) * ss, (x1 - inset) * ss, (y1 - inset) * ss],
        radius=max(1, (rad - inset)) * ss, fill=255)
    return m.resize((size, size), Image.LANCZOS)


def mul(a, b):
    return Image.fromarray((np.array(a, np.float32) * np.array(b, np.float32) / 255).astype(np.uint8))


def vgrad(c0, c1, y0, y1):
    g = Image.new("RGBA", (TILE, TILE))
    d = ImageDraw.Draw(g)
    for y in range(TILE):
        t = min(max((y - y0) / (y1 - y0), 0), 1)
        d.line([(0, y), (TILE, y)], fill=mix(c0, c1, t) + (255,))
    return g


def shadow(img, box, rad, strength=95, blur=8, dy=9):
    sh = Image.new("L", (TILE, TILE), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 3, y0 + dy, x1 - 3, y1 + dy], radius=rad, fill=strength)
    img.paste((10, 14, 20, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))


def fit_font(path, text, maxw, start, minsize=18):
    size = start
    while size > minsize:
        f = ImageFont.truetype(path, size)
        bb = f.getbbox(text)
        if bb[2] - bb[0] <= maxw:
            return f
        size -= 2
    return ImageFont.truetype(path, minsize)


def draw_label(img, text, font, cx, cy, fill, shade=None):
    bb = font.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tx, ty = cx - tw / 2 - bb[0], cy - th / 2 - bb[1]
    if shade:
        tl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(tl).text((tx, ty + 3), text, font=font, fill=shade)
        img.alpha_composite(tl.filter(ImageFilter.GaussianBlur(2)))
    ImageDraw.Draw(img).text((tx, ty), text, font=font, fill=fill)


def place_glyph(img, gm, x, y, fill, shade=None, shade_dy=5, blur=4):
    if shade:
        s = gm.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * shade[3] / 255))
        img.paste(shade[:3] + (255,), (x, y + shade_dy), s)
    img.paste(fill + (255,) if len(fill) == 3 else fill, (x, y), gm)


# ---------------------------------------------------------------- styles
def tile_3ds(label, kind, colour, fontpath):
    c = hexrgb(colour)
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    x0, y0, x1, y1 = BODY
    cw = x1 - x0
    shadow(img, BODY, RAD)
    mask = rr_mask(BODY, RAD)

    top, bot = mix(c, (255, 255, 255), 0.30), mix(c, (0, 0, 0), 0.16)
    body = vgrad(top, bot, y0, y1)
    # soft radial glow behind the art
    glow = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(glow).ellipse([x0 + cw * 0.12, y0 + cw * 0.02, x1 - cw * 0.12, y0 + cw * 0.78], fill=70)
    body.paste((255, 255, 255, 255), (0, 0), glow.filter(ImageFilter.GaussianBlur(28)))
    # diagonal pinstripes
    st = Image.new("L", (TILE, TILE), 0)
    sd = ImageDraw.Draw(st)
    for k in range(-TILE, TILE * 2, 30):
        sd.line([(k, 0), (k + TILE, TILE)], fill=14, width=10)
    body.paste((255, 255, 255, 255), (0, 0), st)
    img.paste(body, (0, 0), mask)

    # glossy top half
    gl = Image.new("L", (TILE * 4, TILE * 4), 0)
    ImageDraw.Draw(gl).ellipse([(x0 - 80) * 4, (y0 - 210) * 4, (x1 + 80) * 4, (y0 + cw * 0.47) * 4], fill=74)
    img.paste((255, 255, 255, 255), (0, 0), mul(gl.resize((TILE, TILE), Image.LANCZOS), mask))
    # bevel: light inner rim, darker bottom edge
    rim = Image.fromarray(np.clip(np.array(mask, np.int16) - np.array(rr_mask(BODY, RAD, inset=5), np.int16), 0, 255).astype(np.uint8))
    img.paste((255, 255, 255, 255), (0, 0), rim.point(lambda v: v * 0.55))
    lower = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(lower).rectangle([0, y0 + cw * 0.62, TILE, TILE], fill=255)
    img.paste(mix(c, (0, 0, 0), 0.45) + (255,), (0, 0), mul(rim, lower).point(lambda v: v * 0.5))

    G = int(cw * 0.58)
    gm = glyph(kind, G)
    place_glyph(img, gm, x0 + (cw - G) // 2, y0 + int(cw * 0.07), (255, 255, 255),
                shade=mix(c, (0, 0, 0), 0.5) + (120,))
    f = fit_font(fontpath, label, cw * 0.82, 60)
    draw_label(img, label, f, x0 + cw / 2, y0 + cw * 0.82, (255, 255, 255, 255),
               shade=mix(c, (0, 0, 0), 0.55) + (150,))
    return img


def tile_wii(label, kind, colour, fontpath):
    c = hexrgb(colour)
    ink = mix(c, (0, 0, 0), 0.35) if lum(c) > 0.55 else c
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    x0, y0, x1, y1 = BODY
    cw = x1 - x0
    shadow(img, BODY, RAD, strength=70)
    outer = rr_mask(BODY, RAD)
    # silver frame
    img.paste(vgrad((214, 220, 228), (176, 184, 194), y0, y1), (0, 0), outer)
    inner = rr_mask(BODY, RAD, inset=7)
    face = vgrad((255, 255, 255), (232, 237, 243), y0, y1)
    # faint channel scanlines
    sl = Image.new("L", (TILE, TILE), 0)
    sd = ImageDraw.Draw(sl)
    for y in range(0, TILE, 6):
        sd.line([(0, y), (TILE, y)], fill=10, width=2)
    face.paste((120, 140, 160, 255), (0, 0), sl)
    # coloured glow pool behind the art
    pool = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(pool).ellipse([x0 + cw * 0.14, y0 + cw * 0.06, x1 - cw * 0.14, y0 + cw * 0.74], fill=58)
    face.paste(mix(c, (255, 255, 255), 0.25) + (255,), (0, 0), pool.filter(ImageFilter.GaussianBlur(30)))
    img.paste(face, (0, 0), inner)
    # glass highlight on top
    gl = Image.new("L", (TILE * 4, TILE * 4), 0)
    ImageDraw.Draw(gl).ellipse([(x0 - 60) * 4, (y0 - 230) * 4, (x1 + 60) * 4, (y0 + cw * 0.36) * 4], fill=150)
    img.paste((255, 255, 255, 255), (0, 0), mul(gl.resize((TILE, TILE), Image.LANCZOS), inner))
    # thin inner edge line
    edge = Image.fromarray(np.clip(np.array(inner, np.int16) - np.array(rr_mask(BODY, RAD, inset=10), np.int16), 0, 255).astype(np.uint8))
    img.paste((255, 255, 255, 255), (0, 0), edge)

    G = int(cw * 0.56)
    gm = glyph(kind, G)
    place_glyph(img, gm, x0 + (cw - G) // 2, y0 + int(cw * 0.08), ink,
                shade=mix(c, (0, 0, 0), 0.2) + (90,), shade_dy=6, blur=6)
    # glossy sheen on the art
    sheen = Image.new("L", (G, G), 0)
    ImageDraw.Draw(sheen).rectangle([0, 0, G, G * 0.42], fill=70)
    img.paste((255, 255, 255, 255), (x0 + (cw - G) // 2, y0 + int(cw * 0.08)), mul(sheen, gm))
    f = fit_font(fontpath, label, cw * 0.80, 56)
    draw_label(img, label, f, x0 + cw / 2, y0 + cw * 0.82, ink + (255,))
    return img


def tile_wiiu(label, kind, colour, fontpath):
    c = hexrgb(colour)
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    x0, y0, x1, y1 = BODY
    cw = x1 - x0
    shadow(img, BODY, RAD * 0.62, strength=85)
    rad = int(RAD * 0.62)
    mask = rr_mask(BODY, rad)
    body = vgrad(mix(c, (255, 255, 255), 0.12), mix(c, (0, 0, 0), 0.10), y0, y1)
    # big faint watermark of the glyph, tilted
    W = int(cw * 1.25)
    wm = glyph(kind, W).rotate(-14, resample=Image.BICUBIC, expand=False)
    wl = Image.new("L", (TILE, TILE), 0)
    wl.paste(wm, (x0 + int(cw * 0.25), y0 - int(cw * 0.28)))
    body.paste((255, 255, 255, 255), (0, 0), wl.point(lambda v: int(v * 0.14)))
    img.paste(body, (0, 0), mask)
    # white name band
    band_top = y0 + int(cw * 0.70)
    bm = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(bm).rectangle([0, band_top, TILE, TILE], fill=255)
    img.paste((255, 255, 255, 255), (0, 0), mul(bm, mask))
    ImageDraw.Draw(img).line([(x0, band_top), (x1, band_top)], fill=mix(c, (0, 0, 0), 0.25) + (90,), width=2)
    # outline
    rim = Image.fromarray(np.clip(np.array(mask, np.int16) - np.array(rr_mask(BODY, rad, inset=3), np.int16), 0, 255).astype(np.uint8))
    img.paste(mix(c, (0, 0, 0), 0.35) + (255,), (0, 0), rim.point(lambda v: v * 0.6))

    G = int(cw * 0.52)
    gm = glyph(kind, G)
    place_glyph(img, gm, x0 + (cw - G) // 2, y0 + int(cw * 0.09), (255, 255, 255),
                shade=mix(c, (0, 0, 0), 0.5) + (110,), shade_dy=4, blur=3)
    ink = mix(c, (0, 0, 0), 0.35) if lum(c) > 0.55 else c
    f = fit_font(fontpath, label, cw * 0.80, 48)
    draw_label(img, label, f, x0 + cw / 2, band_top + (y1 - band_top) / 2 + 1, ink + (255,))
    return img


STYLES = {"3ds": tile_3ds, "wii": tile_wii, "wiiu": tile_wiiu}

# visible body of the tile relative to the png size (used to place the cursor ring)
BODY_FRAC = (BODY[2] - BODY[0]) / TILE
BODY_OFFSET_FRAC = LIFT / TILE
