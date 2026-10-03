# WordPress migration guide

This document maps the static HTML site to its WordPress equivalents so the migration
developer knows exactly where to cut. Read `docs/brand-guide.html` for the visual
reference (colors, type, buttons, spacing) and `OPEN-ITEMS.md` for content gaps.

---

## Architecture overview

| Static site | WordPress equivalent |
| :-- | :-- |
| `css/site.css` `:root` tokens | `theme.json` design tokens (colors, spacing, typography) |
| `css/site.css` component classes | Theme stylesheet (`style.css`) |
| `js/site.js` | Enqueued theme script (`assets/js/site.js`) |
| `fonts/` directory | `assets/fonts/` in the theme, loaded via `@font-face` in stylesheet |
| `content/*.json` | ACF field groups or WordPress custom fields |
| `vercel.json` rewrites | WordPress permalink settings (already clean URLs) |
| `vercel.json` redirects | Redirection plugin or `.htaccess` rules |
| `vercel.json` security headers | `.htaccess` or server config |

**Recommendation:** Build a custom block theme (Full Site Editing), not Elementor or Divi.
The existing CSS maps 1:1 to `theme.json` tokens, and `site.js` can be enqueued as-is.
A page builder would fight this design system.

---

## Template parts

Each HTML page uses the same header and footer. These become WordPress template parts.

| HTML section | WP template part | Notes |
| :-- | :-- | :-- |
| `<header class="header">` | `parts/header.html` or `get_template_part('header')` | Includes the logo, nav links, and menu button |
| `<nav id="overlay">` | `parts/overlay-menu.html` | Full-screen overlay menu with accordion sections |
| `<footer class="footer">` | `parts/footer.html` | Newsletter form, legal block, social links |
| SVG icon sprite | Inline in `functions.php` via `wp_body_open` hook | `img/icons.svg` content |

---

## Page-to-template mapping

| HTML file | WordPress template | Content type |
| :-- | :-- | :-- |
| `index.html` | `front-page.php` or Front Page block template | Page |
| `learn.html` | Custom page template `page-learn.php` | Page |
| `science.html` | Custom page template `page-science.php` | Page |
| `about.html` | Page template (default) | Page |
| `about-governance.html` | Page template (child of About) | Page |
| `about-team.html` | Custom page template `page-team.php` | Page, with team member CPT query |
| `about-elaine.html` | Page template (child of About) | Page |
| `practice.html` | Custom page template with case study CPT query | Page |
| `community.html` | Custom page template | Page |
| `calendar.html` | Custom page template with event CPT query | Page |
| `research.html` | Custom page template with publication CPT query | Page |
| `donate.html` | Page template | Page |
| `contact.html` | Page template | Page |
| `volunteer.html` | Custom page template | Page |
| `directory.html` | Custom page template with directory CPT query | Page |
| `news.html` | Archive template (`archive.php`) | Posts |
| `news/wild-ken-hill-2026.html` | Single post (`single.php`) | Post |
| `projects/market-garden-sweden.html` | Single CPT (`single-case_study.php`) | Case study CPT |
| `privacy.html` | Page template | Page |
| `terms.html` | Page template | Page |
| `accessibility.html` | Page template | Page |

---

## Custom post types (CPT)

| CPT | Source in static site | Fields |
| :-- | :-- | :-- |
| `team_member` | Cards in `about-team.html` | Name, title, bio, portrait, order |
| `case_study` | Cards in `practice.html`, pages in `projects/` | Title, body, before/after photos, Vimeo ID, hash, location |
| `publication` | List in `research.html`, data in `content/research.json` | Title, authors, journal, year, DOI, collection |
| `event` | Rows in `calendar.html`, data in `content/calendar.json` | Title, dates, location, link, type (workshop/webinar) |

---

## Block patterns

Reusable HTML sections that become WordPress block patterns.

