# Link map

Every link and button on the Soil Food Web Foundation site: what it says, where it goes, and why it goes there.

Built 11 September 2026 for Phase 1 of the final build. Checked by `tools/linkcheck.py`, which fails on a missing file or a missing anchor.

## The four destinations

Every primary call to action on the site lands in one of four places:

| Destination | What it is |
| :-- | :-- |
| A program on school.soilfoodweb.com | The Thinkific school. Courses live there and stay there; this site is the shop window and the map. |
| The calendar | `calendar.html`. Every dated thing: workshops, cohorts, webinars. |
| Donate | `donate.html`. |
| Join the community | `community.html#join`. |

Secondary links may go anywhere on the site. Every one of them names its destination: "See every program and price", never "Learn more".

## Section mapping

The staging menu at new.soilfoodweb.com is the newest decision, so the site has five sections: About us, Learn, Science, Practice, Community. Copy deck v2 was written against an older structure. Every mapping made:

| Copy deck v2 | This site | Why |
| :-- | :-- | :-- |
| `/projects` | `practice.html` | Practice is the staging menu's name for the pillar. The Projects section itself is removed until the projects database has real entries (Evan, 8 September); case studies carry the section for now. |
| `/projects/[slug]` | `projects/[slug].html` | Individual case studies keep their own pages, reached from Practice. |
| `/projects#field-trials`, `/projects#hubs` | `practice.html#case-studies` | Neither section exists yet. Both anchors pointed at nothing. |
| `/now` | `calendar.html` and `news.html` | "Now" split in two: dated things go to the calendar, written things to news. The overlay menu's Happening now panel and every "what's happening" link now point at the calendar. |
| `/learn/workshops` | `calendar.html#workshops` | Workshops are a filtered view of the calendar, not a page of their own (Site Map, 7 September). |
| `/publications` | `research.html` | Holds until the Publications page is built in Phase 3, when this flips back. `vercel.json` already 301s `/publications` to `/research`. |
| `/how-it-works` | `science.html` | Science is the staging menu's name for the pillar. |
| `/community/directory` | `directory.html` | Reached from Practice only, single door (Site Map, 7 September). |

`vercel.json` carries these as 301s. Copy deck v2 section 22 is the master redirect list and stays current as pages change.

## Global chrome, on every page

Rendered by `chrome()` in `tools/build.py` from `content/global.json`, and re-stamped into the hand-written pages by the same script, so a label changes in one place.

### Utility bar

| Label | Destination | Why |
| :-- | :-- | :-- |
| Student login | `login.html` | The LMS chooser. Students arrive looking for their course before anything else. |
| Subscribe to the newsletter | `news.html#subscribe` | The signup form. Said in full so it is not mistaken for a paid subscription. |
| Donate | `donate.html` | One of the four destinations. The only gold button on the site. |

### Header

| Label | Destination | Why |
| :-- | :-- | :-- |
| Soil Food Web Foundation (wordmark) | `index.html` | Convention. |
| About us | `about.html` | Section landing. |
| Learn | `learn.html` | Section landing. |
| Science | `science.html` | Section landing. |
| Practice | `practice.html` | Section landing. |
| Community | `community.html` | Section landing. |
| Donate | `donate.html` | Repeated from the utility bar deliberately: it is the one thing a visitor may want at any moment. |
| Menu | opens the overlay | Every section and its children, plus what is happening now. |

### Overlay menu

| Section | Label | Destination | Why |
| :-- | :-- | :-- | :-- |
| About us | Mission, vision and story | `about.html#mission` | The ratified mission and vision, and the history. |
| | Our team and board | `about-team.html` | Who governs and who teaches. |
| | Governance and financials | `about-governance.html` | What a funder checks first. Was missing from the menu and reachable only from the footer. |
| | Dr. Elaine Ingham | `about-elaine.html` | Her own page. Renamed from "Dr. Elaine's Research": the page is about her, not only the research. |
| | Foundation news | `news.html#foundation` | Pre-filtered news for funders and press. |
| | Contact us | `contact.html` | Address, email, press, logo use. |
| Learn | Every program and what it costs | `learn.html` | Says what the page gives you. The old label, "Programs Overview", did not. |
| | Courses on school.soilfoodweb.com | `https://school.soilfoodweb.com` | Names the external host, so nobody presses it expecting to stay on this site. |
| | In-person workshops | `calendar.html#workshops` | Filtered calendar view. |
| | Calendar of events | `calendar.html` | Everything dated. |
| | Free webinars | `learn-webinars.html` | The easiest first step, and free. |
| | Scholarships | `learn-scholarships.html` | |
| | Student login | `login.html` | Deliberate repeat of the utility bar. |
| Science | How the soil food web works | `science.html` | The six mechanisms. |
| | Research and publications | `research.html` | Renamed from "Research Database": a database is what it is built on, not what a reader wants. |
| | Partner on research | `research.html#work-with-us` | Data access, replication, university partnerships. |
| Practice | Case studies | `practice.html#case-studies` | |
| | Find a professional | `directory.html` | The single door to the directory. |
| | Work with us | `practice.html#work-with-us` | Land, trials, restoration partnerships. |
| Community | Community map | `community.html#community-map` | |
| | News and stories | `news.html` | |
| | Calendar of events | `calendar.html` | Second door to the same page, for the community audience. |
| | Join the community | `community.html#join` | One of the four destinations. |

