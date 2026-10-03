# Site structure, Soil Food Web Foundation

Companion to the design prompt. This document defines every page, its URL, its sections in order, and which of the three audiences it serves. Build all of it.

Audience codes used below: **F** farmer or grower, **S** prospective or current student, **G** grant-giver, funder or institutional partner.

---

## 1. Global elements

### 1.1 Header, persistent on every page

| Element | Behaviour |
| :-- | :-- |
| Wordmark, left | Two lines: "Soil Food Web Foundation" and beneath it, smaller, "A 501(c)(3) nonprofit". Links home. |
| What's happening | Text link to /now |
| Student login | Text link to /login |
| Donate | Filled button to /donate. Never hidden in a menu, never removed on mobile. |
| Menu | Button, top right, opens the overlay navigation |

On mobile the three text links collapse into the overlay. Donate stays visible.

### 1.2 Overlay navigation

Full viewport, floods to deep green. Opens from the Menu button, closes on the close button, on Escape, and on any link click. Focus moves into the panel on open and returns to the trigger on close. Body scroll locks while open.

Left column: six sections as an accordion. Each closed row shows the section name at large size and a one-line descriptor at small size, right-aligned. Opening one closes the others.

Right column: "Happening now", three dated items, then a link to /now.

A cut-out moss form grows across one corner of the overlay.

| Section | Descriptor | Children |
| :-- | :-- | :-- |
| About us | Who we are and how we're governed | Mission, vision and story · Our team and board · Governance and financials · Dr. Elaine Ingham · Contact |
| Learn | Courses, workshops and free resources | All programmes and what they cost · In-person workshops · Free webinars · Scholarships · Student login |
| Science | How the soil food web works | The six mechanisms · Publications · Dr. Elaine's research |
| Projects | Where this is being done, by whom | All case studies · Field trials · Ecoregion hubs |
| Community | Find people, or join them | Find a professional · Community map · Join the community · Volunteer |

Note: "Now" is reached from the header, not the overlay accordion, because it is a destination rather than a category.

### 1.3 Footer, every page

Four columns plus a newsletter block.

- **Column 1**: wordmark, the line "Healing soil. Feeding humanity. Restoring the living world.", newsletter field with a single email input and a subscribe button
- **Foundation**: About us · Team and board · Governance and financials · Contact
- **Learn**: All programmes · Workshops · Free webinars · Scholarships
- **Get involved**: Donate · Volunteer · Find a professional · What's happening

Legal block beneath, on every page without exception:

> Soil Food Web Foundation is a 501(c)(3) nonprofit organisation, EIN 39-4439236, registered at 5441 S Macadam Ave Ste N, Portland, Oregon 97239. The Soil Food Web School is a programme of the Soil Food Web Foundation. Our Form 990 and financial statements are available on the governance page and on request.

Then: © 2026 Soil Food Web Foundation · Privacy · Terms · Accessibility

---

## 2. Sitemap

```
/                           Homepage
/about                      Mission, vision and story
/about/team                 Team and board
/about/governance           Governance and financials
/about/elaine               Dr. Elaine Ingham
/contact                    Contact and legal
/learn                      All programmes and costs
/learn/workshops            In-person workshops
/learn/webinars             Free webinars
/learn/scholarships         Scholarships
/login                      Student login chooser
/science                    How the soil food web works
/science/publications       Publications
/projects                   All case studies, filterable
/projects/[slug]            Individual case study
/community                  Community and map
/community/directory        Find a professional
/now                        Dated index of current activity
/donate                     Donate and get involved
/privacy                    Privacy policy
/terms                      Terms
/accessibility              Accessibility statement
```

Twenty-one templates. Nothing sits more than two clicks from the homepage.

---

## 3. Homepage, `/`

Serves **F, S and G** simultaneously. This is the only page that must serve all three at once, and it does so by giving each a distinct route out.

| # | Section | Contents | Serves |
| :-- | :-- | :-- | :-- |
| 1 | Hero | Heading, body paragraph, two actions: "Start learning" to /learn and "See the evidence" to /projects. One large photograph, hands holding living soil with roots and fungal strands visible. Page is visually sparse here. | all |
| 2 | Statistics | Three figures, each with its source printed beneath in small type. Not animated. | G |
| 3 | A nonprofit, and a school inside it | Two-column. Left: heading and two paragraphs, link to /about. Right: four pillars, Teaching, Research, Practice, Community, each a heading and two lines. | G |
| 4 | What it looks like on real land | Three named case studies as cards. Each names a person, a place, a scale. Link to /projects. | F |
| 5 | Start where you are | Three programme rows with visible prices, including a free option first. Link to /learn. | S |
| 6 | What's happening now | Three dated rows, mixed types. Link to /now. | all |

Texture accumulation runs across the whole page: almost none at section 1, heaviest at sections 5 and 6.

---

## 4. About us

### 4.1 `/about`, mission, vision and story. Serves G.

1. Page heading and introduction
2. Mission and vision, side by side, in the organisation's ratified wording
3. Timeline, "How we got here", with a vertical rule and dated entries: 1981 doctorate, 1985 the foundational paper with its journal citation, 1986 to 2002 Oregon State University, 1996 Soil Foodweb Inc., 2019 the School, October 2025 the Foundation, February 2026 her death and the work continuing
4. Links to team, governance and Dr. Elaine's research

Timeline rule: facts only, every date traceable. No narrative flourishes.

### 4.2 `/about/team`. Serves G.

1. Heading and one line of introduction
2. Staff and instructors, photo grid, name and role
3. Board of directors, separate grid, name and role, with a line explaining that a 501(c)(3) is governed by a board
4. Note where the roster is still to be confirmed

