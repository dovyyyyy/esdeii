"""Approximate mock renderer for the esdeii layouts (not ES-DE itself).

Draws panels, text, carousel, grid and list from the generated layout data so
proportions and spacing can be checked without a device.
"""
import json, math, os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DATA = json.load(open(sys.argv[1]))
THEME = sys.argv[2]
OUTDIR = sys.argv[3]
FONTDIR = os.path.join(THEME, "assets/fonts")
IMGDIR = os.path.join(THEME, "assets/images")
SYSDIR = os.path.join(THEME, "systems")
H = 1080

SAMPLE = dict(theme="snes", full="Nintendo SNES (Super Nintendo)", count="142 games, 12 favorites",
              game="Stellar Quest: The Lost Kingdom", dev="Moonbeam Works", genre="Platform",
              players="1-2", date="1995-11-21",
              desc=("A bright side-scrolling adventure across floating islands. Collect star shards, "
                    "rescue the sky villagers and outsmart the clockwork king in over sixty stages "
                    "packed with secrets, bonus rooms and hidden warp pipes."))
CAROUSEL = ["nes", "famicom", "gb", "gbc", "snes", "n64", "gba", "nds", "n3ds", "gc", "wii", "psx"]
GAMES = ["Stellar Quest", "Turbo Kart Rally", "Puzzle Pop Deluxe", "Dungeon Bells", "Ocean Racer 2",
         "Sky Garden", "Mecha Duel X", "Pixel Golf", "Haunted Manor", "Frost Byte", "Neon Runner",
         "Castle Clash", "Bubble Bay", "Rocket Rangers", "Farm Friends", "Comet Chasers"]
COVERS = ["E5484D", "4A90E2", "2FA84F", "F2A33A", "7B61D9", "1FB5A8", "E35D8F", "3D4250"]
DEFZ = dict(image=30, video=30, animation=35, badges=35, text=40, datetime=40, gamelistinfo=45,
            rating=45, carousel=50, grid=50, textlist=50, clock=900, systemstatus=900, helpsystem=900)


def hexc(s):
    s = s.strip()
    r, g, b = (int(s[i:i + 2], 16) for i in (0, 2, 4))
    a = int(s[6:8], 16) if len(s) == 8 else 255
    return (r, g, b, a)


def font(path, px):
    return ImageFont.truetype(path, max(6, int(px)))


def fontp(p):
    return os.path.join(FONTDIR, os.path.basename(p))