Happening now panel, same overlay: the two dated items below, then **Everything that is happening** to `calendar.html`.

| Dated item | Destination | Why |
| :-- | :-- | :-- |
| 16 September to 20 December 2026, Permaculture Design Certification cohort | `learn.html#permaculture` | The program row, with the price. Anchor renamed from `#pdc`: no acronyms in public copy or in URLs people share. |
| 18 to 31 October 2026, dates to confirm, India Accelerator Workshop, Coimbatore | `calendar.html#workshops` | The listing, with its unresolved dates on the line. Decision 12. |

### Footer

Reconciled against the footer on new.soilfoodweb.com, which is the newest decision. Its three columns are kept and every entry it carries that this site was missing has been added. Resources stays, because those pages exist and would otherwise be reachable only from the menu.

| Column | Label | Destination | Note |
| :-- | :-- | :-- | :-- |
| Foundation | About us | `about.html` | |
| | Our team and board | `about-team.html` | Staging says "Our Team" |
| | Dr. Elaine's research | `about-elaine.html` | Was missing from the footer |
| | Governance and financials | `about-governance.html` | Staging says "Nonprofit & legal info" |
| | Contact us | `contact.html` | |
| Learn | Every program and what it costs | `learn.html` | Staging says "Programs Overview" |
| | Courses on school.soilfoodweb.com | `https://school.soilfoodweb.com` | Was missing from the footer |
| | Workshops and events | `calendar.html#workshops` | Was missing from the footer |
| | Calendar of events | `calendar.html` | |
| | Free webinars | `learn-webinars.html` | |
| | Scholarships | `learn-scholarships.html` | |
| Resources | How the soil food web works | `science.html` | Not on the staging footer |
| | Research and publications | `research.html` | Not on the staging footer |
| | Case studies | `practice.html#case-studies` | Not on the staging footer |
| | Media and press | `contact.html#media` | Not on the staging footer |
| Get involved | Donate | `donate.html` | |
| | Volunteer with us | `volunteer.html` | |
| | Invite us to speak | `contact.html#speak` | Was missing from the footer |
| | Find a professional | `directory.html` | Not on the staging footer |
| | Logo and name use | `contact.html#logo` | Staging says "Logo & Brand Use" |
| Legal block | governance page | `about-governance.html` | |
| | Privacy · Terms · Accessibility | `privacy.html` · `terms.html` · `accessibility.html` | |

The staging footer also carries four social icons (X, Facebook, Google, Instagram). No account addresses were supplied, so the footer prints a placeholder rather than four links to nowhere.

The legal block prints on every page: EIN 39-4439236, the registered office, and where to find the Form 990.

## Page by page

Chrome links are not repeated here.

### index.html, home

| Label | Destination | Why |
| :-- | :-- | :-- |
| Join the community | `community.html#join` | Primary. One of the four destinations. |
| See every program and price | `learn.html` | Secondary. The price is the thing people go looking for, so the button says it. |
| **Farm with biology** — Find a trained professional near you | `directory.html` | Doorway one. A farmer's first need is a person who already does this, not a course. |
| **Restore your land** — See restoration work and start a conversation | `practice.html#work-with-us` | Doorway two. Restoration runs through the Foundation as a partnership, and that section holds the form. |
| **Bring it to your classroom** — See every program and price | `learn.html` | Doorway three. An educator is buying or adapting a curriculum, so they need the programs and the costs. |
| How the soil food web works → | `science.html` | Microscope circle one. |
| Every program and its price → | `learn.html` | Microscope circle two. |
| Research and publications → | `research.html` | Microscope circle three. |
| Read our mission and story → | `about.html` | From the legacy section. |
| See case studies from the field → | `practice.html#case-studies` | The old label said "See how it works" but the link went to case studies. |
| Foundation Courses / See the Foundation Courses and price → | `learn.html#foundation-courses` | |
| Advanced Programs / See the Soil Food Web Consultant path → | `learn.html#complete-practicum` | The Practicum is what earns the title, so that is where the row points. |
| Permaculture Design Certification / See the Permaculture Design Certification → | `learn.html#permaculture` | |
| Ecosystem Restoration Courses / See Introduction to Ecosystem Restoration → | `learn.html#restoration` | |
| Workshops / See the calendar of workshops → | `calendar.html` | |
| Permaculture Design Certification cohort begins | `learn.html#permaculture` | |
| India Accelerator Workshop, Coimbatore | `calendar.html#workshops` | |
| All events → | `calendar.html` | |
| All news and stories → | `news.html` | |
| Start a partnership conversation | `practice.html#work-with-us` | The ecosystem strip. "Partner with us" did not say what happens next. |
| Join the community | `community.html#join` | Closing band. |
| Donate | `donate.html` | Closing band. |

