# Rebuilding the trifold

Print only. Nothing in this folder is served by the website, linked from it, or built by
`tools/build.py`, and nothing here touches `css/site.css`.

```
pip3 install segno pillow                      # once
python3 "Trifold Design/build/make-qr.py"      # writes build/qr/*.svg
node    "Trifold Design/build/render.js"       # writes the two PNGs
```

Both commands run from the repository root. `render.js` prints an overflow figure for each of the
six panels; anything other than `0` means text is running past a panel edge and the panel needs
trimming before the PNG is usable.

- `outside.html` is panels 1, 2, 3. `inside.html` is panels 4, 5, 6.
- `trifold.css` holds the geometry. `--pad` is the safe margin, `--bleed` the bleed.
  Colour tokens and `@font-face` rules are copied from `css/site.css` sections 1 and 2; if those
  change on the site, change them here too.
- The first and last panel on each sheet carry `panel--first` / `panel--last`. Those classes add the
  bleed to the panel's width and padding, which is what lets a photograph run past the trim. Move the
  classes if the panel order changes.
- `render.js` serves the repository over a local http port rather than opening the files directly,
  because Chromium will not load `@font-face` files across a `file://` origin.

Read `../NOTES.md` before changing any copy. Several facts on these panels are deliberately unprinted.
