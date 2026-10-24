# esdeii — a dual-screen theme for ES-DE

A DS / 3DS-inspired theme: two rounded "screens" joined by a hinge, a
graph-paper background, glossy rounded system icons, and speaker, D-pad and
button details in the side margins on wide screens.

![Preview](preview.png)

*(Preview is a mockup, not a real ES-DE screenshot.)*

## Install (Android)

1. Download this repo (**Code → Download ZIP**) and unzip it, or `git clone` it.
2. Put the folder into the `themes` folder inside your ES-DE data folder
   (the one you picked during ES-DE setup), e.g.
   `Internal storage/ES-DE/themes/esdeii`
3. Restart ES-DE, open **Menu → UI Settings → Theme** and pick **ESDEII**.

To update, replace the folder with a fresh download (or `git pull`).

## Options (Menu → UI Settings)

- **Theme variant**: Icon grid (3DS style), Game list (DS style), and the
  same two without videos.
- **Theme color scheme**: Ice White, Cosmo Black, Flame Red, Aqua Blue.
- **Theme aspect ratio**: leave on Automatic. Layouts are included for
  16:9, 16:10, 3:2, 4:3, 5:3, 5:4, 8:7, 19.5:9, 20:9 and 21:9.
- **Theme transitions**: esdeii slide (default) or esdeii fade.
- Turn on **Display clock** and the system status indicators to fill the
  status bar.

## Media

- The game grid shows **box covers**; games without a cover show their name.
- The top screen shows the **screenshot** (then title screen, then miximage)
  and plays the game **video** after a short delay in the video variants.

## Customising

- System icons are the PNGs in `systems/`, named after the ES-DE system
  (`snes.png`, `n3ds.png` ...). Replace any with your own 320x320 PNG.
  Systems without a file get a coloured tile with their name.
- Colours are at the top of `theme.xml`.
- `layouts/` is generated. To change the layout, edit `tools/make_xml.py`
  and run `python3 tools/make_xml.py .` from the repo root.
  `tools/make_assets.py` regenerates icons, graphics and sounds.

## Credits

Nunito font by Vernon Adams et al., SIL Open Font License
(`assets/fonts/OFL.txt`). Icons, sounds and graphics were made for this
theme. Not affiliated with any console maker.