### 4.3 `/about/governance`. Serves G. **This page does not exist on the current site and is the highest-value addition in the build.**

Two columns.

Left: legal status, in full, with EIN and registered address. A statement that the School is a programme of the Foundation and that course fees fund charitable programmes. Then a list of public documents: Form 990, IRS determination letter, annual report, financial statements.

Right: where donations go. Conflict of interest, whistleblower and document retention policies. How to reach the board.

### 4.4 `/about/elaine`. Serves G and S.

Two columns, biography and portrait. Her publication record in numbers. The line about her role shifting from authority to origin. Link to /science/publications.

---

## 5. Learn

### 5.1 `/learn`, all programmes and costs. Serves S, and F deciding whether to train.

1. Heading and introduction
2. A single table of every programme, in order of commitment. Each row: name, format and duration, one paragraph, price. The free webinar is the first row.
   - Free webinars, free
   - Foundation Courses, four courses, price
   - Soil Microscopy, advanced, price
   - Compost Production, advanced, price
   - Liquid Amendments, advanced, price
   - Field Trial, advanced, mentored, price
   - Permaculture Design Certification, cohort, next date, price
   - In-person workshops, periodic, price
3. Total path cost note, the full Consultant pathway stated in one figure
4. Two actions: apply for a scholarship, start with a free webinar

No programme card anywhere on the site shows a price without also linking here.

### 5.2 `/learn/workshops`. Serves S and F.

Three groups in this order: **Confirmed** with dates and registration. **Being planned**, with an interest-list signup and a line explaining that dates are announced as soon as they are fixed. **Previously**, past workshops with photographs.

The past group is not an archive afterthought. It is proof the organisation does this regularly.

### 5.3 `/learn/webinars`. Serves S and F.

Next live session as a prominent card with a registration action, then recent recordings as an index. Free is stated plainly.

### 5.4 `/learn/scholarships`. Serves S, F and G.

Two columns. Left: who is prioritised, what is covered, application action. Right: fund a place, linking to /donate, plus recipient stories when permissions allow.

### 5.5 `/login`. Serves S.

Two large panels, one per learning platform, each listing which programmes it hosts. A help line beneath for anyone unsure.

---

## 6. Science

### 6.1 `/science`, how the soil food web works. Serves F, S and G.

1. Heading and introduction
2. Six mechanisms as rows, each a short heading and a paragraph: the web itself, nutrient cycling, building structure, suppressing weeds, protecting plants, storing carbon
3. Each mechanism may carry an explainer animation or microscopy image
4. Closing note on claims discipline
5. Two actions: see it on real land, read the research

This is the only page where motion is permitted beyond the menu, and only where it explains a mechanism.

### 6.2 `/science/publications`. Serves G.

Dense index, no pagination. Each entry: title, journal or publisher, year, one plain-language line, link to DOI or source. Grouped by type: journal papers, book chapters, technical reports. A note explaining that every entry has been verified against its source and that corrections are welcome.

---

## 7. Projects

### 7.1 `/projects`. Serves F primarily, G secondarily.

1. Heading and introduction on claims discipline
2. Filter chips: All, Farmer case studies, Consultant case studies, Field trials, Ecoregion hubs
3. Dense card index. Every card names a person, a place and a scale.

Case-study video lives here, as cards within this index, not in a separate video section.

### 7.2 `/projects/[slug]`, individual case study. Serves F.

Fixed structure, every case study, no exceptions:

1. Breadcrumb back to the index
2. Title, then practitioner, place and country as a single line
3. **The site**, what the land was and what condition it was in
4. **What was done**, the intervention
5. **What was measured**, results with the measurement method stated, and estimates labelled as estimates
6. **What we cannot claim**, the honest limits of a single site
7. Media, the practitioner's own presentation where one exists

Section 6 is mandatory. It is the reason a funder can trust sections 3 to 5.

---

## 8. Community

### 8.1 `/community`. Serves F and S.

1. Heading and introduction
2. Interactive map, opt-in member locations at city level, hubs and workshop sites marked distinctly
3. Two columns: join the community, and volunteer

### 8.2 `/community/directory`, find a professional. Serves F.

1. Heading and a paragraph explaining exactly what each title required
2. Filter chips: All, Consultants, Lab technicians, By region
3. Dense list. Each row: name, earned title, region, verification marker
4. A note that this replaces three previous directories and that practitioners maintain their own entries

---

## 9. `/now`. Serves all three, and is the page that proves the organisation is alive.

1. Heading and a line stating that everything here carries a date
2. Filter chips: Everything, Enrolling, Workshops, Webinars, Writing, Video
3. Reverse-chronological index mixing every content type. Each row: type label, date, heading, one line

This page pulls from every other section. It creates nothing of its own.

---

## 10. `/donate`. Serves G and general supporters.

Two columns. Left: one-time amounts, then monthly giving with a short case for it. Right: where money goes, other ways to help linking to volunteer and speaking, and a tax-deductibility note with the EIN.

No urgency devices, no thermometer, no countdown.

---

## 11. `/contact` and legal pages

Contact: how to reach us, physical address, and a legal block linking to governance.

Privacy, Terms and Accessibility are clean standalone templates linked from the footer. They are not allowed to dominate any other page.

---

## 12. Cross-cutting rules

- Every page states the 501(c)(3) status via the footer legal block
- Every number anywhere on the site has its source printed beside or beneath it
- Every dated item shows its date
- Index pages filter, they do not paginate
- No page is more than two clicks from the homepage
- The same card component is used for case studies, videos, publications, practitioners and events. One container, different metadata.
