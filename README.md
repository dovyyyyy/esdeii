# esdeii — console-menu theme for ES-DE

One theme, five looks. Pick them in **Menu → UI Settings → Theme variant**.

| Look | What it is |
|---|---|
| **Channel wall** | wide channel tiles with empty slots and a curved clock bar with a blinking clock |
| **Home screen** | framed square tiles with a Start cursor and a dock |
| **Home screen, glossy icons** | the same with glossy icons |
| **Dual screen, icon grid** | two screens and a hinge, systems in a grid of icons |
| **Dual screen, icon row** | two screens, systems in a row with a breathing cursor |

### Channel wall
![Channel wall](previews/esdeii-channel-wall.png)

### Home screen
![Home screen](previews/esdeii-home-screen.png)

### Dual screen
![Dual screen](previews/esdeii-dual-screen.png)

### 3D boxes in the game grid
![3D boxes](previews/esdeii-3d-boxes.png)

*(Previews are mockups, not real ES-DE screenshots.)*

## Install (Android)

1. Download the latest version:
   https://github.com/dovyyyyy/esdeii/archive/refs/heads/main.zip
2. Unzip it and copy the **esdeii** folder into the `themes` folder inside
   your ES-DE data folder, e.g. `Internal storage/ES-DE/themes/`.
   **Delete any old `esde3ds` or `esdeiiu` folders** — the dual-screen look
   is now part of esdeii.
3. Restart ES-DE, open **Menu → UI Settings → Theme** and pick **ESDEII**.

To update, download again and replace the folder.

## Customisation (Menu → UI Settings)

- **Theme variant** — look · how games are shown · box art, for example
  *Channel wall · icon grid · 3D boxes*:
  - games as an **icon grid**, a **cover shelf** or a **game list**;
  - **box art** or **3D boxes** for the grid and shelf. Each falls back to
    the other, so games scraped with only 3D boxes (or only covers) still
    show their art.
- **Theme color scheme** — Silver Menu, Cloud White, Ice White, Cosmo Black,
  Flame Red, Aqua Blue, Mint Green, Lavender, Sunset Orange, Sakura Pink,
  Midnight Blue, Retro Pocket, plus **Light / Dark + system colours**
  where the accent matches each console. In the dual-screen look each scheme
  has its own background pattern.
- **Theme font size** — extra small to extra large.
- **Theme transitions** — *Smooth* (default: whole pages glide in and out
  when you open a system or go back, like the console menu), *Snappy*
  (instant) or *Fade*.
- **Theme aspect ratio** — leave on Automatic (16:9, 16:10, 3:2, 4:3, 5:3,
  5:4, 8:7, 19.5:9, 20:9 and 21:9 are included).
- Navigation sounds can be turned off in ES-DE's **Sound settings**.

## Sounds

One matching set of soft, glassy clicks and airy swooshes, all in the same
key and the same small room and levelled to the same loudness: moving the
cursor always makes the same short click, opening something gives a rising
swoosh and a two-note ding, going back plays it in reverse, and starting a
game swells into a bright chord.

## Features

- Softly drifting bubbles in the background, tinted with your colour scheme.
  They only float in free space, never behind the clock, text or games, and
  they fade in and out, so when ES-DE restarts them (it does that every time
  you pick another system or open a game list) new bubbles simply rise
  instead of jumping back to where they started.
- Rounded console-style lettering (M PLUS Rounded 1c).
- **Empty slots** fill the rest of every grid, like the blank channels on
  a console menu (plain, without any logo).
- Small animations: blinking clock colon, a nudging
  page arrow on the channel wall and a breathing cursor in the icon row.
  They are tiny, so they cost almost nothing to draw.
- The clock, date and battery hide while the ES-DE menu is open.
- Icons for all 197 systems ES-DE supports, each drawn after its real
  controller or console.
- System info line: maker, release year and type for every console.
- Game count, clock, date, battery and Wi-Fi.
- **Featured game**: a random game from the selected system.
- **Jump back in** (dual screen): your three most recently played games.
- Game details: release date, players, developer, genre, last played, play
  time, rating, badges and a scrolling description.
- Game videos (start after 1 s), with the scraped **game logo** in the corner.
- Games without a screenshot (for example Android apps) show their box art
  instead.

## Performance

- The drifting bubbles are light: instead of one full-screen animation that
  the phone redrew every frame, each bubble is a small, short animation.
  ES-DE draws their frames once, keeps them in memory and just replays them,
  so they barely cost anything after the first loop.
- On a slow device pick the *Snappy* transition profile: it switches views
  instantly.
- The font only contains Latin, Greek, Cyrillic and kana, so it stays small;
  other scripts (e.g. kanji) use ES-DE's built-in fallback fonts.
- Every layout is checked against ES-DE's theme reference
  (`tools/validate.py`), so ES-DE doesn't spend time logging bad properties.

## Media used

- Grids, shelves and "Jump back in" use **box art** or **3D boxes**
  (your choice, each falling back to the other).
- The game screen uses the **screenshot**, then title screen, then
  miximage, plus the game **video** and **marquee** (logo).

## Changing things

- System icons live in `esdeii/systems/<style>/`, named after the ES-DE
  system (`snes.png`, `n3ds.png` ...). Replace any with your own PNG of the
  same size.
- Everything is generated by `tools/build.py` (layouts in `tools/layouts.py`,
  icons in `tools/icons.py` and `tools/shapes.py`, sounds in
  `tools/audio.py`, other artwork and the small Lottie animations in `tools/themeart.py`).
  Rebuild with `python3 tools/build.py . <font folder> <OFL.txt> [cache]`, where
  the font folder holds the M PLUS Rounded 1c TTFs from
  [Google Fonts](https://github.com/google/fonts/tree/main/ofl/mplusrounded1c)
  (if the folder doesn't exist it reuses the fonts already in the theme).

## Credits

M PLUS Rounded 1c font by the M+ and Rounded M+ Project Authors, SIL Open
Font License (`assets/fonts/OFL.txt`). Icons, artwork and sounds were made for these
themes. Not affiliated with any console maker.