class R:
    def __init__(self, W, scheme):
        self.W = W
        self.Wp = round(W * H)
        self.img = Image.new("RGBA", (self.Wp, H), (0, 0, 0, 255))
        self.vars = scheme

    def res(self, s):
        return re.sub(r"\$\{(\w+)\}", lambda m: self.vars.get(m.group(1), m.group(0)), s)

    def pair(self, s):
        a, b = (float(v) for v in s.split())
        return a, b

    def px(self, p):
        x, y = self.pair(p)
        return x * self.Wp, y * H

    def box(self, props, wh=None):
        x, y = self.px(props.get("pos", "0 0"))
        w, h = wh if wh else self.px(props.get("size", props.get("cropSize", "0 0")))
        ox, oy = self.pair(props.get("origin", "0 0"))
        return x - ox * w, y - oy * h, w, h

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))

    def comp(self, lay, opacity=1.0):
        if opacity < 1:
            a = lay.split()[3].point(lambda v: int(v * opacity))
            lay.putalpha(a)
        self.img.alpha_composite(lay)

    def rrect(self, x, y, w, h, rad, color):
        lay = self.layer()
        ImageDraw.Draw(lay).rounded_rectangle([x, y, x + w, y + h], radius=max(0, min(rad, w / 2, h / 2)),
                                             fill=color)
        self.comp(lay)

    def paste(self, im, x, y, w, h, tint=None, radius=0):
        im = im.convert("RGBA").resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
        if tint:
            r, g, b, a = tint
            px = im.split()
            im = Image.merge("RGBA", [px[0].point(lambda v: v * r // 255), px[1].point(lambda v: v * g // 255),
                                      px[2].point(lambda v: v * b // 255), px[3].point(lambda v: v * a // 255)])
        if radius:
            m = Image.new("L", im.size, 0)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius=radius, fill=255)
            a = Image.composite(im.split()[3], Image.new("L", im.size, 0), m)
            im.putalpha(a)
        lay = self.layer()
        lay.paste(im, (int(x), int(y)), im)
        self.comp(lay)

    def textbox(self, s, x, y, w, h, fsize, fpath, color, halign="left", valign="center",
                ls=1.5, bg=None, bgm=(0, 0), bgr=0, case="none", wrap=True):
        if case == "uppercase":
            s = s.upper()
        f = font(fontp(fpath), fsize * H * 1.18)
        d = ImageDraw.Draw(self.img)
        lines = []
        if w > 0 and wrap and (h == 0 or h > fsize * H * 1.6):
            words, cur = s.split(), ""
            for wd in words:
                t = (cur + " " + wd).strip()
                if d.textlength(t, font=f) <= w:
                    cur = t
                else:
                    lines.append(cur)
                    cur = wd
            lines.append(cur)
        else:
            t = s
            if w > 0:
                while d.textlength(t, font=f) > w and len(t) > 3:
                    t = t[:-2]
                if t != s:
                    t = t[:-1] + "…"
            lines = [t]
        lh = fsize * H * ls
        if h > 0:
            maxl = max(1, int((h + 0.5 * lh) // lh))
            lines = lines[:maxl]
        tw = max(d.textlength(l, font=f) for l in lines)
        th = lh * len(lines)
        if w == 0:
            w = tw
        if h == 0:
            h = th
        if valign == "top":
            ty = y
        elif valign == "bottom":
            ty = y + h - th
        else:
            ty = y + (h - th) / 2
        if bg:
            self.rrect(x - bgm[0], y, w + bgm[0] + bgm[1], h, bgr, bg)
        for i, l in enumerate(lines):
            lw = d.textlength(l, font=f)
            lx = x if halign == "left" else (x + (w - lw) / 2 if halign == "center" else x + w - lw)
            ImageDraw.Draw(self.img).text((lx, ty + i * lh + lh / 2), l, font=f, fill=color, anchor="lm")
        return w, h


def fake_screenshot(w, h, seed=0):
    im = Image.new("RGB", (160, 90))
    d = ImageDraw.Draw(im)
    for yy in range(90):
        d.line([(0, yy), (160, yy)], fill=(90 + yy, 160 + yy // 2, 240))
    d.ellipse([10, 60, 90, 120], fill=(80, 170, 80))
    d.ellipse([70, 55, 170, 130], fill=(60, 150, 70))
    d.rectangle([0, 78, 160, 90], fill=(170, 110, 60))
    for i in range(8):
        d.rectangle([i * 20, 76, i * 20 + 18, 78], fill=(120, 200, 90))
    d.rectangle([60, 40, 92, 48], fill=(220, 140, 70))
    d.rectangle([66, 66, 74, 77], fill=(230, 60, 60))
    d.ellipse([120, 10, 140, 30], fill=(255, 230, 120))
    for cx in (20, 50, 110):
        d.ellipse([cx, 14, cx + 22, 24], fill=(255, 255, 255))
    return im.resize((int(w), int(h)), Image.NEAREST)


def cover(w, h, i):
    c = hexc(COVERS[i % len(COVERS)])
    im = Image.new("RGBA", (int(w), int(h)), c)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h * 0.16], fill=(255, 255, 255, 230))
    d.ellipse([w * 0.2, h * 0.32, w * 0.8, h * 0.78], fill=(255, 255, 255, 90))
    f = font(fontp("Nunito-Black.ttf"), h * 0.1)
    t = GAMES[i % len(GAMES)].split()[0]
    d.text((w / 2, h * 0.88), t, font=f, fill=(255, 255, 255), anchor="mm")
    return im


def render(key, scheme_name, view):
    lay = DATA["layouts"][key]
    r = R(lay["W"], DATA["schemes"][scheme_name])
    els = lay["views"][view]
    order = sorted(range(len(els)), key=lambda i: float(els[i][2].get("zIndex", DEFZ.get(els[i][0], 30))))
    for i in order:
        et, name, p = els[i]
        p = {k: r.res(str(v)) for k, v in p.items()}
        if et == "image":
            path = p.get("path", "")
            col = hexc(p.get("color", "FFFFFFFF"))
            rad = float(p.get("cornerRadius", 0)) * r.Wp
            if "imageType" in p:
                x, y, w, h = r.box(p)
                r.paste(fake_screenshot(w, h).convert("RGBA"), x, y, w, h, radius=rad)
                continue
            path = path.replace("${system.theme}", SAMPLE["theme"])
            fn = os.path.join(THEME, path.replace("./../", "").replace("./", ""))
            if p.get("tile") == "true":
                tile = Image.open(fn).convert("RGBA")
                th = float(p["tileSize"].split()[1]) * H
                tw = th * tile.size[0] / tile.size[1]
                t = tile.resize((int(tw), int(th)))
                big = Image.new("RGBA", r.img.size)
                for xx in range(0, r.Wp, int(tw)):
                    for yy in range(0, H, int(th)):
                        big.paste(t, (xx, yy))
                r.paste(big, 0, 0, r.Wp, H, tint=col)
                continue
            x, y, w, h = r.box(p)
            if path.endswith("white.png"):
                r.rrect(x, y, w, h, rad, col)
            else:
                r.paste(Image.open(fn), x, y, w, h, tint=col if col != (255, 255, 255, 255) else None, radius=rad)
        elif et == "video":
            x, y, w, h = r.box(p)
            r.paste(fake_screenshot(w, h).convert("RGBA"), x, y, w, h,
                    radius=float(p.get("imageCornerRadius", 0)) * r.Wp)
        elif et in ("text", "datetime", "gamelistinfo"):
            x, y, w, h = r.box(p)
            if et == "datetime":
                s = SAMPLE["date"]
            elif et == "gamelistinfo":
                s = "142 GAMES"
            elif "systemdata" in p:
                s = SAMPLE["count"]
            elif "metadata" in p:
                s = dict(name=SAMPLE["game"], description=SAMPLE["desc"], developer=SAMPLE["dev"],
                         genre=SAMPLE["genre"], players=SAMPLE["players"]).get(p["metadata"], "?")
            else:
                s = p.get("text", "").replace("${system.fullName}", SAMPLE["full"])
            bg = hexc(p["backgroundColor"]) if "backgroundColor" in p else None
            bgm = tuple(float(v) * r.Wp for v in p.get("backgroundMargins", "0 0").split())
            r.textbox(s, x, y, w, h, float(p.get("fontSize", 0.045)), p.get("fontPath", "Nunito-SemiBold.ttf"),
                      hexc(p.get("color", "000000")), p.get("horizontalAlignment", "left"),
                      p.get("verticalAlignment", "center"), float(p.get("lineSpacing", 1.5)),
                      bg, bgm, float(p.get("backgroundCornerRadius", 0)) * r.Wp, p.get("letterCase", "none"),
                      wrap=et == "text")
        elif et == "rating":
            x, y = r.px(p["pos"])
            hh = float(p["size"].split()[1]) * H
            for k in range(5):
                fn = "star-filled.svg" if k < 4 else "star-unfilled.svg"
                st = Image.new("RGBA", (100, 100))
                sd = ImageDraw.Draw(st)
                pts = [(50 + 40 * math.cos(-math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45),
                        52 + 40 * math.sin(-math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
                sd.polygon(pts, fill=(255, 194, 26) if k < 4 else (185, 192, 202))
                r.paste(st, x + k * hh, y, hh, hh)
        elif et == "badges":
            x, y, w, h = r.box(p)
            for k, c in enumerate(("F2B705", "2FA84F")):
                r.rrect(x + w - (k + 1) * h * 1.15, y, h, h, h * 0.25, hexc(c))
        elif et == "carousel":
            x, y, w, h = r.box(p)
            iw, ih = r.pair(p["itemSize"])
            iw, ih = iw * r.Wp, ih * H
            m = float(p["maxItemCount"])
            step = w / m
            sc = float(p["itemScale"])
            sel = CAROUSEL.index(SAMPLE["theme"])
            cx, cy = x + w / 2, y + h / 2
            n = int(m / 2) + 2
            for k in list(range(-n, 0)) + list(range(n, 0, -1)) + [0]:
                idx = (sel + k) % len(CAROUSEL)
                s = sc if k == 0 else 1.0
                ww, hh = iw * s, ih * s
                ix = cx + k * step - ww / 2
                if ix + ww < x or ix > x + w:
                    continue
                im = Image.open(os.path.join(SYSDIR, CAROUSEL[idx] + ".png"))
                if k != 0:
                    im = Image.eval(im.convert("RGBA"), lambda v: v)
                r.paste(im, ix, cy - hh / 2, ww, hh)
        elif et == "grid":
            x, y, w, h = r.box(p)
            iw, ih = r.pair(p["itemSize"])
            iw, ih = iw * r.Wp, ih * H
            sx, sy = r.pair(p["itemSpacing"])
            sx, sy = sx * r.Wp, sy * H
            cols = int((w + sx) // (iw + sx))
            rows = int((h + sy) // (ih + sy))
            ox = x + (w - (cols * iw + (cols - 1) * sx)) / 2
            sc = float(p["itemScale"])
            bgc = hexc(p["backgroundColor"])
            selc = hexc(p["selectorColor"])
            k = 0
            items = []
            for rr_ in range(rows):
                for cc in range(cols):
                    items.append((rr_, cc, k))
                    k += 1
            selk = 2
            for rr_, cc, k in sorted(items, key=lambda t: t[2] == selk):
                s = sc if k == selk else 1
                ww, hh = iw * s, ih * s
                ix = ox + cc * (iw + sx) + iw / 2 - ww / 2
                iy = y + rr_ * (ih + sy) + ih / 2 - hh / 2
                if k == selk:
                    r.rrect(ix, iy, ww, hh, float(p["selectorCornerRadius"]) * r.Wp * s, selc)
                br = float(p["backgroundRelativeScale"])
                r.rrect(ix + ww * (1 - br) / 2, iy + hh * (1 - br) / 2, ww * br, hh * br,
                        float(p["backgroundCornerRadius"]) * r.Wp * s * br, bgc)
                irs = float(p["imageRelativeScale"])
                ch = hh * irs
                cw = ch * 0.72
                r.paste(cover(cw, ch, k), ix + (ww - cw) / 2, iy + (hh - ch) / 2, cw, ch,
                        radius=float(p["imageCornerRadius"]) * r.Wp)
        elif et == "textlist":
            x, y, w, h = r.box(p)
            fs = float(p["fontSize"])
            lh = fs * H * float(p["lineSpacing"])
            n = int(h // lh)
            hm = float(p.get("horizontalMargin", 0)) * r.Wp
            for k in range(n):
                ly = y + k * lh
                sel = k == 2
                if sel:
                    m = float(p["selectedBackgroundMargins"].split()[0]) * r.Wp
                    r.rrect(x - m, ly + lh * 0.12, w + 2 * m, lh * 0.76,
                            float(p["selectedBackgroundCornerRadius"]) * r.Wp, hexc(p["selectedBackgroundColor"]))
                col = hexc(p["selectedColor"] if sel else p["primaryColor"])
                f = font(fontp(p["fontPath"]), fs * H * 1.18)
                ImageDraw.Draw(r.img).text((x + hm, ly + lh / 2), GAMES[k % len(GAMES)], font=f, fill=col, anchor="lm")
        elif et == "clock":
            x, y = r.px(p["pos"])
            f = font(fontp(p["fontPath"]), float(p["fontSize"]) * H * 1.18)
            ImageDraw.Draw(r.img).text((x, y), "21:47", font=f, fill=hexc(p["color"]), anchor="lm")
        elif et == "systemstatus":
            x, y = r.px(p["pos"])
            hh = float(p["height"]) * H
            col = hexc(p["color"])
            f = font(fontp(p["fontPath"]), hh * 1.0)
            d = ImageDraw.Draw(r.img)
            tw = d.textlength("86%", font=f)
            d.text((x, y), "86%", font=f, fill=col, anchor="rm")
            bx = x - tw - hh * 1.9
            d.rounded_rectangle([bx, y - hh * 0.32, bx + hh * 1.6, y + hh * 0.32], radius=hh * 0.12, outline=col, width=3)
            d.rectangle([bx + 4, y - hh * 0.32 + 4, bx + hh * 1.2, y + hh * 0.32 - 4], fill=col)
            wx = bx - hh * 1.2
            for k in range(3):
                rr_ = hh * (0.25 + 0.25 * k)
                d.arc([wx - rr_, y + hh * 0.3 - rr_, wx + rr_, y + hh * 0.3 + rr_], 225, 315, fill=col, width=3)
        elif et == "helpsystem":
            x, y = r.px(p["pos"])
            fs = float(p["fontSize"]) * H
            col = hexc(p["textColor"])
            f = font(fontp(p["fontPath"]), fs * 1.18)
            fb = font(fontp(p["fontPath"]), fs * 0.75)
            d = ImageDraw.Draw(r.img)
            items = [("+", "Choose"), ("A", "Select"), ("B", "Back"), ("X", "Random"), ("Y", "Favorite"), ("≡", "Menu")]
            cx = x
            for ic, label in items:
                d.ellipse([cx, y - fs * 0.62, cx + fs * 1.24, y + fs * 0.62], fill=col)
                d.text((cx + fs * 0.62, y), ic, font=fb, fill=hexc(r.vars["bgColor"]), anchor="mm")
                cx += fs * 1.24 + 8
                d.text((cx, y), label, font=f, fill=col, anchor="lm")
                cx += d.textlength(label, font=f) + fs * 0.9
    return r.img.convert("RGB")


os.makedirs(OUTDIR, exist_ok=True)
jobs = [a.split(",") for a in sys.argv[4:]]
for key, scheme, view, out in jobs:
    render(key, scheme, view).save(os.path.join(OUTDIR, out))
    print("rendered", out)
