# Migrating to Salient (Nonprofit demo) with WPBakery Visual Composer

This maps every section in the static site to the Salient/WPBakery element that replaces it, plus instructions for the microscopy video circles, buttons, and interactive components.

Updated 13 September 2026 against Evan's audit. The brief for the rebuild is `salient-rebuild-brief.md`; the photograph list is `image-map-for-salient.md`. Line numbers below refer to the pages on branch `claude/new-session-12x7z2`.

## Audit changes that must carry into WordPress

Every one of these is already on the static pages. Check each against the Salient build before sign-off.

| Where | Now reads | Never |
| :-- | :-- | :-- |
| Utility bar (dark strip above the header) | "The Soil Food Web Foundation 501(c)(3)", with Student login, Subscribe, Donate | "Join a global community..." as the strip text |
| Homepage h1 | "Join a global community of Soil Regenerators" | The tagline as the h1 |
| Homepage lede under the h1 | "Healing soil. Feeding humanity. Restoring the living world." | |
| Learn page h1 | "Partner with nature's intelligence" | "Work with the life in your soil" |
| Every programs button | "Explore our programs" | "See every program and price" |
| Newsletter button and utility link | "Subscribe" | "Subscribe to the newsletter" |
| Anywhere | | "nature's operating system", em dashes, "certified", FC, AP or PDC as acronyms, a percentage without a named source |

Layout points Evan stressed:

- The hero is two columns inside the content width: text on the left, photograph on the right. Never edge to edge.
- The hero photograph is a group photograph from a workshop, people around a compost pile, not a portrait at a microscope. The static build uses `img/w/workshop-group-around-compost-pile.jpg`; the caption is still to come from the Foundation.
- Microscopy is the differentiator. The floating microbe cutouts (`img/uploads/1.png` to `7.png`) sit near the top of Science and on Volunteer, and the Science hero is a microscope image.
- More photographs, less white space: where a section is text-heavy, use Salient's large image cards (`[fancy_box]` or `[nectar_image_with_hotspots]`) with text beside or over the picture.
- The stats row shows all three numbers: 100+ countries, 10,000+ enrolled, 40-year legacy. Each keeps its source line.
- The learning pathway on Learn is an eight-column grid, every column visible at once (horizontal scroll on phones). It is not an accordion and nothing is hidden behind a click.

---

## How to use the exported video assets

The `exports/circular-videos/` folder contains ready-to-upload versions of the three microscopy loops from the homepage:

| File | What it is | How to use in Salient |
| :-- | :-- | :-- |
| `amoeba-square-1.mp4` (316 KB) | Square-cropped loop, amoeba | Upload to Media Library. Use in a **Self-Hosted Video** element or as a **Video BG** on a row |
| `amoeba-square-2.mp4` (246 KB) | Square-cropped loop, lab footage | Same |
| `amoeba-square-3.mp4` (156 KB) | Square-cropped loop, hero footage | Same |
| `amoeba-circular-alpha-1.webm` (551 KB) | Circular with transparent background | Use as a background video or image; the circle is baked in. Browser support: Chrome, Firefox, Edge |
| `amoeba-circular-alpha-2.webm` (375 KB) | Circular with transparent background | Same |
| `amoeba-circular-alpha-3.webm` (260 KB) | Circular with transparent background | Same |
| `amoeba-circle-1.gif` (1.7 MB) | Animated GIF, square crop | Universal fallback. Upload as an image, displays everywhere including email |
| `amoeba-circle-2.gif` (1.2 MB) | Animated GIF, square crop | Same |
| `amoeba-circle-3.gif` (844 KB) | Animated GIF, square crop | Same |
| `amoeba-poster-1.jpg` (24 KB) | Still frame from loop 1 | Use as the poster/placeholder while video loads |
| `amoeba-poster-2.jpg` (24 KB) | Still frame from loop 2 | Same |
| `amoeba-poster-3.jpg` (29 KB) | Still frame from loop 3 | Same |

### Recreating the circular video look in Salient

**Option A: Salient's built-in column video background**
1. Add a `[vc_row]` with three `[vc_column width="1/3"]`
2. On each column, set Background Type to **Self-Hosted Video**, upload the square MP4
3. Add this custom CSS to the column: `border-radius: 50%; overflow: hidden; aspect-ratio: 1;`
4. Below each video circle, add a `[vc_column_text]` with the label

**Option B: Use the alpha-channel WebM**
1. Upload the `.webm` files to Media Library
2. Use `[nectar_video_player_self_hosted]` or a raw HTML element
3. The circle is already baked into the video, no CSS needed
4. Provide the `.gif` or `.jpg` poster as a fallback for Safari (no WebM alpha support)

