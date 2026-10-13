# Open House post (Fri Oct 16, 2026)

Instagram post for the Soil Food Web Foundation one-year Open House. 1080x1350.

- `open-house-oct16-1080x1350.png`: the post.
- `build.py`: builds it. Run from the repo root: `python3 social/open-house-2026-10-16/build.py`
- `cutouts/`: background-removed PNGs from SFW's own photos (Costa Rica, Wild Ken Hill, Synergia, team photos) plus three cutouts from the hero-collage-parked branch. `build.py` cleans their edges at render time.
- Photos inside the house (doorway, two round windows) and the compost ground come from `img/new-2026-10/`.
- `open-house-oct16-editable.pptx`: the same post as one editable PowerPoint slide (10 x 12.5 in). Every cut-out is a separate picture and the text is real text boxes (EB Garamond, Montserrat). Rebuild with `node social/open-house-2026-10-16/make-pptx.js` after `build.py`.
- `layers/`, `layout.json`: the separate layers and their positions, written by `build.py`.
- **Version 2** (`open-house-oct16-v2-1080x1350.png`, `open-house-oct16-v2-editable.pptx`): the ground is cut open under the house to show the soil food web (roots, fungal hyphae, earthworm, pebbles, five labelled student micrographs), plus a steaming compost pile with the thermometer and a laptop showing the Living Legacy webinar. Build with `python3 social/open-house-2026-10-16/build_v2.py` then `node social/open-house-2026-10-16/make-pptx.js v2`.
