# Motion exports as GIF

Every moving thing on the live site, exported as a looping GIF for use off the web
(slides, email, social, print reference). Made from the source videos in `video/` and
from Playwright captures of the live pages.

37 files, about 84 MB.

## From the site's own video loops

| File | Source | Size | Where it appears |
|---|---|---|---|
| `amoeba-loop-square.gif` | `video/sfw-amoeba-loop-square` | 360x360, 10s | Home slideshow, first slide |
| `amoeba-lab.gif` | `video/sfw-amoeba-lab-640` | 400x225, 10s | Home slideshow, learn, volunteer |
| `amoeba-loop-hero.gif` | `video/sfw-amoeba-loop-hero` | 400x225, 10s | Home slideshow, third slide |
| `amoeba-social-square.gif` | `video/sfw-amoeba-instagram-4x5` | 360x360, 10s | Not on a page. Caption card cropped off, full frame kept. |
| `amoeba-social-4x5.gif` | `video/sfw-amoeba-instagram-4x5` | 320x400, 10s | Not on a page. Same clip at 4:5, side cropped so no caption. |
| `wkh-clip-1465.gif` | `video/wild-ken-hill/IMG_1465` | 260x461, 8s | Wild Ken Hill workshop |
| `wkh-clip-1467.gif` | `video/wild-ken-hill/IMG_1467` | 260x461, 8s | Wild Ken Hill workshop |
| `wkh-clip-1471.gif` | `video/wild-ken-hill/IMG_1471` | 260x461, 7s | Wild Ken Hill workshop |
| `wkh-reel-excerpt.gif` | `video/wild-ken-hill/wkh-2026-reel-web` | 260x461, 8s | First 8s only. The full reel is 41s, too long for a usable GIF. |

## Circular, on white

Cut to a circle with a white surround. The amoeba set is 400x400, the field set
360x360, both at 10fps.

| File | Source |
|---|---|
| `amoeba-circle-square.gif` | `video/sfw-amoeba-loop-square` |
| `amoeba-circle-lab.gif` | `video/sfw-amoeba-lab-640`, centre cropped to square first |
| `amoeba-circle-hero.gif` | `video/sfw-amoeba-loop-hero`, centre cropped to square first |
| `amoeba-circle-social.gif` | `video/sfw-amoeba-instagram-4x5`, caption card cropped off first |
| `wkh-circle-1465.gif` | `video/wild-ken-hill/IMG_1465`, centre cropped to square first |
| `wkh-circle-1467.gif` | `video/wild-ken-hill/IMG_1467`, centre cropped to square first |
| `wkh-circle-1471.gif` | `video/wild-ken-hill/IMG_1471`, centre cropped to square first |
| `wkh-circle-reel.gif` | `video/wild-ken-hill/wkh-2026-reel-web`, first 8s, centre cropped |
| `teas-circle.gif` | `video/sfw-teas-square`, the compost tea clip |

These are larger than the rectangular versions, 2 to 6 MB, and the reason is worth
knowing before anyone tries to shrink them. Three things each cost the white surround
its purity, and all three had to go:

1. **An alpha mask.** Building the circle by compositing through a mask PNG left the
   surround at about 226,226,226, a faint ghost of the footage, because the mask's
   black came back in limited range so "transparent" was never quite zero. The circle
   is now painted directly with `geq`: inside the radius keep the pixel, outside write
   255. No alpha anywhere.
2. **Dithering.** Any dither stipples a flat area. `dither=none` for all eight.
3. **`gifsicle --lossy`.** It shifts pixels against their neighbours, which pulls a
   flat white field off white. Dropped entirely for these.

One more, specific to the amoeba set: `palettegen=stats_mode=diff` builds its palette
from frame to frame differences, and the static white surround never registers as a
difference, so pure white never made it into the palette and the nearest neighbour was
used instead. `stats_mode=full` fixes it and is why these files are bigger.

Check a rebuild by measuring, not by looking. Sample the top left corner and require
exactly 255,255,255. The leak is invisible on the pale microscopy footage and obvious
on the field clips, so eyeballing one clip proves nothing about the others.

Note that `exports/circular-videos/amoeba-circle-1..3.gif`, which predate all of this,
are not circular at all despite the name. They are plain 400x400 squares.

## Supplied separately

| File | Source | Note |
|---|---|---|
| `teas7.gif` | `Teas7.mov`, supplied by Linnea | 400x224, 3.9s, full landscape frame. |