**Option C: Animated GIF (simplest)**
1. Upload the `.gif` to Media Library
2. Use a regular `[image_with_animation]` element
3. Set border-radius to 50% via custom CSS class
4. Works everywhere, slightly lower quality

---

## Homepage section-by-section mapping

### 0. Utility bar (every page)
**Static:** `.utility` > `.utility__tagline` + `.utility__links`

**Salient:** Header Builder > Secondary Navigation. Left text "The Soil Food Web Foundation 501(c)(3)". Right links: Student login, Subscribe, Donate. Dark background (Deep Loam), small type.

### 1. Hero (lines 218-236 in index.html)
**Static:** `.stratum` > `.wrap` > `.grid` with `.span-5` text (eyebrow, h1, lede, one paragraph, two buttons) and `.span-7` photograph (`.shot`, rounded corners), vertically centred. On a phone the text comes first and the photograph below.

**Salient:**
```
[vc_row type="in_container" equal_height="yes" content_placement="middle"]
  [vc_column width="5/12"]
    [vc_column_text]
      <p class="eyebrow">SOIL FOOD WEB FOUNDATION</p>
      <h1>Join a global community of Soil Regenerators</h1>
      <p class="lede">Healing soil. Feeding humanity. Restoring the living world.</p>
      <p>The ground beneath our farms and forests is alive. Learn, restore, and demonstrate the power of the soil food web on every continent.</p>
    [/vc_column_text]
    [nectar_btn url="community#join" text="Join the community" ...]
    [nectar_btn url="learn" text="Programs" style="see-through" ...]
  [/vc_column]
  [vc_column width="7/12"]
    [image_with_animation image_url="workshop-group-around-compost-pile.jpg" alignment="center" img_link_large="no" border_radius="10px"]
  [/vc_column]
[/vc_row]
```
Do not use `full_width_content` for the photograph: Evan asked that the hero not run edge to edge.

### 2. Photo filmstrip (lines 192-202)
**Static:** `.bleed` > `.filmstrip` (horizontal scroll of 5 images)

**Salient:**
```
[vc_row type="full_width_content"]
  [vc_column]
    [vc_gallery type="image_grid" images="id1,id2,id3,id4,id5"
     img_size="400x267" columns="5" onclick="custom_link"]
  [/vc_column]
[/vc_row]
```
Or use `[nectar_cascading_images]` for the filmstrip scroll effect.

### 3. Stats (lines 243-264)
**Static:** three `.stat` large numbers, each with `.stat__label` and a `.source` line

**Salient:**
```
[vc_row]
  [vc_column width="1/3"]
    [milestone number="100" symbol="+" heading_tag="p"
     text="Countries in our student & practitioner community"]
  [/vc_column]
  [vc_column width="1/3"]
    [milestone number="10000" symbol="+" heading_tag="p"
     text="Individuals enrolled in our programs"]
  [/vc_column]
  [vc_column width="1/3"]
    [milestone number="40" heading_tag="p"
     text="Year legacy of pioneering soil biology research & regenerative practice"]
  [/vc_column]
[/vc_row]
```
All three must be visible on every screen size. Keep the source line under each number as a `[vc_column_text]` in small type.

### 4. Choose your path (lines 266-300)
**Static:** `.doors` > `.door` (3-column linked cards with images). The heading is "Choose your path". Evan flagged the old "three ways in" and "come in the door that is yours" wording as reading like a machine wrote it; do not bring it back.

**Salient:**
```
[vc_row]
  [vc_column width="1/3"]
    [fancy_box image_url="harringtons.jpg" style="default"
     link_url="directory" link_text="Find a trained professional"]
      <h3>Farm with biology</h3>
      <p>Cut back on synthetic inputs...</p>
    [/fancy_box]
  [/vc_column]
  [vc_column width="1/3"]
    [fancy_box ...] ... [/fancy_box]
  [/vc_column]
  [vc_column width="1/3"]
    [fancy_box ...] ... [/fancy_box]
  [/vc_column]
[/vc_row]
```

### 5. Microscopy circles (lines 302-346)
**Static:** `.slides` > `.slide` > `.slide__disc` (CSS circle-masked video)

**Salient:** See "Recreating the circular video look in Salient" above.

### 5b. Floating microbe gallery (science.html and volunteer.html)
**Static:** `.microbe-gallery` > `.microbe-gallery__item` (seven transparent PNG cutouts, `img/uploads/1.png` to `7.png`, each with a caption, drifting up and down on a four-second loop, staggered)

