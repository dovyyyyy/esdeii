"""Write the XML for the esdeii ES-DE theme.

All layout maths is done in "height units": the screen is 1.0 tall and W wide,
where W is the aspect ratio. Values are converted to ES-DE's normalized
coordinates (0..1 on both axes) when written out. Corner radii in ES-DE are a
fraction of screen *width*, so they get divided by W too.
"""
import json, os, sys
from xml.sax.saxutils import escape

OUT = sys.argv[1]
os.makedirs(os.path.join(OUT, "layouts"), exist_ok=True)

ASPECTS = [
    ("16:9", 16 / 9), ("16:10", 1.6), ("3:2", 1.5), ("4:3", 4 / 3), ("5:3", 5 / 3),
    ("5:4", 1.25), ("8:7", 8 / 7), ("19.5:9", 19.5 / 9), ("20:9", 20 / 9), ("21:9", 2560 / 1080),
]

VARIANTS = [
    # name, label, gamelist primary, use video
    ("grid", "Icon grid (3DS style)", "grid", True),
    ("list", "Game list (DS style)", "list", True),
    ("gridStatic", "Icon grid, no videos", "grid", False),
    ("listStatic", "Game list, no videos", "list", False),
]

SCHEMES = {
    "iceWhite": ("Ice White", dict(
        bgColor="EEF1F5", panelColor="FFFFFF", borderColor="D3D9E1", shadowColor="1E28361C",
        textColor="2F3640", subColor="7D8693", accentColor="1FA5EA", accentText="FFFFFF",
        screenColor="2B313B", tileColor="EEF2F7", decoColor="CDD3DC", dividerColor="E5E9EF",
        dimText="5A626E")),
    "cosmoBlack": ("Cosmo Black", dict(
        bgColor="1A1D22", panelColor="2A2F37", borderColor="0E1013", shadowColor="00000070",
        textColor="EEF1F5", subColor="98A2AF", accentColor="3CB8FF", accentText="FFFFFF",
        screenColor="14171B", tileColor="363C46", decoColor="30353D", dividerColor="3A404A",
        dimText="C3CAD4")),
    "flameRed": ("Flame Red", dict(
        bgColor="F7E8E7", panelColor="FFFFFF", borderColor="E8C8C6", shadowColor="5A1E1A1C",
        textColor="3A2E2E", subColor="8C7676", accentColor="E5404A", accentText="FFFFFF",
        screenColor="2E2A2E", tileColor="F8EEED", decoColor="E6C2BF", dividerColor="F1E1E0",
        dimText="604E4E")),
    "aquaBlue": ("Aqua Blue", dict(
        bgColor="E2F0FA", panelColor="FFFFFF", borderColor="C0DAEC", shadowColor="0F3C5A1C",
        textColor="24384A", subColor="6E8597", accentColor="1683D9", accentText="FFFFFF",
        screenColor="22303C", tileColor="ECF5FB", decoColor="B7D3E6", dividerColor="DDEBF5",
        dimText="4A6072")),
}

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

    # coordinate helpers -------------------------------------------------
    def x(self, v):
        return v / self.W

    def pair(self, x, y):
        return f"{f(self.x(x))} {f(y)}"

    def rad(self, r):
        return f(r / self.W)

    def add(self, view, etype, name, **props):
        self.views[view].append((etype, name, props))
        return props

    # building blocks ------------------------------------------------------
    def panel(self, view, name, x0, y0, w, h, r=0.034, z=5):
        """Rounded 'screen' panel: soft shadow + border + face."""
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

    def text(self, view, name, x0, y0, w, h, size, font=FONT_REG, color="${textColor}", z=40,
             origin=None, **extra):
        p = dict(pos=self.pair(x0, y0), size=self.pair(w, h), fontPath=font, fontSize=f(size),
                 color=color, zIndex=f(z))
        if origin:
            p["origin"] = origin
        p.update(extra)
        self.add(view, "text", name, **p)


