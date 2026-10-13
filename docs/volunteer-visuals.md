# Volunteer page, visual system

Prepared 11 September 2026 for `/volunteer`. Twelve visuals, where each one goes, what to make,
and who makes it. Every slot listed here is **already built and wired on the page**: until the real
asset exists the slot holds a toned block carrying its own brief on `data-empty`. Add `?notes=1`
to `volunteer.html` to see every brief in place.

Nothing in this document names a person, a place, a farm, a date or a figure that has not been
supplied. Where a caption needs one, the row says so.

---

## 1. The production list

Status values: **built, waiting** the slot exists and needs the asset · **not started** no slot and
no asset yet · **stand-in in place** something from the Foundation's own library is holding the
space and is labelled as a stand-in.

| # | Visual | Where it goes | What to film or photograph | Format and size | Who could make it | Status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | **Microscope loops** | Behind the green "Start in the next ten minutes" band (`.loopbg`) | Slow loops of protozoa, fungal hyphae and nematodes moving. Brightfield, 400x. No cuts, no zoom, nothing on screen but the organisms | MP4 (h.264) **and** WebM, 1280 wide, 15 to 25 s, silent, **under 3 MB each**. Plus one JPEG poster frame at 1600 wide | Staff microscopy, or a trained volunteer filming down their own eyepiece (this is role "Share your microscope") | **Stand-in in place.** The Foundation's own amoeba reel (`video/sfw-amoeba-lab-640.*`, 600 KB) is running there now. It is the right register; it is one clip rather than three |
| 2 | **Real roots in the ladder** | Down the left edge of the four soil layers, in the numeral column | A whole root system washed clean and laid on a flatbed scanner, cut out to transparency. Fine roots matter more than the tap root | PNG with alpha, about 900 × 6000, long and narrow to run the full four layers. Under 400 KB after compression | A volunteer with a flatbed scanner and a plant; `tools/cutout.py` is already in the repo for the cut-out | **Built, waiting.** A drawn hairline root is in the slot now (`.root-line`, scroll-drawn, still under reduced motion) |
| 3 | **Soil core texture** | The four bands of the ladder (`.layer--1` to `.layer--4`) | One soil core photographed from the side against a neutral card, whole, with a scale beside it. Then one crop per horizon | Four JPEGs, 1600 wide, seamless enough to tile vertically. One master of the whole core at 2400 for the archive | Staff or a soil scientist with a corer; any volunteer collecting field data could take it | **Built, waiting.** Flat colours read off a real profile are in place |
| 4 | **Hands from everywhere** | The five-cell hero collage, and the three portrait slots beside the quotes | A volunteer's own hands holding soil from their own land, shot from directly above, daylight, no flash. The place is written underneath, in their words | JPEG, 1600 on the long edge, 4:3 and 1:1 crops both useful. Needs the place, the date, and written permission from the person | Volunteers themselves. A phone is enough; this is the point of it | **Stand-in in place** in the hero (five photographs from `img/`, labelled as stand-ins). **Built, waiting** beside the quotes |
| 5 | **Hello in every language** | The "Translate the science" role, and the volunteer quotes band | Sixty seconds. Each volunteer says one sentence about soil in their own language, straight to camera, one after another | MP4 and WebM, 1920 × 1080, burnt-in subtitles **and** a separate WebVTT track. Under 20 MB; this one is a foreground video with a facade, not a background loop | Volunteers record themselves; staff or a volunteer editor cuts it together | **Not started.** No slot yet: it needs a home on the page first |
| 6 | **Compost time-lapse** | The "Host a compost day" role card, and the first YouTube Short tile | One pile over 30 days. Thermometer and a written date visible in every frame. Fixed camera, same position, once or twice a day | Source frames at 4000 wide. Deliver a 9:16 MP4 under 30 s for the Short, and a 16:9 version. One poster JPEG | A volunteer hosting a compost day, with a phone on a stake and a tripod mount | **Built, waiting** (Short tile). The card itself takes visual 8 |
| 7 | **Field to microscope zoom** | Hero, as the first collage cell or as a full-width video above it | One continuous move: drone over the field, down to a person, to the hand, to the clump of soil, to the microscope view. The cut to the eyepiece is the only cut | MP4 and WebM, 1920 × 1080, 20 to 40 s, silent. Poster JPEG at 2400. Under 3 MB if it becomes a background loop, otherwise a facade with a play button | Staff with a drone operator, on a workshop day, alongside visual 6 | **Not started.** The hero collage holds the space |
| 8 | **Objects on the role cards** | One per role card, above the heading, twelve in all | Real objects photographed flat on plain paper, lit evenly, then cut out: microscope slide, pitchfork, clipboard with a data sheet, camera, event table cloth, notebook, and so on | PNG with alpha, 800 × 800, under 120 KB each. A `.slot` goes above each `.card__title` | Staff, one afternoon with a sheet of paper and a window. `tools/cutout.py` does the cut-out | **Built, waiting.** Hairline engraved icons from the site's own sprite are in place and are a real design, not a placeholder; the photographs would replace them |
| 9 | **Before and after slider** | The "Watch the network at work" band (`.compare`) | The same field in year one and year three. Same camera position, marked so it can be repeated, same season, same time of day | Two JPEGs, identical dimensions, 2000 wide. **Both dates, the place and the grower's name are required** or the pair does not go up | A grower with a marked post and a phone. Staff to gather the permission | **Built, waiting.** The slider is built, keyboard-operable and wired |
| 10 | **Field notebook scans** | Beside "What collecting data looks like" in the roles band | Real handwritten notes and completed data sheets. Not recreated, not tidied | Flatbed scan, 300 dpi, JPEG at 2000 on the long edge. The volunteer's name removed unless they want it shown | Field-data volunteers post or scan their sheets | **Built, waiting** |
| 11 | **"Show us your soil" wall** | The Instagram panel (`.wall`), six squares | Photographs growers tag. Chosen by hand, not pulled by a widget: a feed widget is a third-party script on every page load and it cannot ask permission | JPEG, 1080 × 1080, under 150 KB each. Each square links to its post | Community, gathered by whoever runs the account. **Written permission from each poster before it appears** | **Built, waiting** |
| 12 | **Cut-out moss and fungi** | Two margins: beside the statement, and beside the network band. Never more than two in view | Real moss, lichen or a mushroom on a flatbed scanner, cut out to transparency | PNG with alpha, 1200 on the long edge, under 200 KB | Anyone with a scanner and a walk outside | **Built, waiting.** The repo's own `img/cutout-placeholder.svg` is in both slots |

