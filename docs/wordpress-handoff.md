# WordPress Handoff: SFW Foundation site into Salient theme

Target theme: **Salient** by ThemeNectar (nonprofit demo)
Page builder: **WPBakery** (bundled with Salient)

This document maps every component in the static HTML prototype to what
Salient provides out of the box vs. what needs custom code.

---

## What Salient handles natively (NO custom code)

These are built-in Salient elements or WPBakery rows. Just configure them
in the page builder:

| Our component | Salient equivalent |
|---|---|
| **12-column grid** (`.grid`, `.span-*`) | WPBakery rows + columns (1/2, 1/3, 1/4, etc.) |
| **Hero section** (text left, image right) | Salient "Split Content" or WPBakery 2-column row with parallax/image bg |
| **Buttons** (`.btn`, `.btn--ghost`, `.btn--donate`) | Nectar Button element (solid, outlined, see-through styles) |
| **Stats / counters** (`.stat`) | **Milestone** element (animated number counters with caption) |
| **Cards** (`.card`) | Salient "Fancy Box" or "Post Grid" elements |
| **Team member bios** (about-team page) | **Team Member** element (photo, name, role, bio, social links) |
| **Testimonials / quotes** (`.statement`) | **Testimonial Slider** element |
| **Accordion / toggle** (FAQ sections) | **Toggle** element (expand/collapse panels) |
| **Footer** with columns + newsletter | Salient footer builder + Nectar newsletter widget |
| **Forms** (contact, volunteer signup) | WPForms or Gravity Forms plugin (Salient styled) |
| **Image gallery** | Salient **Gallery** element with lightbox |
| **Video embed** | WPBakery Video Player or Salient Video Lightbox |
| **Section bands** (`.stratum--moss`, `--deep`) | WPBakery row with background color/image |
| **Sticky header** | Salient header builder (built-in sticky option) |
| **Dropdown menus** | WordPress native menus + Salient mega menu |
| **Responsive breakpoints** | Salient is fully responsive by default |
| **Typography / headings** | Salient typography panel in Theme Options |
| **Eyebrow labels** (`.eyebrow`) | Nectar "Badge" or styled span in heading element |
| **Pull quotes** | WPBakery blockquote or Salient "Highlighted Text" |
| **Dated news items** | Salient Blog Post Grid (date, title, excerpt) |
| **Newsletter signup** | Mailchimp for WP or Salient newsletter widget |

**Count: ~20 components, zero custom code.**

---

## Reduced custom code: Salient gets us most of the way

These need minor CSS tweaks or a small shortcode, but Salient does 80% of the work:

### 1. Utility bar (`.utility`)
**Salient has:** Secondary header bar (Header > Secondary Navigation in theme options).
**Custom needed:** Minor CSS to match the dark brown color (`--ground: #231F1D`) and specific link styling. ~10 lines of CSS in the child theme.

### 2. Overlay navigation
**Salient has:** Built-in fullscreen overlay menu (Header > Menu Style > "Slide Out from Right" or "Fullscreen Overlay").
**Custom needed:** Customize the background color to `--moss: #22371F` and add the "Happening now" sidebar column. ~30 lines of CSS + a widget area.

### 3. Filter chips (`.chips`)
**Salient has:** Portfolio/blog filtering with Isotope (built-in category filters).
**Custom needed:** Restyle the filter buttons as oval chips instead of text links. ~20 lines of CSS.

### 4. Filmstrip (horizontal scroll images)
**Salient has:** Horizontal scrolling carousels via the Carousel element.
**Custom needed:** CSS to make it a continuous strip rather than paginated slides. ~15 lines of CSS.

### 5. Plate/figure (`.plate`)
**Salient has:** Image with caption element.
**Custom needed:** Numbered series styling and specific caption formatting. ~15 lines of CSS, or a simple shortcode.

**Count: 5 components, ~90 lines of CSS total in child theme. No PHP.**

---

## Actually needs custom code (build once)

These do not exist in Salient and need to be built. Each one is a
standalone piece: build it, test it, done.

### 6. Pathway diagram (learn page)
**What it is:** 5-column tiered layout showing Foundation Courses flowing into Advanced Programs, with boxes that link to course pages.
**Implementation:** Custom WPBakery element or a shortcode. The CSS is ~40 lines (flexbox tiers). No JS needed.
**Markup:**
```html
<div class="pathway">
  <div class="pathway__tier">
    <a class="pathway__box" href="/course-link/">Foundation Courses</a>
  </div>
  <div class="pathway__tier">
    <a class="pathway__box" href="#">Soil Microscopy</a>
    <a class="pathway__box" href="#">Complete Practicum</a>
    <a class="pathway__box" href="#">BioComplete Compost</a>
  </div>
</div>
```
**CSS:** Already in `site.css` lines 281-286. Copy the `.pathway`, `.pathway__tier`, `.pathway__box` rules into the child theme.