def build(W, variant):
    vname, _, primary, use_video = variant
    L = Layout(W)

    decor = W >= 1.6
    side = min(0.24, (W - 1.30) / 2) if decor else 0.03
    px, pw = side, W - 2 * side
    wide = pw >= 1.6

    for view in ("system", "gamelist"):
        # background: DS graph paper, tinted by the colour scheme
        L.add(view, "image", "background", pos="0 0", size="1 1", path=IMG + "bg-grid.png",
              tile="true", tileSize=f"0 {f(0.09)}", color="${bgColor}", stationary="always", zIndex="0")

    # ------------------------------------------------------------------ geometry
    geo = {
        "system": dict(up=(0.035, 0.555), lo=(0.595, 0.915)),
        "gamelist": dict(up=(0.035, 0.485), lo=(0.525, 0.915)),
    }

    for view, g in geo.items():
        uy0, uy1 = g["up"]
        ly0, ly1 = g["lo"]
        L.panel(view, "upperScreen", px, uy0, pw, uy1 - uy0)
        L.panel(view, "lowerScreen", px, ly0, pw, ly1 - ly0)
        # hinge between the two screens
        hy = (uy1 + ly0) / 2 - 0.011
        for i, hx in enumerate((px + 0.10, px + pw - 0.10 - 0.20)):
            L.add(view, "image", f"hinge{i}", pos=L.pair(hx, hy), size=L.pair(0.20, 0.022),
                  path=IMG + "pill.png", color="${borderColor}", zIndex="4")
        # status bar divider inside the upper screen
        L.rect(view, "statusDivider", px + 0.02, uy0 + 0.067, pw - 0.04, 0.0028, "${dividerColor}", z=7)
        # DS-style decorations in the side margins
        if decor:
            cxl, cxr = side / 2, W - side / 2
            sw, sh = min(0.085, side * 0.42), min(0.085, side * 0.42) * 150 / 110
            uc = (uy0 + uy1) / 2
            for i, cx in enumerate((cxl, cxr)):
                L.add(view, "image", f"speaker{i}", pos=L.pair(cx, uc), origin="0.5 0.5",
                      size=L.pair(sw, sh), path=IMG + "speaker.png", color="${decoColor}", zIndex="3")
            lc = (ly0 + ly1) / 2
            ds = min(0.14, side * 0.62)
            L.add(view, "image", "dpad", pos=L.pair(cxl, lc), origin="0.5 0.5", size=L.pair(ds, ds),
                  path=IMG + "dpad.png", color="${decoColor}", zIndex="3")
            L.add(view, "image", "faceButtons", pos=L.pair(cxr, lc), origin="0.5 0.5",
                  size=L.pair(ds, ds), path=IMG + "buttons.png", color="${decoColor}", zIndex="3")
            # power LED
            L.add(view, "image", "powerLed", pos=L.pair(cxl, ly1 - 0.01), origin="0.5 0.5",
                  size=L.pair(0.016, 0.016), path=IMG + "white.png", color="${accentColor}",
                  cornerRadius=L.rad(0.008), zIndex="3")

        # status bar: clock left, battery etc right
        sy = uy0 + 0.034
        L.add(view, "clock", "clock", pos=L.pair(px + 0.03, sy), origin="0 0.5",
              fontPath=FONT_BOLD, fontSize="0.03", color="${subColor}", format="%H:%M")
        L.add(view, "systemstatus", "systemStatus", pos=L.pair(px + pw - 0.03, sy), origin="1 0.5",
              height="0.03", color="${subColor}", fontPath=FONT_BOLD)

        # help prompts under the lower screen
        L.add(view, "helpsystem", "help", pos=L.pair(px + 0.01, 0.958), origin="0 0.5",
              fontPath=FONT_BOLD, fontSize="0.028", textColor="${subColor}", iconColor="${subColor}",
              letterCase="capitalize", entrySpacing="0.012")

    # ================================================================== SYSTEM VIEW
    uy0, uy1 = geo["system"]["up"]
    ly0, ly1 = geo["system"]["lo"]
    v = "system"

    tile = 0.34
    tx, ty = px + 0.045, uy0 + 0.095
    L.add(v, "image", "systemTile", pos=L.pair(tx, ty), size=L.pair(tile, tile),
          path=SYS + "${system.theme}.png", default=SYS + "_default.png", zIndex="20")

    nx = tx + tile + 0.04
    if wide:
        prev_w, prev_h = 0.56, 0.315
        prev_x = px + pw - 0.04 - prev_w
        name_w = prev_x - 0.04 - nx
    else:
        name_w = px + pw - 0.04 - nx

    L.text(v, "systemName", nx, uy0 + 0.11, name_w, 0.15, 0.056, FONT_BLACK, "${textColor}",
           text="${system.fullName}", verticalAlignment="top", lineSpacing="1.12", z=40)
    L.text(v, "gameCount", nx + 0.012, uy0 + 0.285, 0, 0, 0.03, FONT_BOLD, "${accentText}",
           systemdata="gamecount", backgroundColor="${accentColor}",
           backgroundMargins=f"{L.rad(0.014)} {L.rad(0.014)}", backgroundCornerRadius=L.rad(0.03),
           lineSpacing="1.6", z=41)

    # featured random game from the system
    L.add(v, "gameselector", "featured", selection="random", gameCount="1")
    L.text(v, "featuredLabel", nx, uy0 + 0.375, name_w, 0.03, 0.022, FONT_BOLD, "${subColor}",
           text="Featured game", letterCase="uppercase", z=40)
    L.text(v, "featuredName", nx, uy0 + 0.405, name_w, 0.04, 0.032, FONT_BOLD, "${dimText}",
           metadata="name", systemNameSuffix="false", z=40)
    if wide:
        py = uy0 + 0.09 + (uy1 - uy0 - 0.09 - prev_h) / 2 - 0.005
        L.rect(v, "previewScreen", prev_x, py, prev_w, prev_h, "${screenColor}", 0.016, z=18)
        L.add(v, "image", "featuredImage", pos=L.pair(prev_x, py), cropSize=L.pair(prev_w, prev_h),
              imageType="screenshot, titlescreen, miximage", cornerRadius=L.rad(0.016), zIndex="19")

    # lower screen: DSi-style row of tiles with a fixed cursor in the middle
    item = 0.165
    scale = 1.32
    step = 0.255
    car_y0, car_h = ly0 + 0.005, ly1 - ly0 - 0.01
    L.add(v, "carousel", "systemcarousel", pos=L.pair(px + 0.01, car_y0),
          size=L.pair(pw - 0.02, car_h), type="horizontal",
          staticImage=SYS + "${system.theme}.png",
          itemSize=L.pair(item, item), itemScale=f(scale), maxItemCount=f((pw - 0.02) / step),
          unfocusedItemOpacity="1", unfocusedItemDimming="0.94", imageFit="contain",
          color="00000000", text="${system.fullName}", fontPath=FONT_BLACK, fontSize="0.026",
          textColor="FFFFFF", textBackgroundColor="${accentColor}",
          textBackgroundCornerRadius=L.rad(0.04), textRelativeScale="0.85", lineSpacing="1.15",
          itemVerticalAlignment="center", fastScrolling="true", zIndex="50")
    # cursor ring around the selected (always centred) tile
    content = item * scale * (284 / 320)  # visible body of the tile png
    ring = content + 0.034
    cy = car_y0 + car_h / 2 - item * scale * (4 / 320)
    L.add(v, "image", "cursor", pos=L.pair(px + pw / 2, cy), origin="0.5 0.5",
          size=L.pair(ring, ring), path=IMG + "cursor.png", color="${accentColor}", zIndex="55")

    # ================================================================== GAMELIST VIEW
    uy0, uy1 = geo["gamelist"]["up"]
    ly0, ly1 = geo["gamelist"]["lo"]
    v = "gamelist"

    # system name in the middle of the status bar
    L.text(v, "systemLabel", px + pw / 2 - (0 if decor else 0.1), uy0 + 0.034, pw * (0.5 if decor else 0.34), 0.032, 0.028, FONT_BOLD,
           "${subColor}", origin="0.5 0.5", text="${system.fullName}", horizontalAlignment="center",
           z=40)

    body_y0 = uy0 + 0.088
    body_y1 = uy1 - 0.022
    mh = body_y1 - body_y0
    mw = min(mh * 16 / 9, pw * 0.44)
    mx = px + 0.025
    L.rect(v, "mediaScreen", mx, body_y0, mw, mh, "${screenColor}", 0.016, z=18)
    media = dict(pos=L.pair(mx, body_y0), zIndex="20", imageType="screenshot, titlescreen, miximage",
                 scrollFadeIn="true")
    if use_video:
        L.add(v, "video", "gameVideo", **media, cropSize=L.pair(mw, mh),
              defaultImage=IMG + "noimage.png", imageCornerRadius=L.rad(0.016),
              videoCornerRadius=L.rad(0.016), delay="1.6", fadeInTime="0.6", audio="true")
    else:
        L.add(v, "image", "gameImage", **media, cropSize=L.pair(mw, mh),
              default=IMG + "noimage.png", cornerRadius=L.rad(0.016))

    x0 = mx + mw + 0.035
    xr = px + pw - 0.03
    if wide:
        dw = 0.44
        cw = xr - x0 - dw - 0.035
    else:
        cw = xr - x0

    if wide:
        L.text(v, "gameName", x0, body_y0, cw, 0.1, 0.042, FONT_BLACK, "${textColor}",
               metadata="name", verticalAlignment="top", lineSpacing="1.15", z=40)
        r1 = body_y0 + 0.115
    else:
        L.text(v, "gameName", x0, body_y0, cw, 0.05, 0.04, FONT_BLACK, "${textColor}",
               metadata="name", z=40)
        r1 = body_y0 + 0.065
    col2 = x0 + cw / 2 + 0.01
    half = cw / 2 - 0.015
    lab = dict(letterCase="uppercase", metadataElement="true")

    def row(y, left, right):
        (ln, lt, lkind, lmeta), (rn, rt, rkind, rmeta) = left, right
        for xx, nm, title, kind, meta in ((x0, ln, lt, lkind, lmeta), (col2, rn, rt, rkind, rmeta)):
            L.text(v, nm + "Label", xx, y, half, 0.026, 0.019, FONT_BOLD, "${subColor}", text=title,
                   **lab)
            if kind == "datetime":
                L.add(v, "datetime", nm, pos=L.pair(xx, y + 0.024), size=L.pair(half, 0.034),
                      metadata=meta, fontPath=FONT_BOLD, fontSize="0.027", color="${dimText}",
                      format="%Y-%m-%d", defaultValue="Unknown")
            else:
                L.text(v, nm, xx, y + 0.024, half, 0.034, 0.027, FONT_BOLD, "${dimText}",
                       metadata=meta, defaultValue="Unknown")

    row(r1, ("released", "Released", "datetime", "releasedate"), ("players", "Players", "text", "players"))
    r2 = r1 + 0.068
    row(r2, ("developer", "Developer", "text", "developer"), ("genre", "Genre", "text", "genre"))
    r3 = r2 + 0.074
    L.add(v, "rating", "gameRating", pos=L.pair(x0, r3), size="0 0.03",
          filledPath=IMG + "star-filled.svg", unfilledPath=IMG + "star-unfilled.svg",
          interpolation="linear", zIndex="45")
    L.add(v, "badges", "gameBadges", pos=L.pair(x0 + cw, r3 - 0.002), origin="1 0",
          size=L.pair(min(0.32, cw * 0.55), 0.034), horizontalAlignment="right", direction="row",
          lines="1", itemsPerLine="8", itemMargin=f"{L.rad(0.006)} 0.006",
          slots="favorite completed kidgame broken controller altemulator manual", zIndex="45")
    if wide:
        dx = xr - dw
        L.text(v, "descriptionLabel", dx, body_y0, dw, 0.026, 0.019, FONT_BOLD, "${subColor}",
               text="About", **lab)
        L.text(v, "gameDescription", dx, body_y0 + 0.034, dw, mh - 0.034, 0.026, FONT_REG,
               "${dimText}", metadata="description", lineSpacing="1.35", containerStartDelay="5",
               z=40)
    else:
        dy = r3 + 0.048
        L.text(v, "gameDescription", x0, dy, cw, body_y1 - dy, 0.024, FONT_REG, "${dimText}",
               metadata="description", lineSpacing="1.3", containerStartDelay="5", z=40)

    # game counter under the lower screen, right aligned
    # on narrow screens the help prompts need the whole bottom row, so the
    # counter moves into the status bar, next to the battery
    info_pos = L.pair(px + pw - 0.01, 0.958) if decor else L.pair(px + pw - 0.25, uy0 + 0.034)
    L.add(v, "gamelistinfo", "gamelistInfo", pos=info_pos, origin="1 0.5",
          size=L.pair(pw * 0.4 if decor else 0.2, 0.034), fontPath=FONT_BOLD,
          fontSize="0.026", color="${subColor}",
          horizontalAlignment="right", zIndex="45")

    # lower screen: the game picker
    if primary == "grid":
        it = 0.158
        sp = 0.022
        gh = 2 * it + sp + 0.004
        gy0 = ly0 + (ly1 - ly0 - gh) / 2
        avail = pw - 0.056
        cols = int((avail + sp) // (it + sp))
        gw = cols * (it + sp) - sp + 0.004
        L.add(v, "grid", "gamelistgrid", pos=L.pair(px + (pw - gw) / 2, gy0), size=L.pair(gw, gh),
              imageType="cover", itemSize=L.pair(it, it), itemScale="1.12",
              itemSpacing=f"{f(L.x(sp))} {f(sp)}", scaleInwards="true", fractionalRows="false",
              imageFit="contain", imageRelativeScale="0.78", imageCornerRadius=L.rad(0.006),
              backgroundColor="${tileColor}", backgroundCornerRadius=L.rad(0.026),
              backgroundRelativeScale="0.9",
              selectorColor="${accentColor}", selectorCornerRadius=L.rad(0.03), selectorLayer="bottom",
              textColor="${textColor}", fontPath=FONT_BOLD, fontSize="0.02",
              textRelativeScale="0.72", lineSpacing="1.15", unfocusedItemOpacity="1",
              zIndex="50")
    else:
        L.add(v, "textlist", "gamelisttextlist", pos=L.pair(px + 0.035, ly0 + 0.02),
              size=L.pair(pw - 0.07, ly1 - ly0 - 0.04), fontPath=FONT_BOLD, fontSize="0.031",
              lineSpacing="1.75", primaryColor="${textColor}", secondaryColor="${accentColor}",
              selectedColor="${accentText}", selectedSecondaryColor="${accentText}",
              selectedBackgroundColor="${accentColor}",
              selectedBackgroundMargins=f"{L.rad(0.016)} {L.rad(0.016)}",
              selectedBackgroundCornerRadius=L.rad(0.04), selectorColor="00000000",
              horizontalMargin=f(L.x(0.016)), indicators="symbols", zIndex="50")
    return L


def props_xml(props, ind):
    out = []
    for k, val in props.items():
        out.append(f"{ind}<{k}>{escape(str(val))}</{k}>")
    return "\n".join(out)


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
            fh.write(f"<!-- esdeii theme layout: aspect ratio {ar}, variant {var[0]} (generated) -->\n")
            fh.write(views_xml(L))
        layouts[(ar, var[0])] = (fn, L)

# ------------------------------------------------------------------ capabilities.xml
cap = ["<!-- Theme capabilities for esdeii -->", "<themeCapabilities>", "    <themeName>esdeii</themeName>", ""]
for ar, _ in ASPECTS:
    cap.append(f"    <aspectRatio>{ar}</aspectRatio>")
cap.append("")
for key, (label, _) in SCHEMES.items():
    cap += [f'    <colorScheme name="{key}">', f"        <label>{label}</label>", "    </colorScheme>"]
cap.append("")
cap += [
    '    <transitions name="esdeiiSlide">',
    "        <label>esdeii slide</label>",
    "        <systemToSystem>instant</systemToSystem>",
    "        <systemToGamelist>slide</systemToGamelist>",
    "        <gamelistToGamelist>instant</gamelistToGamelist>",
    "        <gamelistToSystem>slide</gamelistToSystem>",
    "        <startupToSystem>fade</startupToSystem>",
    "        <startupToGamelist>fade</startupToGamelist>",
    "    </transitions>",
    '    <transitions name="esdeiiFade">',
    "        <label>esdeii fade</label>",
    "        <systemToSystem>instant</systemToSystem>",
    "        <systemToGamelist>fade</systemToGamelist>",
    "        <gamelistToGamelist>instant</gamelistToGamelist>",
    "        <gamelistToSystem>fade</gamelistToSystem>",
    "    </transitions>",
    "",
]
for name, label, _, _ in VARIANTS:
    cap += [f'    <variant name="{name}">', f"        <label>{label}</label>",
            "        <selectable>true</selectable>", "    </variant>"]
cap.append("</themeCapabilities>")
with open(os.path.join(OUT, "capabilities.xml"), "w") as fh:
    fh.write("\n".join(cap) + "\n")

# ------------------------------------------------------------------ theme.xml
t = ["<!-- esdeii: a dual-screen handheld inspired theme for ES-DE -->", "<theme>",
     "    <include>./navigationsounds.xml</include>", ""]
for key, (label, vars_) in SCHEMES.items():
    t.append(f'    <colorScheme name="{key}">')
    t.append("        <variables>")
    for k, val in vars_.items():
        t.append(f"            <{k}>{val}</{k}>")
    t.append("        </variables>")
    t.append("    </colorScheme>")
t.append("")
for name, _, _, _ in VARIANTS:
    t.append(f'    <variant name="{name}">')
    for ar, _ in ASPECTS:
        fn = layouts[(ar, name)][0]
        t.append(f'        <aspectRatio name="{ar}">')
        t.append(f"            <include>./layouts/{fn}</include>")
        t.append("        </aspectRatio>")
    t.append("    </variant>")
t.append("</theme>")
with open(os.path.join(OUT, "theme.xml"), "w") as fh:
    fh.write("\n".join(t) + "\n")

# ------------------------------------------------------------------ navigation sounds
ns = ["<theme>", '    <view name="all">']
for s in ("systembrowse", "quicksysselect", "select", "back", "scroll", "favorite", "launch"):
    ns += [f'        <sound name="{s}">', f"            <path>./assets/sounds/{s}.wav</path>", "        </sound>"]
ns += ["    </view>", "</theme>"]
with open(os.path.join(OUT, "navigationsounds.xml"), "w") as fh:
    fh.write("\n".join(ns) + "\n")

# dump layouts for the preview renderer
dump = {f"{ar}|{var}": {"W": L.W, "views": L.views} for (ar, var), (_, L) in layouts.items()}
with open(os.path.join(os.path.dirname(OUT.rstrip('/')), "layouts.json"), "w") as fh:
    json.dump({"layouts": dump, "schemes": {k: v[1] for k, v in SCHEMES.items()}}, fh)
print("xml done:", len(layouts), "layout files")
