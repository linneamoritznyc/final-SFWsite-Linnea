# Soil Food Web Foundation — Website

A static HTML website for the Soil Food Web Foundation. No framework, no build step,
no dependencies. Open any `.html` file in a browser.

**Stack:** HTML, one stylesheet (`css/site.css`), one script (`js/site.js`), self-hosted fonts.

**Deploy:** Configured for Vercel (`vercel.json`). The `outputDirectory` is the repo root.

---

## Quick start

1. Clone the repo.
2. Run `python3 -m http.server 8000` and open `http://localhost:8000`.
3. For the design system reference, open `_dev/design-system.html`.

---

## Repository structure

```
├── index.html                  # Homepage
├── learn.html                  # Programs and pathway diagram
├── science.html                # Science explainer with Vimeo animations
├── about.html                  # About the Foundation
├── about-governance.html       # Governance and transparency
├── about-team.html             # Team bios
├── about-elaine.html           # Dr. Elaine Ingham's biography
├── practice.html               # Case studies and fieldwork
├── community.html              # Community page
├── calendar.html               # Workshops and events
├── research.html               # Publications and research
├── donate.html                 # Donation page
├── contact.html                # Contact form
├── volunteer.html              # Volunteer program
├── directory.html              # Consultant and lab tech directory
├── learn-scholarships.html     # Scholarship program
├── learn-webinars.html         # Webinar series
├── login.html                  # Platform login routing
├── news.html                   # News index
├── privacy.html                # Privacy policy
├── terms.html                  # Terms of service
├── accessibility.html          # Accessibility statement
│
├── css/
│   └── site.css                # Single stylesheet; tokens in :root
│
├── js/
│   └── site.js                 # Single script; vanilla JS, no dependencies
│
├── img/                        # All images (filenames match Google Drive)
│   ├── icons.svg               # Inline SVG icon sprite
│   ├── video/                  # Video poster thumbnails (still images, not video files)
│   └── w/                      # Responsive variants (full + 800px width)
│
├── video/                      # Amoeba animation clips (mp4 + webm pairs)
│
├── fonts/                      # EB Garamond, Source Sans 3, Montserrat (WOFF2 + licences)
│
├── content/                    # Structured page data (JSON)
│   ├── home.json
│   ├── learn.json
│   ├── videos.json             # Vimeo IDs and privacy hashes
│   └── ...
│
├── cal/                        # Calendar files (.ics)
│
├── news/                       # Individual news stories
│   └── wild-ken-hill-2026.html
│
├── projects/                   # Individual case study pages
│   └── market-garden-sweden.html
│
├── public/
│   └── assets/community/       # Community page assets (photos and clips to be added)
│       ├── img/
│       └── video/
│
├── docs/                       # Project documentation and briefs (not deployed)
│   ├── copy-deck-v2.md         # All site copy
│   ├── sfw-website-audit-verbatim.md  # Evan's feedback and spec
│   ├── link-map.md             # Internal and external link inventory
│   └── ...
│
├── tools/                      # Build and QA utilities (Python)
│   ├── build.py                # Injects partials (icons, header, footer)
│   ├── crawl.py                # Old WordPress site scraper (reference)
│   ├── csscheck.py             # Unused CSS class detector
│   ├── imagecheck.py           # Missing image audit
│   ├── linkcheck.py            # Broken link scanner
│   ├── images.py               # Responsive image generator
│   └── ...
│
├── _dev/                       # Internal reference pages (not deployed)
│   ├── design-system.html      # Visual component catalogue
│   └── motion.html             # Animation studies
│
├── _archive/                   # Historical material
│   └── lovable/                # Early Lovable prototyping mockups
│
├── vercel.json                 # Deployment config: rewrites, redirects, security headers
├── CLAUDE.md                   # AI assistant instructions for this repo
└── OPEN-ITEMS.md               # Placeholder tracking: what is still needed and from whom
```

---

## Design decisions

- **No framework.** The site is 20 pages of content. Static HTML is the right tool:
  fastest possible load, zero JavaScript required for content, fully accessible without JS.
- **One CSS file, one JS file.** Design tokens live in `:root` custom properties at the
  top of `site.css`. The JS handles progressive enhancements only (menu, accordion,
  scroll animation, video facades). Everything works without it.
- **Self-hosted fonts.** EB Garamond (serif), Source Sans 3 (sans), Montserrat (accent).
  All SIL Open Font License. No external font service requests.
- **Video facades.** Vimeo videos load nothing until a visitor presses play. The platform
  script (`player.vimeo.com`) is the only external dependency and is loaded on demand.
- **Image filenames match Google Drive.** All image filenames are preserved exactly as they
  appear in the Foundation's Google Drive. Do not rename them.

---

## Security

- **Content Security Policy** locks scripts to `self` and `player.vimeo.com`.
- **HSTS** with a two-year max-age and preload.
- **X-Frame-Options** prevents clickjacking.
- **Permissions-Policy** disables camera, microphone, geolocation, and payment APIs.
- **No cookies, no analytics, no tracking.** The `dnt=1` flag is set on every Vimeo embed.
- **No user input processed server-side.** Forms use `mailto:` links; no backend.

---

## Placeholders

Content still needed from the Foundation team is tracked in `OPEN-ITEMS.md`. On any page,
add `?notes=1` to the URL to reveal all placeholder slots (they are hidden from visitors
by default).

---

## WordPress migration

This site is designed for a future migration to WordPress. See
`docs/wordpress-migration-guide.md` for the mapping between HTML sections and WordPress
template parts, block patterns, and custom post types.

---

## Fonts and licences

| Font | Licence | File |
| :-- | :-- | :-- |
| EB Garamond | SIL Open Font License 1.1 | `fonts/LICENSE-eb-garamond.txt` |
| Source Sans 3 | SIL Open Font License 1.1 | `fonts/LICENSE-source-sans-3.txt` |
| Montserrat | SIL Open Font License 1.1 | `fonts/LICENSE-montserrat.txt` |
