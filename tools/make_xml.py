"""Write the XML for the esdeii ES-DE theme.

All layout maths is done in "height units": the screen is 1.0 tall and W wide,
where W is the aspect ratio. Values are converted to ES-DE's normalized
coordinates (0..1 on both axes) when written out. Corner radii in ES-DE are a
fraction of screen *width*, so they get divided by W too.

Run from the repo root:  python3 tools/make_xml.py .
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xml.sax.saxutils import escape
import icons
from systems_data import SYSTEMS

OUT = sys.argv[1]
for d in ("layouts", "systemcolors"):
    os.makedirs(os.path.join(OUT, d), exist_ok=True)

ASPECTS = [
    ("16:9", 16 / 9), ("16:10", 1.6), ("3:2", 1.5), ("4:3", 4 / 3), ("5:3", 5 / 3),
    ("5:4", 1.25), ("8:7", 8 / 7), ("19.5:9", 19.5 / 9), ("20:9", 20 / 9), ("21:9", 2560 / 1080),
]

ICON_STYLES = [("glossy", "glossy", "Glossy"), ("channel", "channel", "Channel"), ("plaza", "plaza", "Plaza")]
GAME_LAYOUTS = [("Grid", "icon grid"), ("List", "game list"), ("Shelf", "cover shelf")]
VARIANTS = [(f"{key}{lay}", f"{label} icons + {desc}", style, lay.lower())
            for style, key, label in ICON_STYLES for lay, desc in GAME_LAYOUTS]


def scheme(bg, panel, border, text, sub, accent, screen, tile, deco, divider, dim,
           shadow="1E28361C", accent_text="FFFFFF"):
    return dict(bgColor=bg, panelColor=panel, borderColor=border, shadowColor=shadow,
                textColor=text, subColor=sub, accentColor=accent, accentText=accent_text,
                screenColor=screen, tileColor=tile, decoColor=deco, dividerColor=divider, dimText=dim)


LIGHT = dict(panel="FFFFFF", screen="2B313B")
SCHEMES = {
    "iceWhite": ("Ice White", scheme("EEF1F5", "FFFFFF", "D3D9E1", "2F3640", "7D8693", "1FA5EA",
                                     "2B313B", "EEF2F7", "CDD3DC", "E5E9EF", "5A626E")),
    "cosmoBlack": ("Cosmo Black", scheme("1A1D22", "2A2F37", "0E1013", "EEF1F5", "98A2AF", "3CB8FF",
                                         "14171B", "363C46", "30353D", "3A404A", "C3CAD4", "00000070")),
    "silverMenu": ("Silver Menu", scheme("E9EBEE", "FFFFFF", "C8CDD3", "3B4047", "8A9099", "34BEED",
                                   "2E3238", "F2F4F6", "C6CBD1", "E3E6EA", "5F656D")),
    "flameRed": ("Flame Red", scheme("F7E8E7", "FFFFFF", "E8C8C6", "3A2E2E", "8C7676", "E5404A",
                                     "2E2A2E", "F8EEED", "E6C2BF", "F1E1E0", "604E4E", "5A1E1A1C")),
    "aquaBlue": ("Aqua Blue", scheme("E2F0FA", "FFFFFF", "C0DAEC", "24384A", "6E8597", "1683D9",
                                     "22303C", "ECF5FB", "B7D3E6", "DDEBF5", "4A6072", "0F3C5A1C")),
    "mintGreen": ("Mint Green", scheme("E4F5EC", "FFFFFF", "BFE3CF", "21382B", "6B8A78", "22B07D",
                                       "22302A", "EEF8F2", "B5DCC7", "DDEFE4", "48604F", "0F3C281C")),
    "lavender": ("Lavender", scheme("EEEAF8", "FFFFFF", "D3CAEC", "2F2A45", "857DA0", "8B5CF6",
                                    "2B2838", "F4F1FB", "CDC3E8", "E8E3F5", "585170", "2A1E5A1C")),
    "sunset": ("Sunset Orange", scheme("FBEDE2", "FFFFFF", "F0D2BC", "3D2E24", "937A68", "F07A2E",
                                       "302A26", "FCF3EC", "EDCAB0", "F5E5D8", "64503F", "5A321A1C")),
    "sakura": ("Sakura Pink", scheme("FBEAF0", "FFFFFF", "F0CBD9", "40283A", "967286", "E8508A",
                                     "302830", "FCF1F5", "EEC4D4", "F6E2EA", "684B5C", "5A1E3A1C")),
    "midnight": ("Midnight Blue", scheme("111827", "1C2638", "0A0F18", "E6EDF7", "8EA0B8", "5AA9FF",
                                         "0D131E", "263247", "1E293B", "2C3A52", "BCC8D8", "00000070")),
    "retroPocket": ("Retro Pocket", scheme("B9C48A", "D4DCA6", "8E9A5E", "0F380F", "306230", "306230",
                                     "0F380F", "C6CF98", "9AA66A", "BCC690", "1E4A1E", "0F380F33",
                                     "D4DCA6")),
    "iceSystem": ("Ice White + system colours", scheme("EEF1F5", "FFFFFF", "D3D9E1", "2F3640", "7D8693",
                                                       "1FA5EA", "2B313B", "EEF2F7", "CDD3DC", "E5E9EF", "5A626E")),
    "cosmoSystem": ("Cosmo Black + system colours", scheme("1A1D22", "2A2F37", "0E1013", "EEF1F5", "98A2AF",
                                                          "3CB8FF", "14171B", "363C46", "30353D", "3A404A",
                                                          "C3CAD4", "00000070")),
}
SYSTEM_ACCENT_SCHEMES = ["iceSystem", "cosmoSystem"]

FONT_SIZES = {"medium": 1.0, "small": 0.88, "large": 1.14}
FS_BASE = dict(fsTitle=0.056, fsGameName=0.041, fsLabel=0.019, fsMeta=0.027, fsDesc=0.025,
               fsList=0.031, fsStatus=0.03, fsHelp=0.028, fsCount=0.03, fsSmall=0.022, fsFeat=0.026)

FONT_REG = "./../assets/fonts/Nunito-SemiBold.ttf"
FONT_BOLD = "./../assets/fonts/Nunito-ExtraBold.ttf"
FONT_BLACK = "./../assets/fonts/Nunito-Black.ttf"
IMG = "./../assets/images/"
SYS = "./../systems/"


def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Layout:
    def __init__(self, W):
        self.W = W
        self.views = {"system": [], "gamelist": []}

    def x(self, v):
        return v / self.W

    def pair(self, x, y):
        return f"{f(self.x(x))} {f(y)}"

    def rad(self, r):
        return f(r / self.W)

    def add(self, view, etype, name, **props):
        self.views[view].append((etype, name, props))

    def panel(self, view, name, x0, y0, w, h, r=0.034, z=5):
        b = 0.006
        self.add(view, "image", name + "Shadow", pos=self.pair(x0 - b, y0 - b + 0.009),
                 size=self.pair(w + 2 * b, h + 2 * b), path=IMG + "white.png",
                 color="${shadowColor}", cornerRadius=self.rad(r + b), zIndex=f(z))
        self.add(view, "image", name + "Border", pos=self.pair(x0 - b, y0 - b),
                 size=self.pair(w + 2 * b, h + 2 * b), path=IMG + "white.png",
                 color="${borderColor}", cornerRadius=self.rad(r + b), zIndex=f(z + 0.1))
        self.add(view, "image", name, pos=self.pair(x0, y0), size=self.pair(w, h),
                 path=IMG + "white.png", color="${panelColor}", cornerRadius=self.rad(r),
                 zIndex=f(z + 0.2))

    def rect(self, view, name, x0, y0, w, h, color, r=0.0, z=6, **extra):
        p = dict(pos=self.pair(x0, y0), size=self.pair(w, h), path=IMG + "white.png",
                 color=color, zIndex=f(z))
        if r:
            p["cornerRadius"] = self.rad(r)
        p.update(extra)
        self.add(view, "image", name, **p)

    def text(self, view, name, x0, y0, w, h, fs, font=FONT_REG, color="${textColor}", z=40,
             origin=None, **extra):
        p = dict(pos=self.pair(x0, y0), size=self.pair(w, h), fontPath=font,
                 fontSize="${" + fs + "}", color=color, zIndex=f(z))
        if origin:
            p["origin"] = origin
        p.update(extra)
        self.add(view, "text", name, **p)


def build(W, variant):
    vname, _, style, layout = variant
    L = Layout(W)
    sysimg = SYS + style + "/"

    decor = W >= 1.6
    side = min(0.24, (W - 1.30) / 2) if decor else 0.03
    px, pw = side, W - 2 * side
    wide = pw >= 1.6

    for view in ("system", "gamelist"):
        L.add(view, "image", "background", pos="0 0", size="1 1", path=IMG + "bg-grid.png",
              tile="true", tileSize=f"0 {f(0.09)}", color="${bgColor}", stationary="always", zIndex="0")

    geo = {"system": dict(up=(0.035, 0.555), lo=(0.595, 0.915)),
           "gamelist": dict(up=(0.035, 0.485), lo=(0.525, 0.915))}

    for view, g in geo.items():
        uy0, uy1 = g["up"]
        ly0, ly1 = g["lo"]
        L.panel(view, "upperScreen", px, uy0, pw, uy1 - uy0)
        L.panel(view, "lowerScreen", px, ly0, pw, ly1 - ly0)
        hy = (uy1 + ly0) / 2 - 0.011
        for i, hx in enumerate((px + 0.10, px + pw - 0.10 - 0.20)):
            L.add(view, "image", f"hinge{i}", pos=L.pair(hx, hy), size=L.pair(0.20, 0.022),
                  path=IMG + "pill.png", color="${borderColor}", zIndex="4")
        L.rect(view, "statusDivider", px + 0.02, uy0 + 0.067, pw - 0.04, 0.0028, "${dividerColor}", z=7)
        if decor:  # speaker grilles beside the top screen
            sw = min(0.085, side * 0.42)
            sh = sw * 150 / 110
            uc = (uy0 + uy1) / 2
            for i, cx in enumerate((side / 2, W - side / 2)):
                L.add(view, "image", f"speaker{i}", pos=L.pair(cx, uc), origin="0.5 0.5",
                      size=L.pair(sw, sh), path=IMG + "speaker.png", color="${decoColor}", zIndex="3")

        sy = uy0 + 0.034
        L.add(view, "clock", "clock", pos=L.pair(px + 0.03, sy), origin="0 0.5",
              fontPath=FONT_BLACK, fontSize="${fsStatus}", color="${subColor}", format="%H:%M")
        if decor:  # no room for the date on narrow screens
            L.add(view, "clock", "date", pos=L.pair(px + 0.135, sy), origin="0 0.5",
                  fontPath=FONT_BOLD, fontSize="${fsStatus}", color="${subColor}", format="%Y-%m-%d",
                  opacity="0.75")
        L.add(view, "systemstatus", "systemStatus", pos=L.pair(px + pw - 0.03, sy), origin="1 0.5",
              height="${fsStatus}", color="${subColor}", fontPath=FONT_BOLD)
        L.add(view, "helpsystem", "help", pos=L.pair(px + 0.01, 0.958), origin="0 0.5",
              fontPath=FONT_BOLD, fontSize="${fsHelp}", textColor="${subColor}", iconColor="${subColor}",
              letterCase="capitalize", entrySpacing="0.012")

    # ================================================================== SYSTEM VIEW
    uy0, uy1 = geo["system"]["up"]
    ly0, ly1 = geo["system"]["lo"]
    v = "system"
    L.add(v, "gameselector", "featured", selection="random", gameCount="1")
    L.add(v, "gameselector", "recent", selection="lastplayed", gameCount="3")

    tile = 0.34
    tx, ty = px + 0.045, uy0 + 0.095
    L.add(v, "image", "systemTile", pos=L.pair(tx, ty), size=L.pair(tile, tile),
          path=sysimg + "${system.theme}.png", default=sysimg + "_default.png", zIndex="20")

    nx = tx + tile + 0.04
    if wide:
        prev_w, prev_h = 0.56, 0.315
        prev_x = px + pw - 0.04 - prev_w
        name_w = prev_x - 0.04 - nx
    else:
        name_w = px + pw - 0.04 - nx

    L.text(v, "systemName", nx, uy0 + 0.10, name_w, 0.14, "fsTitle", FONT_BLACK, "${textColor}",
           text="${system.fullName}", verticalAlignment="top", lineSpacing="1.12")
    L.text(v, "gameCount", nx + 0.012, uy0 + 0.262, 0, 0, "fsCount", FONT_BOLD, "${accentText}",
           systemdata="gamecount", backgroundColor="${accentColor}",
           backgroundMargins=f"{L.rad(0.014)} {L.rad(0.014)}", backgroundCornerRadius=L.rad(0.03),
           lineSpacing="1.6", z=41)

    # "Jump back in": the three most recently played games as little covers
    L.text(v, "recentLabel", nx, uy0 + 0.33, name_w, 0.03, "fsSmall", FONT_BOLD, "${subColor}",
           text="Jump back in", letterCase="uppercase")
    cov_h, cov_w = 0.135, 0.105
    for i in range(3):
        cx = nx + cov_w / 2 + i * (cov_w + 0.025)
        L.add(v, "image", f"recentCover{i}", pos=L.pair(cx, uy0 + 0.37 + cov_h), origin="0.5 1",
              maxSize=L.pair(cov_w, cov_h), imageType="cover, miximage", default=IMG + "nocover.png",
              gameselector="recent", gameselectorEntry=str(i), cornerRadius=L.rad(0.006), zIndex="20")

    if wide:  # random featured game on the right
        py = uy0 + 0.09 + (uy1 - uy0 - 0.09 - prev_h) / 2 - 0.005
        L.rect(v, "previewScreen", prev_x, py, prev_w, prev_h, "${screenColor}", 0.016, z=18)
        L.add(v, "image", "featuredImage", pos=L.pair(prev_x, py), cropSize=L.pair(prev_w, prev_h),
              imageType="screenshot, titlescreen, miximage", gameselector="featured",
              cornerRadius=L.rad(0.016), zIndex="19")
        L.text(v, "featuredName", prev_x + 0.02, py + prev_h - 0.03, 0, 0, "fsFeat", FONT_BOLD,
               "FFFFFF", origin="0 1", metadata="name", gameselector="featured", systemNameSuffix="false",
               backgroundColor="000000A0", backgroundMargins=f"{L.rad(0.012)} {L.rad(0.012)}",
               backgroundCornerRadius=L.rad(0.02), lineSpacing="1.5", z=21)
        L.text(v, "featuredLabel", prev_x + 0.008, py - 0.006, prev_w, 0.026, "fsSmall", FONT_BOLD,
               "${subColor}", origin="0 1", text="Featured", letterCase="uppercase")

    # lower screen: row of system tiles with a fixed cursor in the middle
    item, scale, step = 0.165, 1.32, 0.255
    car_y0, car_h = ly0 + 0.005, ly1 - ly0 - 0.01
    L.add(v, "carousel", "systemcarousel", pos=L.pair(px + 0.01, car_y0),
          size=L.pair(pw - 0.02, car_h), type="horizontal",
          staticImage=sysimg + "${system.theme}.png",
          itemSize=L.pair(item, item), itemScale=f(scale), maxItemCount=f((pw - 0.02) / step),
          unfocusedItemOpacity="1", unfocusedItemDimming="0.94", imageFit="contain",
          color="00000000", text="${system.fullName}", fontPath=FONT_BLACK, fontSize="0.026",
          textColor="FFFFFF", textBackgroundColor="${accentColor}",
          textBackgroundCornerRadius=L.rad(0.04), textRelativeScale="0.85", lineSpacing="1.15",
          itemVerticalAlignment="center", fastScrolling="true", zIndex="50")
    content = item * scale * icons.BODY_FRAC
    ring = content + 0.034
    cy = car_y0 + car_h / 2 - item * scale * icons.BODY_OFFSET_FRAC
    L.add(v, "image", "cursor", pos=L.pair(px + pw / 2, cy), origin="0.5 0.5", size=L.pair(ring, ring),
          path=IMG + "cursor.png",
          color="${accentColor}", zIndex="55")

    # ================================================================== GAMELIST VIEW
    uy0, uy1 = geo["gamelist"]["up"]
    ly0, ly1 = geo["gamelist"]["lo"]
    v = "gamelist"

    L.text(v, "systemLabel", px + pw / 2 + (0.04 if decor else -0.02), uy0 + 0.034,
           pw * (0.42 if decor else 0.3), 0.032, "fsStatus", FONT_BOLD, "${subColor}", origin="0.5 0.5",
           text="${system.fullName}", horizontalAlignment="center")

    body_y0 = uy0 + 0.088
    body_y1 = uy1 - 0.022
    mh = body_y1 - body_y0
    mw = min(mh * 16 / 9, pw * 0.44)
    mx = px + 0.025
    L.rect(v, "mediaScreen", mx, body_y0, mw, mh, "${screenColor}", 0.016, z=18)
    L.add(v, "video", "gameVideo", pos=L.pair(mx, body_y0), zIndex="20",
          imageType="screenshot, titlescreen, miximage", scrollFadeIn="true", cropSize=L.pair(mw, mh),
          defaultImage=IMG + "noimage.png", imageCornerRadius=L.rad(0.016),
          videoCornerRadius=L.rad(0.016), delay="1.6", fadeInTime="0.6")

    x0 = mx + mw + 0.035
    xr = px + pw - 0.03
    if wide:
        dw = 0.44
        cw = xr - x0 - dw - 0.035
        L.text(v, "gameName", x0, body_y0, cw, 0.1, "fsGameName", FONT_BLACK, "${textColor}",
               metadata="name", verticalAlignment="top", lineSpacing="1.15")
        r1, gap = body_y0 + 0.11, 0.062
    else:
        cw = xr - x0
        L.text(v, "gameName", x0, body_y0, cw, 0.05, "fsGameName", FONT_BLACK, "${textColor}",
               metadata="name")
        r1, gap = body_y0 + 0.058, 0.06
    col2 = x0 + cw / 2 + 0.01
    half = cw / 2 - 0.015
    lab = dict(letterCase="uppercase", metadataElement="true")

    def cell(xx, y, nm, title, kind, meta, default="Unknown", **extra):
        L.text(v, nm + "Label", xx, y, half, 0.024, "fsLabel", FONT_BOLD, "${subColor}", text=title, **lab)
        if kind == "datetime":
            L.add(v, "datetime", nm, pos=L.pair(xx, y + 0.022), size=L.pair(half, 0.032), metadata=meta,
                  fontPath=FONT_BOLD, fontSize="${fsMeta}", color="${dimText}", defaultValue=default,
                  **extra)
        else:
            L.text(v, nm, xx, y + 0.022, half, 0.032, "fsMeta", FONT_BOLD, "${dimText}", metadata=meta,
                   defaultValue=default)

    cell(x0, r1, "released", "Released", "datetime", "releasedate", format="%Y-%m-%d")
    cell(col2, r1, "players", "Players", "text", "players")
    cell(x0, r1 + gap, "developer", "Developer", "text", "developer")
    cell(col2, r1 + gap, "genre", "Genre", "text", "genre")
    cell(x0, r1 + 2 * gap, "lastPlayed", "Last played", "datetime", "lastplayed", default="Never")
    L.text(v, "playTimeLabel", col2, r1 + 2 * gap, half, 0.024, "fsLabel", FONT_BOLD, "${subColor}",
           text="Play time", **lab)
    L.text(v, "playTime", col2, r1 + 2 * gap + 0.022, half, 0.032, "fsMeta", FONT_BOLD, "${dimText}",
           metadata="playtime")
    r3 = r1 + 3 * gap + 0.006
    L.add(v, "rating", "gameRating", pos=L.pair(x0, r3), size="0 0.028",
          filledPath=IMG + "star-filled.svg", unfilledPath=IMG + "star-unfilled.svg",
          interpolation="linear", zIndex="45")
    L.add(v, "badges", "gameBadges", pos=L.pair(x0 + cw, r3 - 0.002), origin="1 0",
          size=L.pair(min(0.32, cw * 0.55), 0.032), horizontalAlignment="right", direction="row",
          lines="1", itemsPerLine="8", itemMargin=f"{L.rad(0.006)} 0.006",
          slots="favorite completed kidgame broken controller altemulator manual", zIndex="45")
    if wide:
        dx = xr - dw
        L.text(v, "descriptionLabel", dx, body_y0, dw, 0.024, "fsLabel", FONT_BOLD, "${subColor}",
               text="About", **lab)
        L.text(v, "gameDescription", dx, body_y0 + 0.032, dw, mh - 0.032, "fsDesc", FONT_REG,
               "${dimText}", metadata="description", lineSpacing="1.35", containerStartDelay="5")
    else:
        dy = r3 + 0.04
        if body_y1 - dy > 0.03:
            L.text(v, "gameDescription", x0, dy, cw, body_y1 - dy, "fsDesc", FONT_REG, "${dimText}",
                   metadata="description", lineSpacing="1.3", containerStartDelay="5")

    info_pos = L.pair(px + pw - 0.01, 0.958) if decor else L.pair(px + pw - 0.24, uy0 + 0.034)
    L.add(v, "gamelistinfo", "gamelistInfo", pos=info_pos, origin="1 0.5",
          size=L.pair(pw * 0.4 if decor else 0.2, 0.034), fontPath=FONT_BOLD,
          fontSize="${fsSmall}", color="${subColor}", horizontalAlignment="right", zIndex="45")

    # lower screen: the game picker
    if layout == "grid":
        it, sp = 0.158, 0.022
        gh = 2 * it + sp + 0.004
        gy0 = ly0 + (ly1 - ly0 - gh) / 2
        cols = int((pw - 0.056 + sp) // (it + sp))
        gw = cols * (it + sp) - sp + 0.004
        L.add(v, "grid", "gamelistgrid", pos=L.pair(px + (pw - gw) / 2, gy0), size=L.pair(gw, gh),
              imageType="cover", itemSize=L.pair(it, it), itemScale="1.12",
              itemSpacing=f"{f(L.x(sp))} {f(sp)}", scaleInwards="true", fractionalRows="false",
              imageFit="contain", imageRelativeScale="0.78", imageCornerRadius=L.rad(0.006),
              backgroundColor="${tileColor}", backgroundCornerRadius=L.rad(0.026),
              backgroundRelativeScale="0.9", selectorColor="${accentColor}",
              selectorCornerRadius=L.rad(0.03), selectorLayer="bottom",
              textColor="${textColor}", fontPath=FONT_BOLD, fontSize="0.02",
              textRelativeScale="0.72", lineSpacing="1.15", unfocusedItemOpacity="1", zIndex="50")
    elif layout == "list":
        L.add(v, "textlist", "gamelisttextlist", pos=L.pair(px + 0.035, ly0 + 0.02),
              size=L.pair(pw - 0.07, ly1 - ly0 - 0.04), fontPath=FONT_BOLD, fontSize="${fsList}",
              lineSpacing="1.75", primaryColor="${textColor}", secondaryColor="${accentColor}",
              selectedColor="${accentText}", selectedSecondaryColor="${accentText}",
              selectedBackgroundColor="${accentColor}",
              selectedBackgroundMargins=f"{L.rad(0.016)} {L.rad(0.016)}",
              selectedBackgroundCornerRadius=L.rad(0.04), selectorColor="00000000",
              horizontalMargin=f(L.x(0.016)), indicators="symbols", zIndex="50")
    else:  # shelf: Wii U style row of box covers
        ih, iw = 0.27, 0.20
        L.add(v, "carousel", "gamelistcarousel", pos=L.pair(px + 0.01, ly0 + 0.005),
              size=L.pair(pw - 0.02, ly1 - ly0 - 0.01), type="horizontal", imageType="cover",
              itemSize=L.pair(iw, ih), itemScale="1.2", maxItemCount=f((pw - 0.02) / 0.235),
              imageFit="contain", imageCornerRadius=L.rad(0.008), unfocusedItemOpacity="1",
              unfocusedItemDimming="0.72", color="00000000", fontPath=FONT_BLACK, fontSize="0.024",
              textColor="${accentText}", textBackgroundColor="${accentColor}",
              textBackgroundCornerRadius=L.rad(0.014), textRelativeScale="0.85", lineSpacing="1.2",
              itemVerticalAlignment="center", fastScrolling="true", systemNameSuffix="false",
              zIndex="50")
    return L


def props_xml(props, ind):
    return "\n".join(f"{ind}<{k}>{escape(str(val))}</{k}>" for k, val in props.items())


def views_xml(L):
    parts = ["<theme>"]
    for view, els in L.views.items():
        parts.append(f'    <view name="{view}">')
        for etype, name, props in els:
            parts.append(f'        <{etype} name="{name}">')
            parts.append(props_xml(props, " " * 12))
            parts.append(f"        </{etype}>")
        parts.append("    </view>")
    parts.append("</theme>")
    return "\n".join(parts) + "\n"


layouts = {}
for ar, W in ASPECTS:
    for var in VARIANTS:
        L = build(W, var)
        fn = f"{ar.replace(':', 'x').replace('.', '_')}-{var[0]}.xml"
        with open(os.path.join(OUT, "layouts", fn), "w") as fh:
            fh.write(f"<!-- esdeii layout: aspect ratio {ar}, variant {var[0]} (generated by tools/make_xml.py) -->\n")
            fh.write(views_xml(L))
        layouts[(ar, var[0])] = (fn, L)

# ------------------------------------------------------------------ per-system accent colours
names = ", ".join(SYSTEM_ACCENT_SCHEMES)
for sysname, (_, _, colour) in SYSTEMS.items():
    with open(os.path.join(OUT, "systemcolors", sysname + ".xml"), "w") as fh:
        fh.write(f'<theme>\n    <colorScheme name="{names}">\n        <variables>\n'
                 f"            <accentColor>{colour}</accentColor>\n        </variables>\n"
                 f"    </colorScheme>\n</theme>\n")

# ------------------------------------------------------------------ capabilities.xml
cap = ["<!-- Theme capabilities for esdeii -->", "<themeCapabilities>", "    <themeName>esdeii</themeName>", ""]
cap += [f"    <aspectRatio>{ar}</aspectRatio>" for ar, _ in ASPECTS]
cap.append("")
cap += [f"    <fontSize>{s}</fontSize>" for s in FONT_SIZES]
cap.append("")
for key, (label, _) in SCHEMES.items():
    cap += [f'    <colorScheme name="{key}">', f"        <label>{label}</label>", "    </colorScheme>"]
cap.append("")
for name, label, rows in (
        ("esdeiiSlide", "esdeii slide", dict(systemToGamelist="slide", gamelistToSystem="slide",
                                             startupToSystem="fade", startupToGamelist="fade")),
        ("esdeiiFade", "esdeii fade", dict(systemToGamelist="fade", gamelistToSystem="fade",
                                           startupToSystem="fade", startupToGamelist="fade")),
        ("esdeiiInstant", "esdeii instant", dict(systemToGamelist="instant", gamelistToSystem="instant"))):
    cap += [f'    <transitions name="{name}">', f"        <label>{label}</label>",
            "        <systemToSystem>instant</systemToSystem>",
            "        <gamelistToGamelist>instant</gamelistToGamelist>"]
    cap += [f"        <{k}>{val}</{k}>" for k, val in rows.items()]
    cap.append("    </transitions>")
cap.append("")
for name, label, _, _ in VARIANTS:
    cap += [f'    <variant name="{name}">', f"        <label>{label}</label>",
            "        <selectable>true</selectable>", "    </variant>"]
cap.append("</themeCapabilities>")
with open(os.path.join(OUT, "capabilities.xml"), "w") as fh:
    fh.write("\n".join(cap) + "\n")

# ------------------------------------------------------------------ theme.xml
t = ["<!-- esdeii: a dual-screen handheld inspired theme for ES-DE (generated by tools/make_xml.py) -->",
     "<theme>", "    <include>./navigationsounds.xml</include>", ""]
for key, (label, vars_) in SCHEMES.items():
    t.append(f'    <colorScheme name="{key}">')
    t.append("        <variables>")
    t += [f"            <{k}>{val}</{k}>" for k, val in vars_.items()]
    t.append("        </variables>")
    t.append("    </colorScheme>")
t += ["", "    <!-- Per-system accent colour for the '+ system colours' schemes (missing files are skipped) -->",
      "    <include>./systemcolors/${system.theme}.xml</include>", ""]
for size, mult in FONT_SIZES.items():
    t.append(f'    <fontSize name="{size}">')
    t.append("        <variables>")
    t += [f"            <{k}>{f(v * mult)}</{k}>" for k, v in FS_BASE.items()]
    t.append("        </variables>")
    t.append("    </fontSize>")
t.append("")
for name, _, _, _ in VARIANTS:
    t.append(f'    <variant name="{name}">')
    for ar, _ in ASPECTS:
        t += [f'        <aspectRatio name="{ar}">',
              f"            <include>./layouts/{layouts[(ar, name)][0]}</include>",
              "        </aspectRatio>"]
    t.append("    </variant>")
t.append("</theme>")
with open(os.path.join(OUT, "theme.xml"), "w") as fh:
    fh.write("\n".join(t) + "\n")

ns = ["<theme>", '    <view name="all">']
for s in ("systembrowse", "quicksysselect", "select", "back", "scroll", "favorite", "launch"):
    ns += [f'        <sound name="{s}">', f"            <path>./assets/sounds/{s}.wav</path>", "        </sound>"]
ns += ["    </view>", "</theme>"]
with open(os.path.join(OUT, "navigationsounds.xml"), "w") as fh:
    fh.write("\n".join(ns) + "\n")

if len(sys.argv) > 2:  # optional dump for tools/preview.py
    with open(sys.argv[2], "w") as fh:
        json.dump({"layouts": {f"{ar}|{var}": {"W": L.W, "views": L.views} for (ar, var), (_, L) in layouts.items()},
                   "schemes": {k: v[1] for k, v in SCHEMES.items()},
                   "fonts": FS_BASE}, fh)
print("xml done:", len(layouts), "layout files")