### about.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| doi.org/10.2307/1942528 | DOI | The 1985 paper, cited from the history. |
| Our team and board | `about-team.html` | |
| Read her published research → | `research.html` | |
| Contact us | `contact.html` | |

### about-team.html

Jump links to the six groups on the page (`#g-founder`, `#g-board`, `#g-na`, `#g-eu`, `#g-la`, `#g-other`), and **Dr. Elaine Ingham** to `about-elaine.html`.

### about-elaine.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| Publications | `research.html` | Becomes `publications.html` in Phase 3. |
| Google Scholar profile | scholar.google.com | Her profile. |
| Obituary for Dr. Elaine Ingham | `news.html` | |

### about-governance.html

`info@soilfoodweb.com` with a "For the board" subject.

### learn.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| **What brings you to the soil food web?** I grow food | `#foundation-courses` | The starting point for everyone, until Decision 1 settles what a grower who does not want the Consultant title buys. |
| **What brings you to the soil food web?** I want a new career | `#complete-practicum` | The Practicum earns the Consultant title. |
| **What brings you to the soil food web?** I restore ecosystems | `#restoration` | |
| **What brings you to the soil food web?** I'm just getting curious | `learn-webinars.html` | Free, live and monthly: the cheapest first step. |
| Watch the films from the field | `practice.html#case-studies` | Written graduate testimonials are still being collected. |
| See the Foundation Courses on the school site → | `school.soilfoodweb.com/bundles/soilfoodweb-foundation-courses` | Every program row goes straight to its own Thinkific page. |
| See the Complete Practicum on the school site → | `school.soilfoodweb.com/bundles/complete-practicum` | |
| See the Permaculture Design Certification on the school site → | `school.soilfoodweb.com/courses/permaculture-design-certification` | |
| See Introduction to Ecosystem Restoration on the school site → | `school.soilfoodweb.com/bundles/introduction-to-ecosystem-restoration` | |
| See upcoming workshops → | `calendar.html#workshops` | Workshops are dated, so they live on the calendar. |
| Register for the next webinar → | `learn-webinars.html` | |

### science.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| Case studies | `practice.html#case-studies` | |
| See every program and price | `learn.html` | |
| Watch the films from the field | `practice.html#case-studies` | The written case studies are not compiled yet, so the section sends people to the films that exist. |

The six mechanism animations are embedded here from Vimeo, lazy-loaded, one per mechanism: 372925873, 372474782, 372476056, 372479571, 372480255, 372478833. **Unverified:** if any of them is unlisted rather than public it will need its `h` privacy hash appended, and will show "video not available" without one. That cannot be checked from this build environment.

### practice.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| Read the Sweden market garden case study | `projects/market-garden-sweden.html` | The one case study with its own page. It was unreachable on the deployed site: `vercel.json` redirected `/projects/:slug*` to `/practice`, which swallowed it. Fixed. |
| Three case-study films (Roberto Silva, Cory Miller, Nick Tomasini) | Vimeo, on press | Facades: the player is not fetched until someone presses play. |
| **Farm with biology** — Find a trained professional near you | `directory.html` | Same three doorways as the homepage, same destinations. They used to link to `#work-with-us`, the section the reader was already in. |
| **Restore your land** — See how we partner on land and trials | `research.html#work-with-us` | |
| **Bring it to your classroom** — See every program and price | `learn.html` | |
| Partner on research | `research.html#work-with-us` | |
| Volunteer with us | `volunteer.html` | |

### community.html

| Label | Destination |
| :-- | :-- |
| Find a professional | `directory.html` |
| See every program and price | `learn.html` |
| Start with a free webinar | `learn-webinars.html` |

