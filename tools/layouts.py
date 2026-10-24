"""Layouts for the three esdeii themes.

All layout maths is done in "height units": the screen is 1.0 tall and W wide,
where W is the aspect ratio. Values are converted to ES-DE's normalized
coordinates when written. Corner radii in ES-DE are a fraction of screen
width, so they are divided by W as well.
"""
import icons

# Rounded console-menu lettering (M PLUS Rounded 1c, SIL OFL)
FONT_REG = "./../assets/fonts/MPLUSRounded1c-Medium.ttf"
FONT_BOLD = "./../assets/fonts/MPLUSRounded1c-Bold.ttf"
FONT_BLACK = "./../assets/fonts/MPLUSRounded1c-ExtraBold.ttf"
IMG = "./../assets/images/"
SYS = "./../systems/"


def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Layout:
    def __init__(self, W, box="cover, 3dbox"):
        self.W = W
        self.box = box                       # scraped box art type(s) for grids, shelves and covers
        self.box3d = box.startswith("3dbox")
        self.views = {"system": [], "gamelist": []}
        # solid areas (height units: x0, y0, x1, y1) per view; bubbles may pass behind these
        self.opaque = {"system": [], "gamelist": []}
        self.opaque_names = {"system": set(), "gamelist": set()}

    def solid(self, view, names, x0, y0, x1, y1):
        """Mark an area as fully covered by an opaque element."""
        self.opaque[view].append((x0, y0, x1, y1))
        self.opaque_names[view].update(names)

    def x(self, v):
        return v / self.W

    def pair(self, x, y):
        return f"{f(self.x(x))} {f(y)}"

    def rad(self, r):
        return f(r / self.W)

    def add(self, view, etype, name, **props):
        self.views[view].append((etype, name, props))

    def img(self, view, name, x, y, w, h, path, z=6, **extra):
        p = dict(pos=self.pair(x, y), size=self.pair(w, h), path=path, zIndex=f(z))
        p.update(extra)
        self.add(view, "image", name, **p)

    def rect(self, view, name, x0, y0, w, h, color, r=0.0, z=6, **extra):
        p = dict(pos=self.pair(x0, y0), size=self.pair(w, h), path=IMG + "white.png", color=color, zIndex=f(z))
        if r:
            p["cornerRadius"] = self.rad(r)
        p.update(extra)
        self.add(view, "image", name, **p)

    def panel(self, view, name, x0, y0, w, h, r=0.034, z=5, border="${borderColor}", face="${panelColor}",
              shadow=True, b=0.006, **extra):
        if shadow:
            self.rect(view, name + "Shadow", x0 - b, y0 - b + 0.009, w + 2 * b, h + 2 * b, "${shadowColor}", r + b, z)
        self.rect(view, name + "Border", x0 - b, y0 - b, w + 2 * b, h + 2 * b, border, r + b, z + 0.1)
        self.rect(view, name, x0, y0, w, h, face, r, z + 0.2, **extra)
        # the rounded corners are not solid, so only count the panel minus its corner radius
        self.solid(view, (name + "Shadow", name + "Border", name), x0 + r * 0.3, y0 + r * 0.3,
                   x0 + w - r * 0.3, y0 + h - r * 0.3)

    def text(self, view, name, x0, y0, w, h, fs, font=FONT_REG, color="${textColor}", z=40, origin=None, **extra):
        p = dict(pos=self.pair(x0, y0), size=self.pair(w, h), fontPath=font,
                 fontSize=fs if fs.startswith("0") else "${" + fs + "}", color=color, zIndex=f(z))
        if origin:
            p["origin"] = origin
        p.update(extra)
        self.add(view, "text", name, **p)


# ================================================================== shared pieces
# Drifting bubbles: small separate animations instead of one full-screen one, so
# ES-DE can cache their frames. They are placed per view in the free background
# only - never behind the clock, text, the game grid or anything else that is not
# solid - so they can't show through or look as if they sit on top of it.
BUBBLE_SIZES = (0.2, 0.17, 0.15, 0.13, 0.12, 0.11, 0.1)
BUBBLE_KINDS = "acbdcab"
BUBBLE_MARGIN = 0.012


def _nums(v):
    try:
        return [float(t) for t in str(v).split()]
    except ValueError:
        return None


def _rect(L, etype, p):
    """Rough area (height units) an element covers, or None if it draws nothing."""
    if etype in ("gameselector", "sound") or "pos" not in p:
        return None
    x, y = _nums(p["pos"])
    x *= L.W
    size = _nums(p.get("size") or p.get("maxSize") or "")
    w = h = 0.0
    if size:
        w, h = size[0] * L.W, size[1]
    est = {"clock": (0.2, 0.08), "datetime": (0.3, 0.05), "systemstatus": (0.26, 0.06),
           "helpsystem": (min(L.W * 0.9, 1.3), 0.06), "text": (0.3, 0.06), "animation": (0.06, 0.08)}
    if w <= 0 or h <= 0:
        ew, eh = est.get(etype, (0.2, 0.06))
        w, h = (w if w > 0 else ew), (h if h > 0 else eh)
    ox, oy = _nums(p.get("origin", "0 0")) or (0, 0)
    x0, y0 = x - ox * w, y - oy * h
    return (x0, y0, x0 + w, y0 + h)