The `.mov` master is not in the repo. The square crop of it is, as
`video/sfw-teas-square.mp4` and `.webm`, so `teas-circle.gif` can be rebuilt but
`teas7.gif` cannot.

## Captured from the live pages

Two kinds sit in this list, and the frame count tells them apart. A **transition**
animates over roughly 320ms and has ten or more frames. A **state swap** changes
instantly because the property involved does not animate, so it has three or four
frames and reads as a flick between two states rather than a movement.

| File | What it shows | Kind |
|---|---|---|
| `btn-primary-hover.gif` | `.btn` rest to hover: green to moss, 1px lift, corner radius morph | transition |
| `btn-ghost-hover.gif` | `.btn--ghost`: outline fills green | transition |
| `btn-donate-hover.gif` | `.btn--donate`: gold to deeper gold | transition |
| `card-hover.gif` | `.card` lifts 2px, its image scales to 1.03 | transition |
| `entry-hover.gif` | `.entry` row lifts 2px, title underline sweeps in | transition |
| `slide-hover.gif` | Home slideshow panel: arrow slides right, label underlines | transition |
| `door-hover.gif` | `.door` image gains saturation, scales to 1.03, arrow slides | transition |
| `steps-hover.gif` | `.steps` item lifts, its step number takes the accent colour | transition |
| `chip-hover.gif` | `.chip` border and label take the accent colour | transition |
| `nowlist-hover.gif` | Happening now link underlines | transition |
| `theatre-item-hover.gif` | `.theatre__item` thumbnail brightens and saturates | transition |
| `theatre-poster-hover.gif` | `.theatre__poster` image fades up, play control morphs to a blob radius | transition |
| `microbe-hover.gif` | Single microbe cutout, hover scale to 1.1 | transition |
| `microbe-float.gif` | All seven microbes, one full 4s `microbeFloat` cycle with the stagger | loop |
| `overlay-menu.gif` | The full screen menu opening and closing | state swap |
| `menu-btn-hover.gif` | `.menu-btn` inverts to solid ink | state swap |
| `acc-btn-hover.gif` | Menu accordion row, name underlines | state swap |

`microbe-float.gif` is captured with the gallery forced onto one row. On the live page
at 1440 it wraps to five items and then two, which leaves a lopsided block with a hole
in it. The single row is the usable asset; it is not what the page looks like.

## Not exported, and why

- `wordmark:hover` turns the wordmark green, but at desktop width the part that changes
  is not visible in the logo's own box, so the capture came out with nothing moving.
- `grow`, `marq`, `sfwdrift`, `sfwfield`, `pgdrift`, `pgbreathe` and `scoperack` are
  defined in `css/site.css` but no page currently uses them. They look like leftovers
  from the `_dev/` mockups. Worth a look on the next cleanup pass.
- `fadeUp` is used only by `.role-picker__courses.is-visible`, which no current page
  builds.
- The first `.chip` on community.html is already in its active green state, so hovering
  it changes nothing. `chip-hover.gif` uses the second chip, which does change.

## A note on baked in text

`video/sfw-amoeba-instagram-4x5.mp4` is the only source with text burned into the
picture: a white caption card reading "What lives in one drop?" over the bottom 270px.
The video area above it is a clean 1080x1080. Both GIFs made from it crop that card
away. Every other source in `video/` is clean footage with no text.

## How these were made, and the settings that matter

ffmpeg with a generated palette, then `gifsicle -O3`. Settings differ by footage type,
and getting this wrong is visible:

- **Live action (the Wild Ken Hill clips): a per frame palette, no dithering**
  (`palettegen=stats_mode=single` with `paletteuse=new=1:dither=none`). These were first
  encoded at 64 colours with heavy Bayer dither and `--lossy=110` to hold them under
  3 MB. That was wrong twice over: skin tones shifted from pink to sandy beige because
  the palette was taken over by the sand and concrete, and the dithering laid a visible
  stipple over faces. A palette recomputed for each frame, with no dithering at all, is
  indistinguishable from the source. It costs about 7 MB a clip, which is the honest
  price of correct colour on this footage.
- **Microscopy (the amoeba loops): 64 colours, Bayer dither, `--lossy=110`.** Checked
  against source and fine. That footage is close to monochrome grey and olive, so a
  small palette costs nothing visible.
- **Interface captures: 96 to 128 colours, no dithering**, so the flat brand colours
  stay flat rather than being stippled.

There is no checked in script. If you regenerate any of these, compare a frame against
the source before trusting the result, and check the frame count: a hover GIF that
collapses to one frame means the hover never fired during capture.
