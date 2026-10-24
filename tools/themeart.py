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


def round_button(path, glyph_kind=None, S=300, text=None, fontpath=None):
    """Glossy round menu button with a grey glyph (or short lettering)."""
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
    if text:
        f = ImageFont.truetype(fontpath, int(S * 0.36))
        ImageDraw.Draw(img).text((S / 2, S * 0.44), text, font=f, fill=(140, 147, 156, 255), anchor="mm")
    else:
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
    """Cyan glass frame drawn over the selected tile (no lettering)."""
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


def _scanlines(size, box, rad, step=6):
    """Light console-menu 'empty slot' fill: soft grey with faint horizontal lines."""
    W, H = size
    x0, y0, x1, y1 = box
    fill = icons._vgrad((236, 238, 241), (226, 229, 233), y0, y1, size)
    d = ImageDraw.Draw(fill)
    for y in range(int(y0), int(y1), step):
        d.line([(0, y), (W, y)], fill=(244, 245, 247, 255), width=2)
    return fill


def slot_empty_wide(path, fontpath):
    """Empty channel slot (wide), shown where the wall has no channel."""
    W, H = icons.WT_W, icons.WT_H
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = icons.WBODY
    img.paste((196, 202, 210, 255), (0, 0), icons._rr(icons.WBODY, icons.WRAD, (W, H)))
    inner = icons._rr((x0 + 3, y0 + 3, x1 - 3, y1 - 3), icons.WRAD - 3, (W, H))
    img.paste(_scanlines((W, H), icons.WBODY, icons.WRAD), (0, 0), inner)
    img.save(path, optimize=True)


def slot_empty_square(path, fontpath):
    """Empty square slot, same frame geometry as the square system tiles."""
    S = icons.TILE
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    x0, y0, x1, y1 = icons.BODY
    img.paste((196, 202, 210, 255), (0, 0), rr_mask(icons.BODY, icons.RAD))
    inner = rr_mask(icons.inset(icons.BODY, 3), icons.RAD - 3)
    img.paste(_scanlines((S, S), icons.BODY, icons.RAD), (0, 0), inner)
    img.save(path, optimize=True)


def sd_card(path, S=120):
    """Small SD-card glyph for the bar (white, tinted in theme)."""
    def draw(d, s, big):
        W, H = big.size
        pts = [(26 * s, 8 * s), (W - 22 * s, 8 * s), (W - 22 * s, H - 8 * s), (22 * s, H - 8 * s),
               (22 * s, 30 * s), (26 * s, 26 * s)]
        d.rounded_rectangle([22 * s, 8 * s, W - 22 * s, H - 8 * s], radius=10 * s, fill=(255, 255, 255, 255))
        d.polygon([(22 * s, 8 * s), (44 * s, 8 * s), (22 * s, 30 * s)], fill=(0, 0, 0, 0))
        for i in range(4):
            x = 38 * s + i * 13 * s
            d.rounded_rectangle([x, 18 * s, x + 7 * s, 38 * s], radius=2 * s, fill=(0, 0, 0, 0))
    ss_draw((S, S), draw).save(path, optimize=True)


# ---------------------------------------------------------------- small Lottie animations
# All are tiny (a few % of the screen) so rlottie renders them cheaply, unlike a
# full-screen animation. Shapes are white; the theme tints them with `color`.
def _st(v):
    return {"a": 0, "k": v}


def _anim(keys):
    """Animated property from [(frame, value), ...] with smooth easing."""
    out = []
    for n, (t, v) in enumerate(keys):
        fr = {"t": t, "s": v if isinstance(v, list) else [v]}
        if n < len(keys) - 1:
            fr.update(i={"x": [0.45], "y": [1]}, o={"x": [0.55], "y": [0]})
        out.append(fr)
    return {"a": 1, "k": out}


def _tr():
    return {"ty": "tr", "p": _st([0, 0]), "a": _st([0, 0]), "s": _st([100, 100]), "r": _st(0), "o": _st(100),
            "sk": _st(0), "sa": _st(0)}