def _inside(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


def _overlap(a, b):
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def _hits(a, b, m=0.0):
    return a[0] < b[2] + m and a[2] > b[0] - m and a[1] < b[3] + m and a[3] > b[1] - m


def bubbles(L, z="2"):
    """Call last, once everything else in the layout has been added."""
    for v, els in L.views.items():
        blocks = []
        for etype, name, p in els:
            if name.startswith(("background", "bubble", "backdrop")) or name in L.opaque_names[v]:
                continue
            r = _rect(L, etype, p)
            if r and not any(_inside(r, o) for o in L.opaque[v]):
                blocks.append(r)
        placed = []
        step = 0.02
        cands = [(i * step, j * step) for i in range(1, int(L.W / step)) for j in range(1, int(1 / step))]
        for size in BUBBLE_SIZES:
            best, best_d = None, -1.0
            for cx, cy in cands:
                box = (cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2)
                if box[0] < -size * 0.25 or box[2] > L.W + size * 0.25 or box[1] < 0 or box[3] > 1:
                    continue
                if any(_hits(box, b, BUBBLE_MARGIN) for b in blocks):
                    continue
                if sum(_overlap(box, o) for o in L.opaque[v]) > 0.4 * size * size:
                    continue  # would be mostly hidden behind a panel
                d = min([((cx - px) ** 2 + (cy - py) ** 2) ** 0.5 - (size + ps) / 2 for px, py, ps in placed],
                        default=1.0)
                if d < 0.04:
                    continue
                d += 0.001 * (cy + cx)  # deterministic tie-break
                if d > best_d:
                    best, best_d = (cx, cy), d
            if best:
                placed.append((best[0], best[1], size))
        for i, (cx, cy, size) in enumerate(placed):
            kind = BUBBLE_KINDS[i % len(BUBBLE_KINDS)]
            L.add(v, "animation", f"bubble{i}", pos=L.pair(cx, cy), origin="0.5 0.5", size=L.pair(size, size),
                  path=IMG + f"anim-bubble-{kind}.json", color="${accentColor}", opacity="${bubbleOpacity}",
                  direction="normal", zIndex=z)


def background(L, path, tile_h=0.09, overlay=None):
    for v in ("system", "gamelist"):
        L.add(v, "image", "background", pos="0 0", size="1 1", path=IMG + path, tile="true",
              tileSize=f"0 {f(tile_h)}", color="${bgColor}", zIndex="0")
        if overlay:
            L.add(v, "image", "backgroundOverlay", pos="0 0", size="1 1", path=IMG + overlay,
                  opacity="${overlayOpacity}", zIndex="1")


def backdrop(L, view, gameselector=None):
    """Faint full-screen artwork of the selected (or featured) game behind
    everything, fading in as you move - like the artwork backdrops of modern
    handheld launchers. Fan art first, then the screenshot."""
    p = dict(pos="0 0", cropSize="1 1", imageType="fanart, screenshot", scrollFadeIn="true",
             opacity="${artOpacity}", saturation="0.85", zIndex="1.5")
    if gameselector:
        p["gameselector"] = gameselector
    L.add(view, "image", "backdrop", **p)


def clock(L, view, x, y, origin, fs="fsStatus", date=False, color="${subColor}", font=FONT_BLACK, name="clock",
          fmt=None):
    L.add(view, "clock", name, pos=L.pair(x, y), origin=origin, fontPath=font, fontSize="${" + fs + "}"
          if not fs.startswith("0") else fs, color=color, format=fmt or ("%Y-%m-%d" if date else "%H:%M"), scope="view")


def status(L, view, x, y, origin="1 0.5", fs="fsStatus"):
    L.add(view, "systemstatus", "systemStatus", pos=L.pair(x, y), origin=origin, height="${" + fs + "}",
          color="${subColor}", fontPath=FONT_BOLD, scope="view")


def help_(L, view, x, y, origin="0 0.5", fs="fsHelp", pill=False):
    p = dict(pos=L.pair(x, y), origin=origin, fontPath=FONT_BOLD, fontSize="${" + fs + "}",
             textColor="${subColor}", iconColor="${subColor}", letterCase="capitalize", entrySpacing="0.012")
    if pill:  # button prompts on a rounded pill, like modern handheld launchers
        p.update(backgroundColor="${panelColor}", backgroundHorizontalPadding=f"{L.rad(0.022)} {L.rad(0.022)}",
                 backgroundVerticalPadding="0.01 0.01", backgroundCornerRadius=L.rad(0.04))
    L.add(view, "helpsystem", "help", **p)


GLASS = "000000A6"  # dark see-through pill / card on top of artwork


def status_bar(L, view, xr, y, w=0.5, h=0.052, z=30):
    """Clock, date and battery on one dark glass pill (right edge at xr)."""
    L.rect(view, "statusPill", xr - w, y - h / 2, w, h, GLASS, h / 2, z=z)
    clock(L, view, xr - w + 0.024, y, "0 0.5", fs="fsPill", color="FFFFFF", font=FONT_BOLD,
          fmt="%H:%M   %d/%m")
    L.add(view, "systemstatus", "systemStatus", pos=L.pair(xr - 0.022, y), origin="1 0.5", height="${fsPill}",
          color="FFFFFF", fontPath=FONT_BOLD, scope="view")


def glass_text(L, view, name, x, y, fs, origin="0 0.5", z=41, **extra):
    """A short line of white text on a dark glass pill (auto width)."""
    L.text(view, name, x, y, 0, 0, fs, FONT_BOLD, "FFFFFF", origin=origin, backgroundColor=GLASS,
           backgroundMargins=f"{L.rad(0.016)} {L.rad(0.016)}", backgroundCornerRadius=L.rad(0.04),
           lineSpacing="1.7", z=z, **extra)


def hero(L, view, x, y, w, h, r=0.034, gameselector=None):
    """Full-bleed game artwork filling a screen: a dark base, the fan art (or
    screenshot) cropped to fill, and the game video on top in the game list."""
    L.rect(view, "heroBase", x, y, w, h, "${screenColor}", r, z=6)
    p = dict(pos=L.pair(x, y), cropSize=L.pair(w, h), imageType="fanart, screenshot, titlescreen",
             cornerRadius=L.rad(r), zIndex="7")
    if gameselector:
        p["gameselector"] = gameselector
    else:
        p["scrollFadeIn"] = "true"
    L.add(view, "image", "heroArt", **p)
    if not gameselector:
        L.add(view, "video", "gameVideo", pos=L.pair(x, y), cropSize=L.pair(w, h), videoCornerRadius=L.rad(r),
              delay="1.5", fadeInTime="0.6", scrollFadeIn="true", zIndex="8")


def media(L, x, y, w, h, r=0.016, z=18, view="gamelist", gameselector=None):
    """Top-screen game media: screenshot/video, with the box cover (e.g. Android
    app icons) shown centred when there is no screenshot."""
    L.rect(view, "mediaScreen", x, y, w, h, "${screenColor}", r, z=z)
    cov = dict(pos=L.pair(x + w / 2, y + h / 2), origin="0.5 0.5", maxSize=L.pair(h * 0.82, h * 0.82),
               imageType=L.box, default=IMG + "noimage.png", cornerRadius=L.rad(0.012), zIndex=f(z + 1))
    if gameselector:
        cov["gameselector"] = gameselector
    L.add(view, "image", "mediaFallback", **cov)
    if view == "gamelist":
        L.add(view, "video", "gameVideo", pos=L.pair(x, y), zIndex=f(z + 2),
              imageType="screenshot, titlescreen, miximage", scrollFadeIn="true", cropSize=L.pair(w, h),
              imageCornerRadius=L.rad(r), videoCornerRadius=L.rad(r), delay="1.0", fadeInTime="0.35")
        # scraped game logo (marquee) in the corner of the screen, like a title banner
        L.add(view, "image", "gameLogo", pos=L.pair(x + 0.022, y + h - 0.02), origin="0 1",
              maxSize=L.pair(w * 0.42, h * 0.3), imageType="marquee", scrollFadeIn="true", zIndex=f(z + 3))
    else:
        L.add(view, "image", "featuredImage", pos=L.pair(x, y), cropSize=L.pair(w, h),
              imageType="screenshot, titlescreen, miximage", gameselector=gameselector,
              cornerRadius=L.rad(r), zIndex=f(z + 2))


def info(L, x0, y0, w, y1, desc_col=None, two_line_name=True, view="gamelist", name=True,
         title="${textColor}", sub="${subColor}", dim="${dimText}"):
    """Game name, details grid, rating/badges and description. With name=False
    the details start at y0 (the name is shown elsewhere)."""
    v = view
    if not name:
        r1, gap = y0, 0.06
    elif two_line_name:
        L.text(v, "gameName", x0, y0, w, 0.1, "fsGameName", FONT_BLACK, title, metadata="name",
               verticalAlignment="top", lineSpacing="1.15")
        r1, gap = y0 + 0.11, 0.062
    else:
        L.text(v, "gameName", x0, y0, w, 0.05, "fsGameName", FONT_BLACK, title, metadata="name")
        r1, gap = y0 + 0.058, 0.06
    col2 = x0 + w / 2 + 0.01
    half = w / 2 - 0.015
    lab = dict(letterCase="uppercase", metadataElement="true")

    def cell(xx, y, nm, title, kind, meta, default="Unknown", **extra):
        L.text(v, nm + "Label", xx, y, half, 0.024, "fsLabel", FONT_BOLD, sub, text=title, **lab)
        if kind == "datetime":
            L.add(v, "datetime", nm, pos=L.pair(xx, y + 0.022), size=L.pair(half, 0.032), metadata=meta,
                  fontPath=FONT_BOLD, fontSize="${fsMeta}", color=dim, defaultValue=default, **extra)
        else:
            L.text(v, nm, xx, y + 0.022, half, 0.032, "fsMeta", FONT_BOLD, dim, metadata=meta,
                   defaultValue=default)

    cell(x0, r1, "released", "Released", "datetime", "releasedate", format="%Y-%m-%d")
    cell(col2, r1, "players", "Players", "text", "players")
    cell(x0, r1 + gap, "developer", "Developer", "text", "developer")
    cell(col2, r1 + gap, "genre", "Genre", "text", "genre")
    cell(x0, r1 + 2 * gap, "lastPlayed", "Last played", "datetime", "lastplayed", default="Never")
    L.text(v, "playTimeLabel", col2, r1 + 2 * gap, half, 0.024, "fsLabel", FONT_BOLD, sub,
           text="Play time", **lab)
    L.text(v, "playTime", col2, r1 + 2 * gap + 0.022, half, 0.032, "fsMeta", FONT_BOLD, dim,
           metadata="playtime")
    r3 = r1 + 3 * gap + 0.006
    L.add(v, "rating", "gameRating", pos=L.pair(x0, r3), size="0 0.028",
          filledPath=IMG + "star-filled.svg", unfilledPath=IMG + "star-unfilled.svg",
          interpolation="linear", zIndex="45")
    L.add(v, "badges", "gameBadges", pos=L.pair(x0 + w, r3 - 0.002), origin="1 0",
          size=L.pair(min(0.32, w * 0.55), 0.032), horizontalAlignment="right", direction="row",
          lines="1", itemsPerLine="8", itemMargin=f"{L.rad(0.006)} 0.006",
          slots="favorite completed kidgame broken controller altemulator manual", zIndex="45")
    if desc_col:
        dx, dy, dw, dh = desc_col
        L.text(v, "descriptionLabel", dx, dy, dw, 0.024, "fsLabel", FONT_BOLD, sub, text="About", **lab)
        L.text(v, "gameDescription", dx, dy + 0.032, dw, dh - 0.032, "fsDesc", FONT_REG, dim,
               metadata="description", lineSpacing="1.35", containerStartDelay="5")
    else:
        dy = r3 + 0.04
        if y1 - dy > 0.03:
            L.text(v, "gameDescription", x0, dy, w, y1 - dy, "fsDesc", FONT_REG, dim,
                   metadata="description", lineSpacing="1.3", containerStartDelay="5")


def empty_slots(L, view, x, y, iw, ih, sp, cols, rows, slot, z=49):
    """Empty placeholder tiles behind a grid, one per visible cell, like the
    blank channel slots on a console menu. ES-DE lays grid items out from the
    top-left corner at (iw + sp) steps (scaleInwards removes the outer margin),
    so filled cells cover their placeholder and only empty cells show it.

    slot is an image path (tinted with the tile colour) or a relative size for
    a plain rounded square."""
    for r in range(rows):
        for c in range(cols):
            cx, cy = x + c * (iw + sp), y + r * (ih + sp)
            nm = f"emptySlot{r * cols + c}"
            if isinstance(slot, str):
                L.img(view, nm, cx, cy, iw, ih, slot, z=z, color="${tileColor}")
            else:
                k = slot
                L.rect(view, nm, cx + iw * (1 - k) / 2, cy + ih * (1 - k) / 2, iw * k, ih * k, "${tileColor}",
                       0.026 * k, z=z, opacity="0.55")


def picker(L, layout, x, y, w, h, grid_style):
    """The game chooser: icon grid, text list or cover shelf."""
    v = "gamelist"
    if layout == "grid":
        it, sp, rows = grid_style["item"], grid_style.get("spacing", 0.022), grid_style.get("rows")
        if rows is None:
            rows = max(1, int((h + sp) // (it + sp)))
        gh = rows * it + (rows - 1) * sp + 0.004
        gy0 = y + (h - gh) / 2
        cols = max(1, int((w + sp) // (it + sp)))
        gw = cols * (it + sp) - sp + 0.004
        gx0 = x + (w - gw) / 2
        empty_slots(L, v, gx0, gy0, it, it, sp, cols, rows,
                    IMG + "slot-empty-square.png" if grid_style.get("slot") else 0.9)
        p = dict(pos=L.pair(gx0, gy0), size=L.pair(gw, gh), imageType=L.box,
                 itemSize=L.pair(it, it), itemScale=grid_style.get("scale", "1.1"),
                 itemSpacing=f"{f(L.x(sp))} {f(sp)}", scaleInwards="true", fractionalRows="false",
                 imageFit="contain", imageCornerRadius=L.rad(0.006), textColor="${textColor}",
                 fontPath=FONT_BOLD, fontSize="0.02", textRelativeScale="0.7", lineSpacing="1.15",
                 unfocusedItemOpacity="1", zIndex="50")
        if grid_style.get("slot"):
            p.update(backgroundImage=IMG + grid_style["slot"], imageRelativeScale="0.62")
        else:
            p.update(backgroundColor="${tileColor}", backgroundCornerRadius=L.rad(0.026),
                     backgroundRelativeScale="0.9", imageRelativeScale="0.78")
        if grid_style.get("selector"):
            p.update(selectorImage=IMG + grid_style["selector"], selectorLayer="top",
                     selectorColor=grid_style.get("selectorColor", "${accentColor}"))
        else:
            p.update(selectorColor="${accentColor}", selectorCornerRadius=L.rad(0.03), selectorLayer="bottom")
        L.add(v, "grid", "gamelistgrid", **p)
    elif layout == "list":
        L.add(v, "textlist", "gamelisttextlist", pos=L.pair(x + 0.01, y), size=L.pair(w - 0.02, h),
              fontPath=FONT_BOLD, fontSize="${fsList}", lineSpacing="1.75", primaryColor="${textColor}",
              secondaryColor="${accentColor}", selectedColor="${accentText}", selectedSecondaryColor="${accentText}",
              selectedBackgroundColor="${accentColor}",
              selectedBackgroundMargins=f"{L.rad(0.016)} {L.rad(0.016)}",
              selectedBackgroundCornerRadius=L.rad(0.04), selectorColor="00000000",
              horizontalMargin=f(L.x(0.016)), indicators="symbols", zIndex="50")
    else:
        ih = min(0.27, h * 0.78)
        iw = ih * (0.9 if L.box3d else 0.74)  # 3D boxes show the spine, so they are a bit wider
        L.add(v, "carousel", "gamelistcarousel", pos=L.pair(x, y), size=L.pair(w, h), type="horizontal",
              imageType=L.box, itemSize=L.pair(iw, ih), itemScale="1.2", maxItemCount=f(w / (iw * 1.18)),
              imageFit="contain", imageCornerRadius=L.rad(0.008), unfocusedItemOpacity="1",
              unfocusedItemDimming="0.72", color="00000000", fontPath=FONT_BLACK, fontSize="0.024",
              textColor="${accentText}", textBackgroundColor="${accentColor}",
              textBackgroundCornerRadius=L.rad(0.014), textRelativeScale="0.85", lineSpacing="1.2",
              itemVerticalAlignment="center", fastScrolling="true", systemNameSuffix="false", zIndex="50")


def system_name(L, x, y, w, h, fs="fsTitle", lines=2, color="${textColor}"):
    L.text("system", "systemName", x, y, w, h, fs, FONT_BLACK, color, text="${system.fullName}",
           verticalAlignment="top", lineSpacing="1.1")


def system_info(L, view, x, y, w, origin=None, align="left", fs="fsSmall"):
    extra = dict(horizontalAlignment=align)
    L.text(view, "systemInfo", x, y, w, 0.032, fs, FONT_BOLD, "${subColor}", origin=origin,
           text="${sysInfo}", **extra)


def count_pill(L, x, y, origin=None, z=41):
    L.text("system", "gameCount", x, y, 0, 0, "fsCount", FONT_BOLD, "${accentText}", origin=origin,
           systemdata="gamecount", backgroundColor="${accentColor}",
           backgroundMargins=f"{L.rad(0.014)} {L.rad(0.014)}", backgroundCornerRadius=L.rad(0.03),
           lineSpacing="1.6", z=z)


# ================================================================== ESDE3DS (dual screen)
def build_3ds(W, style, layout, box="cover, 3dbox"):
    """style is '<iconset>|<mode>' where mode is 'row' (DSi-style row) or 'grid' (HOME-menu grid)."""
    iconset, mode = (style.split("|") + ["row"])[:2]
    L = Layout(W, box)
    sysimg = SYS + iconset + "/"
    decor = W >= 1.6
    side = min(0.24, (W - 1.30) / 2) if decor else 0.03
    px, pw = side, W - 2 * side
    for v in ("system", "gamelist"):  # HOME-menu background pattern chosen by the colour scheme
        L.add(v, "image", "background", pos="0 0", size="1 1", path=IMG + "${bgPattern}", tile="true",
              tileSize="0 ${bgTile}", color="${bgColor}", zIndex="0")
    backdrop(L, "system", "featured")
    backdrop(L, "gamelist")

    sys_geo = dict(up=(0.035, 0.555), lo=(0.595, 0.915)) if mode == "row" else \
        dict(up=(0.035, 0.47), lo=(0.51, 0.915))
    geo = {"system": sys_geo, "gamelist": dict(up=(0.035, 0.485), lo=(0.525, 0.915))}
    for view, g in geo.items():
        uy0, uy1 = g["up"]
        ly0, ly1 = g["lo"]
        L.panel(view, "upperScreen", px, uy0, pw, uy1 - uy0)
        L.panel(view, "lowerScreen", px, ly0, pw, ly1 - ly0)
        status_bar(L, view, px + pw - 0.022, uy0 + 0.045, w=min(0.5, pw * 0.4))
        help_(L, view, px + 0.022, 0.958, fs="fsHelp", pill=True)

    # system view: top screen = the featured game's artwork with the system on top
    uy0, uy1 = geo["system"]["up"]
    ly0, ly1 = geo["system"]["lo"]
    v = "system"
    k = 1.0 if mode == "row" else 0.84
    uh = uy1 - uy0
    L.add(v, "gameselector", "featured", selection="random", gameCount="1")
    hero(L, v, px, uy0, pw, uh, gameselector="featured")
    L.rect(v, "heroShade", px, uy0, pw, uh, "000000D9", 0.034, z=8, colorEnd="00000026", gradientType="horizontal")
    tile = 0.36 * k
    cy = (uy0 + 0.07 + uy1) / 2
    tx, ty = px + 0.05, cy - tile / 2
    L.img(v, "systemTile", tx, ty, tile, tile, sysimg + "${system.theme}.png", z=20, default=sysimg + "_default.png")
    nx = tx + tile + 0.045
    name_w = px + pw - 0.04 - nx
    ny = cy - 0.115 * k - 0.012
    system_name(L, nx, ny, name_w, 0.125 * (1 if mode == "row" else 0.92), "fsName3ds", color="FFFFFF")
    L.text(v, "systemInfo", nx, ny + 0.132 * k, name_w, 0.032, "fsSmall", FONT_BOLD, "FFFFFFC0", text="${sysInfo}")
    count_pill(L, nx + 0.012, ny + 0.18 * k + 0.012)
    glass_text(L, v, "featuredName", px + pw - 0.03, uy1 - 0.035, "fsPill", origin="1 0.5", metadata="name",
               gameselector="featured", systemNameSuffix="false")
    L.text(v, "featuredLabel", px + pw - 0.03, uy1 - 0.072, 0.4, 0.03, "fsLabel", FONT_BOLD, "FFFFFFB0",
           origin="1 0.5", text="Featured", letterCase="uppercase", horizontalAlignment="right")

    # system view: bottom screen
    if mode == "row":
        item, scale, step = 0.165, 1.32, 0.255
        car_y0, car_h = ly0 + 0.005, ly1 - ly0 - 0.01
        L.add(v, "carousel", "systemcarousel", pos=L.pair(px + 0.01, car_y0), size=L.pair(pw - 0.02, car_h),
              type="horizontal", staticImage=sysimg + "${system.theme}.png", itemSize=L.pair(item, item),
              itemScale=f(scale), maxItemCount=f((pw - 0.02) / step), unfocusedItemOpacity="1",
              unfocusedItemDimming="0.94", imageFit="contain", color="00000000", text="${system.fullName}",
              fontPath=FONT_BLACK, fontSize="0.026", textColor="FFFFFF", textBackgroundColor="${accentColor}",
              textBackgroundCornerRadius=L.rad(0.04), textRelativeScale="0.85", lineSpacing="1.15",
              itemVerticalAlignment="center", fastScrolling="true", zIndex="50")
        ring = item * scale * icons.BODY_FRAC + 0.034
        cy = car_y0 + car_h / 2 + item * scale * icons.BODY_OFFSET_FRAC
        L.add(v, "animation", "cursor", pos=L.pair(px + pw / 2, cy), origin="0.5 0.5", size=L.pair(ring, ring),
              path=IMG + "anim-cursor.json", color="${accentColor}", zIndex="55")
    else:  # HOME-menu style grid of icons with a glowing cursor
        it, sp, rows = 0.168, 0.026, 2
        gh = rows * it + (rows - 1) * sp + 0.004
        cols = max(3, int((pw - 0.06 + sp) // (it + sp)))
        gw = cols * (it + sp) - sp + 0.004
        gx0, gy0 = px + (pw - gw) / 2, ly0 + (ly1 - ly0 - gh) / 2
        empty_slots(L, v, gx0, gy0, it, it, sp, cols, rows, IMG + "slot-empty-square.png")
        L.add(v, "grid", "systemgrid", pos=L.pair(gx0, gy0),
              size=L.pair(gw, gh), staticImage=sysimg + "${system.theme}.png", itemSize=L.pair(it, it),
              itemScale="1.1", itemSpacing=f"{f(L.x(sp))} {f(sp)}", scaleInwards="true", fractionalRows="false",
              imageFit="contain", selectorImage=IMG + "select-square.png", selectorColor="${accentColor}",
              selectorLayer="top", text="${system.fullName}", fontPath=FONT_BLACK, fontSize="0.022",
              textColor="FFFFFF", textBackgroundColor="${accentColor}", textBackgroundCornerRadius=L.rad(0.03),
              textRelativeScale="0.8", lineSpacing="1.15", unfocusedItemOpacity="1", zIndex="50")

    # gamelist view
    uy0, uy1 = geo["gamelist"]["up"]
    ly0, ly1 = geo["gamelist"]["lo"]
    v = "gamelist"
    # top screen = the selected game's artwork and video, details on a glass card
    uh = uy1 - uy0
    hero(L, v, px, uy0, pw, uh)
    L.rect(v, "heroShade", px, uy0 + uh * 0.3, pw, uh * 0.7, "00000000", 0.034, z=9, colorEnd="000000C8",
           gradientType="vertical")
    glass_text(L, v, "systemLabel", px + 0.022, uy0 + 0.045, "fsPill", text="${system.fullName}")
    cw = min(0.52, pw * 0.42)
    cx0 = px + pw - cw - 0.022
    cy0, cy1 = uy0 + 0.09, uy1 - 0.022
    L.rect(v, "infoCard", cx0, cy0, cw, cy1 - cy0, GLASS, 0.026, z=10)
    info(L, cx0 + 0.025, cy0 + 0.02, cw - 0.05, cy1 - 0.018, name=False, sub="FFFFFFA8", dim="FFFFFF")
    cov_h = min(0.19, uh * 0.42)
    cov_w = cov_h * (0.9 if L.box3d else 0.74)
    L.add(v, "image", "heroCover", pos=L.pair(px + 0.03, uy1 - 0.03), origin="0 1", maxSize=L.pair(cov_w, cov_h),
          imageType=L.box, cornerRadius=L.rad(0.008), scrollFadeIn="true", zIndex="12")
    nx = px + 0.03 + cov_w + 0.025
    L.text(v, "gameName", nx, uy1 - 0.03 - 0.11, cx0 - 0.03 - nx, 0.11, "fsGameName", FONT_BLACK, "FFFFFF",
           metadata="name", verticalAlignment="bottom", lineSpacing="1.15")
    L.add(v, "gamelistinfo", "gamelistInfo", pos=L.pair(px + pw - 0.022, 0.958), origin="1 0.5",
          size=L.pair(pw * 0.3, 0.034), fontPath=FONT_BOLD, fontSize="${fsSmall}", color="${subColor}",
          horizontalAlignment="right", zIndex="45")
    picker(L, layout, px + 0.028, ly0 + 0.012, pw - 0.056, ly1 - ly0 - 0.024, dict(item=0.158, rows=2, scale="1.12"))
    bubbles(L)
    return L


# ================================================================== ESDEII (living-room menu)
def wii_bottom(L, view, W, m):
    """Curved clock bar: game count, a clock with a blinking colon, the date
    underneath, and battery / Wi-Fi."""
    by = 0.752
    L.img(view, "menuBar", 0, by, W, 1 - by, IMG + "wii-bar.png", z=60, color="${panelColor}")
    # the bar image is solid below its curved top edge
    L.solid(view, ("menuBar", "menuBarLine"), 0, by + (1 - by) * 110 / 300, W, 1.0)
    L.img(view, "menuBarLine", 0, by, W, 1 - by, IMG + "wii-bar-line.png", z=60.1, color="${accentColor}",
          opacity="0.85")
    # clock: hours | blinking colon | minutes (hidden while the ES-DE menu is open)
    cy, gap = 0.893, 0.014
    for name, fmt, x, org in (("clockHours", "%H", W / 2 - gap, "1 0.5"), ("clockMinutes", "%M", W / 2 + gap, "0 0.5")):
        L.add(view, "clock", name, pos=L.pair(x, cy), origin=org, fontPath=FONT_BLACK, fontSize="${fsWiiClock}",
              color="${subColor}", format=fmt, scope="view")
    L.add(view, "animation", "clockColon", pos=L.pair(W / 2, cy - 0.004), origin="0.5 0.5",
          size="0 ${fsColon}", path=IMG + "anim-colon.json", color="${subColor}", zIndex="62")
    L.add(view, "clock", "date", pos=L.pair(W / 2, 0.962), origin="0.5 0.5", fontPath=FONT_BOLD,
          fontSize="${fsSmall}", color="${subColor}", format="%a %d/%m", scope="view")
    side_w = max(0.2, W / 2 - 0.3 - m)
    if view == "system":
        L.text(view, "barCount", m + 0.02, 0.905, side_w, 0.04, "fsCount", FONT_BOLD, "${subColor}",
               origin="0 0.5", systemdata="gamecount", z=62)
    else:
        L.add(view, "gamelistinfo", "gamelistInfo", pos=L.pair(m + 0.02, 0.905), origin="0 0.5",
              size=L.pair(side_w, 0.04), fontPath=FONT_BOLD, fontSize="${fsCount}", color="${subColor}",
              horizontalAlignment="left", zIndex="62")
    status(L, view, W - m - 0.02, 0.905)
    # button prompts sit in the dip above the bar, clear of the title
    help_(L, view, W / 2, 0.795, origin="0.5 0.5", fs="fsSmall")


def build_wii(W, style, layout, box="cover, 3dbox"):
    L = Layout(W, box)
    sysimg = SYS + "channelwide/"
    m = 0.05 if W >= 1.4 else 0.035
    background(L, "bg-wii.png", 0.02)
    backdrop(L, "gamelist")

    # system view: wall of channels, empty slots where there is no channel
    v = "system"
    system_name(L, m, 0.03, W * 0.6, 0.06, "fsWiiHeader", lines=1)
    system_info(L, v, m, 0.092, W * 0.6)
    aspect = icons.WT_W / icons.WT_H
    sp = 0.026
    gy0, gy1 = 0.145, 0.728
    ih = (gy1 - gy0 - 2 * sp) / 3
    iw = ih * aspect
    cols = max(2, int((W - 2 * m - 0.05 + sp) // (iw + sp)))
    gw = cols * (iw + sp) - sp + 0.004
    gx0 = (W - gw) / 2
    empty_slots(L, v, gx0, gy0, iw, ih, sp, cols, 3, IMG + "slot-empty-wide.png")
    L.add(v, "grid", "systemgrid", pos=L.pair(gx0, gy0), size=L.pair(gw, gy1 - gy0 + 0.004),
          staticImage=sysimg + "${system.theme}.png", itemSize=L.pair(iw, ih), itemScale="1.06",
          itemSpacing=f"{f(L.x(sp))} {f(sp)}", scaleInwards="true", fractionalRows="false", imageFit="contain",
          selectorImage=IMG + "select-wide.png", selectorColor="${accentColor}", selectorLayer="top",
          text="${system.fullName}", fontPath=FONT_BLACK, fontSize="0.026", textColor="${dimText}",
          textBackgroundColor="${panelColor}", textBackgroundCornerRadius=L.rad(0.03), textRelativeScale="0.88",
          lineSpacing="1.15", unfocusedItemOpacity="1", zIndex="50")
    # page arrow on the right edge, nudging like the console's
    L.add(v, "animation", "pageArrow", pos=L.pair(W - (W - gw) / 4, (gy0 + gy1) / 2), origin="0.5 0.5",
          size=L.pair(0.04, 0.0625), path=IMG + "anim-arrow.json", color="${accentColor}", zIndex="52")
    wii_bottom(L, v, W, m)

    # gamelist view: info column on the left, games on the right
    v = "gamelist"
    L.text(v, "systemLabel", m, 0.03, W * 0.6, 0.06, "fsWiiHeader", FONT_BLACK, "${textColor}",
           text="${system.fullName}", verticalAlignment="top")
    system_info(L, v, m, 0.092, W * 0.6)
    lw = min(0.86, (W - 2 * m) * 0.52)
    top, bot = 0.15, 0.725
    L.panel(v, "infoCard", m, top, lw, bot - top, r=0.03)
    mh = min((lw - 0.04) / 1.78, 0.25)
    media(L, m + 0.02, top + 0.02, lw - 0.04, mh)
    info(L, m + 0.03, top + 0.02 + mh + 0.022, lw - 0.06, bot - 0.02, two_line_name=False)
    rx = m + lw + 0.04
    rw = W - m - rx
    slot = "slot-square.png"
    picker(L, layout, rx, top - 0.005, rw, bot - top + 0.01,
           dict(item=0.178, rows=3, spacing=0.016, scale="1.05", slot=slot, selector="select-square.png"))
    wii_bottom(L, v, W, m)
    bubbles(L)
    return L


# ================================================================== ESDEIIU (tablet console home)
def wiiu_dock(L, view, W, m):
    L.rect(view, "dockShadow", m, 0.872, W - 2 * m, 0.09, "${shadowColor}", 0.045, z=58)
    L.rect(view, "dock", m, 0.865, W - 2 * m, 0.09, "${panelColor}", 0.045, z=58.1)
    L.solid(view, ("dock", "dockShadow"), m + 0.02, 0.865, W - m - 0.02, 0.955)
    roomy = W >= 1.6
    help_(L, view, W / 2, 0.91, origin="0.5 0.5", fs="fsSmall" if roomy else "fsHelp")
    if not roomy:
        return
    sw = min(0.36, W / 2 - 0.5 - m)
    if view == "system":
        L.text(view, "dockLabel", m + 0.04, 0.892, sw, 0.026, "fsLabel", FONT_BOLD, "${subColor}",
               text="Featured", letterCase="uppercase", z=62)
        L.text(view, "dockFeatured", m + 0.04, 0.918, sw, 0.034, "fsSmall", FONT_BOLD, "${textColor}",
               metadata="name", gameselector="featured", systemNameSuffix="false", z=62)
    else:
        L.add(view, "gamelistinfo", "dockInfo", pos=L.pair(m + 0.04, 0.91), origin="0 0.5", size=L.pair(sw, 0.034),
              fontPath=FONT_BOLD, fontSize="${fsSmall}", color="${subColor}", horizontalAlignment="left",
              zIndex="62")


def wiiu_top(L, view, W, m):
    if view == "system" and W >= 1.6:
        for i in range(6):
            L.rect(view, f"pageDot{i}", W / 2 - 0.111 + i * 0.04, 0.198, 0.022, 0.022,
                   "${accentColor}" if i == 0 else "${decoColor}", 0.011, z=8)
    # clock and battery on rounded pills, like a handheld launcher's status bar
    pill = dict(backgroundColor="${panelColor}", backgroundHorizontalPadding=f"{L.rad(0.018)} {L.rad(0.018)}",
                backgroundVerticalPadding="0.008 0.008", backgroundCornerRadius=L.rad(0.04))
    L.add(view, "clock", "clock", pos=L.pair(W - m - 0.018, 0.05), origin="1 0.5", fontPath=FONT_BOLD,
          fontSize="${fsPill}", color="${textColor}", format="%H:%M   %d/%m", scope="view", **pill)
    L.add(view, "systemstatus", "systemStatus", pos=L.pair(W - m - 0.018, 0.112), origin="1 0.5",
          height="${fsPill}", color="${subColor}", fontPath=FONT_BOLD, scope="view", **pill)


def build_wiiu(W, style, layout, box="cover, 3dbox"):
    L = Layout(W, box)
    sysimg = SYS + style + "/"
    m = 0.05 if W >= 1.4 else 0.035
    background(L, "bg-wiiu.png", 0.11, overlay="wiiu-swirl.png")
    backdrop(L, "system", "featured")
    backdrop(L, "gamelist")
    us = 0.17  # "user" square size

    # system view
    v = "system"
    L.add(v, "gameselector", "featured", selection="random", gameCount="1")
    L.img(v, "userSlot", m, 0.03, us, us, IMG + "slot-square.png", z=10)
    inner = us * (icons.ART[2] - icons.ART[0]) / icons.TILE
    L.add(v, "image", "userCover", pos=L.pair(m + us / 2, 0.03 + us / 2), origin="0.5 0.5",
          maxSize=L.pair(inner * 0.9, inner * 0.9), imageType=L.box, gameselector="featured",
          default=IMG + "nocover.png", cornerRadius=L.rad(0.006), zIndex="11")
    tx = m + us + 0.03
    system_name(L, tx, 0.045, W - m - 0.3 - tx, 0.06, "fsWiiHeader", lines=1)
    system_info(L, v, tx, 0.115, W * 0.42)
    count_pill(L, tx + 0.012, 0.152)
    wiiu_top(L, v, W, m)
    sp, it = 0.02, 0.19
    gy0, gy1 = 0.235, 0.845
    rows = 3
    gh = rows * it + (rows - 1) * sp
    cols = max(3, int((W - 2 * m - 0.12 + sp) // (it + sp)))
    gw = cols * (it + sp) - sp + 0.004
    gx0, gy0 = (W - gw) / 2, gy0 + (gy1 - gy0 - gh) / 2
    empty_slots(L, v, gx0, gy0, it, it, sp, cols, rows, IMG + "slot-empty-square.png")
    L.add(v, "grid", "systemgrid", pos=L.pair(gx0, gy0), size=L.pair(gw, gh + 0.004),
          staticImage=sysimg + "${system.theme}.png", itemSize=L.pair(it, it), itemScale="1.04",
          itemSpacing=f"{f(L.x(sp))} {f(sp)}", scaleInwards="true", fractionalRows="false", imageFit="contain",
          selectorImage=IMG + "select-start.png", selectorColor="FFFFFFFF", selectorLayer="top",
          text="${system.fullName}", fontPath=FONT_BLACK, fontSize="0.024", textColor="FFFFFF",
          textBackgroundColor="${accentColor}", textBackgroundCornerRadius=L.rad(0.03), textRelativeScale="0.8",
          lineSpacing="1.15", unfocusedItemOpacity="1", zIndex="50")
    wiiu_dock(L, v, W, m)

    # gamelist view
    v = "gamelist"
    L.add(v, "image", "userSystem", pos=L.pair(m + us / 2, 0.03 + us / 2), origin="0.5 0.5",
          size=L.pair(us * 1.0, us * 1.0), path=sysimg + "${system.theme}.png", default=sysimg + "_default.png",
          zIndex="11")
    L.text(v, "systemLabel", tx, 0.045, W - m - 0.3 - tx, 0.06, "fsWiiHeader", FONT_BLACK, "${textColor}",
           text="${system.fullName}", verticalAlignment="top")
    system_info(L, v, tx, 0.115, W * 0.42)
    if W < 1.6:
        L.add(v, "gamelistinfo", "gamelistInfo", pos=L.pair(tx, 0.175), origin="0 0.5", size=L.pair(W * 0.4, 0.034),
              fontPath=FONT_BOLD, fontSize="${fsSmall}", color="${subColor}", horizontalAlignment="left", zIndex="45")
    wiiu_top(L, v, W, m)
    top, bot = 0.225, 0.52
    mw = min((bot - top) * 16 / 9, (W - 2 * m) * 0.46)
    L.panel(v, "mediaFrame", m, top, mw + 0.03, bot - top, r=0.035, face="FFFFFF", border="B9C1CB")
    media(L, m + 0.015, top + 0.015, mw, bot - top - 0.03, r=0.022)
    cx = m + mw + 0.06
    cw = W - m - cx
    L.panel(v, "infoCard", cx, top, cw, bot - top, r=0.035)
    wide = cw > 0.95
    if wide:
        dw = min(0.5, cw * 0.45)
        info(L, cx + 0.03, top + 0.025, cw - dw - 0.09, bot - 0.02, two_line_name=False,
             desc_col=(cx + cw - dw - 0.03, top + 0.025, dw, bot - top - 0.05))
    else:
        info(L, cx + 0.03, top + 0.025, cw - 0.06, bot - 0.02, two_line_name=False)
    picker(L, layout, m, 0.545, W - 2 * m, 0.305,
           dict(item=0.145, rows=2, spacing=0.012, scale="1.04", slot="slot-square.png",
                selector="select-start.png", selectorColor="FFFFFFFF"))
    wiiu_dock(L, v, W, m)
    bubbles(L)
    return L


def build_ii(W, style, layout, box="cover, 3dbox"):
    return (build_wii if style == "channelwide" else build_wiiu)(W, style, layout, box)


BUILDERS = {"3ds": build_3ds, "ii": build_ii}
