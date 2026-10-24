"""Build all esdeii themes into the repo root.

    python3 tools/build.py <repo root> <Nunito[wght].ttf> <OFL.txt> [cache dir] [--json out.json]

Creates esde3ds/, esdeii/, esdeiiu/ (each a complete ES-DE theme) and music/.
"""
import json, os, shutil, sys, tempfile
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

import audio, icons, layouts, shapes, themeart
from systems_data import SYSTEMS, DEFAULT_TILE
from systems_info import INFO, line as info_line

ROOT, NUNITO_VF, NUNITO_OFL = sys.argv[1:4]
CACHE = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else tempfile.mkdtemp()
JSON_OUT = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
os.makedirs(CACHE, exist_ok=True)

ASPECTS = [("16:9", 16 / 9), ("16:10", 1.6), ("3:2", 1.5), ("4:3", 4 / 3), ("5:3", 5 / 3), ("5:4", 1.25),
           ("8:7", 8 / 7), ("19.5:9", 19.5 / 9), ("20:9", 20 / 9), ("21:9", 2560 / 1080)]
GAME_LAYOUTS = [("Grid", "icon grid"), ("List", "game list"), ("Shelf", "cover shelf")]


def scheme(bg, panel, border, text, sub, accent, screen, tile, deco, divider, dim, shadow="1E28361C",
           accent_text="FFFFFF", overlay="0.9"):
    return dict(bgColor=bg, panelColor=panel, borderColor=border, shadowColor=shadow, textColor=text,
                subColor=sub, accentColor=accent, accentText=accent_text, screenColor=screen, tileColor=tile,
                decoColor=deco, dividerColor=divider, dimText=dim, overlayOpacity=overlay)


S = {
    "cloudWhite": ("Cloud White", scheme("EDEFF2", "FFFFFF", "CBD2DA", "33393F", "7F8790", "1FB8E8", "2B313B",
                                         "F1F3F6", "C9D0D8", "E4E8EC", "5A616A")),
    "silverMenu": ("Silver Menu", scheme("E9EBEE", "FFFFFF", "C8CDD3", "3B4047", "8A9099", "34BEED", "2E3238",
                                         "F2F4F6", "C6CBD1", "E3E6EA", "5F656D")),
    "iceWhite": ("Ice White", scheme("EEF1F5", "FFFFFF", "D3D9E1", "2F3640", "7D8693", "1FA5EA", "2B313B",
                                     "EEF2F7", "CDD3DC", "E5E9EF", "5A626E")),
    "cosmoBlack": ("Cosmo Black", scheme("1A1D22", "2A2F37", "0E1013", "EEF1F5", "98A2AF", "3CB8FF", "14171B",
                                         "363C46", "30353D", "3A404A", "C3CAD4", "00000070", overlay="0.08")),
    "flameRed": ("Flame Red", scheme("F7E8E7", "FFFFFF", "E8C8C6", "3A2E2E", "8C7676", "E5404A", "2E2A2E",
                                     "F8EEED", "E6C2BF", "F1E1E0", "604E4E", "5A1E1A1C")),
    "aquaBlue": ("Aqua Blue", scheme("E2F0FA", "FFFFFF", "C0DAEC", "24384A", "6E8597", "1683D9", "22303C",
                                     "ECF5FB", "B7D3E6", "DDEBF5", "4A6072", "0F3C5A1C")),
    "mintGreen": ("Mint Green", scheme("E4F5EC", "FFFFFF", "BFE3CF", "21382B", "6B8A78", "22B07D", "22302A",
                                       "EEF8F2", "B5DCC7", "DDEFE4", "48604F", "0F3C281C")),
    "lavender": ("Lavender", scheme("EEEAF8", "FFFFFF", "D3CAEC", "2F2A45", "857DA0", "8B5CF6", "2B2838",
                                    "F4F1FB", "CDC3E8", "E8E3F5", "585170", "2A1E5A1C")),
    "sunset": ("Sunset Orange", scheme("FBEDE2", "FFFFFF", "F0D2BC", "3D2E24", "937A68", "F07A2E", "302A26",
                                       "FCF3EC", "EDCAB0", "F5E5D8", "64503F", "5A321A1C")),
    "sakura": ("Sakura Pink", scheme("FBEAF0", "FFFFFF", "F0CBD9", "40283A", "967286", "E8508A", "302830",
                                     "FCF1F5", "EEC4D4", "F6E2EA", "684B5C", "5A1E3A1C")),
    "midnight": ("Midnight Blue", scheme("111827", "1C2638", "0A0F18", "E6EDF7", "8EA0B8", "5AA9FF", "0D131E",
                                         "263247", "1E293B", "2C3A52", "BCC8D8", "00000070", overlay="0.06")),
    "retroPocket": ("Retro Pocket", scheme("B9C48A", "D4DCA6", "8E9A5E", "0F380F", "306230", "306230", "0F380F",
                                           "C6CF98", "9AA66A", "BCC690", "1E4A1E", "0F380F33", "D4DCA6", "0.25")),
    "lightSystem": ("Light + system colours", scheme("EEF1F5", "FFFFFF", "D3D9E1", "2F3640", "7D8693", "1FA5EA",
                                                     "2B313B", "EEF2F7", "CDD3DC", "E5E9EF", "5A626E")),
    "darkSystem": ("Dark + system colours", scheme("1A1D22", "2A2F37", "0E1013", "EEF1F5", "98A2AF", "3CB8FF",
                                                   "14171B", "363C46", "30353D", "3A404A", "C3CAD4", "00000070",
                                                   overlay="0.08")),
}
SYSTEM_ACCENT = ["lightSystem", "darkSystem"]
REST = ["cosmoBlack", "flameRed", "aquaBlue", "mintGreen", "lavender", "sunset", "sakura", "midnight", "retroPocket"]

