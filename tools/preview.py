"""Approximate mock renderer for the esdeii layouts (not ES-DE itself).

    python3 tools/preview.py <layouts.json> <repo root> <out dir> "theme|ar|variant,scheme,view,out.png[,items]" ...

items = how many systems/games to show in grids (the rest show as empty slots).
Lottie animations are drawn from still frames in $ESDEII_FRAMES (written by build.py
to <cache>/frames).
"""
import json, math, os, re, sys
from PIL import Image, ImageDraw, ImageFont

DATA = json.load(open(sys.argv[1]))
FRAMES = os.environ.get("ESDEII_FRAMES", "")
ITEMS = [99]
ROOT = sys.argv[2]
OUTDIR = sys.argv[3]
H = 1080
SAMPLE = dict(theme="snes", full="Nintendo SNES (Super Nintendo)", count="142 games, 12 favorites",
              info="Nintendo  ·  1991  ·  Home console", game="Stellar Quest: The Lost Kingdom",
              dev="Moonbeam Works", genre="Platform", players="1-2", date="1995-11-21", playtime="12 hours",
              desc=("A bright side-scrolling adventure across floating islands. Collect star shards, rescue the "
                    "sky villagers and outsmart the clockwork king in over sixty stages packed with secrets, "
                    "bonus rooms and hidden warp pipes."))
SYSTEMS = ["nes", "famicom", "gb", "gbc", "snes", "n64", "gba", "nds", "n3ds", "gc", "wii", "wiiu", "switch",
           "psx", "ps2", "psp", "genesis", "dreamcast", "xbox", "arcade", "auto-favorites", "c64", "dos", "segacd"]
GAMES = ["Stellar Quest", "Turbo Kart Rally", "Puzzle Pop Deluxe", "Dungeon Bells", "Ocean Racer 2", "Sky Garden",
         "Mecha Duel X", "Pixel Golf", "Haunted Manor", "Frost Byte", "Neon Runner", "Castle Clash", "Bubble Bay",
         "Rocket Rangers", "Farm Friends", "Comet Chasers"]
COVERS = ["E5484D", "4A90E2", "2FA84F", "F2A33A", "7B61D9", "1FB5A8", "E35D8F", "3D4250"]
DEFZ = dict(animation=35, image=30, video=30, badges=35, text=40, datetime=40, gamelistinfo=45, rating=45, carousel=50, grid=50,
            textlist=50, clock=900, systemstatus=900, helpsystem=900)


