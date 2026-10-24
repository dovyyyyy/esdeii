"""Theme-specific artwork: backgrounds, Wii-style clock bar, menu buttons,
selector frames and empty slot frames."""
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import icons
import shapes
from icons import mix, mul, scale, rr_mask, vgrad, frame


def ss_draw(size, fn, ss=4):
    big = Image.new("RGBA", (size[0] * ss, size[1] * ss), (0, 0, 0, 0))
    fn(ImageDraw.Draw(big), ss, big)
    return big.resize(size, Image.LANCZOS)


# ---------------------------------------------------------------- backgrounds (white-based, tinted in theme)
def bg_wii(path):
    im = Image.new("RGB", (64, 14), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.line([(0, 0), (64, 0)], fill=(238, 240, 243), width=3)
    im.save(path)


def bg_wiiu(path):
    T = 120
    im = Image.new("RGB", (T, T), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for k in range(-T, 2 * T, 30):
        d.line([(k, T), (k + T, 0)], fill=(243, 245, 247), width=8)
    im.save(path)


def wiiu_swirl(path, W=1920, H=1080):
    """Faint white swooshes laid over the Wii U background."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay = Image.new("L", (W * 2, H * 2), 0)
    d = ImageDraw.Draw(lay)
    for k, (cx, cy, r, w) in enumerate(((W * 0.18, H * 1.3, H * 1.05, 90), (W * 0.95, H * -0.2, H * 0.75, 70),
                                        (W * 0.55, H * 1.6, H * 1.25, 40))):
        d.ellipse([(cx - r) * 2, (cy - r) * 2, (cx + r) * 2, (cy + r) * 2], outline=255, width=w * 2)
    lay = lay.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    im.paste((255, 255, 255, 255), (0, 0), scale(lay, 0.55))
    im.save(path, optimize=True)


# ---------------------------------------------------------------- Wii-style bottom bar
def wii_bar(path_bar, path_line, W=2400, H=300):
    """Curved bottom bar (grayscale, tinted in theme) plus its accent line."""
    def outline(scale_=1):
        pts = []
        bump = 430
        for i in range(0, W + 1, 4):
            if i < bump:
                t = i / bump
                y = 22 + (1 - math.cos(t * math.pi)) / 2 * 88
            elif i > W - bump:
                t = (W - i) / bump
                y = 22 + (1 - math.cos(t * math.pi)) / 2 * 88
            else:
                y = 110
            pts.append((i * scale_, y * scale_))
        return pts
    ss = 2
    bar = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(bar)
    pts = outline(ss)
    d.polygon(pts + [(W * ss, H * ss), (0, H * ss)], fill=255)
    bar = bar.resize((W, H), Image.LANCZOS)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(g)
    for y in range(H):
        t = y / H
        v = int(255 - 26 * t)
        gd.line([(0, y), (W, y)], fill=(v, v, v, 255))
    img.paste(g, (0, 0), bar)
    img.save(path_bar, optimize=True)
    ln = Image.new("L", (W * ss, H * ss), 0)
    ImageDraw.Draw(ln).line(pts, fill=255, width=6 * ss)
    line = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    line.putalpha(ln.resize((W, H), Image.LANCZOS))
    line.save(path_line, optimize=True)


def round_button(path, glyph_kind, S=300):
    """Glossy round menu button with a grey glyph."""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    def body(d, s, big):
        W = big.size[0]
        d.ellipse([10 * s, 16 * s, W - 10 * s, W - 4 * s], fill=(20, 30, 45, 70))
    img.alpha_composite(ss_draw((S, S), body).filter(ImageFilter.GaussianBlur(5)))
    def ringd(d, s, big):
        W = big.size[0]
        d.ellipse([12 * s, 8 * s, W - 12 * s, W - 16 * s], fill=(186, 194, 203, 255))
        d.ellipse([18 * s, 14 * s, W - 18 * s, W - 22 * s], fill=(255, 255, 255, 255))
    img.alpha_composite(ss_draw((S, S), ringd))
    shade = Image.new("L", (S, S), 0)
    ImageDraw.Draw(shade).ellipse([18, S * 0.42, S - 18, S - 22], fill=40)
    inner = Image.new("L", (S, S), 0)
    ImageDraw.Draw(inner).ellipse([18, 14, S - 18, S - 22], fill=255)
    img.paste((150, 160, 172, 255), (0, 0), mul(shade.filter(ImageFilter.GaussianBlur(20)), inner))
    g = shapes.glyph(glyph_kind, int(S * 0.42))
    gx = (S - g.size[0]) // 2
    gy = int(S * 0.46 - g.size[1] / 2)
    img.paste((140, 147, 156, 255), (gx, gy), g)
    img.save(path, optimize=True)


# ---------------------------------------------------------------- selectors
def wii_selector(path, W=480, H=300):
    """Glowing rounded ring for the wide channel grid (white, tinted)."""
    x0, y0, x1, y1 = icons.WBODY
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).rounded_rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], radius=icons.WRAD + 4,
                                           outline=255, width=14)
    img.paste((255, 255, 255, 255), (0, 0), scale(glow.filter(ImageFilter.GaussianBlur(7)), 0.9))
    ring = Image.new("L", (W * 4, H * 4), 0)
    ImageDraw.Draw(ring).rounded_rectangle([(x0 - 2) * 4, (y0 - 2) * 4, (x1 + 2) * 4, (y1 + 2) * 4],
                                           radius=(icons.WRAD + 2) * 4, outline=255, width=7 * 4)
    img.paste((255, 255, 255, 255), (0, 0), ring.resize((W, H), Image.LANCZOS))
    img.save(path, optimize=True)


def wiiu_selector(path, fontpath, S=360, colour=(31, 184, 232)):
    """Cyan glass frame with a 'Start' tab, drawn over the selected tile."""
    x0, y0, x1, y1 = icons.BODY
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], radius=icons.RAD + 6, outline=255, width=16)
    img.paste(colour + (255,), (0, 0), scale(glow.filter(ImageFilter.GaussianBlur(8)), 0.8))
    ring = Image.new("L", (S * 4, S * 4), 0)
    ImageDraw.Draw(ring).rounded_rectangle([(x0 - 3) * 4, (y0 - 3) * 4, (x1 + 3) * 4, (y1 + 3) * 4],
                                           radius=(icons.RAD + 3) * 4, outline=255, width=11 * 4)
    img.paste(colour + (255,), (0, 0), ring.resize((S, S), Image.LANCZOS))
    hl = Image.new("L", (S * 4, S * 4), 0)
    ImageDraw.Draw(hl).rounded_rectangle([(x0 - 1) * 4, (y0 - 1) * 4, (x1 + 1) * 4, (y1 + 1) * 4],
                                         radius=(icons.RAD + 1) * 4, outline=255, width=2 * 4)
    img.paste((255, 255, 255, 255), (0, 0), scale(hl.resize((S, S), Image.LANCZOS), 0.7))
    # Start tab
    tab = (S * 0.26, y1 - 30, S * 0.74, y1 + 10)
    tb = Image.new("L", (S * 4, S * 4), 0)
    ImageDraw.Draw(tb).rounded_rectangle([v * 4 for v in tab], radius=20 * 4, fill=255)
    img.paste(mix(colour, (255, 255, 255), 0.1) + (255,), (0, 0), tb.resize((S, S), Image.LANCZOS))
    f = ImageFont.truetype(fontpath, 26)
    ImageDraw.Draw(img).text(((tab[0] + tab[2]) / 2, (tab[1] + tab[3]) / 2), "Start", font=f,
                             fill=(255, 255, 255, 255), anchor="mm")
    img.save(path, optimize=True)


def square_ring(path, S=360):
    """Plain glowing ring sized to the square tile frame (white, tinted)."""
    x0, y0, x1, y1 = icons.BODY
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    glow = Image.new("L", (S, S), 0)
    ImageDraw.Draw(glow).rounded_rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], radius=icons.RAD + 6, outline=255, width=16)
    img.paste((255, 255, 255, 255), (0, 0), scale(glow.filter(ImageFilter.GaussianBlur(8)), 0.75))
    ring = Image.new("L", (S * 4, S * 4), 0)
    ImageDraw.Draw(ring).rounded_rectangle([(x0 - 3) * 4, (y0 - 3) * 4, (x1 + 3) * 4, (y1 + 3) * 4],
                                           radius=(icons.RAD + 3) * 4, outline=255, width=10 * 4)
    img.paste((255, 255, 255, 255), (0, 0), ring.resize((S, S), Image.LANCZOS))
    img.save(path, optimize=True)


# ---------------------------------------------------------------- empty slots
def slot_square(path):
    """Glass frame with an empty light inner area (grid item background)."""
    img = Image.new("RGBA", (icons.TILE, icons.TILE), (0, 0, 0, 0))
    art = frame(img)
    x0, y0, x1, y1 = icons.ART
    img.paste(vgrad((246, 248, 250), (232, 236, 241), y0, y1), (0, 0), art)
    img.save(path, optimize=True)


def slot_wide(path):
    W, H = icons.WT_W, icons.WT_H
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = icons.WBODY
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([x0 + 4, y0 + 8, x1 - 4, y1 + 8], radius=icons.WRAD, fill=60)
    img.paste((20, 30, 45, 255), (0, 0), sh.filter(ImageFilter.GaussianBlur(7)))
    img.paste((186, 193, 202, 255), (0, 0), icons._rr(icons.WBODY, icons.WRAD, (W, H)))
    img.paste(icons._vgrad((255, 255, 255), (232, 236, 240), y0, y1, (W, H)), (0, 0),
              icons._rr((x0 + 2.5, y0 + 2.5, x1 - 2.5, y1 - 2.5), icons.WRAD - 2.5, (W, H)))
    img.save(path, optimize=True)


def build_all(img_dir, fontpath):
    bg_wii(os.path.join(img_dir, "bg-wii.png"))
    bg_wiiu(os.path.join(img_dir, "bg-wiiu.png"))
    wiiu_swirl(os.path.join(img_dir, "wiiu-swirl.png"))
    wii_bar(os.path.join(img_dir, "wii-bar.png"), os.path.join(img_dir, "wii-bar-line.png"))
    bubbles_lottie(os.path.join(img_dir, "bubbles.json"))
    patterns(img_dir)
    wii_selector(os.path.join(img_dir, "select-wide.png"))
    wiiu_selector(os.path.join(img_dir, "select-start.png"), fontpath)
    square_ring(os.path.join(img_dir, "select-square.png"))
    slot_square(os.path.join(img_dir, "slot-square.png"))
    slot_wide(os.path.join(img_dir, "slot-wide.png"))


# ---------------------------------------------------------------- animated background
def bubbles_lottie(path, W=1920, H=1080, fps=24, seconds=20, count=14, seed=5):
    """Slowly drifting soft circles and rings as a looping Lottie animation.
    White shapes at low opacity; the theme tints them with the accent colour."""
    import json, random
    rnd = random.Random(seed)
    op = fps * seconds

    def static(v):
        return {"a": 0, "k": v}

    layers = []
    for i in range(count):
        d = rnd.choice((90, 130, 180, 240, 320, 420))
        ring = rnd.random() < 0.35
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        pts = [(x0, y0)]
        for _ in range(3):
            pts.append((x0 + rnd.uniform(-160, 160), y0 + rnd.uniform(-110, 110)))
        pts.append((x0, y0))
        kf = []
        for k, (x, y) in enumerate(pts):
            frame = {"t": int(op * k / (len(pts) - 1)), "s": [round(x, 1), round(y, 1), 0]}
            if k < len(pts) - 1:
                frame.update(i={"x": [0.5], "y": [1]}, o={"x": [0.5], "y": [0]})
            kf.append(frame)
        paint = ({"ty": "st", "c": static([1, 1, 1, 1]), "o": static(100), "w": static(round(d * 0.06, 1)),
                  "lc": 2, "lj": 2, "nm": "s"} if ring else
                 {"ty": "fl", "c": static([1, 1, 1, 1]), "o": static(100), "r": 1, "nm": "f"})
        layers.append({
            "ddd": 0, "ind": i + 1, "ty": 4, "nm": f"b{i}", "sr": 1, "ao": 0, "ip": 0, "op": op, "st": 0, "bm": 0,
            "ks": {"o": static(rnd.choice((10, 14, 18, 24))), "r": static(0), "p": {"a": 1, "k": kf},
                   "a": static([0, 0, 0]), "s": static([100, 100, 100])},
            "shapes": [{"ty": "gr", "nm": "g", "it": [
                {"ty": "el", "d": 1, "s": static([d, d]), "p": static([0, 0]), "nm": "e"},
                paint,
                {"ty": "tr", "p": static([0, 0]), "a": static([0, 0]), "s": static([100, 100]), "r": static(0),
                 "o": static(100), "sk": static(0), "sa": static(0)}]}],
        })
    anim = {"v": "5.7.4", "fr": fps, "ip": 0, "op": op, "w": W, "h": H, "nm": "bubbles", "ddd": 0,
            "assets": [], "layers": layers}
    with open(path, "w") as fh:
        json.dump(anim, fh, separators=(",", ":"))


# ---------------------------------------------------------------- HOME-menu background patterns
# All white-based with light grey detail; the theme multiplies them by the scheme's background colour.
def patterns(img_dir):
    L1, L2 = (232, 235, 240), (244, 246, 249)

    def save(name, im):
        im.save(os.path.join(img_dir, name), optimize=True)

    T = 96
    im = Image.new("RGB", (T, T), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for k in range(-T, 2 * T, 24):
        d.line([(k, T), (k + T, 0)], fill=L1, width=9)
    save("bg-stripes.png", im)

    im = Image.new("RGB", (T * 4, T * 4), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, T * 4, 48):
        for x in range(0, T * 4, 48):
            o = 24 if (y // 48) % 2 else 0
            d.ellipse([x + o + 12, y + 12, x + o + 36, y + 36], fill=L1)
    im = im.resize((T, T), Image.LANCZOS)
    save("bg-dots.png", im)

    im = Image.new("RGB", (T, T), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for c in (16, 64):
        d.rectangle([c, 0, c + 14, T], fill=L2)
        d.rectangle([0, c, T, c + 14], fill=L2)
    for c in (16, 64):
        d.rectangle([c + 5, 0, c + 8, T], fill=L1)
        d.rectangle([0, c + 5, T, c + 8], fill=L1)
    save("bg-plaid.png", im)

    S = T * 4
    im = Image.new("RGB", (S, S), (255, 255, 255))
    d = ImageDraw.Draw(im)
    import random
    rnd = random.Random(3)
    for _ in range(14):
        cx, cy, r = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(14, 34)
        pts = [(cx + (r if i % 2 == 0 else r * 0.42) * math.cos(-math.pi / 2 + i * math.pi / 5),
                cy + (r if i % 2 == 0 else r * 0.42) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
        d.polygon(pts, fill=L1)
    save("bg-stars.png", im.resize((T * 2, T * 2), Image.LANCZOS))

    im = Image.new("RGB", (32, 32), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, 32, 8):
        for x in range(0, 32, 8):
            if (x // 8 + y // 8) % 2 == 0:
                d.rectangle([x, y, x + 7, y + 7], fill=L2)
    save("bg-pixels.png", im)

    W2, H2 = T * 4, T * 2
    im = Image.new("RGB", (W2, H2), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for row in range(0, H2, 48):
        pts = [(x, row + 24 + 10 * math.sin(x / W2 * 4 * math.pi)) for x in range(0, W2 + 1, 4)]
        d.line(pts, fill=L1, width=8)
    save("bg-waves.png", im.resize((T * 2, T), Image.LANCZOS))