---

## 2. The components these drop into

Four reusable components were built for this page. All four live in `css/site.css` section 21 and
`js/site.js` jobs 13 to 15, and all four are on `/volunteer` now with marked placeholders in them.

### `.loopbg`, a muted looping background video
```html
<section class="stratum stratum--moss loopbg">
  <div class="loopbg__media" data-loopbg>
    <img src="img/w/poster.jpg" alt="" loading="lazy" decoding="async">
    <video data-src="video/clip.webm,video/clip.mp4" poster="img/w/poster.jpg"
           muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video>
  </div>
  <div class="wrap"> ... </div>
</section>
```
- Nothing downloads until the band is within 200px of the viewport (`data-src`, not `src`).
- The clip pauses the moment the band leaves the viewport.
- **Under `prefers-reduced-motion: reduce` the `<video>` element is removed from the document**, so
  nothing is fetched and nothing can start. The poster is what the reader sees.
- A pause button is written in by script, beside the clip, only where a clip is actually playing.
  Motion that starts on its own and runs more than five seconds needs a control (WCAG 2.2.2).
- Keep the file under 3 MB. The clip in place is 600 KB.

### `.compare`, before and after with a caption line
```html
<figure class="compare" data-compare>
  <div class="compare__frame">
    <img src="before.jpg" alt="...">
    <span class="compare__tag compare__tag--a">Year one</span>
    <div class="compare__after"><img src="after.jpg" alt="..."></div>
    <span class="compare__tag compare__tag--b">Year three</span>
    <span class="compare__line" aria-hidden="true"></span>
    <label class="visually-hidden" for="ba-1">Drag to compare year one and year three</label>
    <input class="compare__range" id="ba-1" type="range" min="0" max="100" value="50">
  </div>
  <figcaption>Grower, place, both dates.</figcaption>
</figure>
```
The handle is a real `<input type="range">`, not a draggable div: it is reachable by keyboard, it
announces its value, and pointer dragging is what a range already does. With no script the "after"
photograph is simply shown whole.

### `.wall`, the photo grid
Squares, 2px apart, nothing between them. Each cell may wrap in a link to its post. No captions:
the accumulation is the point and anything set between the squares breaks it up.

### `.cut`, a cut-out in the margin
Absolutely positioned at the band's own edge, `aria-hidden`, purely decorative, and hidden entirely
below 62em where there is no margin to put it in. Never more than two in view.

