# What the WordPress staging site actually has (new.soilfoodweb.com, crawled 2 October 2026)

This folder exists so that the prototype in this repo and the WordPress build the team is doing from it stop drifting apart. Everything below was read off the staging site itself (689 URLs, every page fetched twice, every link and image checked); nothing is assumed. The raw data is in `docs/staging-export/`: one markdown file per staging page, post, event, team member, video and testimonial, plus JSON and CSV. The full defect list is `docs/staging-export/audit-report.md`.

Use it three ways: to answer open items with what staging already holds (section 3), to send the team one URL list instead of three (section 2), and to make sure the prototype does not copy staging's mistakes while the team copies the prototype's design (sections 4 and 5).

## 1. Where the WordPress build stands

* WordPress 7.1.2, Salient 18.2.1 with a `salient-child` theme, WPBakery 8.7.3, Cloudflare in front. A custom plugin `sfw-programs` renders the programme cards. The child theme ships its own CSS modules: `buttons.css`, `flip-box.css`, `news.css`, `off-canvas.css`, `site-footer.css`, `utility-bar.css`, `programs.css`. Copies are in `docs/staging-export/theme-css/`.
* **The child theme already uses this repo's tokens**: `--sfw-gold #c9a227`, `--sfw-green #156826`, `--sfw-moss #22371f`, `--sfw-soil #4f3433`, `--sfw-footer-ground #231f1d`, Montserrat / Source Sans 3 / EB Garamond, `--sfw-btn-radius 1.9em 0.6em` with the hover flip. The team is building from `css/site.css`. What has not been carried over is in section 4.
* Content types in place: 31 pages, 18 posts, 10 calendar events (`sfw_calendar_event`), 15 programme cards (`sfw_program`), 22 team members (`team_member`), 169 directory members (`directory_member`), 134 publications (`sfw_publication`), 20 videos (`sfw_video`), 5 testimonials (`sfw_testimonial`), 9 timeline entries (`sfw_timeline`). All readable at `/wp-json/wp/v2/<type>`.
* Every page is `noindex, nofollow`, there is no XML sitemap, no analytics or tag manager of any kind, and the viewport tag blocks pinch zoom (`user-scalable=0`). Both of the last two are Salient/WordPress settings, not content.
* Pages that exist on staging but are linked from nowhere: `/team/`, `/sfw-directory/`, `/student-map/`, `/timeline-preview/`, `/programs-carousel-preview/`, `/nonprofit-landing/` (old draft with theme demo text), `/templates/` and `/templates-2/` (Salient demo pages, Lorem ipsum), `/contact-info/` and `/foundation-legal/` (empty).

## 2. One URL list, please: prototype vs approved plan vs staging today

Three URL schemes are in play. This repo's `vercel.json` and `sitemap.xml` use scheme A. The approved list Linnea gave the audit on 2 October is scheme B. Staging has scheme C. Rows marked ⚠ are where the prototype's own redirects send the approved address somewhere else, and rows marked ✗ are approved addresses that exist nowhere yet.