def _layer(i, shapes_, op, opacity=None, pos=(0, 0), position=None, scale_=None, anchor=(0, 0)):
    return {"ddd": 0, "ind": i, "ty": 4, "nm": f"l{i}", "sr": 1, "ao": 0, "ip": 0, "op": op, "st": 0, "bm": 0,
            "ks": {"o": opacity or _st(100), "r": _st(0), "p": position or _st([pos[0], pos[1], 0]),
                   "a": _st([anchor[0], anchor[1], 0]), "s": scale_ or _st([100, 100, 100])},
            "shapes": [{"ty": "gr", "nm": "g", "it": shapes_ + [_tr()]}]}


def _write_lottie(path, w, h, fps, op, layers):
    import json
    with open(path, "w") as fh:
        json.dump({"v": "5.7.4", "fr": fps, "ip": 0, "op": op, "w": w, "h": h, "nm": os.path.basename(path),
                   "ddd": 0, "assets": [], "layers": layers}, fh, separators=(",", ":"))


FILL = {"ty": "fl", "c": _st([1, 1, 1, 1]), "o": _st(100), "r": 1, "nm": "f"}


def lottie_colon(path, frame_png):
    """Blinking clock colon (1 s cycle), placed between the hour and minute clocks."""
    dots = [{"ty": "el", "d": 1, "s": _st([17, 17]), "p": _st([20, y]), "nm": "e"} for y in (40, 82)]
    _write_lottie(path, 40, 120, 30, 30, [_layer(1, dots + [FILL], 30,
                                                 opacity=_anim([(0, 100), (12, 100), (16, 15), (27, 15), (30, 100)]))])
    im = Image.new("RGBA", (40, 120), (0, 0, 0, 0))
    for y in (40, 82):
        ImageDraw.Draw(im).ellipse([11.5, y - 8.5, 28.5, y + 8.5], fill=(255, 255, 255, 255))
    im.save(frame_png)


def lottie_arrow(path, frame_png):
    """Page arrow on the right edge of the channel wall, gently nudging right."""
    tri = {"ty": "sh", "nm": "p", "ks": _st({"c": True, "v": [[0, -34], [30, 0], [0, 34]],
                                              "i": [[0, 0], [0, 0], [0, 0]], "o": [[0, 0], [0, 0], [0, 0]]})}
    stroke = {"ty": "st", "c": _st([1, 1, 1, 1]), "o": _st(100), "w": _st(10), "lc": 2, "lj": 2, "nm": "s"}
    _write_lottie(path, 64, 100, 30, 48, [
        _layer(1, [tri, stroke, FILL], 48, position=_anim([(0, [22, 50, 0]), (24, [32, 50, 0]), (48, [22, 50, 0])]),
               opacity=_anim([(0, 80), (24, 100), (48, 80)]))])
    im = Image.new("RGBA", (64, 100), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(22, 16), (52, 50), (22, 84)], fill=(255, 255, 255, 255))
    im.save(frame_png)


def lottie_glow_ring(path, frame_png):
    """Soft pulsing ring around the mail button (like the blinking message light)."""
    ring = [{"ty": "el", "d": 1, "s": _st([176, 176]), "p": _st([0, 0]), "nm": "e"},
            {"ty": "st", "c": _st([1, 1, 1, 1]), "o": _st(100), "w": _st(9), "lc": 2, "lj": 2, "nm": "s"}]
    _write_lottie(path, 200, 200, 30, 90, [
        _layer(1, ring, 90, pos=(100, 100), opacity=_anim([(0, 0), (20, 85), (45, 0), (90, 0)]),
               scale_=_anim([(0, [94, 94, 100]), (45, [106, 106, 100]), (90, [106, 106, 100])]))])
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([10, 10, 190, 190], outline=(255, 255, 255, 190), width=9)
    im.save(frame_png)


