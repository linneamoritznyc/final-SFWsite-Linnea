# Community assets

Photographs and video clips for the Community page and for community stories.
Drop the real files in here under the exact names below and nothing else has to
change: every page already points at these paths.

Until a file arrives its slot fails gracefully. A missing photograph prints its
alt text in a toned box instead of a broken-image icon, and a missing clip shows
its poster, or its caption if the poster is missing too. Nothing shifts, nothing
breaks, no page errors.

Folders:

    public/assets/community/img/      photographs and video posters
    public/assets/community/video/    video clips

---

## Formats

**Photographs.** JPEG or WebP. Not HEIC, not PNG for a photograph, not TIFF.
Longest edge 1600px, progressive, quality around 80, under 400 KB. sRGB.
Strip GPS from the EXIF before uploading: these are people's farms and homes.

**Video.** Two files per clip, same base name:

- `.mp4`, H.264 (High profile), AAC or no audio track at all, faststart on
- `.webm`, VP9

Every clip is silent on the page (`muted loop playsinline`), so an audio track
only adds weight. Strip it if the original has one.

**Posters.** Every clip needs a poster image with the same base name as the
clip, as `.jpg`, in `img/`. `wild-ken-hill-turning.mp4` pairs with
`wild-ken-hill-turning.jpg`. The poster is what a visitor sees before the clip
loads, and the only thing they see when they have asked their system for
reduced motion. Take it from a representative frame, not from black.

---

## The circle clips

The workshop clips on the Wild Ken Hill story are masked into circles, so the
frame is cropped to a square from the centre and then to a circle inside that.
Shoot or crop accordingly: **keep the subject centred and away from the
corners**, because the corners are cut away.

- Square, 1080 × 1080, is the ideal source. A 1920 × 1080 clip works, it is
  centre-cropped.
- 6 to 12 seconds. They loop, so a clip that ends near where it began loops
  without a visible jump.
- Under 3 MB per file. Four clips autoplay on the page, and a phone on farm
  signal pays for all of them.
- No audio, no on-screen text, no titles or transitions.

---

## Expected filenames

### Wild Ken Hill workshop, June 2026

Photographs, in `img/`:

| File | What it should show |
| :-- | :-- |
| `wild-ken-hill-group.jpg` | The group on the farm. The lead photograph for the story and its share card. Landscape. |
| `wild-ken-hill-pile-build.jpg` | A pile going up by hand, materials still in heaps around it. |
| `wild-ken-hill-recipe-board.jpg` | Recipes, temperatures or the day's charts, written up where the group could read them. |
| `wild-ken-hill-brew-tank.jpg` | Brewing at the larger scale, the tank and the people running it. |
| `wild-ken-hill-field-application.jpg` | A liquid amendment going out in the field. |
| `wild-ken-hill-microscope.jpg` | A mentor at a student's shoulder at the microscope. |

Video clips, in `video/`, with their posters in `img/`:

| Clip | Poster | What it should show |
| :-- | :-- | :-- |
| `wild-ken-hill-turning.mp4` + `.webm` | `wild-ken-hill-turning.jpg` | Turning a pile by hand, forks moving. |
| `wild-ken-hill-temperature.mp4` + `.webm` | `wild-ken-hill-temperature.jpg` | A probe going into a pile and the reading being called out. |
| `wild-ken-hill-extract.mp4` + `.webm` | `wild-ken-hill-extract.jpg` | Extract or tea moving, the brew running. |
| `wild-ken-hill-slide.mp4` + `.webm` | `wild-ken-hill-slide.jpg` | What is on the slide, or the moment of finding it. |

### The community log

These sit beside their posts on `community.html`. The approved mockup pulled
them from `soilfoodweb.com/wp-content/uploads`; they are referenced from this
folder instead so the new site does not depend on the old one staying up. Copy
the originals across rather than hot-linking them, and re-encode to the sizes
above.

| File | What it should show |
| :-- | :-- |
| `living-legacy-webinar.jpg` | Daniel Tyrkiel and Adam Swann presenting in the Living Legacy webinar series. |
| `soil-health-week-karachi-university.jpg` | Nick Padwick teaching soil biology at Karachi University. |
| `soil-health-week-pakistan.jpg` | Soil Health Week 2025 in Pakistan. |
| `costa-rica-liquid-amendments.jpg` | Gerald Ramirez demonstrating liquid amendments in Costa Rica. |
| `costa-rica-microscopes.jpg` | Students and mentors at microscopes in Costa Rica. |

`wild-ken-hill-group.jpg` from the table above is used twice: it leads the
story and it carries the feature block at the top of the Community page.

---

## Checking what is still missing

    python3 tools/imagecheck.py

It lists every file the pages reference that is not yet on disk, this folder
included. The list empties as the uploads land.

---

## Before anything goes up

- **Permission.** Anyone recognisable in a photograph or clip has agreed to it
  being published. Names only where the person said yes to their name.
- **Alt text and captions.** Every slot on the page carries provisional alt
  text written from the story, not from the footage, because the footage was
  not available when the page was built. Once the real files are in, read every
  alt attribute against the picture it now describes and correct it. The page
  marks these with a placeholder note; add `?notes=1` to the page URL to see
  every one of them at once.
- **Dates.** Every story on the site shows its date. The date belongs to the
  event, not to the upload.