| Content | A: this repo | B: approved final address | C: on staging today | Note |
|---|---|---|---|---|
| Home | / | / | / (page 793 'New Homepage') |  |
| About / mission | /about | /about/ | /about-us/ | staging `/about/` 301s to a **video page** (WordPress guess redirect) ⚠ |
| Team and board | /about/team (`about-team.html`) | (not in plan; `/about/#team`) | /about-us/#team, hidden `/team/` |  |
| Governance | /about/governance | (not in plan) | nothing; footer link is `#` | the page the prototype calls the highest-value addition does not exist on staging |
| Dr. Elaine | /about/elaine | (not in plan; `/about/#dr-elaine`) | /about-us/#dr-elaine, /team-member/dr-elaine-ingham/ |  |
| Contact | /contact | /contact/ | `/contact/` 301s to `/contact-info/` which is **empty**; details live at /about-us/#contact-legal | ✗ no real page |
| Programmes | /learn | /programs/ | /programs-overview/; staging `/programs/` 301s to the hidden `/programs-carousel-preview/` | ⚠ `vercel.json` has no `/programs` route |
| Workshops | /calendar#workshops (vercel 301s `/learn/workshops` → `/calendar`) | /workshops/ | /workshops/ exists but holds only the H1 | ⚠ prototype has no `/workshops` page |
| Webinars | /learn/webinars | (not in plan; external) | header + footer link straight to webinar.soilfoodweb.com |  |
| Scholarships | /learn/scholarships | /scholarships/ | /scholarship/ (singular) + hidden /scholarship-opportunities/ (form) | ✗ `/scholarships/` is 404 on staging; prototype 301s `/scholarship-opportunities` → `/learn/scholarships` |
| Login | /login | /login/ | /login/ |  |
| Science | /science (vercel 301s `/how-it-works` → `/science`) | /how-it-works/ | /how-it-works/ | ⚠ prototype redirects the approved address away |
| Publications | /research (vercel 301s `/publications` → `/research`) | /publications/ | /publications/ (+ 3 `?sfw_pub_collection=` views, 134 entries) | ⚠ prototype redirects the approved address away |
| Case studies / practice | /practice (vercel 301s `/case-studies` → `/practice#case-studies`) | /case-studies/ | /practice/#CASE-STUDIES (title tag says 'Projects') | ✗ `/case-studies/` is 404 on staging |
| Work with us | /practice (form) | /work-with-us/ | /practice/#work-with-us (one paragraph) | ✗ 404 on staging |
| Speaking | (contact form) | /speaking/ | /invite-us-to-speak/ (H1 only) | ✗ 404 on staging |
| Press | (news#foundation) | /press/ | footer 'Media and press' → /contact/ → empty | ✗ 404 on staging |
| Donate | /donate (vercel 301s `/donations` → `/donate`) | /donations/ | /donations/; footer links to `/donate/` which is 404 | ⚠ prototype redirects the approved address to `/donate`; staging footer uses `/donate/` |
| Volunteer | /volunteer | /volunteer/ | /volunteer/ (a near copy of About with broken anchors) |  |
| Calendar | /calendar | /calendar/ | /calendar/ + 10 `/calendar-event/<slug>/` pages |  |
| News | /news, /news/<slug> | /news/ | /news/, posts at `/<slug>/` (no prefix), 12 `/category/<slug>/` archives |  |
| Community | /community | /community/ | /community/ (71 words + map) |  |
| Directory | /community/directory (`directory.html`) | /directory/ | /find-a-professional/ (+ hidden duplicate /sfw-directory/, 169 `/directory-member/<slug>/` pages, login at /directory-portal/) | staging `/directory/` 301s to the **member login** ⚠ |
| App | /community/app (`app.html`) | (not in plan) | nothing |  |
| Privacy / Terms | /privacy, /terms | /privacy/, /terms/ | /privacy/, /terms/ |  |
| Accessibility | /accessibility | (not in plan) | footer links to /accessibility/ which is **404** |  |
| Logo use | (not in prototype) | (not in plan) | /logo-brand-use/ (H1 only) |  |

Two more things on URLs. `sitemap.xml` in this repo lists `https://soilfoodweb.org/…`; the site launches on **soilfoodweb.com**. And staging posts live at the root (`/obituary-for-dr-elaine-ingham/`), not under `/news/`, so the prototype's `/news/<slug>` pattern and the WordPress permalink setting need to agree before any redirect list is written.

## 3. Open items that staging already answers

Cross-checked against `OPEN-ITEMS.md`. 'Staging has it' means it is on the WordPress site today and can be copied; it does not mean it has been approved by anyone.

### 3.1 Staff portraits (OPEN-ITEMS: 'everyone else still needs one')

Staging has a portrait for every team member except where noted. Full-size files are PNGs in `/wp-content/uploads/2026/06/`; several are over 900 KB and Loida Vasquez's is a screenshot file.

| Name | Role on staging | Portrait on staging |
|---|---|---|
| Stephanie McDaniel | Director of Operations | /wp-content/uploads/2026/06/stephanie.png |
| Delvin Solkinson | SFW Permaculture Lead | /wp-content/uploads/2026/06/delvin.png |
| Pranjal Rajput | Technical Innovation Specialist | /wp-content/uploads/2026/06/pranjal.png |
| Elena Kalli | School Administration Officer | /wp-content/uploads/2026/06/elena.jpg |
| Alex Andreou | IT Department | /wp-content/uploads/2026/06/alex.jpg |
| Sammie Bass | Marketing Associate | /wp-content/uploads/2026/06/sammie.jpg |
| Isadora Shmidt | SFW Consultant & Mentor | /wp-content/uploads/2026/06/isadora.png |
| Ayşen Üstünay | SFW Consultant & Mentor | /wp-content/uploads/2026/06/aysen-1024x954.png |
| Brian Daubenspeck | SFW Consultant & Mentor | /wp-content/uploads/2026/06/brian.png |
| Wesley Sander | SFW Consultant & Mentor | /wp-content/uploads/2026/06/wes.png |
| Casey Williams | SFW Consultant & Mentor | /wp-content/uploads/2026/06/casey.png |
| Ib Borup Pedersen | Farmer, SFW Consultant & Mentor | /wp-content/uploads/2026/06/ib-1024x1024.png |
| Nick Padwick | Farmer, SFW Consultant & Mentor | /wp-content/uploads/2026/06/nick.png |
| Dora Tkalec |  | /wp-content/uploads/2026/06/dora.png |
| Gerald Ramírez | SFW Mentor | /wp-content/uploads/2026/06/Gerald-1024x1024.jpg |
| Dr. Carla Ribeiro Machado e Portugal | SFW Mentor | /wp-content/uploads/2026/06/carla.jpg |
| Loida Vasquez | Advanced Programs Lead | /wp-content/uploads/2026/06/Screenshot-2026-06-16-172957.png |
| Jenna Noel | Executive Committee | /wp-content/uploads/2026/06/jenna.png |
| Eric Feiler | Executive Committee | /wp-content/uploads/2026/06/eric.png |
| Leslie W. Lewis, Ph.D. | Executive Committee | /wp-content/uploads/2026/06/leslie.png |
| Dr. Elaine Ingham | Founder | /wp-content/uploads/2026/06/elaine.jpg |
| Evan Buckman | Executive Director | /wp-content/uploads/2026/06/evan.png |

Dora Tkalec has no role text on staging. 'Kavi Reddy' and 'Dr. Adam Cobb' from OPEN-ITEMS are **not** on staging's team at all. The roles on staging still use the 'SFW' acronym everywhere.

### 3.2 Vimeo IDs (brief: 'Confirm Vimeo embed IDs are final')

Staging's 20 video pages embed `https://player.vimeo.com/video/<id>?h=<hash>`. The six science animations on `/how-it-works/` and the homepage film are listed after the table.

| Video | Playlist on staging | Vimeo id | Hash |
|---|---|---|---|
| SFW Consultant Todd Harrington | testimonials | 470279480 | 103139eeb8 |
| SFW Consultant Nick Tomasini | testimonials | 410049306 | 251e4606ca |
| Compost Producers Keisha and Casey | testimonials | 380297602 | 7a71e6701c |
| SFW Consultant Brian Vagg | testimonials | (no id in page) |  |
| About the Soil Food Web | implementing-the-soil-food-web | 466000315 | 2a1509b00f |
| Using the Microscope | implementing-the-soil-food-web | (no id in page) |  |
| Making Compost Extract and Tea | implementing-the-soil-food-web | 525025259 | 11f6b261ce |
| Cory Miller | farmer-case-studies | 812185778 | dd3a45ec17 |
| Jenn Sirp | farmer-case-studies | 812188293 | 6ed8f0fbef |
| Roberto Silva | farmer-case-studies | 790985081 | 92231c295c |
| Adam York | farmer-case-studies | 792733797 | e809b1fad3 |
| 4,000 acres Norfolk, England | consultant-case-studies | 1034550940 | 7f0f78d4e3 |
| 172 Acre Park Project | consultant-case-studies | 498144316 | 5a85131b62 |
| Organic Banana Farm, South Africa | consultant-case-studies | 498143744 | c4ba30014d |
| Alfalfa, Potatoes, & Beans | consultant-case-studies | 538767686 | ca0eecb84e |
| Grapes, Cannabis, Turmeric & more | consultant-case-studies | 537963453 | 11f160622a |
| Corn & Soy: 10,000 Acres | consultant-case-studies | 537972167 | f6a32ff941 |
| Renald Flores | consultant-case-studies | 537966540 | a79eb5d201 |
| Students | meet-the-soil-food-web-family | 534172809 | 3842558f66 |
| Consultants | meet-the-soil-food-web-family | 440097560 | 529443df10 |

Science page (`/how-it-works/`): 372925873 h=707aa77aa3 (the soil food web), 372474782 h=a5ae5edb4a, 372476056 h=fd05a7dc60, 372478833 h=7c10d53c26, 372479571 h=4cced96d80, 372480255 h=7c04397066. Homepage 'Hear from our students' film: 439617042 h=5314d77a00. **Renald Flores is 537966540 with h=a79eb5d201**, which answers the open item that said the id alone would not embed. Brian Vagg (380296081) and Using the Microscope (542881348) are embedded without a hash on staging.

### 3.3 Events on the staging calendar (10)

| Event | Dates on the page | Enrol link |
|---|---|---|
| Accelerator Workshop \| UK | 13 September to 1 October 2027 |  |
| Permaculture Design Certificate \| 2026 Cohort #3 | 5 October to 24 December 2026 | https://school.soilfoodweb.com/courses/permaculture-design-certification |
| Permaculture Design Certificate \| 2027 Cohort #2 | October 4- December 19 | https://school.soilfoodweb.com/courses/permaculture-design-certification |
| Permaculture Design Certificate \| 2027 Cohort #1 | April 19- July 3rd | https://school.soilfoodweb.com/courses/permaculture-design-certification |
| Biological Liquid Amendments Intensive Course | 26 July to 3 September 2027 |  |
| Compost Intensive Course \| 2027 Cohort #2 | 10 May to 23 July 2027 | https://school.soilfoodweb.com/courses/compost-intensive-program |
| Compost Intensive Course \| 2027 Cohort #1 | 18 January to 26 March 2027 | https://school.soilfoodweb.com/courses/compost-intensive-program |
| Accelerator Workshop \| Costa Rica | 18 to 29 January 2027 | https://school.soilfoodweb.com/pages/workshop-interest |
| Accelerator Workshop \| New Mexico USA | 3 to 14 May 2027 | https://school.soilfoodweb.com/pages/workshop-interest |
| Community Event \| Celebrating Our First Year as a Foundation! | 16 October 2026, 3:27 p.m. UTC | https://webinar.soilfoodweb.com/ |

All are future dated. The calendar files the three intensive courses under the event type 'Promotions' and the anniversary event under 'Webinars'; the two 2027 PDC cohorts fall outside the calendar's twelve-month window. Source of truth for dates is still the WordPress `sfw_calendar_event` post, entered by hand; nothing is fed from Thinkific or webinar.soilfoodweb.com.

### 3.4 Facts and wording staging has settled (or not)

| Open item | What staging says |
|---|---|
| Refund rule (Decision 2) | `/terms/` §3: *"Unless a program page states otherwise, you may request a full refund within 30 days of registration provided you have not accessed a substantial portion of the course content. No refunds are available after the applicable refund period."* Donations non-refundable. No programme page repeats it. |
| Contracting entity (Decision 8) | `/privacy/` and `/terms/`: *"The Foundation operates the Soil Food Web School as a doing-business-as (DBA) name."* The homepage and About say *"a program of the Soil Food Web Foundation"*. Both wordings are live at once. |
| Tax status | Footer and `/donations/`: *"a 501(c)(3) nonprofit, gifts are tax-deductible"*. `/terms/` §4: status **pending**, donations via the fiscally sponsored *Soil Food Web Fund*. Not settled. |
| EIN and address | EIN 39-4439236, 5441 S Macadam Ave Ste N, Portland, OR 97239 (About, footer, Terms, Privacy). Same as this repo. |
| Publications count | 134 entries: 86 Dr. Elaine's, 5 internet articles, 43 other. 82 of them link out to a DOI or source. |
| Directory counts (Decision 15) | 169 published members. Page text mentions Lab-Tech on 160 profiles and Consultant on 70, 61 carry both. Country filter on staging: All countries Argentina Australia Austria Belgium Bolivia Brazil Bulgaria Canada Chile Costa Rica Denmark Ecuador Finland France Germany Guinea India Ireland Israel Italy Libya Mexico Netherlands Antilles Netherlands The New Zealand Nigeria Peru Poland Portugal Serbia South Africa Spain Suriname Sweden Switzerland Turkey United Kingdom United States Zambia Bioregion All bioregions Adriatic Sea & C… |
| Statistics | Homepage: 100+ countries, 10,000+ enrolled, and a third figure '40'. Other staging pages say 130 countries and 6,000+ students. Staging gives no source line for any of them. |
| Social accounts | Staging has no social links. The live site's footer has: facebook.com/soilfoodwebschool, instagram.com/soilfoodwebschool, linkedin.com/company/soilfoodwebschool, youtube.com/channel/UCSAU5ludwNyqMHBaR1ZfheQ. |
| Hero photograph | Staging homepage uses `Elaine-Ceremonial-Compost-Group-Photo-scaled-1.jpg` and a 2.4 MB screenshot (`Screenshot-2026-09-29-161820.png`) for the stats block. `/community/` uses `mar-group-photo-2.jpg` and `mar25-group-photo-rotated.jpg`. No captions anywhere. |
| Microbe cutouts | `/how-it-works/` carries attachment pages 6, 7, 8, 9 and the files `2.jpg`, `6.jpg`, `7.jpg`, matching this repo's `img/uploads/2.png`, `6.png`, `7.png`. |
| Dr. Ingham's dates | Team page: PhD Colorado State 1981, first papers 1982, School 2019; the obituary post gives the rest. No birth year on staging. |
| Scholarship review cadence | Still a placeholder on staging too: *"[VERIFY review cadence and criteria with the education team.]"* |
| Impact lines for donation amounts | Still a placeholder on staging too: *"[IMPACT LINES — pair with preset amounts … VERIFY amounts with operations …]"* |
| Scholar stories | Staging has five **invented** testimonials (John Doe, Amara Okafor, David Vance, Marcus Thorne, Yuki Tanaka). This repo's 'the program is growing' framing is the right call; do not import them. |
| Newsletter tool (Decision 14) | Staging footer has an email field and Subscribe button with no form action either. |

## 4. Design: what the child theme did not carry over from `site.css`

| Token / rule | This repo | Staging |
|---|---|---|
| Theme accent | `--green #156826` for links and buttons | Salient's theme-level accent is still **#59a76c** (`--nectar-accent-color`), the colour this repo marks 'decorative only, fails contrast'. It is used 47 times in the generated theme CSS. |
| Extra colours | `--legacy #6B4C7A` (Dr. Elaine only), `--soil #4F3433` | Salient extra-color-1 is **#652e90** (a different purple), extra-color-2 is #4e3432 (one digit off soil), extra-color-3 is the gold |
| Education blue | `--edu #3780B8` | programme cards use `--sfw-programs-accent #2f73a6` |
| Fonts | Montserrat, Source Sans 3, EB Garamond, self-hosted | the same three, served through Cloudflare fonts, **plus Open Sans, Roboto and Poppins** still loaded as Salient defaults (80, 54 and 34 declarations) |
| Body text | `--t1` 16→18 px fluid | 18 px / 32 px line height fixed |
| Container | — | `--container-width 1600px`, padding 90 px |
| Viewport | zoom allowed | `maximum-scale=1, user-scalable=0` (Salient option 'Prevent user scaling'); fails WCAG 1.4.4 |
| Headings | tokens | `/workshops/` and others set `color: #4E3432` inline in WPBakery |
| Images | WebP, 800 px variants, filenames from Drive | 48 body images over 500 KB (largest 4.4 MB), 30 are screenshots used as content, most team portraits are PNG; only 13 of 112 staging body images share a filename with this repo's `img/` |

## 5. Do not copy these from staging

The full list of 68 defects is in `docs/staging-export/audit-report.md`. The ones most likely to leak into a replica because they look like content:

* Footer 'Donate' → `/donate/` (404); the page is `/donations/`.
* 'Donate to support scholarships' → `/donate-get-involved/` (404).
* Foundation Course 1 → `school.soilfoodweb.com/courses/foundation-couse-1` (404 on Thinkific; the real slug is `foundation-course-1`).
* Permaculture Design Certification card → `http://localhost:8080/learn/`.
* 'Start with a free webinar' on the directory page → the paid Complete Practicum bundle.
* 'Join the community' on `/login/` → the programmes page.
* 'Partner on Research' (menu) and 'Governance and financials' (footer) → `#`.
* Five 'Scholar Stories' are invented.
* '[IMPACT LINES …]' and '[VERIFY review cadence …]' editorial notes are public.
* Two student quotes credited to 'Jennifer Ralston · Country' and 'Adam Queen · Country'.
* Privacy effective 16 Oct 2025, Terms effective 16 Oct **2026**.
* Duplicate paragraph on `/how-it-works/` ('Beneficial bacteria produce glues…') and on the obituary.
* 'prerequesites', 'Spoil Sponge Workshop', 'USDA USDA', 'Biocomplete™' vs 'BioComplete™'.
* `/workshops/`, `/invite-us-to-speak/`, `/logo-brand-use/` are heading-only pages that the menus link to.

What staging gets right that this repo should keep in mind: the five-section menu (About us, Learn, Science, Practice, Community) with 'Donate' as the only button; the off-canvas 'Happening now' panel showing two dated items; the footer legal block with EIN and address; the programme cards as a reusable component (`sfw-programs`).

## 6. Files in `docs/staging-export/`

| File | What it is |
|---|---|
| `content/pages/*.md` (31), `content/posts/*.md` (18), `content/events/*.md` (10), `content/team/*.md` (22), `content/videos/*.md` (20), `content/testimonials/*.md` (5) | Every staging page as markdown: title, H1, headings, paragraphs, links and image URLs, in page order. The quickest way to see what the team wrote. |
| `pages.csv` | One row per staging URL (689): status, title, H1, robots, canonical, word count, menu version, inbound links, flags. |
| `team.json`, `events.json`, `videos.json` | The structured data behind sections 3.1 to 3.3. |
| `misc.json` | Programme cards with their Thinkific links, timeline entries, testimonials, directory stats, publication counts, social links, footer and off-canvas text, key page texts. |
| `images.csv` | 112 body images on staging: largest variant size, type, alt text, pages. |
| `theme-css/` | The child theme's CSS modules and Salient's generated dynamic CSS, as served on 2 October 2026. |
| `audit-report.md` | The full audit: defects by Ad Grant impact, cache check, URL plan, site tree, hidden pages, analytics. |
