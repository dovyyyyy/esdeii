"""Layouts for the three esdeii themes.

All layout maths is done in "height units": the screen is 1.0 tall and W wide,
where W is the aspect ratio. Values are converted to ES-DE's normalized
coordinates when written. Corner radii in ES-DE are a fraction of screen
width, so they are divided by W as well.
"""
import icons

FONT_REG = "./../assets/fonts/Nunito-SemiBold.ttf"
FONT_BOLD = "./../assets/fonts/Nunito-ExtraBold.ttf"
FONT_BLACK = "./../assets/fonts/Nunito-Black.ttf"
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

    def text(self, view, name, x0, y0, w, h, fs, font=FONT_REG, color="${textColor}", z=40, origin=None, **extra):
        p = dict(pos=self.pair(x0, y0), size=self.pair(w, h), fontPath=font,
                 fontSize=fs if fs.startswith("0") else "${" + fs + "}", color=color, zIndex=f(z))
        if origin:
            p["origin"] = origin
        p.update(extra)
        self.add(view, "text", name, **p)


# ================================================================== shared pieces
def background(L, path, tile_h=0.09, overlay=None):
    for v in ("system", "gamelist"):
        L.add(v, "image", "background", pos="0 0", size="1 1", path=IMG + path, tile="true",
              tileSize=f"0 {f(tile_h)}", color="${bgColor}", stationary="always", zIndex="0")
        if overlay:
            L.add(v, "image", "backgroundOverlay", pos="0 0", size="1 1", path=IMG + overlay,
                  stationary="always", opacity="${overlayOpacity}", zIndex="1")


def clock(L, view, x, y, origin, fs="fsStatus", date=False, color="${subColor}", font=FONT_BLACK, name="clock",
          fmt=None):
    L.add(view, "clock", name, pos=L.pair(x, y), origin=origin, fontPath=font, fontSize="${" + fs + "}"
          if not fs.startswith("0") else fs, color=color, format=fmt or ("%Y-%m-%d" if date else "%H:%M"), scope="view")


def status(L, view, x, y, origin="1 0.5", fs="fsStatus"):
    L.add(view, "systemstatus", "systemStatus", pos=L.pair(x, y), origin=origin, height="${" + fs + "}",
          color="${subColor}", fontPath=FONT_BOLD, scope="view")


def help_(L, view, x, y, origin="0 0.5", fs="fsHelp"):
    L.add(view, "helpsystem", "help", pos=L.pair(x, y), origin=origin, fontPath=FONT_BOLD,
          fontSize="${" + fs + "}", textColor="${subColor}", iconColor="${subColor}", letterCase="capitalize",
          entrySpacing="0.012")


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


