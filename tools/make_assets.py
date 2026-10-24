"""Generate all bitmap / font / sound assets for the esdeii ES-DE theme."""
import math, os, shutil, struct, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from systems_data import SYSTEMS, DEFAULT_TILE

OUT = sys.argv[1]
NUNITO_VF = sys.argv[2]
NUNITO_OFL = sys.argv[3]

A = os.path.join(OUT, "assets")
for d in ("fonts", "images", "sounds"):
    os.makedirs(os.path.join(A, d), exist_ok=True)
os.makedirs(os.path.join(OUT, "systems"), exist_ok=True)

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


# d-pad, white
def dpad(d, s, img):
    W, _ = img.size
    a, w, r = W * 0.46, W * 0.17, W * 0.05
    c = W / 2
    d.rounded_rectangle([c - w, c - a, c + w, c + a], radius=r, fill=(255, 255, 255, 255))
    d.rounded_rectangle([c - a, c - w, c + a, c + w], radius=r, fill=(255, 255, 255, 255))
    rad = w * 0.55
    d.ellipse([c - rad, c - rad, c + rad, c + rad], fill=(0, 0, 0, 0))
supersampled((160, 160), dpad).save(os.path.join(IMG, "dpad.png"))


# four face buttons in a diamond, white
def face(d, s, img):
    W, _ = img.size
    c, off, r = W / 2, W * 0.29, W * 0.155
    for dx, dy in ((0, -off), (off, 0), (0, off), (-off, 0)):
        d.ellipse([c + dx - r, c + dy - r, c + dx + r, c + dy + r], fill=(255, 255, 255, 255))
supersampled((160, 160), face).save(os.path.join(IMG, "buttons.png"))


# hinge pill
def pill(d, s, img):
    W, H = img.size
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=H / 2, fill=(255, 255, 255, 255))
supersampled((240, 30), pill).save(os.path.join(IMG, "pill.png"))


# selection cursor ring for the system carousel (white, tinted with accent)
RING = 400
def ring(d, s, img):
    W, _ = img.size
    t = 16 * s
    rad = 92 * s
    d.rounded_rectangle([0, 0, W - 1, W - 1], radius=rad, fill=(255, 255, 255, 255))
    d.rounded_rectangle([t, t, W - 1 - t, W - 1 - t], radius=rad - t, fill=(0, 0, 0, 0))
supersampled((RING, RING), ring).save(os.path.join(IMG, "cursor.png"))


# rating stars (SVG keeps them crisp)
STAR = "M50 6 L62.9 34.2 L93.8 37.6 L70.8 58.4 L77.2 88.8 L50 73.4 L22.8 88.8 L29.2 58.4 L6.2 37.6 L37.1 34.2 Z"
for name, fill in (("star-filled.svg", "#FFC21A"), ("star-unfilled.svg", "#B9C0CA")):
    with open(os.path.join(IMG, name), "w") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
                 f'<g transform="translate(50 50) scale(0.82) translate(-50 -50)">'
                 f'<path d="{STAR}" fill="{fill}" stroke="{fill}" stroke-width="6" stroke-linejoin="round"/></g></svg>')