### calendar.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| Register your interest on the school site | `school.soilfoodweb.com/pages/workshop-interest` | Names the host. "Get notified" did not say where it went or who would hold the address. |
| Free educational webinar | `learn-webinars.html` | |

### research.html

| Label | Destination |
| :-- | :-- |
| The 1985 citation | doi.org/10.2307/1942528 |
| Start a research conversation | `mailto:info@soilfoodweb.com` |

### learn-webinars.html

| Label | Destination | Why |
| :-- | :-- | :-- |
| Save my seat, free | `webinar.soilfoodweb.com` | The registration page. |
| our community space | `school.soilfoodweb.com/products/communities/SFW-public-community` | The recordings backlog. |
| **Free resources** — Watch the six animations | `science.html` | The educational videos are the six mechanism animations. |
| **Free resources** — See the programs these come from | `learn.html` | The three short guides do not exist yet; this holds until they do. |
| **Free resources** — Watch the films from the field | `practice.html#case-studies` | The case studies. |
| **Where to go from here** — Watch the six animations | `science.html` | A webinar is the first step; these are the next ones. |
| **Where to go from here** — See every program and price | `learn.html` | |
| **Where to go from here** — Find a professional | `directory.html` | |
| **Where to go from here** — See how scholarships work | `learn-scholarships.html` | |

### learn-scholarships.html

| Label | Destination |
| :-- | :-- |
| Apply for a scholarship | `mailto:info@soilfoodweb.com` (twice: once from the waiting-on-stories section, once under the three steps) |
| Donate to the scholarship fund | `donate.html` |

### login.html

One button, **Log in**, to `school.soilfoodweb.com/users/sign_in`. The second platform card carries no button: its name and address are not known yet, and a button to `#` is worse than no button.

### donate.html

**Contact us →** to `contact.html`.

### contact.html

Five `mailto:info@soilfoodweb.com` links, each with its own subject line: general, speaking invitation, volunteer, press enquiry, logo use.

### projects/market-garden-sweden.html

**← All case studies** to `../practice.html`.

### Pages with no outbound body links

`directory.html`, `news.html`, `privacy.html`, `terms.html`, `accessibility.html`. All five carry the full chrome.

### Reference pages, not in the public nav

`design-system.html` and `motion.html` are internal. They are reachable only by typing the address and are linked from nowhere on the site. Both were repaired in Phase 1 so they no longer point at pages that do not exist.

## External links

| URL | Where it appears | Status |
| :-- | :-- | :-- |
| `school.soilfoodweb.com` | every page, via the Learn menu | Not reachable from this build environment, see below |
| `school.soilfoodweb.com/bundles/soilfoodweb-foundation-courses` | learn.html | Not verified |
| `school.soilfoodweb.com/bundles/complete-practicum` | learn.html | Not verified |
| `school.soilfoodweb.com/courses/permaculture-design-certification` | learn.html | Not verified |
| `school.soilfoodweb.com/bundles/introduction-to-ecosystem-restoration` | learn.html | Not verified |
| `school.soilfoodweb.com/pages/workshop-interest` | calendar.html | Not verified |
| `school.soilfoodweb.com/products/communities/SFW-public-community` | learn-webinars.html | Not verified |
| `school.soilfoodweb.com/users/sign_in` | login.html | Not verified |
| `webinar.soilfoodweb.com` | learn-webinars.html | Not verified |
| `doi.org/10.2307/1942528` | about.html, research.html, design-system.html | Not verified |
| `scholar.google.com/citations?user=iOm3z4AAAAAJ` | about-elaine.html | Not verified |

**Every external link is unverified.** This build environment has no outbound network access beyond an allow list that does not include soilfoodweb.com, school.soilfoodweb.com, vimeo.com or doi.org. Each URL above is carried over from the copy deck or the earlier build and is spelled the way the copy deck spells it. They need one pass from a machine with normal internet access before launch. Phase 5 covers it.

No link on this site points at the WordPress shop or at `/foundation-courses-2/`.

## Anchors

Every anchor a link points at exists on the page it names. `tools/linkcheck.py` proves it and exits non-zero if that stops being true. Anchors in use:

`#main` · `about.html#mission` · `contact.html#speak` · `calendar.html#workshops` · `community.html#community-map` · `community.html#join` · `contact.html#media` · `contact.html#logo` · `volunteer.html` · `learn.html#foundation-courses` · `learn.html#complete-practicum` · `learn.html#permaculture` · `learn.html#restoration` · `news.html#subscribe` · `news.html#foundation` · `practice.html#case-studies` · `research.html#work-with-us` · the six `about-team.html` group anchors · the sixteen `motion.html` study anchors.
