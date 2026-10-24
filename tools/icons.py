"""System icon artwork for esdeii.

Every tile uses the same glassy white frame with the artwork inset (the
console menu look from the reference screenshots). Three art styles:
  glossy  - colourful gradient art, 3D white object, white name
  channel - white art panel, 3D coloured object, grey name, colour swoosh
  plaza   - bold colour art panel, 3D white object, dark name band
Glyph silhouettes live in shapes.py.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import shapes

TILE = 360
BODY = (20, 14, 340, 334)      # glass frame (visible tile)
RAD = 70                       # frame corner radius
INSET = 24                     # frame thickness
IRAD = 44                      # artwork corner radius
ART = (BODY[0] + INSET, BODY[1] + INSET, BODY[2] - INSET, BODY[3] - INSET)

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
    "psp": "psp", "psvita": "psp", "nds": "dual", "n3ds": "dual3d", "gameandwatch": "dual",
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


def rr_mask(box, rad, size=TILE, ss=4):
    m = Image.new("L", (size * ss, size * ss), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(m).rounded_rectangle([x0 * ss, y0 * ss, x1 * ss, y1 * ss], radius=rad * ss, fill=255)
    return m.resize((size, size), Image.LANCZOS)


def inset(box, d):
    return (box[0] + d, box[1] + d, box[2] - d, box[3] - d)


def mul(*ms):
    a = np.array(ms[0], np.float32)
    for m in ms[1:]:
        a = a * np.array(m, np.float32) / 255
    return Image.fromarray(a.astype(np.uint8))


def sub(a, b):
    return Image.fromarray(np.clip(np.array(a, np.int16) - np.array(b, np.int16), 0, 255).astype(np.uint8))


def scale(m, k):
    return m.point(lambda v: int(v * k))


def vgrad(c0, c1, y0, y1, size=TILE):
    g = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(g)
    for y in range(size):
        t = min(max((y - y0) / max(1, (y1 - y0)), 0), 1)
        d.line([(0, y), (size, y)], fill=tuple(mix(c0, c1, t)) + (255,))
    return g


def shift(m, dx, dy, size=TILE):
    out = Image.new("L", (size, size), 0)
    out.paste(m, (dx, dy))
    return out


def fit_font(path, text, maxw, start, minsize=16):
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


def object3d(img, kind, size, x, y, top, bottom, edge, clip=None, gloss=0.55, drop=(0, 0, 0, 70)):
    """Paint a glossy 3D object (extruded glyph) onto img."""
    g = shapes.glyph(kind, size)
    m = Image.new("L", (TILE, TILE), 0)
    m.paste(g, (x, y))
    depth = max(3, int(size * 0.035))
    # soft drop shadow
    sh = shift(m, 0, depth + 3).filter(ImageFilter.GaussianBlur(size * 0.03))
    if clip is not None:
        sh = mul(sh, clip)
    img.paste(drop[:3] + (255,), (0, 0), scale(sh, drop[3] / 255))
    # extrusion (side walls)
    ext = Image.new("L", (TILE, TILE), 0)
    for k in range(1, depth + 1):
        ext = Image.fromarray(np.maximum(np.array(ext), np.array(shift(m, 0, k))))
    if clip is not None:
        ext = mul(ext, clip)
    img.paste(tuple(edge) + (255,), (0, 0), ext)
    # face with vertical gradient
    bb = g.getbbox() or (0, 0, size, size)
    fy0, fy1 = y + bb[1], y + bb[3]
    face = vgrad(top, bottom, fy0, fy1)
    img.paste(face, (0, 0), m)
    # crisp top-edge highlight
    rim = sub(m, shift(m, 0, 2))
    img.paste((255, 255, 255, 255), (0, 0), scale(rim, 0.8))
    # gloss over the upper part
    gl = Image.new("L", (TILE * 2, TILE * 2), 0)
    gx0, gx1 = (x + bb[0]) * 2, (x + bb[2]) * 2
    h = fy1 - fy0
    ImageDraw.Draw(gl).ellipse([gx0 - h * 0.6, (fy0 - h * 0.9) * 2, gx1 + h * 0.6, (fy0 + h * 0.48) * 2], fill=255)
    gl = gl.resize((TILE, TILE), Image.LANCZOS)
    img.paste((255, 255, 255, 255), (0, 0), scale(mul(gl, m), gloss * 0.6))


def frame(img):
    """Glassy white frame + returns the artwork mask."""
    sh = Image.new("L", (TILE, TILE), 0)
    x0, y0, x1, y1 = BODY
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 4, y0 + 10, x1 - 4, y1 + 10], radius=RAD, fill=80)
    img.paste((20, 30, 45, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(9)))
    outer = rr_mask(BODY, RAD)
    img.paste((178, 188, 199, 255), (0, 0), outer)                       # outer edge
    body = rr_mask(inset(BODY, 3), RAD - 3)
    img.paste(vgrad((255, 255, 255), (226, 232, 238), y0, y1), (0, 0), body)
    # glassy highlight across the top of the frame
    hl = Image.new("L", (TILE * 2, TILE * 2), 0)
    ImageDraw.Draw(hl).ellipse([(x0 - 40) * 2, (y0 - 200) * 2, (x1 + 40) * 2, (y0 + 120) * 2], fill=255)
    img.paste((255, 255, 255, 255), (0, 0), scale(mul(hl.resize((TILE, TILE), Image.LANCZOS), body), 0.7))
    # recessed lip around the artwork
    lip = rr_mask(inset(ART, -3), IRAD + 3)
    img.paste((160, 170, 182, 255), (0, 0), lip)
    lip2 = rr_mask(inset(ART, -1), IRAD + 1)
    img.paste((205, 212, 220, 255), (0, 0), lip2)
    return rr_mask(ART, IRAD)


def art_gloss(img, art, strength=0.35):
    x0, y0, x1, y1 = ART
    gl = Image.new("L", (TILE * 2, TILE * 2), 0)
    ImageDraw.Draw(gl).ellipse([(x0 - 70) * 2, (y0 - 230) * 2, (x1 + 70) * 2, (y0 + (y1 - y0) * 0.42) * 2], fill=255)
    img.paste((255, 255, 255, 255), (0, 0), scale(mul(gl.resize((TILE, TILE), Image.LANCZOS), art), strength))


# ---------------------------------------------------------------- styles
AW = ART[2] - ART[0]


def tile_glossy(label, kind, colour, fontpath):
    c = hexrgb(colour)
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    art = frame(img)
    x0, y0, x1, y1 = ART
    bg = vgrad(mix(c, (255, 255, 255), 0.30), mix(c, (0, 0, 0), 0.18), y0, y1)
    glow = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(glow).ellipse([x0 + AW * 0.1, y0 + AW * 0.0, x1 - AW * 0.1, y0 + AW * 0.75], fill=90)
    bg.paste((255, 255, 255, 255), (0, 0), glow.filter(ImageFilter.GaussianBlur(26)))
    st = Image.new("L", (TILE, TILE), 0)
    sd = ImageDraw.Draw(st)
    for k in range(-TILE, TILE * 2, 26):
        sd.line([(k, 0), (k + TILE, TILE)], fill=12, width=9)
    bg.paste((255, 255, 255, 255), (0, 0), st)
    img.paste(bg, (0, 0), art)
    S = int(AW * 0.66)
    object3d(img, kind, S, x0 + (AW - S) // 2, y0 + int(AW * 0.03), (255, 255, 255), (226, 232, 240),
             mix(c, (0, 0, 0), 0.38), clip=art, drop=mix(c, (0, 0, 0), 0.6) + (110,))
    f = fit_font(fontpath, label, AW * 0.84, 46)
    draw_label(img, label, f, x0 + AW / 2, y0 + AW * 0.83, (255, 255, 255, 255),
               shade=mix(c, (0, 0, 0), 0.55) + (170,))
    art_gloss(img, art, 0.28)
    return img


def tile_channel(label, kind, colour, fontpath):
    c = hexrgb(colour)
    ink = mix(c, (0, 0, 0), 0.30) if lum(c) > 0.55 else c
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    art = frame(img)
    x0, y0, x1, y1 = ART
    bg = vgrad((255, 255, 255), (234, 238, 243), y0, y1)
    # colour swoosh along the bottom (channel style)
    sw = Image.new("L", (TILE * 2, TILE * 2), 0)
    sd = ImageDraw.Draw(sw)
    sd.ellipse([(x0 - AW * 0.6) * 2, (y1 - AW * 0.13) * 2, (x1 + AW * 0.9) * 2, (y1 + AW * 0.62) * 2], fill=255)
    sd.ellipse([(x0 - AW * 0.7) * 2, (y1 - AW * 0.095) * 2, (x1 + AW * 0.8) * 2, (y1 + AW * 0.66) * 2], fill=0)
    sw = sw.resize((TILE, TILE), Image.LANCZOS)
    fill = Image.new("L", (TILE * 2, TILE * 2), 0)
    ImageDraw.Draw(fill).ellipse([(x0 - AW * 0.7) * 2, (y1 - AW * 0.065) * 2, (x1 + AW * 0.8) * 2,
                                  (y1 + AW * 0.66) * 2], fill=255)
    fill = fill.resize((TILE, TILE), Image.LANCZOS)
    bg.paste(mix(c, (255, 255, 255), 0.15) + (255,), (0, 0), sw)
    bg.paste(mix(c, (255, 255, 255), 0.62) + (255,), (0, 0), fill)
    img.paste(bg, (0, 0), art)
    S = int(AW * 0.58)
    object3d(img, kind, S, x0 + (AW - S) // 2, y0 + int(AW * 0.04), mix(c, (255, 255, 255), 0.25),
             mix(c, (0, 0, 0), 0.08), mix(c, (0, 0, 0), 0.40), clip=art, drop=(40, 50, 70, 60))
    f = fit_font(fontpath, label, AW * 0.80, 44)
    draw_label(img, label, f, x0 + AW / 2, y0 + AW * 0.735, (126, 133, 142, 255))
    art_gloss(img, art, 0.22)
    return img


def tile_plaza(label, kind, colour, fontpath):
    c = hexrgb(colour)
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    art = frame(img)
    x0, y0, x1, y1 = ART
    bg = vgrad(mix(c, (255, 255, 255), 0.18), mix(c, (0, 0, 0), 0.20), y0, y1)
    # radial spotlight + large faint watermark
    glow = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(glow).ellipse([x0 - AW * 0.1, y0 - AW * 0.2, x1 + AW * 0.1, y0 + AW * 0.7], fill=80)
    bg.paste((255, 255, 255, 255), (0, 0), glow.filter(ImageFilter.GaussianBlur(30)))
    W = int(AW * 1.3)
    wm = shapes.glyph(kind, W).rotate(-16, resample=Image.BICUBIC)
    wl = Image.new("L", (TILE, TILE), 0)
    wl.paste(wm, (x0 + int(AW * 0.25), y0 - int(AW * 0.30)))
    bg.paste((255, 255, 255, 255), (0, 0), scale(wl, 0.10))
    img.paste(bg, (0, 0), art)
    S = int(AW * 0.62)
    object3d(img, kind, S, x0 + (AW - S) // 2, y0 + int(AW * 0.02), (255, 255, 255), (222, 228, 236),
             mix(c, (0, 0, 0), 0.42), clip=art, drop=(0, 0, 0, 100))
    # dark name band (like a store / virtual console strip)
    band_top = y0 + int(AW * 0.74)
    bm = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(bm).rectangle([0, band_top, TILE, TILE], fill=255)
    img.paste((38, 42, 48, 255), (0, 0), scale(mul(bm, art), 0.9))
    ImageDraw.Draw(img).line([(x0, band_top), (x1, band_top)], fill=(255, 255, 255, 60), width=2)
    f = fit_font(fontpath, label, AW * 0.82, 40)
    draw_label(img, label, f, x0 + AW / 2, band_top + (y1 - band_top) / 2, (255, 255, 255, 255))
    art_gloss(img, art, 0.25)
    return img


STYLES = {"glossy": tile_glossy, "channel": tile_channel, "plaza": tile_plaza}

# visible body of the tile relative to the png size (used to place the cursor ring)
BODY_FRAC = (BODY[2] - BODY[0]) / TILE
BODY_OFFSET_FRAC = ((BODY[1] + BODY[3]) / 2 - TILE / 2) / TILE
