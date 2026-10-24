"""Generate all bitmap / font / sound assets for the esdeii ES-DE theme."""
import math, os, shutil, struct, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT = sys.argv[1]
NUNITO_VF = sys.argv[2]
NUNITO_OFL = sys.argv[3]

A = os.path.join(OUT, "assets")
for d in ("fonts", "images", "sounds"):
    os.makedirs(os.path.join(A, d), exist_ok=True)

# ------------------------------------------------------------------ fonts
FONTS = {}
for name, wght in (("Nunito-SemiBold", 600), ("Nunito-ExtraBold", 800), ("Nunito-Black", 900)):
    f = TTFont(NUNITO_VF)
    inst = instancer.instantiateVariableFont(f, {"wght": wght}, updateFontNames=False)
    p = os.path.join(A, "fonts", name + ".ttf")
    inst.save(p)
    FONTS[name] = p
shutil.copy(NUNITO_OFL, os.path.join(A, "fonts", "OFL.txt"))


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c, d, t):
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c, d))


def rr(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


# ------------------------------------------------------------------ simple images
IMG = os.path.join(A, "images")

Image.new("RGBA", (16, 16), (255, 255, 255, 255)).save(os.path.join(IMG, "white.png"))

# DS-style graph-paper background tile: white base with soft grey lines.
# It gets multiplied by the colour scheme's background colour in the theme.
T = 96
bg = Image.new("RGB", (T, T), (255, 255, 255))
d = ImageDraw.Draw(bg)
line = (236, 238, 242)
d.line([(0, 0), (T, 0)], fill=line, width=2)
d.line([(0, 0), (0, T)], fill=line, width=2)
d.line([(0, T // 2), (T, T // 2)], fill=(246, 247, 249), width=1)
d.line([(T // 2, 0), (T // 2, T)], fill=(246, 247, 249), width=1)
bg.save(os.path.join(IMG, "bg-grid.png"))


def supersampled(size, fn, ss=4):
    big = Image.new("RGBA", (size[0] * ss, size[1] * ss), (0, 0, 0, 0))
    fn(ImageDraw.Draw(big), ss, big)
    return big.resize(size, Image.LANCZOS)


# speaker grille (dots), white, tinted in theme
def speaker(d, s, img):
    W, H = img.size
    cols, rows = 3, 6
    r = 7 * s
    for i in range(cols):
        for j in range(rows):
            cx = W / 2 + (i - 1) * 26 * s + (13 * s if j % 2 else 0) - 6 * s
            cy = 20 * s + j * 22 * s
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255))
supersampled((110, 150), speaker).save(os.path.join(IMG, "speaker.png"))


# hinge pill
def pill(d, s, img):
    W, H = img.size
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=H / 2, fill=(255, 255, 255, 255))
supersampled((240, 30), pill).save(os.path.join(IMG, "pill.png"))


# selection cursor ring for the system carousel (white, tinted with accent)
RING = 400
for fname, rad_px in (("cursor.png", 100), ("cursor-square.png", 66)):
    def ring(d, s, img, rad_px=rad_px):
        W, _ = img.size
        t = 16 * s
        rad = rad_px * s
        d.rounded_rectangle([0, 0, W - 1, W - 1], radius=rad, fill=(255, 255, 255, 255))
        d.rounded_rectangle([t, t, W - 1 - t, W - 1 - t], radius=rad - t, fill=(0, 0, 0, 0))
    supersampled((RING, RING), ring).save(os.path.join(IMG, fname))


# rating stars (SVG keeps them crisp)
STAR = "M50 6 L62.9 34.2 L93.8 37.6 L70.8 58.4 L77.2 88.8 L50 73.4 L22.8 88.8 L29.2 58.4 L6.2 37.6 L37.1 34.2 Z"
for name, fill in (("star-filled.svg", "#FFC21A"), ("star-unfilled.svg", "#B9C0CA")):
    with open(os.path.join(IMG, name), "w") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
                 f'<g transform="translate(50 50) scale(0.82) translate(-50 -50)">'
                 f'<path d="{STAR}" fill="{fill}" stroke="{fill}" stroke-width="6" stroke-linejoin="round"/></g></svg>')

# ------------------------------------------------------------------ system tiles
import icons
from systems_data import SYSTEMS, DEFAULT_TILE
for style, fn in icons.STYLES.items():
    d_ = os.path.join(OUT, "systems", style)
    os.makedirs(d_, exist_ok=True)
    for name, (label, kind, colour) in list(SYSTEMS.items()) + [("_default", DEFAULT_TILE)]:
        g = icons.GLYPHS.get(name, icons.CATEGORY_GLYPH.get(kind, "console"))
        fn(label, g, colour, FONTS["Nunito-Black"]).save(os.path.join(d_, name + ".png"), optimize=True)
    print("icons:", style)


def glyph_mask(kind, G):
    return icons.glyph(kind, G)


# placeholder for games without media: a dark "screen" with a small cartridge
def noimage():
    Wd, Hd = 640, 360
    im = Image.new("RGBA", (Wd, Hd), (52, 58, 68, 255))
    d = ImageDraw.Draw(im)
    for k in range(-Hd, Wd, 28):
        d.line([(k, Hd), (k + Hd, 0)], fill=(58, 64, 75, 255), width=10)
    g = glyph_mask("console", 150)
    im.paste((92, 100, 114, 255), ((Wd - 150) // 2, (Hd - 150) // 2), g)
    im.convert("RGB").save(os.path.join(IMG, "noimage.png"), optimize=True)
noimage()


def nocover():
    Wd, Hd = 360, 500
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, Wd - 1, Hd - 1], radius=26, fill=(214, 220, 228, 255))
    d.rounded_rectangle([16, 16, Wd - 17, Hd - 17], radius=16, fill=(238, 241, 245, 255))
    g = glyph_mask("cart", 170)
    im.paste((176, 184, 194, 255), ((Wd - 170) // 2, (Hd - 170) // 2), g)
    im.save(os.path.join(IMG, "nocover.png"), optimize=True)
nocover()

# ------------------------------------------------------------------ sounds
SR = 44100
SND = os.path.join(A, "sounds")


def tone(freqs, dur, vol=0.35, wave_="sine", attack=0.004, decay=None):
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = np.interp(t, np.linspace(0, dur, len(freqs)), freqs) if len(freqs) > 1 else np.full(n, freqs[0])
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave_ == "sine":
        s = np.sin(ph)
    else:  # soft square-ish (DS chime flavour)
        s = np.sin(ph) + 0.25 * np.sin(3 * ph) + 0.08 * np.sin(5 * ph)
        s /= 1.33
    env = np.minimum(1, t / attack) * np.exp(-t / (decay or dur / 3.5))
    return s * env * vol


def seq(parts, gap=0.0):
    out = []
    for p in parts:
        out.append(p)
        if gap:
            out.append(np.zeros(int(SR * gap)))
    return np.concatenate(out)


def save(name, s):
    s = np.concatenate([s, np.zeros(int(SR * 0.01))])
    data = (np.clip(s, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(os.path.join(SND, name), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)


save("scroll.wav", tone([1760], 0.035, 0.22, "soft", decay=0.010))
save("systembrowse.wav", tone([1318, 1568], 0.06, 0.25, "soft", decay=0.018))
save("quicksysselect.wav", seq([tone([1175], 0.05, 0.25, "soft", decay=0.015), tone([1568], 0.07, 0.25, "soft", decay=0.02)]))
save("select.wav", seq([tone([1047], 0.06, 0.3, "soft", decay=0.02), tone([1568], 0.12, 0.3, "soft", decay=0.04)]))
save("back.wav", seq([tone([988], 0.06, 0.28, "soft", decay=0.02), tone([659], 0.11, 0.28, "soft", decay=0.035)]))
save("favorite.wav", seq([tone([1568], 0.05, 0.25, decay=0.02), tone([2093], 0.05, 0.25, decay=0.02), tone([2637], 0.14, 0.25, decay=0.05)]))
save("launch.wav", seq([tone([f], 0.09, 0.28, "soft", decay=0.04) for f in (784, 988, 1175)] + [tone([1568], 0.32, 0.3, "soft", decay=0.12)]))

print("assets done")