### 7. Pathway grid (learn page)
**What it is:** 8-column horizontally scrolling matrix mapping roles (Designer, Farmer, Consultant, etc.) to their recommended courses.
**Implementation:** Custom shortcode or raw HTML in a WPBakery Text Block. CSS is ~20 lines (CSS Grid).
**Markup:**
```html
<div class="pathway-grid">
  <div class="pathway-grid__inner">
    <div class="pathway-grid__col">
      <span class="pathway-grid__oval">Designer</span>
      <a class="pathway-grid__box" href="#">Permaculture Design</a>
      <a class="pathway-grid__box" href="#">Foundation Courses</a>
    </div>
    <!-- repeat for each role -->
  </div>
</div>
```
**CSS:** `site.css` lines 288-294.

### 8. Role picker (learn page)
**What it is:** Row of oval buttons; clicking one highlights the matching column in the pathway grid.
**Implementation:** ~15 lines of JS (toggle an `aria-pressed` attribute, show/hide grid columns).
**JS:** Already in `site.js`. Search for `role-picker` or `pathway-grid`.

### 9. Microbe gallery (volunteer page)
**What it is:** Circular cutout images of microorganisms with a gentle floating animation.
**Implementation:** CSS-only (the animation is `@keyframes microbeFloat`). ~30 lines of CSS.
**Markup:**
```html
<div class="microbe-gallery">
  <figure class="microbe-gallery__item">
    <img src="microbe-1.png" alt="Amoeba">
    <figcaption>Amoeba</figcaption>
  </figure>
  <!-- repeat -->
</div>
```
**CSS:** `site.css` lines 296-310.

### 10. Calendar timeline (calendar page)
**What it is:** Horizontal year timeline with colored bars showing course/event durations and a "today" marker.
**Implementation:** Custom shortcode with inline CSS variables (`--l` for left position, `--w` for width). ~50 lines of CSS + ~20 lines of JS for the today marker.
**CSS:** Search `site.css` for "calendar" or "timeline" section.

### 11. Root line / scroll-driven SVG (science page)
**What it is:** An SVG root illustration whose stroke draws as the user scrolls down the page.
**Implementation:** ~15 lines of JS (IntersectionObserver sets a `--draw` CSS variable). The SVG is inline.
**JS:** Already in `site.js`. Search for `--draw` or `stroke-dashoffset`.

### 12. Donate widget (donate page)
**What it is:** Monthly/one-time toggle with preset amount buttons ($10, $25, $50, $100, Other).
**Implementation:** ~30 lines of JS for the toggle and amount selection. In production this will connect to a payment processor (Stripe, PayPal, etc.).
**Markup:**
```html
<div class="donate-widget">
  <div class="donate-widget__freq">
    <button class="btn btn--sm" aria-pressed="true">Monthly</button>
    <button class="btn btn--sm btn--ghost" aria-pressed="false">One-time</button>
  </div>
  <div class="donate-widget__amounts">
    <button class="btn btn--ghost">$10</button>
    <button class="btn" aria-pressed="true">$25</button>
    <button class="btn btn--ghost">$50</button>
    <button class="btn btn--ghost">$100</button>
    <button class="btn btn--ghost">Other amount</button>
  </div>
  <button class="btn btn--donate">Donate</button>
</div>
```

**Count: 7 components needing custom code.**

---

## Summary for Alex

| Category | Count | Effort |
|---|---|---|
| Salient handles natively | ~20 | Zero custom code |
| Minor CSS tweaks in child theme | 5 | ~90 lines of CSS total |
| Custom build (one-time) | 7 | ~200 lines CSS + ~80 lines JS total |

**Revised total: 12 items need any custom work at all** (down from the original 17 estimate, because Salient's built-in elements cover stats, team members, testimonials, accordions, galleries, and video natively).

Of those 12, only 7 are truly custom builds. The other 5 are CSS tweaks
to Salient's existing elements.

**All CSS and JS is already written and tested** in the static prototype.
The files to copy from:
- `css/site.css` — search for the class names listed above
- `js/site.js` — search for the function names listed above

The child theme needs:
1. `style.css` — paste the custom component CSS (~290 lines)
2. `functions.php` — register any shortcodes
3. Page templates are not needed; use WPBakery's raw HTML block for the
   7 custom components, or register them as shortcodes for cleaner editing.

---

## Design tokens (paste into child theme style.css)

Copy the `:root` block from `css/site.css` (lines 11-75) into the child
theme. Every color, spacing, and type size is a CSS variable. To change
a brand color site-wide, change one variable.

```css
:root {
  --paper:        #FFFFFF;
  --panel-green:  #E6EADC;
  --panel:        #F4F1EA;
  --scope:        #3C3841;
  --ink:          #333130;
  --soil:         #4F3433;
  --moss:         #22371F;
  --green:        #156826;
  --gold:         #C9A227;
  --ground:       #231F1D;
  /* ... full list in site.css lines 11-75 */
}
```

---

## Fonts

The site uses two self-hosted fonts (no Google Fonts dependency):
- **Display / headings:** `Fraunces` (variable weight)
- **Body / UI:** `Figtree` (variable weight)

Font files are in `fonts/`. Register them in the child theme's `style.css`
with `@font-face` declarations (copy from `site.css` lines ~80-120).