| Pattern name | Where it appears | Key classes |
| :-- | :-- | :-- |
| Hero band | Top of most pages | `.band`, `.hero` |
| Card grid | Learn, community, about-team | `.cards`, `.card` |
| Testimonial | Index, learn | `.quote` |
| Before/after comparison | Practice page | `[data-compare]` |
| Video facade | Practice, science | `[data-film]` |
| Pathway diagram | Learn page | `[data-pathway]` |
| Filter chips | Research, community, volunteer | `[data-filter-for]`, `.chips` |
| Accordion | Learn, overlay menu | `[data-accordion]` |
| Photo ledger | Multiple pages | `.ledger` |
| Step list | Learn-scholarships, volunteer | `.step` |

---

## Interactive components — how each one works

Every interactive feature on this site is driven by `js/site.js` (982 lines, vanilla JS,
zero dependencies). **Enqueue it as-is in the WordPress theme.** Do not replace these
with plugins — they handle accessibility (keyboard, focus, reduced-motion) correctly and
load nothing until needed.

Each component below shows the exact HTML structure the JS expects, the CSS classes that
style it, and the data attributes that wire it up. WordPress templates must output this
same markup for the JS to work.

### 1. Microscopy video loops (homepage amoeba circles)

Three circular video clips of brightfield microscopy that auto-play when scrolled into
view and pause when scrolled out. Reduced-motion users see the poster image only.

**Pages:** `index.html`

**Where the files live:**
- Video: `video/sfw-amoeba-loop-square.mp4/.webm`, `video/sfw-amoeba-lab-640.mp4/.webm`, `video/sfw-amoeba-loop-hero.mp4/.webm`
- Poster: `img/w/sfw-amoeba-still-square.jpg`
- In WP theme: copy to `assets/video/` and `assets/img/` respectively

**HTML structure the JS expects:**

```html
<ul class="slides">
  <li>
    <a class="slide" href="science.html">
      <span class="slide__disc">
        <video data-loop data-start="0.0" muted loop playsinline preload="none"
               poster="assets/img/sfw-amoeba-still-square.jpg"
               data-src="assets/video/sfw-amoeba-loop-square.webm,assets/video/sfw-amoeba-loop-square.mp4">
        </video>
      </span>
      <span class="slide__n">How the soil food web works</span>
    </a>
  </li>
</ul>
```

**How it works:**
- The **circle** is CSS: `.slide__disc` has `border-radius: 50%; overflow: hidden; aspect-ratio: 1`. The video files are square — the circle is a mask, not baked in.
- The **lazy loading** is JS: `data-src` holds the source URLs (comma-separated webm,mp4). JS injects `<source>` elements when the element is ~200px from viewport (IntersectionObserver).
- The **start time** is `data-start` — sets `currentTime` on load so each disc shows a different moment.
- Some discs use inline `style="transform: scale(1.6) translate(0%, 0%)"` to zoom/pan within the circle.
- `data-loaded` flag prevents re-initialization.

**CSS classes:** `.slides` (3-column grid at 44em+), `.slide` (block link), `.slide__disc` (circle mask), `.slide__n` (label below), `.slide__go` (arrow)

**JS section:** 8 ("Microscopy loops")