def lottie_cursor(path, frame_png, S=400):
    """Breathing selection ring for the icon row (replaces the static cursor.png)."""
    rect = [{"ty": "rc", "d": 1, "s": _st([S - 24, S - 24]), "p": _st([0, 0]), "r": _st(96), "nm": "r"},
            {"ty": "st", "c": _st([1, 1, 1, 1]), "o": _st(100), "w": _st(16), "lc": 2, "lj": 2, "nm": "s"}]
    _write_lottie(path, S, S, 30, 60, [
        _layer(1, rect, 60, pos=(S / 2, S / 2), opacity=_anim([(0, 100), (30, 55), (60, 100)]),
               scale_=_anim([(0, [100, 100, 100]), (30, [97, 97, 100]), (60, [100, 100, 100])]))])
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([12, 12, S - 12, S - 12], radius=96, outline=(255, 255, 255, 255), width=16)
    im.save(frame_png)


def lottie_bubble(path, frame_png, ring=False, drift=(0, 0), fps=12, seconds=7.0):
    """One soft bubble gliding slowly out to one side, back through the middle
    to the other side and back again - a seamless loop that never fades.

    It starts (and ends) in the middle of its path, so when ES-DE restarts the
    animation (it does on every system change) the bubble only moves back a
    little instead of jumping from one end to the other. Each one is small and
    short, so ES-DE renders the frames once and just replays them."""
    C, d = 200, 116
    paint = ({"ty": "st", "c": _st([1, 1, 1, 1]), "o": _st(100), "w": _st(8), "lc": 2, "lj": 2, "nm": "s"}
             if ring else FILL)
    op = int(round(fps * seconds))
    dx, dy = drift
    c = [C / 2, C / 2, 0]
    pos = _anim([(0, c), (op // 4, [C / 2 + dx, C / 2 + dy, 0]), (op // 2, c),
                 (3 * op // 4, [C / 2 - dx, C / 2 - dy, 0]), (op, c)])
    shape = [{"ty": "el", "d": 1, "s": _st([d, d]), "p": _st([0, 0]), "nm": "e"}, paint]
    _write_lottie(path, C, C, fps, op, [_layer(1, shape, op, opacity=_st(20), position=pos)])
    im = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    box = [C / 2 - d / 2, C / 2 - d / 2, C / 2 + d / 2, C / 2 + d / 2]
    if ring:
        ImageDraw.Draw(im).ellipse(box, outline=(255, 255, 255, 51), width=8)
    else:
        ImageDraw.Draw(im).ellipse(box, fill=(255, 255, 255, 51))
    im.save(frame_png)


# Mostly sideways, a little up or down; different lengths so they never move in step.
BUBBLES = {"anim-bubble-a": dict(drift=(30, -6), seconds=9.0),
           "anim-bubble-b": dict(ring=True, drift=(-28, 8), seconds=11.0),
           "anim-bubble-c": dict(drift=(28, 8), seconds=8.0),
           "anim-bubble-d": dict(ring=True, drift=(-30, -6), seconds=12.0)}


def build_all(img_dir, fontpath, frames_dir=None):
    frames_dir = frames_dir or img_dir
    os.makedirs(frames_dir, exist_ok=True)
    bg_wii(os.path.join(img_dir, "bg-wii.png"))
    bg_wiiu(os.path.join(img_dir, "bg-wiiu.png"))
    wiiu_swirl(os.path.join(img_dir, "wiiu-swirl.png"))
    wii_bar(os.path.join(img_dir, "wii-bar.png"), os.path.join(img_dir, "wii-bar-line.png"))
    patterns(img_dir)
    slot_empty_wide(os.path.join(img_dir, "slot-empty-wide.png"), fontpath)
    slot_empty_square(os.path.join(img_dir, "slot-empty-square.png"), fontpath)
    for fn, name in ((lottie_colon, "anim-colon"), (lottie_arrow, "anim-arrow"),
                     (lottie_cursor, "anim-cursor")):
        fn(os.path.join(img_dir, name + ".json"), os.path.join(frames_dir, name + ".png"))
    for name, kw in BUBBLES.items():
        lottie_bubble(os.path.join(img_dir, name + ".json"), os.path.join(frames_dir, name + ".png"), **kw)
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