**Salient:**
```
[vc_row]
  [vc_column]
    [vc_column_text]<h2 style="text-align:center">The organisms in your soil</h2>[/vc_column_text]
    [image_with_animation image_url="1.png" animation="Fade In" ...] x7, in a 7-column or flex row
  [/vc_column]
[/vc_row]
```
Add the `.microbe-gallery` rules from site.css (lines 297-310) to the custom CSS so the cutouts float. Microscopy is the differentiator, so this block sits high on Science, directly under the hero.

### 6. Who we are (lines 305-324)
**Static:** `.grid` 7/5 split, text + image

**Salient:**
```
[vc_row]
  [vc_column width="7/12"]
    [vc_column_text] ... [/vc_column_text]
  [/vc_column]
  [vc_column width="5/12"]
    [image_with_animation image_url="hand-wet-dirt-worm.jpg" animation="Fade In"]
  [/vc_column]
[/vc_row]
```

### 7. Four-step approach (lines 326-378)
**Static:** 4x `.step` with numbered figures

**Salient:**
```
[vc_row]
  [vc_column width="1/4"]
    [image_with_animation image_url="soil-sample-close-up-test-tube.jpg"]
    [vc_column_text]
      <span class="fig-n">Fig. 01</span>
      <h3>Observe and assess</h3>
      <p>Put your soil under the microscope...</p>
    [/vc_column_text]
  [/vc_column]
  ... (repeat for each step)
[/vc_row]
```

### 8. Learn cards (lines 381-427)
**Static:** `.cards` > `.card` (5-card grid with images and tags)

**Salient:** Use `[nectar_blog]` styled as cards, or:
```
[vc_row]
  [vc_column width="1/3"]
    [fancy_box image_url="..." style="default" link_url="learn#foundation-courses"]
      <div class="card__kind"><span>Start here</span></div>
      <h3>Foundation Courses</h3>
      <p>The complete introduction...</p>
    [/fancy_box]
  [/vc_column]
  ... (repeat)
[/vc_row]
```

### 9. What's new (lines 429-452)
**Static:** `.rule-list--thumb` with thumbnail + date + title

**Salient:** Use `[nectar_blog]` element with "standard list" layout, or `[recent_posts]`.

### 10. Testimonial (lines 454-464)
**Static:** `.testimonial` blockquote

**Salient:**
```
[testimonial_slider style="default"]
  [testimonial quote="Restoring the Soil Food Web..." 
   name="Dr. David Johnson" title="Research Scientist, NMSU"]
[/testimonial_slider]
```

### 11. Partners (lines 466-480)
**Static:** `.partners` list

**Salient:** `[clients columns="4"]` with partner logos, or a simple `[vc_column_text]` block.

### 12. CTA banner (lines 482-491)
**Static:** `.banner.bleed` with background image + overlay text

**Salient:**
```
[vc_row type="full_width_background" bg_image="erc-rancho-cacachilas-agro.jpg"
 bg_image_position="center center" bg_color_overlay="rgba(0,0,0,0.4)"
 text_color="light"]
  [vc_column]
    [vc_column_text]
      <h2>Be part of the soil-ution</h2>
      <p>Wherever you are...</p>
    [/vc_column_text]
    [nectar_btn url="community#join" text="Join the community"]
    [nectar_btn url="donate" text="Donate" style="see-through"]
  [/vc_column]
[/vc_row]
```

---

## Button styles mapping

| Static site class | Salient equivalent | Notes |
| :-- | :-- | :-- |
| `.btn` (green fill) | `[nectar_btn color="extra-color-1" style="..." size="large"]` | Set extra-color-1 to `#156826` in Salient Options > Color |
| `.btn--ghost` (outline) | `[nectar_btn style="see-through-2" ...]` | |
| `.btn--donate` (gold) | `[nectar_btn color="extra-color-2" ...]` | Set extra-color-2 to `#C9A227` |
| `.btn--outline` | `[nectar_btn style="see-through" ...]` | |

---

## Design tokens to set in Salient Options

Go to **Salient > Options** and set:

| Setting | Value | From token |
| :-- | :-- | :-- |
| Overall Body Font | Source Sans 3 | `--sans` |
| Header Font | Montserrat | `--display` |
| Body Font Color | `#333130` | `--ink` |
| Accent Color | `#156826` | `--green` |
| Extra Color 1 | `#156826` | `--green` (buttons) |
| Extra Color 2 | `#C9A227` | `--gold` (donate) |
| Extra Color 3 | `#3C3841` | `--scope` (dark sections) |
| Header BG Color | `#FFFFFF` | `--paper` |
| Header Font Color | `#333130` | `--ink` |
| Footer BG Color | `#231F1D` | `--ground` |
| Footer Font Color | `#FFFFFF` | `--white` |