THEMES = {
    "esde3ds": dict(builder="3ds", styles=[("glossy", "Glossy"), ("channel", "Channel"), ("plaza", "Plaza")],
                    sounds="chime", schemes=["iceWhite"] + REST + ["silverMenu", "cloudWhite"] + SYSTEM_ACCENT,
                    blurb="dual-screen handheld style"),
    "esdeii": dict(builder="wii", styles=[("channelwide", None)], sounds="click",
                   schemes=["silverMenu", "iceWhite"] + REST + ["cloudWhite"] + SYSTEM_ACCENT,
                   blurb="living-room console menu style"),
    "esdeiiu": dict(builder="wiiu", styles=[("plaza", "Plaza"), ("glossy", "Glossy")], sounds="pop",
                    schemes=["cloudWhite", "iceWhite"] + REST + ["silverMenu"] + SYSTEM_ACCENT,
                    blurb="tablet console home screen style"),
}

FONT_SIZES = {"medium": 1.0, "small": 0.88, "large": 1.14}
FS_BASE = dict(fsTitle=0.056, fsName3ds=0.05, fsWiiHeader=0.05, fsWiiClock=0.075, fsGameName=0.041,
               fsLabel=0.019, fsMeta=0.027, fsDesc=0.025, fsList=0.031, fsStatus=0.03, fsHelp=0.028,
               fsCount=0.03, fsSmall=0.022, fsFeat=0.026)
TRANSITIONS = [
    ("slide", "Slide", dict(systemToGamelist="slide", gamelistToSystem="slide", startupToSystem="fade",
                            startupToGamelist="fade")),
    ("fade", "Fade", dict(systemToGamelist="fade", gamelistToSystem="fade", startupToSystem="fade",
                          startupToGamelist="fade")),
    ("instant", "Instant", dict(systemToGamelist="instant", gamelistToSystem="instant")),
]


# ---------------------------------------------------------------- cached assets
def fonts():
    d = os.path.join(CACHE, "fonts")
    if not os.path.exists(os.path.join(d, "Nunito-Black.ttf")):
        os.makedirs(d, exist_ok=True)
        for name, wght in (("Nunito-SemiBold", 600), ("Nunito-ExtraBold", 800), ("Nunito-Black", 900)):
            inst = instancer.instantiateVariableFont(TTFont(NUNITO_VF), {"wght": wght}, updateFontNames=False)
            inst.save(os.path.join(d, name + ".ttf"))
        shutil.copy(NUNITO_OFL, os.path.join(d, "OFL.txt"))
    return d