def hexc(s):
    s = s.strip()
    r, g, b = (int(s[i:i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, int(s[6:8], 16) if len(s) == 8 else 255)


class R:
    def __init__(self, theme, W, vars_):
        self.theme, self.W, self.Wp, self.vars = theme, W, round(W * H), vars_
        self.img = Image.new("RGBA", (self.Wp, H), (0, 0, 0, 255))

    def font(self, p, px):
        return ImageFont.truetype(os.path.join(ROOT, self.theme, "assets/fonts", os.path.basename(p)), max(6, int(px)))

    def path(self, p):
        p = p.replace("${system.theme}", SAMPLE["theme"])
        return os.path.normpath(os.path.join(ROOT, self.theme, "layouts", p))

    def res(self, s):
        return re.sub(r"\$\{([\w.]+)\}", lambda m: self.vars.get(m.group(1), m.group(0)), s)

    def pair(self, s):
        a, b = (float(v) for v in s.split())
        return a, b

    def px(self, p):
        x, y = self.pair(p)
        return x * self.Wp, y * H

    def box(self, p, wh=None):
        x, y = self.px(p.get("pos", "0 0"))
        w, h = wh if wh else self.px(p.get("size", p.get("cropSize", p.get("maxSize", "0 0"))))
        ox, oy = self.pair(p.get("origin", "0 0"))
        return x - ox * w, y - oy * h, w, h

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))

    def comp(self, lay, op=1.0):
        if op < 1:
            lay.putalpha(lay.split()[3].point(lambda v: int(v * op)))
        self.img.alpha_composite(lay)

    def rrect(self, x, y, w, h, rad, color, op=1.0):
        lay = self.layer()
        ImageDraw.Draw(lay).rounded_rectangle([x, y, x + w, y + h], radius=max(0, min(rad, w / 2, h / 2)), fill=color)
        self.comp(lay, op)

    def paste(self, im, x, y, w, h, tint=None, radius=0, op=1.0):
        im = im.convert("RGBA").resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
        if tint and tint != (255, 255, 255, 255):
            r, g, b, a = tint
            ch = im.split()
            im = Image.merge("RGBA", [ch[0].point(lambda v: v * r // 255), ch[1].point(lambda v: v * g // 255),
                                      ch[2].point(lambda v: v * b // 255), ch[3].point(lambda v: v * a // 255)])
        if radius:
            m = Image.new("L", im.size, 0)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], radius=radius, fill=255)
            im.putalpha(Image.composite(im.split()[3], Image.new("L", im.size, 0), m))
        lay = self.layer()
        lay.paste(im, (int(x), int(y)), im)
        self.comp(lay, op)

    def text(self, s, x, y, w, h, fs, fp, color, halign="left", valign="center", ls=1.5, bg=None, bgm=(0, 0),
             bgr=0, case="none", wrap=True):
        if case == "uppercase":
            s = s.upper()
        f = self.font(fp, fs * H * 1.18)
        d = ImageDraw.Draw(self.img)
        lines = []
        if w > 0 and wrap and (h == 0 or h > fs * H * 1.6):
            cur = ""
            for wd in s.split():
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
                t = t if t == s else t[:-1] + "…"
            lines = [t]
        lh = fs * H * ls
        if h > 0:
            lines = lines[:max(1, int((h + 0.5 * lh) // lh))]
        tw = max(d.textlength(l, font=f) for l in lines)
        th = lh * len(lines)
        w, h = (w or tw), (h or th)
        ty = y if valign == "top" else (y + h - th if valign == "bottom" else y + (h - th) / 2)
        if bg:
            self.rrect(x - bgm[0], y, w + bgm[0] + bgm[1], h, bgr, bg)
        for i, l in enumerate(lines):
            lw = d.textlength(l, font=f)
            lx = x if halign == "left" else (x + (w - lw) / 2 if halign == "center" else x + w - lw)
            ImageDraw.Draw(self.img).text((lx, ty + i * lh + lh / 2), l, font=f, fill=color, anchor="lm")


def screenshot(w, h):
    im = Image.new("RGB", (160, 90))
    d = ImageDraw.Draw(im)
    for yy in range(90):
        d.line([(0, yy), (160, yy)], fill=(90 + yy, 160 + yy // 2, 240))
    d.ellipse([10, 60, 90, 120], fill=(80, 170, 80))
    d.ellipse([70, 55, 170, 130], fill=(60, 150, 70))
    d.rectangle([0, 78, 160, 90], fill=(170, 110, 60))
    d.rectangle([60, 40, 92, 48], fill=(220, 140, 70))
    d.rectangle([66, 66, 74, 77], fill=(230, 60, 60))
    d.ellipse([120, 10, 140, 30], fill=(255, 230, 120))
    for cx in (20, 50, 110):
        d.ellipse([cx, 14, cx + 22, 24], fill=(255, 255, 255))
    return im.resize((max(1, int(w)), max(1, int(h))), Image.NEAREST).convert("RGBA")


def is_box(t):
    first = t.split(",")[0].strip()
    return first in ("cover", "3dbox")


def cover(w, h, i, font, box3d=False):
    c = hexc(COVERS[i % len(COVERS)])
    im = Image.new("RGBA", (max(1, int(w)), max(1, int(h))), c)
    d = ImageDraw.Draw(im)
    if box3d:  # quick 3D-box look: darker spine on the left
        sw = w * 0.16
        d.polygon([(0, h * 0.04), (sw, 0), (sw, h), (0, h * 0.96)], fill=tuple(int(v * 0.6) for v in c[:3]) + (255,))
        d.rectangle([sw, 0, w, h * 0.16], fill=(255, 255, 255, 230))
        d.ellipse([sw + (w - sw) * 0.2, h * 0.32, sw + (w - sw) * 0.8, h * 0.78], fill=(255, 255, 255, 90))
        d.text((sw + (w - sw) / 2, h * 0.88), GAMES[i % len(GAMES)].split()[0], font=font(h * 0.09),
               fill=(255, 255, 255), anchor="mm")
        return im
    d.rectangle([0, 0, w, h * 0.16], fill=(255, 255, 255, 230))
    d.ellipse([w * 0.2, h * 0.32, w * 0.8, h * 0.78], fill=(255, 255, 255, 90))
    d.text((w / 2, h * 0.88), GAMES[i % len(GAMES)].split()[0], font=font(h * 0.1), fill=(255, 255, 255), anchor="mm")
    return im


def render(key, scheme, view):
    lay = DATA["layouts"][key]
    theme = key.split("|")[0]
    vars_ = dict(DATA["schemes"][scheme])
    vars_.update({k: str(v) for k, v in DATA["fonts"].items()})
    vars_["sysInfo"] = SAMPLE["info"]
    r = R(theme, lay["W"], vars_)
    cf = lambda px_: r.font("MPLUSRounded1c-ExtraBold.ttf", px_)
    els = lay["views"][view]
    order = sorted(range(len(els)), key=lambda i: float(r.res(str(els[i][2].get("zIndex", DEFZ.get(els[i][0], 30))))))
    for i in order:
        et, name, p = els[i]
        p = {k: r.res(str(v)) for k, v in p.items()}
        op = float(p.get("opacity", 1))
        if p.get("visible") == "false":
            continue
        if et == "image":
            col = hexc(p.get("color", "FFFFFFFF"))
            rad = float(p.get("cornerRadius", 0)) * r.Wp
            if "imageType" in p:
                if is_box(p["imageType"]):
                    b3 = p["imageType"].startswith("3dbox")
                    mw, mh = r.px(p["maxSize"])
                    cw, ch = mh * (0.86 if b3 else 0.72), mh
                    x, y, w, h = r.box(p, (cw, ch))
                    r.paste(cover(cw, ch, int(p.get("gameselectorEntry", 0)) + 3, cf, b3), x, y, cw, ch, radius=rad)
                elif name not in ("mediaFallback", "gameLogo"):
                    x, y, w, h = r.box(p)
                    r.paste(screenshot(w, h), x, y, w, h, radius=rad)
                continue
            fn = r.path(r.res(p["path"]))
            if not os.path.exists(fn):
                fn = r.path(p.get("default", p["path"]))
            if p.get("tile") == "true":
                tile = Image.open(fn).convert("RGBA")
                th = float(r.res(p["tileSize"]).split()[1]) * H
                tw = th * tile.size[0] / tile.size[1]
                t = tile.resize((max(1, int(tw)), max(1, int(th))))
                big = Image.new("RGBA", r.img.size)
                for xx in range(0, r.Wp, max(1, int(tw))):
                    for yy in range(0, H, max(1, int(th))):
                        big.paste(t, (xx, yy))
                r.paste(big, 0, 0, r.Wp, H, tint=col)
                continue
            x, y, w, h = r.box(p)
            if p["path"].endswith("white.png"):
                r.rrect(x, y, w, h, rad, col, op)
            else:
                r.paste(Image.open(fn), x, y, w, h, tint=col, radius=rad, op=op)
        elif et == "animation" and FRAMES and os.path.basename(p["path"]).startswith("anim-"):
            fr = Image.open(os.path.join(FRAMES, os.path.basename(p["path"]).replace(".json", ".png")))
            sw, sh = r.pair(p["size"])
            w, h = sw * r.Wp, sh * H
            if w == 0:
                w = h * fr.size[0] / fr.size[1]
            x0_, y0_ = r.px(p["pos"])
            ox, oy = r.pair(p.get("origin", "0 0"))
            r.paste(fr, x0_ - ox * w, y0_ - oy * h, w, h, tint=hexc(p.get("color", "FFFFFFFF")), op=op)
        elif et == "animation":
            anim = json.load(open(r.path(p["path"])))
            lay_ = r.layer()
            d = ImageDraw.Draw(lay_)
            col = hexc(p.get("color", "FFFFFFFF"))
            sx_, sy_ = r.Wp / anim["w"], H / anim["h"]
            for L_ in anim["layers"]:
                x_, y_, _ = L_["ks"]["p"]["k"][1]["s"]
                o_ = L_["ks"]["o"]["k"] / 100 * op
                it = L_["shapes"][0]["it"]
                dd = it[0]["s"]["k"][0] / 2
                a_ = int(255 * o_)
                box = [(x_ - dd) * sx_, (y_ - dd) * sy_, (x_ + dd) * sx_, (y_ + dd) * sy_]
                if it[1]["ty"] == "fl":
                    d.ellipse(box, fill=col[:3] + (a_,))
                else:
                    d.ellipse(box, outline=col[:3] + (a_,), width=max(1, int(it[1]["w"]["k"] * sx_)))
            r.img.alpha_composite(lay_)
        elif et == "video":
            x, y, w, h = r.box(p)
            r.paste(screenshot(w, h), x, y, w, h, radius=float(p.get("imageCornerRadius", 0)) * r.Wp)
        elif et in ("text", "datetime", "gamelistinfo"):
            x, y, w, h = r.box(p)
            if et == "datetime":
                s = SAMPLE["date"] if p.get("metadata") == "releasedate" else "2 days ago"
            elif et == "gamelistinfo":
                s = "142 GAMES"
            elif "systemdata" in p:
                s = SAMPLE["count"]
            elif "metadata" in p:
                s = dict(name=SAMPLE["game"], description=SAMPLE["desc"], developer=SAMPLE["dev"], genre=SAMPLE["genre"],
                         players=SAMPLE["players"], playtime=SAMPLE["playtime"]).get(p["metadata"], "?")
            else:
                s = p.get("text", "").replace("${system.fullName}", SAMPLE["full"])
            bg = hexc(p["backgroundColor"]) if "backgroundColor" in p else None
            bgm = tuple(float(v) * r.Wp for v in p.get("backgroundMargins", "0 0").split())
            if w == 0:  # auto-sized text: measure, then apply the origin like ES-DE does
                fnt = r.font(p.get("fontPath", "x/MPLUSRounded1c-Medium.ttf"), float(p.get("fontSize", 0.045)) * H * 1.18)
                w = ImageDraw.Draw(r.img).textlength(s, font=fnt)
                h = float(p.get("fontSize", 0.045)) * H * float(p.get("lineSpacing", 1.5))
                ox, oy = r.pair(p.get("origin", "0 0"))
                x0_, y0_ = r.px(p["pos"])
                x, y = x0_ - ox * w, y0_ - oy * h
            r.text(s, x, y, w, h, float(p.get("fontSize", 0.045)), p.get("fontPath", "x/MPLUSRounded1c-Medium.ttf"),
                   hexc(p.get("color", "000000")), p.get("horizontalAlignment", "left"),
                   p.get("verticalAlignment", "center"), float(p.get("lineSpacing", 1.5)), bg, bgm,
                   float(p.get("backgroundCornerRadius", 0)) * r.Wp, p.get("letterCase", "none"), wrap=et == "text")
        elif et == "rating":
            x, y = r.px(p["pos"])
            hh = float(p["size"].split()[1]) * H
            for k in range(5):
                st = Image.new("RGBA", (100, 100))
                pts = [(50 + 40 * math.cos(-math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45),
                        52 + 40 * math.sin(-math.pi / 2 + j * math.pi / 5) * (1 if j % 2 == 0 else 0.45)) for j in range(10)]
                ImageDraw.Draw(st).polygon(pts, fill=(255, 194, 26) if k < 4 else (185, 192, 202))
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
            sel = 4
            cx, cy = x + w / 2, y + h / 2
            n = int(m / 2) + 1
            for k in list(range(-n, 0)) + list(range(n, 0, -1)) + [0]:
                s = sc if k == 0 else 1.0
                ww, hh = iw * s, ih * s
                if cx + k * step + ww / 2 < x or cx + k * step - ww / 2 > x + w:
                    continue
                if "imageType" in p:
                    b3 = p["imageType"].startswith("3dbox")
                    ch = hh
                    cw = min(ww, ch * (0.86 if b3 else 0.72))
                    r.paste(cover(cw, ch, sel + k, cf, b3), cx + k * step - cw / 2, cy - ch / 2, cw, ch,
                            radius=float(p.get("imageCornerRadius", 0)) * r.Wp)
                    if k:
                        r.rrect(cx + k * step - cw / 2, cy - ch / 2, cw, ch, 4, (0, 0, 0, 60))
                else:
                    fn = r.path(p["staticImage"]).replace("snes", SYSTEMS[(sel + k) % len(SYSTEMS)])
                    r.paste(Image.open(fn), cx + k * step - ww / 2, cy - hh / 2, ww, hh)
        elif et == "grid":
            x, y, w, h = r.box(p)
            iw, ih = r.pair(p["itemSize"])
            iw, ih = iw * r.Wp, ih * H
            sx, sy = r.pair(p["itemSpacing"])
            sx, sy = sx * r.Wp, sy * H
            cols = max(1, int((w + sx + 1) // (iw + sx)))
            rows = max(1, int((h + sy + 1) // (ih + sy)))
            ox = x  # ES-DE lays items out from the left edge of the grid box
            sc = float(p["itemScale"])
            selk = 2
            items = [(rr_, cc, rr_ * cols + cc) for rr_ in range(rows) for cc in range(cols)
                     if rr_ * cols + cc < ITEMS[0]]
            for rr_, cc, k in sorted(items, key=lambda t: t[2] == selk):
                s = sc if k == selk else 1
                ww, hh = iw * s, ih * s
                ix = ox + cc * (iw + sx) + iw / 2 - ww / 2
                iy = y + rr_ * (ih + sy) + ih / 2 - hh / 2
                if k == selk and "selectorImage" not in p:
                    r.rrect(ix, iy, ww, hh, float(p["selectorCornerRadius"]) * r.Wp * s, hexc(p["selectorColor"]))
                if "backgroundImage" in p:
                    r.paste(Image.open(r.path(p["backgroundImage"])), ix, iy, ww, hh)
                elif "backgroundColor" in p:
                    br = float(p.get("backgroundRelativeScale", 1))
                    r.rrect(ix + ww * (1 - br) / 2, iy + hh * (1 - br) / 2, ww * br, hh * br,
                            float(p["backgroundCornerRadius"]) * r.Wp * s * br, hexc(p["backgroundColor"]))
                if "staticImage" in p:
                    fn = r.path(p["staticImage"]).replace("/snes.png", "/" + SYSTEMS[k % len(SYSTEMS)] + ".png")
                    r.paste(Image.open(fn), ix, iy, ww, hh)
                else:
                    irs = float(p.get("imageRelativeScale", 1))
                    b3 = p.get("imageType", "").startswith("3dbox")
                    ch = hh * irs
                    cw = ch * (0.86 if b3 else 0.72)
                    r.paste(cover(cw, ch, k, cf, b3), ix + (ww - cw) / 2, iy + (hh - ch) / 2, cw, ch,
                            radius=float(p.get("imageCornerRadius", 0)) * r.Wp)
                if k == selk and "selectorImage" in p:
                    r.paste(Image.open(r.path(p["selectorImage"])), ix, iy, ww, hh, tint=hexc(p["selectorColor"]))
        elif et == "textlist":
            x, y, w, h = r.box(p)
            fs = float(p["fontSize"])
            lh = fs * H * float(p["lineSpacing"])
            hm = float(p.get("horizontalMargin", 0)) * r.Wp
            for k in range(int(h // lh)):
                ly = y + k * lh
                if k == 2:
                    mm = float(p["selectedBackgroundMargins"].split()[0]) * r.Wp
                    r.rrect(x - mm, ly + lh * 0.12, w + 2 * mm, lh * 0.76,
                            float(p["selectedBackgroundCornerRadius"]) * r.Wp, hexc(p["selectedBackgroundColor"]))
                col = hexc(p["selectedColor"] if k == 2 else p["primaryColor"])
                ImageDraw.Draw(r.img).text((x + hm, ly + lh / 2), GAMES[k % len(GAMES)],
                                           font=r.font(p["fontPath"], fs * H * 1.18), fill=col, anchor="lm")
        elif et == "clock":
            x, y = r.px(p["pos"])
            f = r.font(p["fontPath"], float(p["fontSize"]) * H * 1.18)
            s = (p["format"].replace("%H", "21").replace("%M", "47").replace("%Y", "2026").replace("%m", "10")
                 .replace("%d", "24").replace("%a", "Sat"))
            ox, oy = r.pair(p.get("origin", "0 0"))
            tw = ImageDraw.Draw(r.img).textlength(s, font=f)
            ImageDraw.Draw(r.img).text((x - ox * tw, y), s, font=f, fill=hexc(p["color"]), anchor="lm")
        elif et == "systemstatus":
            x, y = r.px(p["pos"])
            hh = float(p["height"]) * H
            col = hexc(p["color"])
            f = r.font(p["fontPath"], hh)
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
            f = r.font(p["fontPath"], fs * 1.18)
            fb = r.font(p["fontPath"], fs * 0.75)
            d = ImageDraw.Draw(r.img)
            items = [("+", "Choose"), ("A", "Select"), ("B", "Back"), ("X", "Random"), ("Y", "Favorite"), ("≡", "Menu")]
            total = sum(fs * 1.24 + 8 + d.textlength(lb, font=f) + fs * 0.9 for _, lb in items)
            ox, _ = r.pair(p.get("origin", "0 0"))
            cx = x - ox * total
            for ic, lb in items:
                d.ellipse([cx, y - fs * 0.62, cx + fs * 1.24, y + fs * 0.62], fill=col)
                d.text((cx + fs * 0.62, y), ic, font=fb, fill=hexc(r.vars["bgColor"]), anchor="mm")
                cx += fs * 1.24 + 8
                d.text((cx, y), lb, font=f, fill=col, anchor="lm")
                cx += d.textlength(lb, font=f) + fs * 0.9
    return r.img.convert("RGB")


os.makedirs(OUTDIR, exist_ok=True)
for job in sys.argv[4:]:
    key, scheme, view, out, *rest = job.split(",")
    ITEMS[0] = int(rest[0]) if rest else 99
    render(key, scheme, view).save(os.path.join(OUTDIR, out))
    print("rendered", out)