---

## Components that need custom CSS in Salient

Some static-site components don't map 1:1 to Salient elements. Add this CSS to **Salient > Custom CSS** (or a child theme):

```css
/* Circular video masks for microscopy loops */
.sfw-video-circle {
  border-radius: 50%;
  overflow: hidden;
  aspect-ratio: 1;
}
.sfw-video-circle video {
  width: 100%; height: 100%; object-fit: cover;
}

/* Eyebrow labels above headings */
.sfw-eyebrow {
  font-family: "Montserrat", sans-serif;
  font-size: 0.8125rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #156826;
  margin-bottom: 0.5rem;
}

/* Figure numbers on the approach steps */
.sfw-fig-n {
  font-family: "EB Garamond", Georgia, serif;
  font-size: 0.875rem;
  font-style: italic;
  color: #6A665C;
  display: block;
  margin-bottom: 0.25rem;
}

/* Source/citation lines */
.sfw-source {
  font-size: 0.8125rem;
  color: #6A665C;
  font-style: italic;
  margin-top: 0.25rem;
}

/* The todo placeholder (production notes visible with ?notes=1) */
.sfw-todo {
  display: none;
  border: 2px dashed #C9A227;
  padding: 1rem;
  background: #FFF8E7;
  font-size: 0.875rem;
}
```

---

## Components to build as custom WPBakery elements (or raw HTML shortcodes)

These components from `site.js` don't have Salient equivalents. Either add them as custom WPBakery elements or use the `[vc_raw_html]` element with the original HTML + enqueue `site.js`:

| Component | Recommendation |
| :-- | :-- |
| **Before/after slider** (`[data-compare]`) | Use Salient's built-in Image Comparison element if available, otherwise raw HTML + site.js |
| **Video theatre with playlist** (`[data-theatre]`) | Raw HTML shortcode + site.js. Too complex for a WPBakery element |
| **Filter chips** (`[data-filter-for]`) | Raw HTML + site.js, or use a taxonomy filter plugin |
| **Learning pathway grid** (`.pathway-grid`, learn.html) | Raw HTML + the `.pathway-grid` rules from site.css. Eight columns, an oval role label over one or two course boxes each, all visible at once and scrolling sideways on phones. CSS only, no script, no accordion. |
| **Overlay menu accordion** | Replace with Salient's built-in Ocm (Off-Canvas Menu) |
| **Scroll-drawn root line** | Raw HTML + site.js (SVG) |

### Enqueuing site.js alongside Salient

In your child theme's `functions.php`:

```php
function sfw_enqueue_custom() {
    wp_enqueue_script('sfw-site', get_stylesheet_directory_uri() . '/assets/js/site.js', [], '1.0', true);
}
add_action('wp_enqueue_scripts', 'sfw_enqueue_custom');
```

The JS hooks on data attributes, not classes or IDs, so it won't conflict with Salient's JS. Both can run side by side.

---

## Header and footer

**Header:** Use Salient's Header Builder (Salient > Header). Recreate:
- Utility bar: enable "Secondary Navigation" in Header options
- Logo: upload `sfwlogo-240.png` (or the final `logo.svg` when it arrives, Decision 16)
- Nav links: About us, Learn, Science, Practice, Community
- Donate button: add as a "Button in Navigation" element, gold color
- Menu button: Salient handles this automatically with its Off-Canvas Menu

**Footer:** Use Salient > Footer options or build with WPBakery in the Footer area:
- 4-column layout matching the current grid (logo+newsletter | Foundation | Learn | Resources | Get involved)
- Legal block below

---

## Fonts

Upload to **Salient > Typography** or add via child theme:

| Font | Weight | Use |
| :-- | :-- | :-- |
| Montserrat (variable) | 400-700 | Headings, nav, buttons, eyebrows |
| Source Sans 3 | 400, 400i, 600 | Body text |
| EB Garamond | 400, 400i, 500, 500i, 600 | Captions, ledes, pull quotes |

Files are in `fonts/` with SIL Open Font License. Upload the `.woff2` files.

---

## What to skip from site.css

Salient provides its own:
- Reset / normalize
- Grid system (uses `[vc_row]` / `[vc_column]`)
- Button styles (use Salient buttons, map colors above)
- Typography base styles
- Header and footer

Keep from site.css (paste into custom CSS or child theme):
- Color tokens (`:root` block) for any custom elements
- `.sfw-*` custom classes listed above
- Any component CSS for elements using `site.js` (compare slider, theatre, filter chips)