# ------------------------------------------------------------------ glyphs
def glyph_mask(kind, G):
    """Return an L-mode mask (G x G) of a white glyph."""
    ss = 4
    S = G * ss
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    on, off = 255, 0

    def R(x0, y0, x1, y1, r, f=on):
        d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=f)

    def C(cx, cy, r, f=on):
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=f)

    def plus(cx, cy, a, w, f=off):
        R(cx - w, cy - a, cx + w, cy + a, w * 0.3, f)
        R(cx - a, cy - w, cx + a, cy + w, w * 0.3, f)

    if kind == "console":
        R(0.06, 0.26, 0.94, 0.66, 0.20)
        C(0.25, 0.62, 0.17)
        C(0.75, 0.62, 0.17)
        plus(0.28, 0.47, 0.10, 0.036)
        C(0.68, 0.42, 0.05, off)
        C(0.79, 0.52, 0.05, off)
    elif kind == "handheld":
        R(0.22, 0.03, 0.78, 0.97, 0.10)
        R(0.30, 0.11, 0.70, 0.47, 0.03, off)
        plus(0.36, 0.70, 0.075, 0.028)
        C(0.62, 0.66, 0.042, off)
        C(0.70, 0.75, 0.042, off)
    elif kind == "dual":
        R(0.10, 0.03, 0.90, 0.47, 0.08)
        R(0.22, 0.09, 0.78, 0.41, 0.025, off)
        R(0.10, 0.53, 0.90, 0.97, 0.08)
        R(0.30, 0.59, 0.70, 0.91, 0.025, off)
        plus(0.20, 0.71, 0.052, 0.02)
        C(0.80, 0.70, 0.032, off)
    elif kind == "computer":
        R(0.06, 0.08, 0.94, 0.68, 0.07)
        R(0.14, 0.16, 0.86, 0.60, 0.03, off)
        R(0.43, 0.66, 0.57, 0.82, 0.0)
        R(0.26, 0.80, 0.74, 0.90, 0.05)
    elif kind == "arcade":
        R(0.14, 0.66, 0.86, 0.94, 0.09)
        R(0.455, 0.30, 0.545, 0.72, 0.03)
        C(0.50, 0.24, 0.17)
        C(0.70, 0.80, 0.045, off)
        C(0.30, 0.80, 0.045, off)
    elif kind == "disc":
        C(0.5, 0.5, 0.46)
        C(0.5, 0.5, 0.15, off)
        C(0.5, 0.5, 0.07)
        d.arc([0.18 * S, 0.18 * S, 0.82 * S, 0.82 * S], 200, 250, fill=off, width=int(0.04 * S))
    elif kind == "phone":
        R(0.27, 0.03, 0.73, 0.97, 0.09)
        R(0.32, 0.12, 0.68, 0.82, 0.03, off)
        C(0.5, 0.895, 0.035, off)
    elif kind == "gear":
        cx = cy = 0.5
        for k in range(8):
            a = k * math.pi / 4
            pts = []
            for da, rr_ in ((-0.17, 0.30), (-0.11, 0.46), (0.11, 0.46), (0.17, 0.30)):
                pts.append(((cx + rr_ * math.cos(a + da)) * S, (cy + rr_ * math.sin(a + da)) * S))
            d.polygon(pts, fill=on)
        C(cx, cy, 0.34)
        C(cx, cy, 0.13, off)
    elif kind == "tv":
        R(0.06, 0.24, 0.94, 0.84, 0.08)
        R(0.14, 0.32, 0.86, 0.76, 0.04, off)
        d.line([(0.34 * S, 0.06 * S), (0.5 * S, 0.24 * S), (0.66 * S, 0.06 * S)], fill=on, width=int(0.05 * S), joint="curve")
        R(0.28, 0.86, 0.40, 0.94, 0.02)
        R(0.60, 0.86, 0.72, 0.94, 0.02)
    elif kind == "star":
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            r = 0.48 if k % 2 == 0 else 0.21
            pts.append(((0.5 + r * math.cos(a)) * S, (0.53 + r * math.sin(a)) * S))
        d.polygon(pts, fill=on)
    elif kind == "clock":
        C(0.5, 0.5, 0.46)
        C(0.5, 0.5, 0.36, off)
        d.line([(0.5 * S, 0.5 * S), (0.5 * S, 0.24 * S)], fill=on, width=int(0.07 * S))
        d.line([(0.5 * S, 0.5 * S), (0.68 * S, 0.6 * S)], fill=on, width=int(0.07 * S))
        C(0.5, 0.5, 0.06)
    elif kind == "stack":
        for i, (x, y) in enumerate(((0.30, 0.06), (0.18, 0.18), (0.06, 0.30))):
            R(x, y, x + 0.64, y + 0.64, 0.08)
            if i < 2:
                R(x + 0.05, y + 0.05, x + 0.59, y + 0.59, 0.05, off)
    elif kind == "folder":
        R(0.06, 0.16, 0.48, 0.34, 0.05)
        R(0.06, 0.24, 0.94, 0.86, 0.08)
    return m.resize((G, G), Image.LANCZOS)


# ------------------------------------------------------------------ system tiles
TILE = 320
PAD = 18  # transparent margin, holds the drop shadow


def load_font(path, size):
    return ImageFont.truetype(path, size)