**To replicate in WP:** Output this exact markup from a custom block or ACF flexible content field. The video files go in the theme (not Media Library — they're decorative, not content). The JS handles everything else automatically.

---

### 2. Video facades for Vimeo

A poster image with a play button. Nothing from Vimeo loads until the visitor clicks.
On click, the poster is replaced with a Vimeo iframe.

**Pages:** `practice.html`, `projects/market-garden-sweden.html`, `science.html`

**HTML structure:**

```html
<figure class="film">
  <button data-film="https://player.vimeo.com/video/VIDEO_ID?h=PRIVACY_HASH&dnt=1&title=0&byline=0&portrait=0"
          aria-label="Play: Video Title" type="button">
    <img src="poster.jpg" alt="" loading="lazy">
  </button>
  <figcaption><b>Title</b> <span>Subtitle</span></figcaption>
</figure>
```

**How it works:**
- On click: creates an `<iframe>` with `src = data-film + "&autoplay=1"`, replaces the button, focuses the iframe.
- The `h=PRIVACY_HASH` in the URL is required for unlisted Vimeo videos.
- The Vimeo Player API script (`player.vimeo.com/api/player.js`) is loaded on demand only when the video theatre needs it — simple facades don't need the SDK at all.

**CSS classes:** `.film` (wrapper), `.film iframe` (16:9 aspect ratio)

**JS section:** 12 ("Films from the field")

**To replicate in WP:** An ACF field group with Vimeo ID, privacy hash, poster image, and title. Template outputs the markup above. Do not use WordPress oEmbed — it loads Vimeo on every page view.

---

### 3. Video theatre with playlist

A single persistent Vimeo player with a scrollable playlist. First click boots the
Vimeo Player SDK. Subsequent videos use `player.loadVideo()`. Includes an 8-second
countdown to the next video and a "still watching?" check after 3 unattended plays.

**Pages:** `practice.html`

**HTML structure:**

```html
<div class="theatre" data-theatre>
  <div class="theatre__stage">
    <div class="theatre__frame" data-frame hidden></div>
    <button class="theatre__poster" data-poster>
      <img src="poster.jpg" alt="">
      <span class="theatre__go">▶</span>
    </button>
    <div class="theatre__panel" data-next hidden>
      <p>Up next: <b data-next-title></b></p>
      <p>Starting in <span data-next-count>8</span></p>
      <button data-next-go>Play now</button>
      <button data-next-cancel>Cancel</button>
    </div>
    <div class="theatre__panel" data-check hidden>
      <p>Are you still watching?</p>
      <button data-check-go>Continue</button>
    </div>
  </div>
  <p class="theatre__now" data-live aria-live="polite">
    <span data-now-title></span><span data-now-sub></span>
  </p>
  <ul class="theatre__list">
    <li data-active="true">
      <button class="theatre__item" type="button" data-i="0" aria-current="true">
        <span class="theatre__thumb"><img src="thumb.jpg" alt=""></span>
        <span class="theatre__t">Video Title</span>
        <span class="theatre__s">Subtitle</span>
      </button>
    </li>
  </ul>
  <script type="application/json" data-theatre-data>
    [{"id":"123456","hash":"abc123","slug":"video-slug","title":"Title","sub":"Subtitle"}]
  </script>
</div>
```

**How it works:**
- Video metadata lives in the `<script type="application/json">` block — Vimeo IDs, privacy hashes, slugs, titles.
- First play loads the Vimeo SDK from `player.vimeo.com/api/player.js`, creates a `Vimeo.Player` in `data-frame`.
- Subsequent plays call `player.loadVideo()` — no iframe recreation.
- URL syncs with `pushState(?v=slug)` so direct links work.
- Constants: `COUNTDOWN = 8` seconds, `STREAK_LIMIT = 3` unattended plays before "still watching?".
- If SDK fails to load, falls back to a plain iframe.

**CSS classes:** `.theatre__stage` (16:9 aspect ratio), `.theatre__list` (horizontal scroll at narrow, 4-col grid at 62em+), `li[data-active="true"]` (highlight)

**JS section:** 11

**To replicate in WP:** ACF repeater field for the playlist (Vimeo ID, hash, slug, title, subtitle, thumbnail). Template outputs the markup + JSON block above. The JS handles all player logic.

---

### 4. Before/after image comparison slider

Two photographs stacked with a draggable divider. Keyboard-accessible via native
`<input type="range">`.

**Pages:** `volunteer.html`

**HTML structure:**

```html
<figure class="compare" data-compare>
  <div class="compare__frame">
    <img src="before.jpg" alt="Description of before state">
    <span class="compare__tag compare__tag--a">Year one</span>
    <div class="compare__after">
      <img src="after.jpg" alt="Description of after state">
    </div>
    <span class="compare__tag compare__tag--b">Year three</span>
    <span class="compare__line" aria-hidden="true"></span>
    <input class="compare__range" type="range" min="0" max="100" value="50" step="1"
           aria-label="Compare before and after">
  </div>
  <figcaption>Caption</figcaption>
</figure>
```

**How it works:**
- The range input is stretched over the entire image (transparent, full overlay).
- JS listens for `input` and `change` events, sets `--split` on the figure.
- CSS clips `.compare__after` with `clip-path: inset(0 0 0 var(--split))`.

**JS section:** 15

**To replicate in WP:** ACF field group with before image, after image, before label, after label. Template outputs the markup. Do not use a slider plugin.

---

### 5. Filter chips

Radio-style buttons that show/hide items in a list. Supports multiple independent
filter groups on the same list and multi-value attributes.

**Pages:** `volunteer.html`, `directory.html`, `community.html`, `news.html`, `calendar.html`

**HTML structure:**

```html
<ul class="chips" data-filter-for="#list-id" data-filter-attr="data-kind"
    aria-label="Filter by role">
  <li><button class="chip" type="button" data-filter="all"
              aria-pressed="true">All</button></li>
  <li><button class="chip" type="button" data-filter="grower"
              aria-pressed="false">Growers</button></li>
</ul>

<ul id="list-id">
  <li data-kind="grower">...</li>
  <li data-kind="researcher">...</li>
  <li data-filter-empty hidden>No results. Try a different filter.</li>
</ul>
```

**How it works:**
- `data-filter-for` is a CSS selector pointing to the target list.
- `data-filter-attr` names the attribute to match (defaults to `data-kind`).
- Items can have space-separated values: `data-kind="grower researcher"` matches either filter.
- `data-filter="all"` shows everything.
- `[data-filter-empty]` is revealed when no items match.
- `aria-pressed` toggles for screen readers.

**JS section:** 4

**To replicate in WP:** For static content, hardcode the chips. For CPT content (directory, calendar), generate chips from a taxonomy and output `data-kind` on each post's `<li>`. The JS handles filtering client-side — no AJAX needed for small lists.

---

### 6. Overlay menu and accordion

Full-viewport deep-green overlay nav with focus trapping and animated accordion sections.

**Pages:** Every page

**How it works:**
- `[data-menu-open]` button opens `#overlay` (sets `data-open="true"`, adds `is-locked` to body for scroll lock).
- `[data-menu-close]` or Escape closes it. Link clicks inside also close.
- Focus is trapped inside the overlay with Tab/Shift+Tab.
- Accordion: `[data-acc-btn]` toggles `data-open` and `aria-expanded` on `[data-acc-item]`. Only one section open at a time.
- Panel height animates via `grid-template-rows: 0fr` → `1fr`.

**JS sections:** 1 (overlay), 2 (accordion)

**To replicate in WP:** Register two WordPress menus (primary and utility). The overlay template part outputs the accordion markup. `wp_nav_menu()` can output the link lists inside each accordion panel. The JS hooks via data attributes, not IDs, so it works regardless of how WP generates the markup — as long as the data attributes are present.

---

### 7. Scroll-triggered reveal animations

Elements below the fold fade up into view on scroll. Fires once per element.
Completely skipped under `prefers-reduced-motion`.

**Pages:** Every page with matching selectors

**How it works:**
- JS finds elements matching: `.shot, .slides > li, .ledger > li, .doors > li, .cards > .card, .step, .banner, .filmstrip, .scope, .plate`
- Elements whose top is below the viewport get class `.rise` (opacity 0, translateY 18px).
- IntersectionObserver swaps `.rise` → `.rise-in` when the element enters (one-shot, then unobserved).
- Elements already in viewport at load time are left alone — no flash.
- Elements inside `[data-still]` are excluded.

**JS section:** 10

**To replicate in WP:** Automatic — if the template outputs elements with these classes, the JS handles it.

---

### 8. Pathway diagram (learn page)

Interactive program map: buttons for each course, info panels that open on hover/focus/click.

**Pages:** `learn.html` (not yet built into the page; CSS and JS are ready)

**HTML structure:**

```html
<div data-pathway>
  <button data-pathway-btn aria-controls="panel-id"
          aria-expanded="false">Course name</button>
  <div id="panel-id" hidden>
    <dl class="card__meta">...</dl>
    <p>Description</p>
  </div>
</div>
```

**JS section:** 5

---

### 9. Other interactive components

| Component | Hook | Where | What it does |
| :-- | :-- | :-- | :-- |
| Scroll-drawn root line | `[data-root-line]` | SVG on science page | SVG path drawn by scroll position via `--draw` CSS property |
| Calendar today marker | `[data-cal]` | `calendar.html` | Positions a dot at today's date between `data-cal-start` and `data-cal-end` |
| Toggle chips | `[data-chips]` | `volunteer.html` | Multi-select chips that show/hide panels via `data-reveals` |
| Background video loop | `[data-loopbg]` | `volunteer.html` | Silent decorative clip behind text, with auto-generated WCAG pause button |
| Reel clips | `[data-clip]` | `news/wild-ken-hill-2026.html` | Short silent clips cut to circles, auto-play on scroll |
| Scroll-scrubbed rack | `[data-scrub]` | Motion studies | Video playhead driven by scroll position |
| Production notes | `?notes=1` URL param | Every page | Reveals `.todo` blocks and `[data-empty]` slots for content review |

---

## CSS token mapping to theme.json

The `:root` tokens in `site.css` map directly to `theme.json` settings:

```
--paper         #FAFAF3  → settings.color.palette[slug: "paper"]
--panel         #F2EFE6  → settings.color.palette[slug: "panel"]
--panel-green   #E8F0E4  → settings.color.palette[slug: "panel-green"]
--scope         #3A6B35  → settings.color.palette[slug: "scope"]   (primary green)
--membrane      #D4E8D0  → settings.color.palette[slug: "membrane"]
--living        #F5F9F3  → settings.color.palette[slug: "living"]
--glow          #F5F9F3  → settings.color.palette[slug: "glow"]
--legacy        #8B4513  → settings.color.palette[slug: "legacy"]
--ink           #23291F  → settings.color.palette[slug: "ink"]
--ink-soft      #4B5244  → settings.color.palette[slug: "ink-soft"]
--ink-faint     #7A8070  → settings.color.palette[slug: "ink-faint"]
--soil          #6B4E37  → settings.color.palette[slug: "soil"]
--moss          #2D5A27  → settings.color.palette[slug: "moss"]
--olive         #7A8C3C  → settings.color.palette[slug: "olive"]
--gold          #C49B2A  → settings.color.palette[slug: "gold"]

--display       Montserrat      → settings.typography.fontFamilies[slug: "display"]
--text-serif    EB Garamond     → settings.typography.fontFamilies[slug: "serif"]
--sans          Source Sans 3   → settings.typography.fontFamilies[slug: "sans"]

--s1 through --s7              → settings.spacing.spacingSizes
--t1 through --t6 (fluid clamp) → custom font sizes
```

---

## Assets

### Images
Copy `img/` contents into the WordPress Media Library. **Do not rename files** — they
match the Foundation's Google Drive. WebP variants are in `img/w/` with `-800` suffixes
for responsive sizes.

### Videos

| File | What it is | Where it goes in WP |
| :-- | :-- | :-- |
| `video/sfw-amoeba-loop-square.mp4/.webm` | Square microscopy loop (homepage circles) | `assets/video/` in theme |
| `video/sfw-amoeba-loop-hero.mp4/.webm` | Wide microscopy loop (hero backgrounds) | `assets/video/` in theme |
| `video/sfw-amoeba-lab-640.mp4/.webm` | Reduced-size lab footage | `assets/video/` in theme |
| `video/sfw-amoeba-lab-512.mp4/.webm` | Smaller lab footage | `assets/video/` in theme |
| `video/sfw-amoeba-instagram-4x5.mp4/.webm` | 4:5 ratio (social) | `assets/video/` in theme |

These are **decorative background videos**, not content. They go in the theme directory,
not the Media Library. The JS lazy-loads them (nothing downloads until scroll). The
circular crop is pure CSS (`border-radius: 50%` on `.slide__disc`).

### Vimeo embeds
Case study and science videos are on Vimeo, embedded via the facade pattern (component 2
above). The site never self-hosts these — only poster thumbnails are in `img/video/`.

### Fonts
Move `fonts/*.woff2` into `assets/fonts/` in the theme. All three families (Montserrat,
EB Garamond, Source Sans 3) are SIL Open Font License. Register them in `theme.json`
under `settings.typography.fontFamilies`.

### SVG icon sprite
`img/icons.svg` contains all icons. Inline it via the `wp_body_open` hook in
`functions.php`. Icons are referenced as `<svg><use href="#icon-name"></svg>` throughout
the templates.

---

## JavaScript

`js/site.js` is 982 lines of vanilla JS with zero dependencies. **Enqueue it as-is.**

```php
// functions.php
function sfw_enqueue_scripts() {
    wp_enqueue_script('sfw-site', get_theme_file_uri('assets/js/site.js'), [], '1.0', true);
}
add_action('wp_enqueue_scripts', 'sfw_enqueue_scripts');
```

The only external script it loads is the Vimeo Player API (`player.vimeo.com/api/player.js`),
and only on demand when a visitor plays a video in the theatre. Make sure the CSP allows
`script-src https://player.vimeo.com`.

The JS hooks onto data attributes (`data-loop`, `data-film`, `data-theatre`, etc.), not
IDs or generated classes. As long as the WordPress templates output the same data
attributes shown in the component docs above, everything works.

### Accessibility handled by site.js
- `prefers-reduced-motion`: all animations skipped, video loops show poster only
- Focus trapping in the overlay menu
- `aria-expanded`, `aria-pressed`, `aria-current` managed on all interactive elements
- Keyboard navigation: Escape closes overlay/panels, Tab moves through focusable elements
- `aria-live` regions for dynamic content (theatre "now playing")

Do not add a separate accessibility plugin for these behaviors — they are already handled.

---

## Redirects

`vercel.json` contains 30+ permanent redirects from old WordPress URLs. Replicate via the
Redirection plugin or `.htaccess`. The full list is in `vercel.json` under `"redirects"`.

Key redirects:

| Old URL | New URL |
| :-- | :-- |
| `/publications`, `/publications/*` | `/research` |
| `/how-it-works` | `/science` |
| `/projects`, `/our-work`, `/our-impact` | `/practice` |
| `/blog`, `/blog/*` | `/news` |
| `/events`, `/now` | `/calendar` |
| `/sfw-courses-overview`, `/foundation-courses-2`, `/course/*` | `/learn` |
| `/certified-listing-directory`, `/consultants`, `/laboratory-technicians` | `/community/directory` |
| `/contact-us` | `/contact` |
| `/donations` | `/donate` |

---

## Security headers

Currently in `vercel.json`. Replicate in `.htaccess` or server config:

```
Content-Security-Policy: default-src 'self';
  script-src 'self' 'unsafe-inline' https://player.vimeo.com;
  frame-src https://player.vimeo.com https://vimeo.com;
  img-src 'self' https://i.vimeocdn.com data:;
  style-src 'self' 'unsafe-inline';
  font-src 'self';
  connect-src 'self' https://fresnel.vimeocdn.com;
  base-uri 'self';
  form-action 'self' mailto:;
  frame-ancestors 'self'
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

Note: WordPress needs `'unsafe-inline'` for scripts too (Gutenberg injects inline JS).
The CSP above includes it. Consider splitting front-end and admin CSP rules.

---

## Content data

The `content/*.json` files hold structured data for initial content import:

| JSON file | WordPress equivalent |
| :-- | :-- |
| `content/videos.json` | ACF repeater field on the Practice page, or a video CPT |
| `content/calendar.json` | Event CPT entries |
| `content/research.json` | Publication CPT entries |
| `content/learn.json` | ACF field group on the Learn page |
| `content/global.json` | Theme options (ACF options page) or `theme.json` |

---

## Suggested plugins (minimal)

| Need | Plugin | Why |
| :-- | :-- | :-- |
| Custom fields | ACF Pro | All CPT fields, repeaters, options pages |
| Redirects | Redirection (or `.htaccess`) | 30+ legacy URL redirects |
| SEO | Yoast or Rank Math | Meta tags, sitemaps |
| Forms | WPForms Lite or Gravity Forms | Contact form, volunteer form |
| Newsletter | Mailchimp for WP (or provider-specific) | Footer subscribe form |

Do not add plugins for: accordions, sliders, video embeds, image comparison, filtering,
or animations. All of these are handled by `site.js`.

---

## What to keep from this repo during migration

1. All CSS class names and design tokens — the design system is done
2. The JS in `site.js` — it works and handles accessibility correctly
3. The `OPEN-ITEMS.md` tracker — outstanding content gaps carry over
4. The image filenames — they match the Google Drive
5. The redirect list in `vercel.json`
6. The `content/*.json` data files for initial content import
7. The `docs/brand-guide.html` for visual reference