def info(L, x0, y0, w, y1, desc_col=None, two_line_name=True, view="gamelist"):
    """Game name, details grid, rating/badges and description."""
    v = view
    if two_line_name:
        L.text(v, "gameName", x0, y0, w, 0.1, "fsGameName", FONT_BLACK, "${textColor}", metadata="name",
               verticalAlignment="top", lineSpacing="1.15")
        r1, gap = y0 + 0.11, 0.062
    else:
        L.text(v, "gameName", x0, y0, w, 0.05, "fsGameName", FONT_BLACK, "${textColor}", metadata="name")
        r1, gap = y0 + 0.058, 0.06
    col2 = x0 + w / 2 + 0.01
    half = w / 2 - 0.015
    lab = dict(letterCase="uppercase", metadataElement="true")

    def cell(xx, y, nm, title, kind, meta, default="Unknown", **extra):
        L.text(v, nm + "Label", xx, y, half, 0.024, "fsLabel", FONT_BOLD, "${subColor}", text=title, **lab)
        if kind == "datetime":
            L.add(v, "datetime", nm, pos=L.pair(xx, y + 0.022), size=L.pair(half, 0.032), metadata=meta,
                  fontPath=FONT_BOLD, fontSize="${fsMeta}", color="${dimText}", defaultValue=default, **extra)
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
    L.add(v, "badges", "gameBadges", pos=L.pair(x0 + w, r3 - 0.002), origin="1 0",
          size=L.pair(min(0.32, w * 0.55), 0.032), horizontalAlignment="right", direction="row",
          lines="1", itemsPerLine="8", itemMargin=f"{L.rad(0.006)} 0.006",
          slots="favorite completed kidgame broken controller altemulator manual", zIndex="45")
    if desc_col:
        dx, dy, dw, dh = desc_col
        L.text(v, "descriptionLabel", dx, dy, dw, 0.024, "fsLabel", FONT_BOLD, "${subColor}", text="About", **lab)
        L.text(v, "gameDescription", dx, dy + 0.032, dw, dh - 0.032, "fsDesc", FONT_REG, "${dimText}",
               metadata="description", lineSpacing="1.35", containerStartDelay="5")
    else:
        dy = r3 + 0.04
        if y1 - dy > 0.03:
            L.text(v, "gameDescription", x0, dy, w, y1 - dy, "fsDesc", FONT_REG, "${dimText}",
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
    wide = pw >= 1.6
    for v in ("system", "gamelist"):  # HOME-menu background pattern chosen by the colour scheme
        L.add(v, "image", "background", pos="0 0", size="1 1", path=IMG + "${bgPattern}", tile="true",
              tileSize="0 ${bgTile}", color="${bgColor}", stationary="always", zIndex="0")

    sys_geo = dict(up=(0.035, 0.555), lo=(0.595, 0.915)) if mode == "row" else \
        dict(up=(0.035, 0.47), lo=(0.51, 0.915))
    geo = {"system": sys_geo, "gamelist": dict(up=(0.035, 0.485), lo=(0.525, 0.915))}
    for view, g in geo.items():
        uy0, uy1 = g["up"]
        ly0, ly1 = g["lo"]
        L.panel(view, "upperScreen", px, uy0, pw, uy1 - uy0)
        L.panel(view, "lowerScreen", px, ly0, pw, ly1 - ly0)
        hy = (uy1 + ly0) / 2 - 0.011
        for i, hx in enumerate((px + 0.10, px + pw - 0.30)):
            L.img(view, f"hinge{i}", hx, hy, 0.20, 0.022, IMG + "pill.png", z=4, color="${borderColor}")
        L.rect(view, "statusDivider", px + 0.02, uy0 + 0.067, pw - 0.04, 0.0028, "${dividerColor}", z=7)
        if decor:
            sw = min(0.085, side * 0.42)
            sh = sw * 150 / 110
            uc = (uy0 + uy1) / 2
            for i, cx in enumerate((side / 2, W - side / 2)):
                L.add(view, "image", f"speaker{i}", pos=L.pair(cx, uc), origin="0.5 0.5",
                      size=L.pair(sw, sh), path=IMG + "speaker.png", color="${decoColor}", zIndex="3")
        sy = uy0 + 0.034
        clock(L, view, px + 0.03, sy, "0 0.5")
        if decor:
            clock(L, view, px + 0.135, sy, "0 0.5", date=True, font=FONT_BOLD, name="date")
        status(L, view, px + pw - 0.03, sy)
        help_(L, view, px + 0.01, 0.958)

    # system view: top screen
    uy0, uy1 = geo["system"]["up"]
    ly0, ly1 = geo["system"]["lo"]
    v = "system"
    k = 1.0 if mode == "row" else 0.84
    L.add(v, "gameselector", "featured", selection="random", gameCount="1")
    L.add(v, "gameselector", "recent", selection="lastplayed", gameCount="3")
    tile = 0.34 * k
    tx, ty = px + 0.045, uy0 + 0.088 + (0.007 if mode == "row" else 0.0)
    L.img(v, "systemTile", tx, ty, tile, tile, sysimg + "${system.theme}.png", z=20, default=sysimg + "_default.png")
    nx = tx + tile + 0.04
    if wide:
        prev_h = (uy1 - uy0 - 0.12)
        prev_w = min(0.56, prev_h * 16 / 9)
        prev_x = px + pw - 0.04 - prev_w
        name_w = prev_x - 0.04 - nx
    else:
        name_w = px + pw - 0.04 - nx
    system_name(L, nx, uy0 + 0.09, name_w, 0.125 * (1 if mode == "row" else 0.92), "fsName3ds")
    system_info(L, v, nx, uy0 + 0.09 + 0.132 * k, name_w)
    count_pill(L, nx + 0.012, uy0 + 0.09 + 0.18 * k)
    rl = uy0 + 0.09 + 0.245 * k
    L.text(v, "recentLabel", nx, rl, name_w, 0.03, "fsSmall", FONT_BOLD, "${subColor}",
           text="Jump back in", letterCase="uppercase")
    cov_h = min(0.13, uy1 - 0.02 - (rl + 0.04))
    cov_w = cov_h * 0.77
    for i in range(3):
        cx = nx + cov_w / 2 + i * (cov_w + 0.025)
        L.add(v, "image", f"recentCover{i}", pos=L.pair(cx, rl + 0.04 + cov_h), origin="0.5 1",
              maxSize=L.pair(cov_w, cov_h), imageType=L.box, default=IMG + "nocover.png",
              gameselector="recent", gameselectorEntry=str(i), cornerRadius=L.rad(0.006), zIndex="20")
    if wide:
        py = uy0 + 0.09 + (uy1 - uy0 - 0.09 - prev_h) / 2 - 0.005
        media(L, prev_x, py, prev_w, prev_h, view="system", gameselector="featured")
        L.text(v, "featuredName", prev_x + 0.02, py + prev_h - 0.03, 0, 0, "fsFeat", FONT_BOLD, "FFFFFF",
               origin="0 1", metadata="name", gameselector="featured", systemNameSuffix="false",
               backgroundColor="000000A0", backgroundMargins=f"{L.rad(0.012)} {L.rad(0.012)}",
               backgroundCornerRadius=L.rad(0.02), lineSpacing="1.5", z=24)
        L.text(v, "featuredLabel", prev_x + 0.008, py - 0.006, prev_w, 0.026, "fsSmall", FONT_BOLD,
               "${subColor}", origin="0 1", text="Featured", letterCase="uppercase")

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
    L.text(v, "systemLabel", px + pw / 2 + (0.04 if decor else -0.02), uy0 + 0.034, pw * (0.42 if decor else 0.3),
           0.032, "fsStatus", FONT_BOLD, "${subColor}", origin="0.5 0.5", text="${system.fullName}",
           horizontalAlignment="center")
    by0, by1 = uy0 + 0.088, uy1 - 0.022
    mh = by1 - by0
    mw = min(mh * 16 / 9, pw * 0.44)
    mx = px + 0.025
    media(L, mx, by0, mw, mh)
    x0 = mx + mw + 0.035
    xr = px + pw - 0.03
    if wide:
        dw = 0.44
        info(L, x0, by0, xr - x0 - dw - 0.035, by1, desc_col=(xr - dw, by0, dw, mh))
    else:
        info(L, x0, by0, xr - x0, by1, two_line_name=False)
    ipos = L.pair(px + pw - 0.01, 0.958) if decor else L.pair(px + pw - 0.24, uy0 + 0.034)
    L.add(v, "gamelistinfo", "gamelistInfo", pos=ipos, origin="1 0.5", size=L.pair(pw * 0.4 if decor else 0.2, 0.034),
          fontPath=FONT_BOLD, fontSize="${fsSmall}", color="${subColor}", horizontalAlignment="right", zIndex="45")
    picker(L, layout, px + 0.028, ly0 + 0.012, pw - 0.056, ly1 - ly0 - 0.024, dict(item=0.158, rows=2, scale="1.12"))
    return L


# ================================================================== ESDEII (living-room menu)
def wii_bottom(L, view, W, m):
    """Curved clock bar: round buttons in the raised corners, SD card, a clock
    with a blinking colon and the date underneath."""
    by = 0.752
    L.img(view, "menuBar", 0, by, W, 1 - by, IMG + "wii-bar.png", z=60, color="${panelColor}", stationary="always")
    L.img(view, "menuBarLine", 0, by, W, 1 - by, IMG + "wii-bar-line.png", z=60.1, color="${accentColor}",
          stationary="always", opacity="0.85")
    # clock: hours | blinking colon | minutes (hidden while the ES-DE menu is open)
    cy, gap = 0.893, 0.014
    for name, fmt, x, org in (("clockHours", "%H", W / 2 - gap, "1 0.5"), ("clockMinutes", "%M", W / 2 + gap, "0 0.5")):
        L.add(view, "clock", name, pos=L.pair(x, cy), origin=org, fontPath=FONT_BLACK, fontSize="${fsWiiClock}",
              color="${subColor}", format=fmt, scope="view")
    L.add(view, "animation", "clockColon", pos=L.pair(W / 2, cy - 0.004), origin="0.5 0.5",
          size="0 ${fsColon}", path=IMG + "anim-colon.json", color="${subColor}", stationary="always", zIndex="62")
    L.add(view, "clock", "date", pos=L.pair(W / 2, 0.962), origin="0.5 0.5", fontPath=FONT_BOLD,
          fontSize="${fsSmall}", color="${subColor}", format="%a %d/%m", scope="view")
    # round corner buttons (decorative); the mail button glows now and then
    bs = 0.15
    bx = max(m + bs / 2, min(W * 0.115, 0.24))
    byc = 0.872
    L.add(view, "image", "homeButton", pos=L.pair(bx, byc), origin="0.5 0.5", size=L.pair(bs, bs),
          path=IMG + "button-home.png", stationary="always", zIndex="61")
    L.add(view, "animation", "mailGlow", pos=L.pair(W - bx, byc - 0.004), origin="0.5 0.5",
          size=L.pair(bs * 0.98, bs * 0.98), path=IMG + "anim-glow.json", color="${accentColor}",
          stationary="always", zIndex="60.5")
    L.add(view, "image", "mailButton", pos=L.pair(W - bx, byc), origin="0.5 0.5", size=L.pair(bs, bs),
          path=IMG + "button-mail.png", stationary="always", zIndex="61")
    roomy = W >= 1.5
    tx = bx + bs / 2 + 0.02
    if roomy:
        L.add(view, "image", "sdCard", pos=L.pair(tx + 0.02, 0.905), origin="0.5 0.5", size=L.pair(0.05, 0.05),
              path=IMG + "sd-card.png", color="${subColor}", stationary="always", zIndex="61")
        tx += 0.055
    side_w = max(0.12, W / 2 - 0.14 - tx)
    if view == "system":
        L.text(view, "barCount", tx, 0.905, side_w, 0.04, "fsSmall", FONT_BOLD, "${subColor}",
               origin="0 0.5", systemdata="gamecount", z=62)
    else:
        L.add(view, "gamelistinfo", "gamelistInfo", pos=L.pair(tx, 0.905), origin="0 0.5",
              size=L.pair(side_w, 0.04), fontPath=FONT_BOLD, fontSize="${fsSmall}", color="${subColor}",
              horizontalAlignment="left", zIndex="62")
    status(L, view, W - bx - bs / 2 - 0.02, 0.905, fs="fsSmall")
    # button prompts sit in the dip above the bar, clear of the title
    help_(L, view, W / 2, 0.795, origin="0.5 0.5", fs="fsSmall")


def build_wii(W, style, layout, box="cover, 3dbox"):
    L = Layout(W, box)
    sysimg = SYS + "channelwide/"
    m = 0.05 if W >= 1.4 else 0.035
    background(L, "bg-wii.png", 0.02)

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
    return L


# ================================================================== ESDEIIU (tablet console home)
def wiiu_dock(L, view, W, m):
    L.rect(view, "dockShadow", m, 0.872, W - 2 * m, 0.09, "${shadowColor}", 0.045, z=58)
    L.rect(view, "dock", m, 0.865, W - 2 * m, 0.09, "${panelColor}", 0.045, z=58.1, opacity="0.92")
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
    L.add(view, "clock", "date", pos=L.pair(W - m - 0.04, 0.91), origin="1 0.5", fontPath=FONT_BOLD,
          fontSize="${fsSmall}", color="${subColor}", format="%Y-%m-%d", horizontalAlignment="right", scope="view")


def wiiu_top(L, view, W, m):
    if view == "system" and W >= 1.6:
        for i in range(6):
            L.rect(view, f"pageDot{i}", W / 2 - 0.111 + i * 0.04, 0.198, 0.022, 0.022,
                   "${accentColor}" if i == 0 else "${decoColor}", 0.011, z=8)
    clock(L, view, W - m, 0.05, "1 0.5", fs="fsStatus")
    status(L, view, W - m, 0.1)


def build_wiiu(W, style, layout, box="cover, 3dbox"):
    L = Layout(W, box)
    sysimg = SYS + style + "/"
    m = 0.05 if W >= 1.4 else 0.035
    background(L, "bg-wiiu.png", 0.11, overlay="wiiu-swirl.png")
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
    return L


def build_ii(W, style, layout, box="cover, 3dbox"):
    return (build_wii if style == "channelwide" else build_wiiu)(W, style, layout, box)


BUILDERS = {"3ds": build_3ds, "ii": build_ii}