def make_tile(label, kind, colour, out_path, show_label=True):
    c = hexrgb(colour)
    top = mix(c, (255, 255, 255), 0.22)
    bot = mix(c, (0, 0, 0), 0.10)
    x0, y0, x1, y1 = PAD, PAD - 4, TILE - PAD, TILE - PAD - 4
    rad = 70

    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))

    # shadow
    sh = Image.new("L", (TILE, TILE), 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 2, y0 + 9, x1 - 2, y1 + 9], radius=rad, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    img.paste((0, 0, 0, 255), (0, 0), sh)

    # body mask (supersampled for smooth corners)
    ss = 4
    mbig = Image.new("L", (TILE * ss, TILE * ss), 0)
    ImageDraw.Draw(mbig).rounded_rectangle([x0 * ss, y0 * ss, x1 * ss, y1 * ss], radius=rad * ss, fill=255)
    mask = mbig.resize((TILE, TILE), Image.LANCZOS)

    # gradient fill
    grad = Image.new("RGBA", (TILE, TILE))
    gd = ImageDraw.Draw(grad)
    for y in range(TILE):
        t = min(max((y - y0) / (y1 - y0), 0), 1)
        gd.line([(0, y), (TILE, y)], fill=mix(top, bot, t) + (255,))
    # soft diagonal stripes
    st = Image.new("L", (TILE, TILE), 0)
    sd = ImageDraw.Draw(st)
    for k in range(-TILE, TILE * 2, 34):
        sd.line([(k, 0), (k + TILE, TILE)], fill=16, width=12)
    grad.paste((255, 255, 255, 255), (0, 0), st)
    img.paste(grad, (0, 0), mask)

    # gloss: top highlight
    gl = Image.new("L", (TILE * ss, TILE * ss), 0)
    ImageDraw.Draw(gl).ellipse([(x0 - 60) * ss, (y0 - 170) * ss, (x1 + 60) * ss, (y0 + 125) * ss], fill=60)
    gl = gl.resize((TILE, TILE), Image.LANCZOS)
    gl = Image.fromarray((np.array(gl).astype(np.float32) * np.array(mask).astype(np.float32) / 255).astype(np.uint8))
    img.paste((255, 255, 255, 255), (0, 0), gl)

    # inner rim
    rimbig = Image.new("L", (TILE * ss, TILE * ss), 0)
    rd = ImageDraw.Draw(rimbig)
    rd.rounded_rectangle([x0 * ss, y0 * ss, x1 * ss, y1 * ss], radius=rad * ss, fill=110)
    t = 5 * ss
    rd.rounded_rectangle([x0 * ss + t, y0 * ss + t, x1 * ss - t, y1 * ss - t], radius=rad * ss - t, fill=0)
    img.paste((255, 255, 255, 255), (0, 0), rimbig.resize((TILE, TILE), Image.LANCZOS))

    # glyph
    cw = x1 - x0
    G = int(cw * (0.50 if show_label else 0.62))
    gm = glyph_mask(kind, G)
    gx = x0 + (cw - G) // 2
    gy = y0 + int(cw * (0.12 if show_label else 0.19))
    shadow = gm.filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.35))
    img.paste(mix(c, (0, 0, 0), 0.45) + (255,), (gx, gy + 4), shadow)
    img.paste((255, 255, 255, 255), (gx, gy), gm)

    # label
    if show_label:
        maxw = cw * 0.84
        size = 64
        while size > 20:
            f = load_font(FONTS["Nunito-Black"], size)
            bb = f.getbbox(label)
            if bb[2] - bb[0] <= maxw:
                break
            size -= 2
        bb = f.getbbox(label)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = x0 + (cw - tw) / 2 - bb[0]
        cy = y0 + cw * 0.80
        ty = cy - th / 2 - bb[1]
        tl = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
        ImageDraw.Draw(tl).text((tx, ty + 3), label, font=f, fill=mix(c, (0, 0, 0), 0.5) + (120,))
        tl = tl.filter(ImageFilter.GaussianBlur(2))
        img.alpha_composite(tl)
        ImageDraw.Draw(img).text((tx, ty), label, font=f, fill=(255, 255, 255, 255))

    img.save(out_path, optimize=True)


for name, (label, kind, colour) in SYSTEMS.items():
    make_tile(label, kind, colour, os.path.join(OUT, "systems", name + ".png"))
make_tile(*DEFAULT_TILE, os.path.join(OUT, "systems", "_default.png"))

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