def ss(size, fn, k=4):
    big = Image.new("RGBA", (size[0] * k, size[1] * k), (0, 0, 0, 0))
    fn(ImageDraw.Draw(big), k, big)
    return big.resize(size, Image.LANCZOS)


def images(fontdir):
    d = os.path.join(CACHE, "images")
    if os.path.exists(os.path.join(d, "done")):
        return d
    os.makedirs(d, exist_ok=True)
    Image.new("RGBA", (16, 16), (255, 255, 255, 255)).save(os.path.join(d, "white.png"))
    T = 96
    bg = Image.new("RGB", (T, T), (255, 255, 255))
    g = ImageDraw.Draw(bg)
    g.line([(0, 0), (T, 0)], fill=(236, 238, 242), width=2)
    g.line([(0, 0), (0, T)], fill=(236, 238, 242), width=2)
    g.line([(0, T // 2), (T, T // 2)], fill=(246, 247, 249), width=1)
    g.line([(T // 2, 0), (T // 2, T)], fill=(246, 247, 249), width=1)
    bg.save(os.path.join(d, "bg-grid.png"))

    def speaker(dr, s, img):
        W, H = img.size
        for i in range(3):
            for j in range(6):
                cx = W / 2 + (i - 1) * 26 * s + (13 * s if j % 2 else 0) - 6 * s
                cy = 20 * s + j * 22 * s
                dr.ellipse([cx - 7 * s, cy - 7 * s, cx + 7 * s, cy + 7 * s], fill=(255, 255, 255, 255))
    ss((110, 150), speaker).save(os.path.join(d, "speaker.png"))
    ss((240, 30), lambda dr, s, img: dr.rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                                           radius=img.size[1] / 2, fill=(255, 255, 255, 255))
       ).save(os.path.join(d, "pill.png"))

    def ring(dr, s, img):
        W = img.size[0]
        t, rad = 16 * s, 96 * s
        dr.rounded_rectangle([0, 0, W - 1, W - 1], radius=rad, fill=(255, 255, 255, 255))
        dr.rounded_rectangle([t, t, W - 1 - t, W - 1 - t], radius=rad - t, fill=(0, 0, 0, 0))
    ss((400, 400), ring).save(os.path.join(d, "cursor.png"))
    star = "M50 6 L62.9 34.2 L93.8 37.6 L70.8 58.4 L77.2 88.8 L50 73.4 L22.8 88.8 L29.2 58.4 L6.2 37.6 L37.1 34.2 Z"
    for name, fill in (("star-filled.svg", "#FFC21A"), ("star-unfilled.svg", "#B9C0CA")):
        with open(os.path.join(d, name), "w") as fh:
            fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
                     f'<g transform="translate(50 50) scale(0.82) translate(-50 -50)"><path d="{star}" '
                     f'fill="{fill}" stroke="{fill}" stroke-width="6" stroke-linejoin="round"/></g></svg>')
    im = Image.new("RGBA", (640, 360), (52, 58, 68, 255))
    g = ImageDraw.Draw(im)
    for k in range(-360, 640, 28):
        g.line([(k, 360), (k + 360, 0)], fill=(58, 64, 75, 255), width=10)
    im.paste((92, 100, 114, 255), (245, 105), shapes.glyph("console", 150))
    im.convert("RGB").save(os.path.join(d, "noimage.png"), optimize=True)
    im = Image.new("RGBA", (360, 500), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    g.rounded_rectangle([0, 0, 359, 499], radius=26, fill=(214, 220, 228, 255))
    g.rounded_rectangle([16, 16, 343, 483], radius=16, fill=(238, 241, 245, 255))
    im.paste((176, 184, 194, 255), (95, 165), shapes.glyph("cart", 170))
    im.save(os.path.join(d, "nocover.png"), optimize=True)
    themeart.build_all(d, os.path.join(fontdir, "Nunito-Black.ttf"))
    open(os.path.join(d, "done"), "w").close()
    return d


def icon_set(style, fontdir):
    d = os.path.join(CACHE, "icons", style)
    if os.path.exists(os.path.join(d, "_default.png")):
        return d
    os.makedirs(d, exist_ok=True)
    fn = icons.STYLES.get(style) or icons.WSTYLES[style]
    for name, (label, kind, colour) in list(SYSTEMS.items()) + [("_default", DEFAULT_TILE)]:
        g = icons.GLYPHS.get(name, icons.CATEGORY_GLYPH.get(kind, "console"))
        fn(label, g, colour, os.path.join(fontdir, "Nunito-Black.ttf")).save(os.path.join(d, name + ".png"),
                                                                            optimize=True)
    print("  icons:", style)
    return d


def sounds(pack):
    d = os.path.join(CACHE, "sounds", pack)
    if not os.path.exists(os.path.join(d, "select.wav")):
        audio.write_pack(pack, d)
    return d


# ---------------------------------------------------------------- XML writing
def props_xml(props, ind):
    return "\n".join(f"{ind}<{k}>{escape(str(v))}</{k}>" for k, v in props.items())


def views_xml(L):
    out = ["<theme>"]
    for view, els in L.views.items():
        out.append(f'    <view name="{view}">')
        for etype, name, props in els:
            out += [f'        <{etype} name="{name}">', props_xml(props, " " * 12), f"        </{etype}>"]
        out.append("    </view>")
    out.append("</theme>")
    return "\n".join(out) + "\n"


def write_theme(key, cfg, fontdir, imgdir, dump):
    out = os.path.join(ROOT, key)
    if os.path.exists(out):
        shutil.rmtree(out)
    for sub in ("layouts", "systeminfo", "assets"):
        os.makedirs(os.path.join(out, sub), exist_ok=True)
    shutil.copytree(fontdir, os.path.join(out, "assets", "fonts"))
    shutil.copytree(imgdir, os.path.join(out, "assets", "images"), ignore=shutil.ignore_patterns("done"))
    shutil.copytree(sounds(cfg["sounds"]), os.path.join(out, "assets", "sounds"))
    for style, _ in cfg["styles"]:
        shutil.copytree(icon_set(style, fontdir), os.path.join(out, "systems", style))

    variants = []
    for style, slabel in cfg["styles"]:
        for lay, desc in GAME_LAYOUTS:
            name = f"{style}{lay}" if slabel else lay.lower()
            label = f"{slabel} icons + {desc}" if slabel else desc.capitalize()
            variants.append((name, label, style, lay.lower()))

    build = layouts.BUILDERS[cfg["builder"]]
    files = {}
    for ar, W in ASPECTS:
        for name, _, style, lay in variants:
            L = build(W, style, lay)
            fn = f"{ar.replace(':', 'x').replace('.', '_')}-{name}.xml"
            with open(os.path.join(out, "layouts", fn), "w") as fh:
                fh.write(f"<!-- {key} layout: {ar}, {name} (generated by tools/build.py) -->\n" + views_xml(L))
            files[(ar, name)] = fn
            if dump is not None:
                dump[f"{key}|{ar}|{name}"] = {"W": W, "views": L.views}

    # per-system info + accent colour
    acc = ", ".join(SYSTEM_ACCENT)
    for sysname, (_, _, colour) in SYSTEMS.items():
        with open(os.path.join(out, "systeminfo", sysname + ".xml"), "w") as fh:
            fh.write(f"<theme>\n    <variables>\n        <sysInfo>{escape(info_line(sysname) or 'Game library')}"
                     f"</sysInfo>\n    </variables>\n    <colorScheme name=\"{acc}\">\n        <variables>\n"
                     f"            <accentColor>{colour}</accentColor>\n        </variables>\n"
                     f"    </colorScheme>\n</theme>\n")

    cap = [f"<!-- Theme capabilities for {key} -->", "<themeCapabilities>", f"    <themeName>{key}</themeName>", ""]
    cap += [f"    <aspectRatio>{ar}</aspectRatio>" for ar, _ in ASPECTS] + [""]
    cap += [f"    <fontSize>{s}</fontSize>" for s in FONT_SIZES] + [""]
    for sk in cfg["schemes"]:
        cap += [f'    <colorScheme name="{sk}">', f"        <label>{S[sk][0]}</label>", "    </colorScheme>"]
    cap.append("")
    for tname, tlabel, rows in TRANSITIONS:
        cap += [f'    <transitions name="{key}{tname.capitalize()}">', f"        <label>{tlabel}</label>",
                "        <systemToSystem>instant</systemToSystem>",
                "        <gamelistToGamelist>instant</gamelistToGamelist>"]
        cap += [f"        <{k}>{v}</{k}>" for k, v in rows.items()] + ["    </transitions>"]
    cap.append("")
    for name, label, _, _ in variants:
        cap += [f'    <variant name="{name}">', f"        <label>{label}</label>",
                "        <selectable>true</selectable>", "    </variant>"]
    cap.append("</themeCapabilities>")
    with open(os.path.join(out, "capabilities.xml"), "w") as fh:
        fh.write("\n".join(cap) + "\n")

    t = [f"<!-- {key}: {cfg['blurb']} theme for ES-DE (generated by tools/build.py) -->", "<theme>",
         "    <include>./navigationsounds.xml</include>", "",
         "    <variables>", "        <sysInfo>Game library</sysInfo>", "    </variables>", ""]
    for sk in cfg["schemes"]:
        t += [f'    <colorScheme name="{sk}">', "        <variables>"]
        t += [f"            <{k}>{v}</{k}>" for k, v in S[sk][1].items()]
        t += ["        </variables>", "    </colorScheme>"]
    t += ["", "    <!-- Per-system info line and accent colour (missing files are skipped) -->",
          "    <include>./systeminfo/${system.theme}.xml</include>", ""]
    for size, mult in FONT_SIZES.items():
        t += [f'    <fontSize name="{size}">', "        <variables>"]
        t += [f"            <{k}>{layouts.f(v * mult)}</{k}>" for k, v in FS_BASE.items()]
        t += ["        </variables>", "    </fontSize>"]
    t.append("")
    for name, _, _, _ in variants:
        t.append(f'    <variant name="{name}">')
        for ar, _ in ASPECTS:
            t += [f'        <aspectRatio name="{ar}">', f"            <include>./layouts/{files[(ar, name)]}</include>",
                  "        </aspectRatio>"]
        t.append("    </variant>")
    t.append("</theme>")
    with open(os.path.join(out, "theme.xml"), "w") as fh:
        fh.write("\n".join(t) + "\n")

    ns = ["<theme>", '    <view name="all">']
    for s in ("systembrowse", "quicksysselect", "select", "back", "scroll", "favorite", "launch"):
        ns += [f'        <sound name="{s}">', f"            <path>./assets/sounds/{s}.wav</path>", "        </sound>"]
    ns += ["    </view>", "</theme>"]
    with open(os.path.join(out, "navigationsounds.xml"), "w") as fh:
        fh.write("\n".join(ns) + "\n")
    print(key, ":", len(variants), "variants,", len(files), "layout files")
    return variants


if __name__ == "__main__":
    fontdir = fonts()
    imgdir = images(fontdir)
    dump = {} if JSON_OUT else None
    for key, cfg in THEMES.items():
        write_theme(key, cfg, fontdir, imgdir, dump)
    mdir = os.path.join(ROOT, "music")
    if not os.path.exists(mdir) or "--music" in sys.argv:
        audio.write_music(mdir, CACHE)
    if JSON_OUT:
        with open(JSON_OUT, "w") as fh:
            json.dump({"layouts": dump, "schemes": {k: v[1] for k, v in S.items()}, "fonts": FS_BASE}, fh)