### Rules that apply to all four
- Every `<img>` and every `<video>` is `loading="lazy"` / `preload="none"`.
- Every photograph carries real alt text. Decorative cut-outs carry `alt=""` and `aria-hidden`.
- Background clips stay under 3 MB. Posters are served from `img/w/` derivatives, never `img/`.

---

## 3. Public domain stand-ins

**Nothing was fetched.** This session's network policy denies outbound connections to every one of
the four sources: `commons.wikimedia.org`, `www.nrcs.usda.gov` and `archive.org` were each tried and
each returned `403` at the egress proxy (only package registries are reachable). No files are in the
repository from any of them, and none are referenced by the page.

No stand-in file, author or licence is recorded below, because recording one without having fetched
and checked the file would be inventing a citation. The table is laid out and empty on purpose.

The Foundation decided on 5 October 2026 not to use openly licensed stand-ins (USDA NRCS and similar) on the site.

### Where to look, and what the licence means before you take anything

| Source | What is there | Licence position | What to check per file |
| :-- | :-- | :-- | :-- |
| **USDA NRCS Soil Biology Primer** | Bacteria, fungi, protozoa and nematode micrographs; soil profile diagrams. Chapters 1 to 5 were written by Dr. Elaine Ingham for the NRCS Soil Quality Institute, and are already cited on `research.html` | Works of US federal employees made in the course of their duties carry no copyright in the US (17 U.S.C. §105) | A federal page can still carry third-party material under its own terms. Confirm the individual image is a federal work and not a contributed one, and keep the page URL |
| **Wikimedia Commons** | Soil micrographs, root systems, soil profiles, compost, lichen and moss | Per file. CC0, CC BY, CC BY-SA and public domain all appear side by side | Open the file page. Record the exact licence, the author's own preferred credit, and the file URL. CC BY-SA means the page it appears on may inherit obligations: prefer CC0 or public domain for anything composited |
| **Biodiversity Heritage Library** | Scanned botanical and mycological plates, root drawings, soil fauna engravings | Per item; many pre-1929 works are public domain, some items are contributed under a licence | Read the rights statement on the item, not the collection. Keep the OCLC or item id |
| **Internet Archive** | Agricultural film, USDA reels, extension bulletins | Per item, and often unstated | If the item does not state a licence or a public domain status plainly, skip it |

**Standing rule: skip anything unclear.** A visual with an uncertain licence on a nonprofit's site is
a liability, and an empty labelled slot is honest. That is why the slots are built the way they are.

### Stand-ins actually in place today
Two, both from the Foundation's own library, both labelled as stand-ins in the page source:

| Where | What is standing in | Why it is allowed |
| :-- | :-- | :-- |
| Hero collage, five cells | `ctpfw-student-moving-compost-1`, `fungal-spores-in-suspension`, `gloved-hands-red-bucket-mulch`, `erc-panchamana-treeplanting-2-…`, `hand-of-compost` | The Foundation's own photographs, already published across this site. Each carries real alt text describing only what is visible, and a `.cap--todo` caption waiting for place, people and date |
| Background of the ten-minute band | `video/sfw-amoeba-lab-640.mp4` / `.webm` | The Foundation's own brightfield microscopy, already used on `index.html` |

---

## 4. What still needs real filming or photography

In the order they would most improve the page:

1. **Visual 4, hands from everywhere.** The hero is standing in with library photographs, none of
   which shows a volunteer volunteering. This is the page's subject.
2. **Visual 9, before and after.** The slider is built and empty. One grower, two photographs, two
   dates and a name.
3. **Visual 1, microscope loops.** One clip is standing in where three were asked for.
4. **Visual 2 and visual 3, the root scan and the soil core.** The ladder is drawn, not photographed.
5. **Visual 8, the twelve objects.** The engraved icons hold up on their own, so this is a want.
6. **Visual 10, notebook scans**, and **visual 11, the Instagram wall.** Both need permission from
   the people whose work they are, which is the slow part, not the photography.
7. **Visual 12, moss and lichen cut-outs.** The repo's placeholder polygon is in both margins.
8. **Visual 5, hello in every language**, and **visual 7, the field to microscope zoom.** Neither has
   a slot yet. Both are shoots rather than pickups, so they need a date in the calendar first.

Also outstanding, and not photography: **every caption on this page.** Every `.cap--todo` on
`/volunteer` needs the place, the people and the date from the Foundation, exactly as the other
fourteen pages do. A caption naming a real place and real people is a claim, so none is invented here.
