# esdeii — a console-menu theme pack for ES-DE

esdeii is a theme for [ES-DE (EmulationStation Desktop Edition)](https://es-de.org)
inspired by the home menus of Nintendo's living-room, tablet and dual-screen
consoles. One download gives you four looks, 14 colour schemes, icons for
every system ES-DE supports and its own set of UI sounds. It is made and
tested first of all for **ES-DE on Android**, but it is a normal ES-DE theme
and also works on Windows, macOS and Linux.

> **Heads-up: this theme pack is vibecoded.** All of it — the layouts, the
> 197 system icons, the artwork, the sounds and this README — was made with
> an AI assistant (Claude), directed and tested by me. If you'd rather not use
> AI-made things, that's completely fine — just skip this one. 🙂

*Not affiliated with Nintendo or any other console maker. All names and
icons are original drawings made for this theme.*

## The four looks

| Look | What it is |
|---|---|
| **Channels** | a wall of wide channel tiles with empty slots, and a curved clock bar at the bottom with a big clock, the date, the game count and the battery |
| **Home** | framed square tiles with a glowing cursor, page dots, a featured box in the corner and a dock with the button prompts |
| **Dual Grid** | two screens: the system and a featured game on top, the systems as a grid of icons below |
| **Dual Row** | two screens: the system and a featured game on top, the systems as a single row below |

### Channels
![Channels — systems](previews/channels-systems.png)
![Channels — games](previews/channels-games.png)

### Home
![Home — systems](previews/home-systems.png)
![Home — games](previews/home-games.png)

### Dual Grid and Dual Row
![Dual Grid — systems](previews/dual-grid-systems.png)
![Dual Row — games](previews/dual-row-games.png)

*Previews are mock-ups drawn from the real layout files with placeholder
art, not screenshots from ES-DE, so fonts and spacing may differ slightly.*

## Install

1. Download **esdeii.zip** from the
   [latest release](https://github.com/dovyyyyy/esdeii/releases/latest).
2. Unzip it. You get a folder called **esdeii**.
3. Copy that folder into the `themes` folder in your ES-DE data folder:
   - **Android:** usually `Internal storage/ES-DE/themes/`
   - **Windows / macOS / Linux:** `ES-DE/themes/` in your ES-DE data folder
     (by default in your home folder).
4. Restart ES-DE, open **Menu → UI Settings → Theme** and pick **ESDEII**.

To update, download the new release and replace the folder.
If you used an early version, delete any old `esde3ds` or `esdeiiu` folders —
those looks are now part of esdeii.

## Settings (Menu → UI Settings)

- **Theme variant** — the look, how games are shown and which box art to
  use, e.g. *Channels · Grid* or *Dual Row · Shelf · 3D*:
  - looks: **Channels**, **Home**, **Dual Grid**, **Dual Row**
  - games as a **Grid** of icons, a **Shelf** of covers or a **List**
  - normal **box art**, or **3D boxes** with *· 3D*. Each falls back to the
    other, so games that only have one kind scraped still show their art.
- **Theme color scheme** — Silver Menu, Cloud White, Ice White, Cosmo Black,
  Flame Red, Aqua Blue, Mint Green, Lavender, Sunset Orange, Sakura Pink,
  Midnight Blue, Retro Pocket, plus **Light / Dark + system colours**, where
  the accent colour changes to match each console. In the Dual looks every
  scheme also has its own background pattern.
- **Theme font size** — extra small to extra large.
- **Theme transitions** — *Smooth* (default: pages slide when you open a
  system or go back) or *Snappy* (instant, best for slow devices).
- **Theme aspect ratio** — leave it on Automatic. 16:9, 16:10, 3:2, 4:3,
  5:3, 5:4, 8:7, 19.5:9, 20:9 and 21:9 are all included, so it fits phones,
  handhelds, tablets and TVs.
- The UI sounds can be turned off in ES-DE's **Sound settings**.

## What's in it

**Systems page**
- Icons for all 197 systems ES-DE supports, each drawn after its real
  console or controller, in three styles (wide channel tiles, framed tiles
  and glossy icons).
- A line with the maker, release year and type of every console, and the
  number of games (and favourites).
- **Empty slots** fill the rest of every grid, like blank channels.
- **Featured game** (Home and Dual): a random game from the selected system.

**Games page**
- A big video screen: the game video starts after a moment, with the
  scraped game logo in the corner. Before the video (or without one) it
  shows the screenshot, title screen or mix image, and games without any of
  those — Android apps, for example — show their box art.
- Release date, players, developer, genre, last played, play time, rating,
  badges and a description that scrolls slowly enough to read.
- Faint artwork of the selected game (fan art, else the screenshot) behind
  the page, fading in as you move. In the Dual looks the top screen is
  filled edge to edge with the game's artwork, with the video on the left and
  the details on a dark glass card on the right.
- Headers over the artwork have a thin outline so they stay readable on any
  custom art.

**Everywhere**
- Softly drifting bubbles in your colour scheme on the systems page, only in
  free space — never over text, panels, the clock or the games. The games
  pages have none, so nothing moves behind the details.
- Rounded console-style lettering (M PLUS Rounded 1c).
- Clock, date, battery and Wi-Fi; they hide while the ES-DE menu is open.
- ES-DE always draws the clock, battery and button prompts in a fixed layer
  on top that never slides, so the theme keeps the surfaces under them still:
  the Channels clock bar and the Home dock stay put while the pages slide,
  and in the Dual looks the clock sits in a strip above the two screens.

## Sounds

One soft, rounded family of UI sounds in the spirit of a tablet console's
home menu, with a touch of phone-UI polish. They are all built from the same
few pieces — a soft tap, warm notes that settle gently onto their pitch and
a light air swell — in one key and the same small, warm room, with no harsh
clicks or hiss, and levelled to the same loudness:

- moving the cursor: a quiet soft tap (the same every time)
- opening a system or game list: a tap and two short notes going up
- going back: the same two notes going down
- favouriting: a quick sparkle of four notes
- starting a game: an airy rise into a soft, open chord

## Media it uses

- Grids and shelves: **box art** or **3D boxes** (your choice, each falling
  back to the other).
- Game screen: **video**, **screenshot** (then title screen, then mix image)
  and the **marquee** (game logo).
- Backdrop: **fan art**, then the **screenshot**.

Scrape these with ES-DE's scraper to get the most out of the theme.

## Performance

- The bubbles are many small, short animations instead of one full-screen
  one, so ES-DE draws their frames once and just replays them.
- On a slow device pick the *Snappy* transitions.
- The font only contains Latin, Greek, Cyrillic and kana to stay small;
  other scripts (such as kanji) use ES-DE's built-in fallback fonts.
- Every layout is checked against ES-DE's theme reference, so ES-DE doesn't
  waste time logging bad theme properties.

## Changing things / building it yourself

- System icons are in `esdeii/systems/<style>/`, named after the ES-DE
  system (`snes.png`, `n3ds.png` …). Replace any of them with your own PNG of
  the same size.
- The whole theme is generated by Python scripts in `tools/`: layouts in
  `layouts.py`, icons in `icons.py` and `shapes.py`, sounds in `audio.py`,
  other artwork and the small Lottie animations in `themeart.py`.
  Rebuild with

  ```
  python3 tools/build.py . <font folder> <OFL.txt> [cache folder]
  ```

  where the font folder holds the M PLUS Rounded 1c TTFs from
  [Google Fonts](https://github.com/google/fonts/tree/main/ofl/mplusrounded1c)
  (if it doesn't exist, the fonts already in the theme are reused). It needs
  Python 3 with Pillow, NumPy, SciPy and fontTools.
- `tools/preview.py` draws the mock-up previews and `tools/validate.py`
  checks the layouts against ES-DE's `THEMES.md`.

## Credits

- M PLUS Rounded 1c font by the M+ and Rounded M+ Project Authors, under
  the SIL Open Font License (`esdeii/assets/fonts/OFL.txt`).
- Icons, artwork and sounds were generated for this theme by the scripts in
  `tools/`; no samples or images from consoles or other themes are used.
- Made with Claude (Anthropic) — see the note at the top.
