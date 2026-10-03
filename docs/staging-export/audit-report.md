# Soil Food Web Foundation – staging site audit (new.soilfoodweb.com)

Audit date: 2026-10-02. Crawled from a cloud container; every URL was fetched twice (plain and with `?nocache=12345`). Companion files: `pages.csv` (one row per URL, 689 rows) and `links.csv` (one row per link on every fetched page, 43,228 rows). The crawl, parse and check scripts are in `scripts/` so the audit can be re-run after fixes.

## 0. What could not be verified (read this first)

* **External links were checked in two passes.** The first pass ran with the container's default network policy, which blocked almost every third-party host. The 158 hosts in `allowlist.txt` were then added to the environment and every previously blocked link was re-checked (`scripts/recheck.py`, then `scripts/recheck_curl.py` with curl for sites such as Thinkific whose bot protection rejects Python's TLS fingerprint). What still could not be verified after that: links whose target redirects on to a host that is not on the list (mostly `doi.org` → the publisher's site, e.g. nature.com, springer.com, tandfonline.com; the DOI itself resolves), and sites that refuse automated requests with 403 or 429 (Instagram, LinkedIn, Facebook, Google Scholar citation pages). Those rows in `links.csv` carry the exact error. See section 1.2 'External links'.
* **No XML sitemap exists.** `/wp-sitemap.xml` → 404 (it redirects `/sitemap.xml` there too), `/sitemap_index.xml` → 404, `/wp-sitemap-posts-page-1.xml` → 404. `robots.txt` is the WordPress default and names no sitemap. Hidden pages were found through the REST API instead.
* **REST endpoints that refused:** `menu-items` and `menus` (401 rest_cannot_view), `templates` and `template-parts` (401), `font-families` (401), `global-styles` (404 no route). All content types were readable: pages (31), posts (18), media (90), sfw_calendar_event (10), directory_member (169), sfw_publication (134), sfw_program (15), team_member (22), sfw_testimonial (5), sfw_timeline (9), sfw_video (20), wp_navigation (1), categories (12), tags (21).
* **Givebutter verified (second pass).** The donation page embeds two `<givebutter-widget>` elements loaded from `widgets.givebutter.com` (account `MLhzWWlS1GmtfZXr`). Givebutter's elements API resolves `g6W2oz` to a giving form for campaign `4PYTEM` (embed `https://givebutter.com/embed/c/sfwf-donate`) and `LlKe9m` to a goal bar for the same campaign (goal $100,000; $50,944.69 raised at audit time). The public campaign page `https://givebutter.com/sfwf-donate` returns 200 and is titled 'Soil Food Web Foundation'. There are still no plain-HTML links to givebutter.com anywhere on the site, so the donation path depends entirely on JavaScript.
* `www.soilfoodweb.com` (the live site with www) returned 403 for the root and was proxy-blocked for the other 6 links; `soilfoodweb.com` without www answered 200 for all 9 links.

## 1. Problems sorted by Google Ad Grant impact

Google's Ad Grant policies require a working, substantive website: no broken links, no placeholder content, a clear nonprofit purpose, a working donation path, and accurate claims. The items below are ordered by how directly they endanger approval.

### 1.1 Donation path (highest impact)

| # | Problem | Where | Evidence |
|---|---|---|---|
| 1 | **Footer 'Donate' link is a 404.** The footer on all 410 HTML pages links to `/donate/`; only `/donations/` exists. | footer, every page | `/donate/` → HTTP 404 |
| 2 | **Editorial placeholder on the donation page.** | `/donations/` | Visible text: *"[IMPACT LINES — pair with preset amounts once program costs are confirmed, e.g. “$25/mo helps fund open-access research” / “$X sponsors a scholarship seat.” VERIFY amounts with operations before publishing specific claims.]"* |
| 3 | **Three calls to action on the donation page have empty `href`.** | `/donations/` | 'Volunteer with us' (twice), 'Invite us to speak', 'Ask about brand use' → `href=""` (reloads the same page) |
| 4 | **'Donate to support scholarships' is a 404.** | `/scholarship/` | links to `/donate-get-involved/` → HTTP 404 |
| 5 | **Donation widget works but has no fallback.** Both Givebutter widgets resolve to the live campaign `sfwf-donate` (see section 0), but they render only with JavaScript and there is no plain link to `https://givebutter.com/sfwf-donate` anywhere. | `/donations/` | add a visible 'Donate on Givebutter' link |
| 6 | **Tax-status claims contradict each other** (donors read this). Footer and `/donations/`: *"a 501(c)(3) nonprofit — gifts are tax-deductible"*. `/terms/` §4: *"The Soil Food Web Fund has been set up as a fiscally sponsored 501(c)(3) entity… The Foundation’s application for independent 501(c)(3) tax-exempt status is pending with the IRS"*. Launch post (Oct 2025): *"application for 501(c)(3) status is pending"*. | footer, `/donations/`, `/terms/`, `/about-us/`, launch post | one of these is out of date |
| 7 | 'Donate' button on the hidden page `/nonprofit-landing/` goes to `#`. | `/nonprofit-landing/` | `href="#"` |
| 8 | **Foundation Course 1 links are a 404 on Thinkific.** The card image, title and 'Learn more →' on the homepage and both programs pages link to `school.soilfoodweb.com/courses/foundation-couse-1` (typo). | `/`, `/programs-overview/`, `/programs-carousel-preview/` | 404 confirmed; `…/foundation-course-1` is 200 |

### 1.2 Broken, empty and wrong-target links

**Internal 404s, localhost and other hard failures** (unique targets; counts are link occurrences across pages):

| Target | Status | Occurrences | On pages | Sections | Link text |
|---|---|---|---|---|---|
| `https://new.soilfoodweb.com/cdn-cgi/l/email-protection` | 404 (Cloudflare email-protection; works only with JavaScript) | 602 | 410 | main, ocm | Email; Email [email protected]; [email protected] |
| `https://new.soilfoodweb.com/donate/` | 404 | 410 | 410 | footer | Donate |
| `https://new.soilfoodweb.com/accessibility/` | 404 | 410 | 410 | footer | Accessibility |
| `https://school.soilfoodweb.com/courses/foundation-couse-1` | 404 | 9 | 3 | main | Foundation Course 1: Introduction to the; Learn more →; [img: Foundation Course 1: Introduction  |
| `http://localhost:8080/learn/` | localhost | 9 | 3 | main | Permaculture Design Certification; See the Permaculture Design Certificatio; [img: Permaculture Design Certification] |
| `https://www.sylvolutions.eu/services/compostage-collectif/` | 404 | 1 | 1 | main | Website www.sylvolutions.eu/services/com |
| `https://new.soilfoodweb.com/donate-get-involved/` | 404 | 1 | 1 | main | Donate to support scholarships |

Notes: `/cdn-cgi/l/email-protection#…` is Cloudflare's e-mail obfuscation. With JavaScript the links become `mailto:info@soilfoodweb.com`; without JavaScript (and for crawlers) they are 404s. The three `/accessibility/`, `/donate/`, `/donate-get-involved/` targets are plain missing pages. The `HTTP 403` rows are plain-`http://` directory-member websites and `www.soilfoodweb.com`; the 403 most likely comes from the container's proxy, so treat them as unverified, not broken. `http://localhost:8080/learn/` is the link behind the **Permaculture Design Certification** card (image and 'See the Permaculture Design Certification →' button) on the homepage, `/programs-overview/` and `/programs-carousel-preview/`: a developer's local URL shipped to staging.

**Links to `#` or with an empty `href`** (template pages `/templates/` and `/templates-2/` excluded; they are demo content and listed in 1.3):

| Section | Link text | href | Occurrences | Example page |
|---|---|---|---|---|
| footer | Governance and financials | `#` | 408 | / |
| header | Subscribe | `#` | 408 | / |
| header | Close Search | `#` | 408 | / |
| header | Partner on Research | `#` | 408 | / |
| main | Share | `#` | 144 | /2025-in-review-a-time-of-transition-honoring-our-founder-and-guiding-spirit-building-stronger-community-and-preparing-for-a-bright-future/ |
| main | Pin | `#` | 36 | /2025-in-review-a-time-of-transition-honoring-our-founder-and-guiding-spirit-building-stronger-community-and-preparing-for-a-bright-future/ |
| main | Start a research conversation | `(empty)` | 4 | /publications/ |
| main | Volunteer with us | `(empty)` | 2 | /donations/ |
| main | case studies & videos | `#` | 1 | / |
| main | Learn more | `#` | 1 | /calendar/ |
| main | Invite us to speak | `(empty)` | 1 | /donations/ |
| main | Ask about brand use | `(empty)` | 1 | /donations/ |
| main | Log in | `#` | 1 | /login/ |
| main | Learn more | `(empty)` | 1 | /nonprofit-landing/ |
| main | View Directory | `(empty)` | 1 | /nonprofit-landing/ |
| main | Get Started | `(empty)` | 1 | /nonprofit-landing/ |
| main | View all | `(empty)` | 1 | /nonprofit-landing/ |
| main | All | `#` | 1 | /nonprofit-landing/ |
| main | Blog | `#` | 1 | /nonprofit-landing/ |
| main | Events | `#` | 1 | /nonprofit-landing/ |
| main | Features | `#` | 1 | /nonprofit-landing/ |
| main | Foundation Update | `#` | 1 | /nonprofit-landing/ |
| main | Microscopy | `#` | 1 | /nonprofit-landing/ |
| main | Newsletter | `#` | 1 | /nonprofit-landing/ |
| main | School Updates | `#` | 1 | /nonprofit-landing/ |
| main | Science & Education | `#` | 1 | /nonprofit-landing/ |
| main | View All Webinars | `#` | 1 | /nonprofit-landing/ |
| main | Donate | `#` | 1 | /nonprofit-landing/ |
| main | See our Impact | `#` | 1 | /nonprofit-landing/ |
| main | Do I need a science background? | `#` | 1 | /programs-overview/ |
| main | I can’t afford the courses. Are there options | `#` | 1 | /programs-overview/ |
| main | What if it’s not for me? | `#` | 1 | /programs-overview/ |
| main | Are there any costs above and beyond the list | `#` | 1 | /programs-overview/ |
| main | Read her published research → | `#` | 1 | /volunteer/ |
| ocm | Close Menu | `#` | 408 | / |
| ocm | Partner on Research | `#` | 408 | / |

The header 'Subscribe' and 'Close Search' and the off-canvas 'Close Menu' are JavaScript toggles and are acceptable. **'Partner on Research'** (header and off-canvas menu on every page) and **'Governance and financials'** (footer on every page) are real navigation items that go nowhere. 'Share' and 'Pin' are social buttons that only work with JavaScript. The FAQ questions on `/programs-overview/` are accordion toggles.

**Link text that does not match the target:**

| Section | Link text | Target | Problem | Occurrences | Example page |
|---|---|---|---|---|---|
| header | Workshops | `https://new.soilfoodweb.com/workshops/` | target page is empty (heading only) | 408 | / |
| header | Partner on Research | `#` | call-to-action links nowhere (# or empty) | 408 | / |
| footer | Governance and financials | `#` | call-to-action links nowhere (# or empty) | 408 | / |
| footer | Workshops and events | `https://new.soilfoodweb.com/workshops/` | target page is empty (heading only) | 408 | / |
| footer | Media and press | `https://new.soilfoodweb.com/contact/` | 'Media and press' goes to /contact/, which redirects to an empty page | 408 | / |
| footer | Donate | `https://new.soilfoodweb.com/donate/` | donate link does not reach a working donation page | 408 | / |
| footer | Accessibility | `https://new.soilfoodweb.com/accessibility/` | target returns 404 | 408 | / |
| ocm | Workshops | `https://new.soilfoodweb.com/workshops/` | target page is empty (heading only) | 408 | / |
| ocm | Partner on Research | `#` | call-to-action links nowhere (# or empty) | 408 | / |
| main | Start a research conversation | `(empty)` | call-to-action links nowhere (# or empty) | 4 | /publications/ |
| main | [img: Foundation Course 1: Introduction to the Soi | `https://school.soilfoodweb.com/courses/foundation-couse-1` | URL slug typo 'couse': target returns 404 on school.soilfoodweb.com (the correct slug foundation-course-1 returns 200) | 3 | / |
| main | Foundation Course 1: Introduction to the Soil Food | `https://school.soilfoodweb.com/courses/foundation-couse-1` | URL slug typo 'couse': target returns 404 on school.soilfoodweb.com (the correct slug foundation-course-1 returns 200) | 3 | / |
| main | [img: Permaculture Design Certification] | `http://localhost:8080/learn/` | points to localhost | 3 | / |
| main | Permaculture Design Certification | `http://localhost:8080/learn/` | points to localhost | 3 | / |
| main | See the Permaculture Design Certification → | `http://localhost:8080/learn/` | points to localhost | 3 | / |
| main | [img: Workshops] | `https://new.soilfoodweb.com/workshops/` | target page is empty (heading only) | 3 | / |
| main | Workshops | `https://new.soilfoodweb.com/workshops/` | target page is empty (heading only) | 3 | / |
| main | See the calendar of workshops → | `https://new.soilfoodweb.com/workshops/` | target page is empty (heading only) | 3 | / |
| main | Learn more | `#` | call-to-action links nowhere (# or empty) | 2 | /calendar/ |
| main | Volunteer with us | `(empty)` | call-to-action links nowhere (# or empty) | 2 | /donations/ |
| main | case studies & videos | `#` | call-to-action links nowhere (# or empty) | 1 | / |
| main | Invite us to speak | `(empty)` | call-to-action links nowhere (# or empty) | 1 | /donations/ |
| main | Ask about brand use | `(empty)` | call-to-action links nowhere (# or empty) | 1 | /donations/ |
| main | Start with a free webinar | `https://school.soilfoodweb.com/bundles/complete-practicum` | text says 'free webinar' but target is not the webinar site | 1 | /find-a-professional/ |
| main | Log in | `#` | call-to-action links nowhere (# or empty) | 1 | /login/ |
| main | Join the community | `https://new.soilfoodweb.com/programs-overview/#path` | 'Join the community' points to programs, not a community page | 1 | /login/ |
| main | View Directory | `(empty)` | call-to-action links nowhere (# or empty) | 1 | /nonprofit-landing/ |
| main | Get Started | `(empty)` | call-to-action links nowhere (# or empty) | 1 | /nonprofit-landing/ |
| main | View All Webinars | `#` | call-to-action links nowhere (# or empty) | 1 | /nonprofit-landing/ |
| main | Donate | `#` | donate link does not reach a working donation page | 1 | /nonprofit-landing/ |
| main | See our Impact | `#` | call-to-action links nowhere (# or empty) | 1 | /nonprofit-landing/ |
| main | Spoil Sponge Workshop | `https://www.soilfoodweb.com/soil-sponge-regeneration-workshop/` | link text typo 'Spoil' (Soil) | 1 | /october-2025-newsletter/ |
| main | Donate to support scholarships | `https://new.soilfoodweb.com/donate-get-involved/` | donate link does not reach a working donation page | 1 | /scholarship/ |
| main | Read her published research → | `#` | call-to-action links nowhere (# or empty) | 1 | /volunteer/ |

Most serious: **'Start with a free webinar'** on `/find-a-professional/` links to `https://school.soilfoodweb.com/bundles/complete-practicum`, a paid course bundle. **'Join the community'** on `/login/` links to `/programs-overview/#path`. **'Media and press'** in the footer goes to `/contact/`, which WordPress redirects (301) to `/contact-info/`, an empty page.

**External links** (after the allowlist and the curl pass). Totals by result:

| Result | Links |
|---|---|
| external OK | 3002 |
| external (redirect) | 172 |
| external – redirect target blocked by container network policy | 66 |
| HTTP 403 – site refused the request (bot protection or login wall) | 28 |
| HTTP 429 – rate-limited, unverified | 26 |
| HTTP 400 | 12 |
| 404 | 10 |
| HTTP 999 | 5 |
| error | 3 |
| external – could not verify (blocked by container network policy) | 1 |

External targets that are not OK (unique targets):

| Target | Result | Final URL / error | Occurrences | Example page | Link text |
|---|---|---|---|---|---|
| `https://school.soilfoodweb.com/courses/foundation-couse-1` | 404 |  | 9 | / | Foundation Course 1: Introduction to the; Learn more → |
| `https://www.nrcs.usda.gov/resources/education-and-teaching-materials/soil-biology-primer` | error | ReadTimeout: HTTPSConnectionPool(host='www.nrcs.usda.gov', port=443): Read timed out. (rea | 2 | /publications/ | The Soil Biology Primer, Chapters 1-5: T |
| `https://soilutions.info/` | error | ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by pe | 1 | /directory-member/josefina-bergsten/ | Website soilutions.info/ |
| `https://www.sylvolutions.eu/services/compostage-collectif/` | 404 |  | 1 | /directory-member/priscille-cazin/ | Website www.sylvolutions.eu/services/com |
| `https://news.okstate.edu/articles/business/2019/mandelafellows_osu.html` | HTTP 403 – site refused the request (bot protection or login wall) |  | 2 | /exploring-soil-food-web-innovations-in-west-afric | Mandela Washington Fellows; Usman Ali Lawran |
| `https://themeforest.net/item/salient-responsive-multipurpose-theme/4363266` | HTTP 403 – site refused the request (bot protection or login wall) |  | 2 | /templates-2/ | Purchase Salient; Sign up now |
| `https://www.linkedin.com/in/permabiologic/` | HTTP 429 – rate-limited, unverified |  | 2 | /directory-member/miguel-ventura-%C2%A6-permabiolo | LinkedIn |
| `https://www.linkedin.com/in/soilfoodwebschool/` | HTTP 429 – rate-limited, unverified |  | 2 | /2025-in-review-a-time-of-transition-honoring-our- | LinkedIn |
| `https://www.sciencedirect.com/science/article/abs/pii/S0038071707001101` | HTTP 403 – site refused the request (bot protection or login wall) |  | 2 | /publications/ | Relative effects of biological amendment |
| `https://www.sciencedirect.com/science/article/abs/pii/S0929139310000119` | HTTP 403 – site refused the request (bot protection or login wall) |  | 2 | /publications/ | Soil life in reconstructed ecosystems: i |
| `https://www.sciencedirect.com/science/article/pii/S0304423812004542` | HTTP 403 – site refused the request (bot protection or login wall) |  | 2 | /publications/ | Biochemical properties of compost tea as |
| `https://www.sciencedirect.com/science/article/pii/S092913939800033X` | HTTP 403 – site refused the request (bot protection or login wall) |  | 2 | /publications/ | Ectomycorrhizae establishment on Douglas |
| `http://www.aboutcookies.org/` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /privacy/ | www.aboutcookies.org |
| `http://www.dynamicwholescapes.ca/` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /directory-member/thomas-schneider/ | Website www.dynamicwholescapes.ca/ |
| `http://www.livingground.art` | HTTP 403 – site refused the request (bot protection or login wall) | http://www.livingground.art/ | 1 | /directory-member/corinne-gwyther/ | Website www.livingground.art |
| `http://www.microvidatv.com/` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /directory-member/niels-de-jong/ | Website www.microvidatv.com/ |
| `http://www.soilfoodweb.com` | HTTP 403 – site refused the request (bot protection or login wall) | http://www.soilfoodweb.com/ | 1 | /soil-food-web-school-first-permaculture-design-ce | www.soilfoodweb.com |
| `http://www.umbhaba.biz/` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /directory-member/shane-plath/ | Website www.umbhaba.biz/ |
| `http://www.widespreadmalus.org` | HTTP 403 – site refused the request (bot protection or login wall) | http://www.widespreadmalus.org/ | 1 | /directory-member/eric-johnson/ | Website www.widespreadmalus.org |
| `https://br.linkedin.com/in/marcelino-meincke-490b6155/en` | HTTP 999 |  | 1 | /directory-member/marcelino-meincke/ | LinkedIn |
| `https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1550-7408.1991.tb01370.x` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /ciliates-soil-health-microscope-watermelon-crop/ | for reproduction |
| `https://soildynamix.com` | HTTP 403 – site refused the request (bot protection or login wall) | https://soildynamix.com/ | 1 | /directory-member/faith-moeser/ | Website soildynamix.com |
| `https://www.facebook.com/people/301-Organics/100068273775691/` | HTTP 400 |  | 1 | /directory-member/christine-lenches-hinkel/ | Facebook |
| `https://www.facebook.com/profile.php?id=100063439943244` | HTTP 400 |  | 1 | /directory-member/veronica-alice/ | Facebook |
| `https://www.facebook.com/profile.php?id=100078575329282` | HTTP 400 |  | 1 | /directory-member/henk-breugem/ | Facebook |
| `https://www.facebook.com/profile.php?id=100087906545933` | HTTP 400 |  | 1 | /directory-member/niels-de-jong/ | Facebook |
| `https://www.facebook.com/profile.php?id=61554686464015` | HTTP 400 |  | 1 | /directory-member/stine-hvidtfeldt-svendsen/ | Facebook |
| `https://www.facebook.com/profile.php?id=61574411548842` | HTTP 400 |  | 1 | /directory-member/leon-du-plessis/ | Facebook |
| `https://www.facebook.com/profile.php?id=61579309719757` | HTTP 400 |  | 1 | /directory-member/ben-padwick/ | Facebook |
| `https://www.facebook.com/search/top?q=liberty%20trace%20farm` | HTTP 400 |  | 1 | /directory-member/kevin-krause/ | Facebook |
| `https://www.facebook.com/share/1BLFwbL1HQ/` | HTTP 400 |  | 1 | /directory-member/dr-carla-portugal/ | Facebook |
| `https://www.facebook.com/share/1Br9mvXbST/?mibextid=wwXIfr` | HTTP 400 |  | 1 | /directory-member/megan-weeber/ | Facebook |
| `https://www.facebook.com/share/1Jnnu2qZxD/` | HTTP 400 |  | 1 | /directory-member/alinani/ | Facebook |
| `https://www.facebook.com/share/1LLY9feJms/?mibextid=wwXIfr` | HTTP 400 |  | 1 | /directory-member/faith-moeser/ | Facebook |
| `https://www.iaea.org/topics/greenhouse-gas-reduction` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /a-blueprint-to-return-to-the-garden-of-eden/ | https://www.iaea.org/topics/greenhouse-g |
| `https://www.linkedin.com/in/alinani-kawala-216702bb?utm_source=share_via&utm_content=profi` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/alinani/ | LinkedIn |
| `https://www.linkedin.com/in/allenfskinner/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/allen-skinner/ | LinkedIn |
| `https://www.linkedin.com/in/anja-fonseka-6a617438a` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/anja-fonseka/ | LinkedIn |
| `https://www.linkedin.com/in/asha-sundararajan-98158b31/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/asha-sundararajan/ | LinkedIn |
| `https://www.linkedin.com/in/astrid-harris-a48153170?utm_source=share_via&utm_content=profi` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/astrid-harris/ | LinkedIn |
| `https://www.linkedin.com/in/brianna-dennison-b26b4526b/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/brianna-dennison/ | LinkedIn |
| `https://www.linkedin.com/in/carolinebustillos/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/caroline-bustillos/ | LinkedIn |
| `https://www.linkedin.com/in/chase-jones-1a3511162` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/chase-jones/ | LinkedIn |
| `https://www.linkedin.com/in/christine-lenches-hinkel-56bbb9b/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/christine-lenches-hinkel/ | LinkedIn |
| `https://www.linkedin.com/in/colleen-dempster-942a7b23/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/colleen-dempster/ | LinkedIn |
| `https://www.linkedin.com/in/doratkalec/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/dora-tkalec/ | LinkedIn |
| `https://www.linkedin.com/in/douglas-ayers-mba-software-engineer-7130a11/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/doug-ayers/ | LinkedIn |
| `https://www.linkedin.com/in/drcarlaportugal/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/dr-carla-portugal/ | LinkedIn |
| `https://www.linkedin.com/in/elizabethromorabago/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/elizabeth-romo-rabago/ | LinkedIn |
| `https://www.linkedin.com/in/ireth-garcia-aguilar-0504661ba/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/ireth-garcia/ | LinkedIn |
| `https://www.linkedin.com/in/jos%C3%A9-santa-cruz-64995a12/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/jose-santa-cruz/ | LinkedIn |
| `https://www.linkedin.com/in/juliadupuis/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/julia-dupuis/ | LinkedIn |
| `https://www.linkedin.com/in/leisha-living-ground-97a1a036/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/corinne-gwyther/ | LinkedIn |
| `https://www.linkedin.com/in/nicholas-garcia-knight-95151183/` | HTTP 999 |  | 1 | /directory-member/nicholas-garcia/ | LinkedIn |
| `https://www.linkedin.com/in/patricia-jim%C3%A9nez-amat-12042820/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/pati-jimenez/ | LinkedIn |
| `https://www.linkedin.com/in/simeon-kleinsasser-51abb1254/` | HTTP 999 |  | 1 | /directory-member/simeon-kleinsasser/ | LinkedIn |
| `https://www.linkedin.com/in/sofya-brown-450500229/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/henk-breugem/ | LinkedIn |
| `https://www.linkedin.com/in/soilcareconsultancysuriname/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/alex-yakaumo/ | LinkedIn |
| `https://www.linkedin.com/in/spero-latchis-14318695` | HTTP 999 |  | 1 | /directory-member/spero-latchis/ | LinkedIn |
| `https://www.linkedin.com/in/tallis-tibbo-246b0528/` | HTTP 999 |  | 1 | /directory-member/tallis-tibbo/ | LinkedIn |
| `https://www.linkedin.com/in/wesley-soule-953384240/` | HTTP 429 – rate-limited, unverified |  | 1 | /directory-member/josh-cheng/ | LinkedIn |
| `https://www.nytimes.com/2026/04/19/science/earth/elaine-ingham-dead.html` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /obituary-for-dr-elaine-ingham/ | https://www.nytimes.com/2026/04/19/scien |
| `https://www.sciencedirect.com/journal/agriculture-ecosystems-and-environment` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /celebrating-world-soil-day-2024/ | Agriculture, Ecosystems & Environment |
| `https://www.sciencedirect.com/journal/geoderma` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /celebrating-world-soil-day-2024/ | Geoderma |
| `https://www.sciencedirect.com/science/article/abs/pii/S003140561830060X` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /exploring-soil-food-web-innovations-in-west-afric | He conducted research in Zambia and Bots |
| `https://www.soils.org/` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /celebrating-world-soil-day-2024/ | Soil Science Society of America Journal |
| `https://www.usda.gov/about-usda/news/press-releases/2025/12/10/usda-launches-new-regenerat` | HTTP 403 – site refused the request (bot protection or login wall) |  | 1 | /2025-in-review-a-time-of-transition-honoring-our- | recently announced |
| `https://doi.org/10.1002/jsfa.3732` | external – redirect target blocked by container network policy | https://scijournals.onlinelibrary.wiley.com/doi/10.1002/jsfa.3732 | 2 | /publications/ | Vermicompost extracts influence growth,  |
| `https://doi.org/10.1016/0038-0717(84)90014-2` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/0038071784900142 | 2 | /publications/ | Soil fungi: Relationships between hyphal |
| `https://doi.org/10.1016/0038-0717(84)90015-4` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/0038071784900154 | 2 | /publications/ | Soil fungi: Measurement of hyphal length |
| `https://doi.org/10.1016/0167-8809(88)90063-1` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/0167880988900631 | 2 | /publications/ | Interactions between soil animals and ec |
| `https://doi.org/10.1016/0167-8809(91)90101-3` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/0167880991901013 | 2 | /publications/ | A comparison of agar film techniques for |
| `https://doi.org/10.1016/0929-1393(95)00075-5` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/0929139395000755 | 2 | /publications/ | Responses of soil foodweb organisms in t |
| `https://doi.org/10.1016/B978-012276460-8/50013-8` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/B9780122764608500138 | 2 | /publications/ | Microflora and microfauna on stems and t |
| `https://doi.org/10.1016/S0031-4056(24)00022-2` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/S0031405624000222 | 2 | /publications/ | Seasonal and faunal effects on decomposi |
| `https://doi.org/10.1016/S0929-1393(02)00039-2` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/S0929139302000392 | 2 | /publications/ | Effect of cover crops and tillage system |
| `https://doi.org/10.1016/S0929-1393(98)00129-2` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/S0929139398001292 | 2 | /publications/ | Effects of Klebsiella planticola SDF20 o |
| `https://doi.org/10.1016/S0929-1393(98)00163-2` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/S0929139398001632 | 2 | /publications/ | Dynamics of soil fungal and bacterial bi |
| `https://doi.org/10.1016/S1002-0160(12)60067-8` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/S1002016012600678 | 2 | /publications/ | Humic-like substances from different com |
| `https://doi.org/10.1016/j.biocontrol.2008.11.008` | external – redirect target blocked by container network policy | https://linkinghub.elsevier.com/retrieve/pii/S1049964408003034 | 2 | /publications/ | Bio-potential of compost tea from agro-w |
| `https://doi.org/10.1023/A:1004211121095` | external – redirect target blocked by container network policy | https://link.springer.com/10.1023/A:1004211121095 | 2 | /publications/ | Chemistry and microbial activity of fore |
| `https://doi.org/10.1038/s41467-019-12798-y` | external – redirect target blocked by container network policy | https://www.nature.com/articles/s41467-019-12798-y | 2 | /publications/ | Fungal-bacterial diversity and microbiom |
| `https://doi.org/10.1094/PHYTO-100-8-0774` | external – redirect target blocked by container network policy | https://apsjournals.apsnet.org/doi/10.1094/PHYTO-100-8-0774 | 2 | /publications/ | Biocontrol activity and induction of sys |
| `https://doi.org/10.1094/PHYTO.1998.88.5.450` | external – redirect target blocked by container network policy | https://apsjournals.apsnet.org/doi/10.1094/PHYTO.1998.88.5.450 | 2 | /publications/ | Compost and compost water extract-induce |
| `https://doi.org/10.1094/PHYTO.2004.94.11.1156` | external – redirect target blocked by container network policy | https://apsjournals.apsnet.org/doi/10.1094/PHYTO.2004.94.11.1156 | 2 | /publications/ | Compost tea as a container medium drench |
| `https://doi.org/10.1105/tpc.108.058784` | external – redirect target blocked by container network policy | https://academic.oup.com/plcell/article/20/2/241-243/6091191 | 2 | /publications/ | Chitin signaling in plants: Insights int |
| `https://doi.org/10.1128/aem.44.2.363-370.1982` | external – redirect target blocked by container network policy | https://journals.asm.org/doi/10.1128/aem.44.2.363-370.1982 | 2 | /publications/ | Relationship between fluorescein diaceta |
| `https://doi.org/10.1371/journal.pone.0091589` | external – redirect target blocked by container network policy | https://dx.plos.org/10.1371/journal.pone.0091589 | 2 | /publications/ | Winter soil CO2 flux from different mid- |
| `https://doi.org/10.1371/journal.pone.0092985` | external – redirect target blocked by container network policy | https://dx.plos.org/10.1371/journal.pone.0092985 | 2 | /publications/ | Comparison of seasonal soil microbial pr |
| `https://doi.org/10.1631/jzus.2005.B0171` | external – redirect target blocked by container network policy | https://link.springer.com/10.1631/jzus.2005.B0171 | 2 | /publications/ | Bioremediation potential of spirulina: t |
| `https://doi.org/10.22043/mi.2019.118205` | external – redirect target blocked by container network policy | https://mij.areeo.ac.ir/article_118205.html | 2 | /publications/ | Biocontrol activity of endophytic fungus |
| `https://doi.org/10.2307/1941256` | external – redirect target blocked by container network policy | https://esajournals.onlinelibrary.wiley.com/doi/10.2307/1941256 | 2 | /publications/ | Nitrogen limitation of decomposition and |
| `https://doi.org/10.3923/ajppaj.2008.15.23` | external – redirect target blocked by container network policy | https://www.scialert.net/abstract/?doi=ajppaj.2008.15.23 | 2 | /publications/ | Effect of bacterial isolates obtained fr |
| `https://doi.org/10.3923/jbs.2006.572.580` | external – redirect target blocked by container network policy | https://www.scialert.net/abstract/?doi=jbs.2006.572.580 | 2 | /publications/ | In vitro and in vivo evaluation of indiv |
| `https://doi.org/10.3923/jps.2008.168.175` | external – redirect target blocked by container network policy | https://www.scialert.net/abstract/?doi=jps.2008.168.175 | 2 | /publications/ | Aerobic compost tea, compost and a combi |
| `https://SoilLab.ca` | external – redirect target blocked by container network policy | https://soilhealthlab.wordpress.com/ | 1 | /directory-member/witold-krawiec/ | Website SoilLab.ca |
| `https://beaumonthealthcare.com` | external – redirect target blocked by container network policy | https://www.beaumonthealthcare.com/ | 1 | /directory-member/lori-von-der-heydt/ | Website beaumonthealthcare.com |
| `https://biodiversedesigns.com` | external – redirect target blocked by container network policy | https://www.biodiversedesigns.com/ | 1 | /directory-member/jayden-fmf/ | Website biodiversedesigns.com |
| `https://groundswellag.com/` | external – redirect target blocked by container network policy | https://www.groundswellag.com/ | 1 | /october-2025-newsletter/ | Groundswell Festival |
| `https://iecompost.com` | external – redirect target blocked by container network policy | https://www.iecompost.com/ | 1 | /directory-member/jason-gearheart/ | Website iecompost.com |
| `https://revive.land` | external – redirect target blocked by container network policy | https://www.revive.land/ | 1 | /directory-member/jeroen-boss/ | Website revive.land |
| `https://www.bing.com/ck/a?!&&p=ab87e36984792014a018724a67c85f0d330cd8d430ec055f2047ccfae79` | external – redirect target blocked by container network policy | https://en.wikipedia.org/wiki/Central_Valley_(California) | 1 | /help-us-celebrate-food-knowledge-and-culture-in-s | Central Valley |
| `https://www.bing.com/ck/a?!&&p=ec60497146fe0a725db2c30764e2e25ac9035339687c32e17651000c0eb` | external – redirect target blocked by container network policy | https://www.visitsacramento.com/ | 1 | /help-us-celebrate-food-knowledge-and-culture-in-s | Sacramento |
| `https://www.living-microbes.com` | external – could not verify (blocked by container network policy) | ProxyError: HTTPSConnectionPool(host='www.living-microbes.com', port=443): Max retries exc | 1 | /directory-member/sarah-talia/ | Website www.living-microbes.com |
| `https://www.springhillsoil-lab.ca` | external – redirect target blocked by container network policy | https://springhillsoil-lab.ca/ | 1 | /directory-member/amy-luck-macgregor/ | Website www.springhillsoil-lab.ca |
| `https://www.tinwaldfarm.co.nz` | external – redirect target blocked by container network policy | https://tinwaldfarm.co.nz/ | 1 | /directory-member/amanda-currie/ | Website www.tinwaldfarm.co.nz |

Reading the table: a `doi.org` row marked 'redirect target blocked' means the DOI resolved (302 from doi.org) but the publisher's domain was not on the allowlist, so the final page is unverified rather than broken. LinkedIn answers 999, Facebook 400, Instagram 429 and YouTube a Google bot challenge to any non-browser request, and several publishers (ScienceDirect, Wiley, NYT, USDA, IAEA) answer 403; those have to be checked by hand. Rows with a real `404` or a connection failure are broken or down.

**Redirects.** 82 `/publication/…/` URLs (every publication that has a DOI or external source) are not pages: they 301-redirect straight to doi.org, sciencedirect.com, scholar.google.com, orgprints.org, cambridge.org, andrewsforest.oregonstate.edu, nrcs.usda.gov. The targets could not be verified (blocked). The 102 attachment pages (`/about-us/screenshot-…/`, `/calendar-event/…/img_1942/`, `/how-it-works/attachment/6/`, `/directory-member/<name>/<photo>/` etc.) 301-redirect to the image file; that is normal WordPress behaviour.

### 1.3 Placeholder and demo content

| Page | What is there | Why it matters |
|---|---|---|
| `/scholarship/` and `/testimonial/*` (5 pages) | **All five 'Scholar Stories' are invented.** 'John Doe – United Kingdom', 'Amara Okafor – Nigeria', 'David Vance – Canada', 'Marcus Thorne – United States', 'Yuki Tanaka – Japan'. The quotes are generic SaaS testimonials (*"the ongoing support from the account management team"*, *"My team’s productivity has spiked by 40%"*, *"scale its deployment company-wide"*). The testimonial carousel on `/scholarship/` is public and linked from the main menu. | Fabricated testimonials on a nonprofit scholarship page are a credibility and policy risk. |
| `/scholarship/` | *"2. We review in cohorts. [VERIFY review cadence and criteria with the education team.]"* | editorial note visible to the public |
| `/donations/` | *"[IMPACT LINES — … VERIFY amounts with operations before publishing specific claims.]"* | see 1.1 |
| `/programs-overview/` | Two student quotes are attributed to *"Jennifer Ralston · Country \| Soil Food Web Consultant"* and *"Adam Queen · Country \| Soil Food Web Consultant"* – the word **Country** is an unfilled field. | placeholder |
| `/publications/` (all three filtered views) and `/publication/in-vitro-studies-on-control-of-soil-borne-plant-pathogens-by-earthworm-eudrilus-eugeniae-exudates/` | *"Shobha, S.V. and R.D. Kale · Journal citation not verified"* | unverified citation shown publicly |
| `/templates-2/` (hidden page, 3,020 words) | Full Salient theme demo: *"Lorem ipsum dolor sit amet…"*, *"Far far away, behind the word mountains…"*, *"Salient will breathe new life to your online presense"*, links to themeforest.net and themenectar.com demo images. | demo page is publicly reachable (noindex, but live) |
| `/templates/` (hidden page, 2,478 words) | Salient demo 'Tether' product page: *"Trusted by the world’s top brands"*, *"Expert financial consulting in Manhattan"*, *"What exactly is Tether?"*, Lorem ipsum, 'Shop Anti-Acne', 'Shop Serums'. | same |
| `/nonprofit-landing/` (hidden page) | Old landing draft. Contains the theme demo testimonial three times: *"Switching to Tether streamlined our operations overnight…"*, the sentence *"Check out Kevin treck some of the most intense courses in all of the Salient area"*, '6000+ Students' and 'over 130 countries' (both contradict the homepage), buttons 'Get Started', 'Learn more', 'View Directory', 'View all' with empty href and 'Donate', 'View All Webinars', 'See our Impact' → `#`. | stale draft, contradictory numbers |
| `/timeline-preview/`, `/programs-carousel-preview/` | Component previews duplicating the About timeline and the programs carousel. | duplicates |
| `/community/` | Only 71 words; the map is a JavaScript embed with no text fallback. | thin |
| 'Country' | The word 'Country' also appears as a normal filter label on `/find-a-professional/` and `/sfw-directory/`, and in '26-Country Journey' in the Sadhguru post. Those are fine. | – |

Not found anywhere: `[PLACEHOLDER]`, 'test event'. 'Lorem' appears only on the two template pages.

### 1.4 Thin and empty pages

Main-content word count excludes header, off-canvas menu and footer. Threshold 300 words. Item pages (directory members, videos, team members, publications, archives) are listed in `pages.csv` and summarised below the table.

| Page | Words | Title | Linked from menu | Comment |
|---|---|---|---|---|
| `/contact-info/` | 0 | Contact Info – Soil Food Web Foundation | no | **empty** (no content at all); `/contact/` redirects here; footer 'Media and press' lands here |
| `/contact/` | 0 | Contact Info – Soil Food Web Foundation | yes | 301 → `/contact-info/` (empty) |
| `/foundation-legal/` | 0 | Foundation legal – Soil Food Web Foundation | no | **empty**; hidden (REST only) |
| `/workshops/` | 1 | Workshops – Soil Food Web Foundation | yes | **only the H1 'Workshops'**; linked from header, footer, homepage card |
| `/invite-us-to-speak/` | 4 | Invite us to speak – Soil Food Web Foundation | yes | only the H1; linked from footer and donations |
| `/logo-brand-use/` | 4 | Logo and name use – Soil Food Web Foundation | yes | only the H1; linked from footer |
| `/student-map/` | 12 | Student Map – Soil Food Web Foundation | no | hidden; map embed only |
| `/scholarship-opportunities/` | 21 | Scholarship Opportunities​​​​​​​ – Soil Food Web Foundation | no | one sentence + a form (form markup not counted) |
| `/directory-portal/` | 38 | Directory Portal – Soil Food Web Foundation | no | login-code form only (functional page) |
| `/community/` | 71 | Community – Soil Food Web Foundation | yes | intro + JS map, no text content |
| `/team/` | 116 | Team – Soil Food Web Foundation | no | hidden duplicate of the About 'Our team' section |
| `/login/` | 136 | login – Soil Food Web Foundation | yes | functional page |
| `/news/page/2/` | 156 | News and stories – Page 2 – Soil Food Web Foundation | no | archive |
| `/donations/` | 240 | Donate – Soil Food Web Foundation | yes | placeholder note inside; see 1.1 |
| `/publications/?sfw_pub_collection=internet-articles` | 242 | Publications – Soil Food Web Foundation | no |  |
| `/practice/` | 264 | Projects – Soil Food Web Foundation | yes | video playlist titles only; title tag says 'Projects' while H1 says 'Taking Action…' |
| `/calendar/` | 286 | Calendar – Soil Food Web Foundation | yes | event list |
| `/scholarship/` | 291 | Scholarship – Soil Food Web Foundation | yes | placeholder + fake testimonials |
| `/news/` | 297 | News and stories – Soil Food Web Foundation | yes | listing page |

Item and archive pages under 300 words: attachment (query): 8 pages (median 120 words); attachment page: 20 pages (median 66 words); author archive: 1 pages (median 201 words); calendar-event: 4 pages (median 191 words); category archive: 12 pages (median 88 words); date archive: 13 pages (median 96 words); directory-member: 170 pages (median 106 words); publication: 52 pages (median 34 words); system: 2 pages (median 53 words); tag archive: 21 pages (median 95 words); team-member: 19 pages (median 171 words); testimonial: 5 pages (median 71 words); video: 20 pages (median 66 words). Directory member and video pages are stubs by design but each one is a separate indexable URL.

### 1.5 Inconsistent facts between pages

| Fact | Version A | Version B | Pages |
|---|---|---|---|
| Countries | **100+** countries (homepage stat, `/community/`, `/news/`, `/timeline-preview/`, `/about-us/` timeline) | **130** countries (`/nonprofit-landing/`, PDC launch post Apr 2026 *"spans more than 130 countries"*, Foundation launch post Oct 2025 *"approximately 130 countries"*) | – |
| Students | **10,000+** individuals enrolled (homepage, timeline) | **6000+** students (`/nonprofit-landing/`) | – |
| Relationship School ↔ Foundation | *"Soil Food Web School is a program of the Soil Food Web Foundation"* (homepage footer block, `/about-us/`) | *"The Foundation operates the Soil Food Web School as a doing-business-as (DBA) name"* (`/privacy/` §1, `/terms/` §1) | – |
| Tax status | *"A 501(c)(3) nonprofit"* / *"gifts are tax-deductible"* (footer, `/donations/`, `/about-us/`, copyright line) | 501(c)(3) status **pending**; donations via fiscally sponsored *Soil Food Web Fund* (`/terms/` §4; launch post) | – |
| Effective dates | Privacy Policy: *Version 1.0 \| Effective Date: October 16th, **2025*** | Terms of Use: *Version 1.0 \| Effective Date: October 16th, **2026*** (two weeks in the future at audit time) | `/privacy/`, `/terms/` |
| Refund rules | `/terms/` §3: *"full refund within 30 days of registration provided you have not accessed a substantial portion of the course content"*; *"Refund terms are specified at enrollment"*; donations non-refundable | No program, workshop or calendar-event page on this site states any refund terms; `/scholarship/` promises *"the same guarantee as every student"* without saying what it is | `/terms/`, `/scholarship/`, `/calendar-event/*` |
| Website address in Privacy Policy | *"our website at www.soilfoodweb.com"* | site is launching at soilfoodweb.com; fine if that is the final host | `/privacy/` |
| Contact e-mails | `info@soilfoodweb.com` (off-canvas menu, About, Terms, Privacy, Publications); `evan@soilfoodweb.com` (team page) | `ebuckman@soilfoodwebfoundation.org`, `jlnoel@…`, `loida@…`, `lwlewis@soilfoodwebfoundation.org` (launch post) — a second domain | – |
| Organisation name | 'Soil Food Web Foundation', 'Soil Food Web School' | 'Soil Foodweb Inc.' (historic company, timeline + retirement post) – correct historically, but 'Soil Food Web school' with lower-case s appears in the launch post | – |
| Product name | 'BioComplete™' | 'Biocomplete™' (Foundation Course 2 card on homepage, programs pages; `/nonprofit-landing/`) | – |
| Title vs H1 | `/practice/` title 'Projects', H1 'Taking Action toward a Healthier World', menu label 'Practice' | – | `/practice/` |

### 1.6 Typos and copy errors

| Page | Text | Fix |
|---|---|---|
| `/programs-overview/` | *"completing prerequesites which are clearly defined"* | prerequisites |
| `/october-2025-newsletter/` | link text *"Spoil Sponge Workshop"* | Soil Sponge Workshop |
| Homepage, `/programs-overview/`, `/programs-carousel-preview/` | course link `school.soilfoodweb.com/courses/foundation-**couse**-1` (9 links: card image, title and 'Learn more →' on three pages) | **confirmed 404** on Thinkific; `foundation-course-1` returns 200 |
| `/2025-in-review-…/` | *"with all the work that that effort entailed"* | remove one 'that' (or keep, it is grammatical but reads badly) |
| `/publications/` | *"NRCS Soil Quality Institute, USDA USDA"* | duplicate 'USDA' |
| `/templates-2/` | *"online presense"*, `/templates/` *"Square footage optimzation"* | demo pages – delete |
| `/nonprofit-landing/` | *"Check out Kevin treck some of the most intense courses"* | demo text – delete |
| `/scholarship-opportunities/` | page title contains seven zero-width spaces: 'Scholarship Opportunities\u200b\u200b…' | clean the title |
| `/how-it-works/` | the paragraph *"Beneficial bacteria produce glues that bind soil particles into microaggregates…"* appears twice on the page | remove duplicate |
| `/obituary-for-dr-elaine-ingham/` | the paragraph *"In addition to her paradigm shifting research…"* appears twice | remove duplicate |
| `/privacy/` | every bullet in §3 (legal bases) and §8 (your rights) is rendered twice | duplicated list markup |
| `/sadhguru-and-the-soil-food-web/` | two quotes appear twice (pull-quote plus body) | check intended |
| `/unconditional-freedom-at-home-and-in-the-world/`, `/a-blueprint-to-return-to-the-garden-of-eden/` | author photos have `src="http://47749"` and `src="http://73685"` (broken images, titles 'Bob Wilms', 'Philip Barton') | re-insert images |
| `/login/` | second 'Log in' button ('Original platform') → `#` | add the old platform URL |
| `/calendar/` | 'Community Event' is filed under event type *Webinars*; the three intensive courses are filed under *Promotions*; the date reads *"16 October 2026, 3:27 p.m. UTC"* | check event types/times |
| `/calendar-event/sfw-turns-one/` | *"could not unhear it"* | intentional? |
| homepage, `/login/`, `/nonprofit-landing/` | 'soil-ution' pun; 'Soil-ution' capitalised differently on `/nonprofit-landing/` | consistency |
| 'On-line Courses' (footer) vs 'Online Courses' (header) | | consistency |

Spell-check of all main-content text (lower-case words not in an English dictionary) found no other misspellings; the remaining unknown words are scientific terms, names and URLs.

### 1.7 Images

Unique images referenced on the site (src and srcset, all sections): 1280; checked by HEAD request. **103 files are over 500 KB**, 98 are named *Screenshot…*, and 326 are PNG. Below: images in page body content only.

**Body images over 500 KB (50):**

| Size | Type | File | Used on |
|---|---|---|---|
| 4.2 MB | png | `/wp-content/uploads/2025/11/Daniel-Tyrkiel-adam-swam-Presentation.png` | /join-the-free-webinar-series-a-living-legacy-the-science-of-the-soil-food-web/ |
| 3.7 MB | png | `/wp-content/uploads/2026/09/CIC-4.png` | /calendar-event/compost-intensive-course-2027-cohort-1/, /calendar-event/compost-intensive-course-2027-cohort-2/ |
| 2.7 MB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM.png` | /student-profile-su-kahumbu-stephanou/ |
| 2.4 MB | png | `/wp-content/uploads/2026/09/Screenshot-2026-09-29-161820.png` | / |
| 1.6 MB | png | `/wp-content/uploads/2026/09/PDC-Community-3.png` | /calendar-event/permaculture-design-certificate-2026-cohort-3/, /calendar-event/permaculture-design-certificate-2027-cohort-1/, /calendar-event/permaculture-design-certificate-2027-cohort-2/ |
| 1.6 MB | png | `/wp-content/uploads/2026/06/aysen-1024x954.png` | /team-member/aysen-ustunay/ |
| 1.5 MB | png | `/wp-content/uploads/2026/02/Eric-Feiler-4.png` | /soil-food-web-foundation-welcomes-eric-feiler/ |
| 1.4 MB | jpeg | `/wp-content/uploads/2026/02/Elaine-Ceremonial-Compost-Group-Photo-scaled-1.jpg` | /obituary-for-dr-elaine-ingham/ |
| 1.4 MB | png | `/wp-content/uploads/2026/06/ib-1024x1024.png` | /team-member/ib-borup-pedersen/ |
| 1.3 MB | jpeg | `/wp-content/uploads/2026/08/IMG_3426-1-scaled.jpg` | /calendar-event/aw-new-mexico-usa-2027/, /calendar-event/sfw-turns-one/ |
| 1.1 MB | png | `/wp-content/uploads/2026/06/Screenshot-2026-06-16-172957.png` | /team-member/loida-vasquez/ |
| 1.1 MB | png | `https://www.soilfoodweb.com/wp-content/uploads/2024/12/Copy-of-5-December-2024-Presentation-1.png` | /celebrating-world-soil-day-2024/ |
| 1.0 MB | png | `/wp-content/uploads/2025/11/Daniel-Tyrkiel-adam-swam-Presentation-800x800.png` | /2025/11/, /author/admin/, /author/admin/page/1/ |
| 1.0 MB | png | `/wp-content/uploads/2026/08/Birgit-Albertsmeier.png` | /directory-member/birgit-albertsmeier/ |
| 1.0 MB | webp | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-172507.png` | /how-it-works/ |
| 1.0 MB | png | `/wp-content/uploads/2026/06/isadora.png` | /, /about-us/, /programs-carousel-preview/ |
| 1.0 MB | png | `/wp-content/uploads/2026/06/Screenshot-2026-06-16-172957-768x724.png` | /about-us/, /team/ |
| 1.0 MB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM-800x728.png` | /2025/02/, /author/admin/page/2/, /tag/africa/ |
| 0.9 MB | png | `/wp-content/uploads/2025/11/Daniel-Tyrkiel-adam-swam-Presentation-1024x576.png` | /category/events/, /news/ |
| 0.9 MB | png | `/wp-content/uploads/2026/06/delvin.png` | /team-member/delvin-solkinson/ |
| 0.9 MB | png | `/wp-content/uploads/2026/08/Profile-photo.png` | /directory-member/barry-mckenna/ |
| 0.9 MB | png | `/wp-content/uploads/2026/06/eric.png` | /team-member/eric-feiler/ |
| 0.9 MB | png | `/wp-content/uploads/2026/06/ib-768x768.png` | /about-us/, /team/ |
| 0.8 MB | png | `/wp-content/uploads/2025/11/Daniel-Tyrkiel-adam-swam-Presentation-900x600.png` | /help-us-celebrate-food-knowledge-and-culture-in-sacramento-this-september/, /soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan/ |
| 0.8 MB | png | `/wp-content/uploads/2026/08/Screenshot-2023-11-20-at-3.17.51-pm.png` | /directory-member/kylie-pickles/ |
| 0.8 MB | png | `/wp-content/uploads/2026/06/brian.png` | /about-us/, /team-member/brian-daubenspeck/, /team/ |
| 0.8 MB | jpeg | `/wp-content/uploads/2026/08/pile-turning-wes-8-scaled.jpg` | /calendar-event/aw-costa-rica-2027/ |
| 0.8 MB | png | `/wp-content/uploads/2026/06/dora.png` | /team-member/dora-tkalec/ |
| 0.8 MB | png | `/wp-content/uploads/2026/06/delvin-768x736.png` | /about-us/, /team/ |
| 0.7 MB | png | `/wp-content/uploads/2026/08/72d55306-29d6-4f2b-9d2d-2787b0089fc6.png` | /directory-member/kent-holle/ |
| 0.7 MB | png | `/wp-content/uploads/2026/05/How-A-Rare-Microscope-Sighting-Desktop-Header-1920×720-scaled.png` | /ciliates-soil-health-microscope-watermelon-crop/ |
| 0.7 MB | png | `/wp-content/uploads/2026/06/wes.png` | /about-us/, /team-member/wesley-sander/, /team/ |
| 0.7 MB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM-1024x362.png` | /category/blogposts/, /news/page/2/ |
| 0.7 MB | png | `/wp-content/uploads/2026/09/1181504_custom_site_themes_id_bzIUE4jRKy3PIhzujoI7_6.png` | /, /programs-carousel-preview/, /programs-overview/ |
| 0.6 MB | webp | `/wp-content/uploads/2026/06/aysen-768x716.png` | /about-us/, /team/ |
| 0.6 MB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-120805.png` | /directory-member/brian-vagg/ |
| 0.6 MB | png | `/wp-content/uploads/2026/06/evan.png` | /about-us/, /team-member/evan-buckman/, /team/ |
| 0.6 MB | jpeg | `/wp-content/uploads/2026/09/mar-group-photo-2.jpg` | /community/ |
| 0.6 MB | jpeg | `/wp-content/uploads/2026/09/garden-vegetable-beds.jpg` | /practice/ |
| 0.6 MB | png | `/wp-content/uploads/2026/08/Screenshot-2026-07-08-162052.png` | /directory-member/maria-loper/ |
| 0.6 MB | png | `/wp-content/uploads/2026/06/casey.png` | /about-us/, /team-member/casey-williams/, /team/ |
| 0.6 MB | jpeg | `/wp-content/uploads/2025/12/2025-year-in-review-Elaine-scaled-1.jpg` | /2025-in-review-a-time-of-transition-honoring-our-founder-and-guiding-spirit-building-stronger-community-and-preparing-for-a-bright-future/ |
| 0.6 MB | png | `/wp-content/uploads/2026/06/eric-768x792.png` | /about-us/, /team/ |
| 0.6 MB | jpeg | `https://www.soilfoodweb.com/wp-content/uploads/2024/03/Phili-Bartons-Syntropic-Forest-Background-Masthead-Images-2742-by-1202-pixels-scaled.jpg` | /a-blueprint-to-return-to-the-garden-of-eden/ |
| 0.6 MB | png | `/wp-content/uploads/2026/06/dora-768x730.png` | /about-us/, /team/ |
| 0.6 MB | png | `/wp-content/uploads/2026/09/1181504_custom_site_themes_id_o0QkYPRBTyujGFmi9M6p_thinkific-images-5.png` | /, /programs-carousel-preview/, /programs-overview/ |
| 0.5 MB | png | `/wp-content/uploads/2026/08/me2-616x1024.png` | /directory-member/corinne-gwyther/ |
| 0.5 MB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-125226.png` | /directory-member/renald-flores/ |
| 0.5 MB | png | `/wp-content/uploads/2024/12/Copy-of-5-December-2024-Presentation-1-800x800.png` | /2024/12/, /author/admin/page/2/, /tag/world-soil-day/ |
| 0.5 MB | webp | `/wp-content/uploads/2026/06/stephanie.png` | /about-us/, /team-member/stephanie-mcdaniel/, /team/ |

**Body images that are screenshots (file name 'Screenshot…', 30):**

| Size | Type | File | Used on |
|---|---|---|---|
| 2781 KB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM.png` | /student-profile-su-kahumbu-stephanou/ |
| 2415 KB | png | `/wp-content/uploads/2026/09/Screenshot-2026-09-29-161820.png` | / |
| 1147 KB | png | `/wp-content/uploads/2026/06/Screenshot-2026-06-16-172957.png` | /team-member/loida-vasquez/ |
| 994 KB | webp | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-172507.png` | /how-it-works/ |
| 991 KB | png | `/wp-content/uploads/2026/06/Screenshot-2026-06-16-172957-768x724.png` | /about-us/, /team/ |
| 983 KB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM-800x728.png` | /2025/02/, /author/admin/page/2/, /tag/africa/ |
| 848 KB | png | `/wp-content/uploads/2026/08/Screenshot-2023-11-20-at-3.17.51-pm.png` | /directory-member/kylie-pickles/ |
| 683 KB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM-1024x362.png` | /category/blogposts/, /news/page/2/ |
| 639 KB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-120805.png` | /directory-member/brian-vagg/ |
| 621 KB | png | `/wp-content/uploads/2026/08/Screenshot-2026-07-08-162052.png` | /directory-member/maria-loper/ |
| 543 KB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-125226.png` | /directory-member/renald-flores/ |
| 454 KB | png | `/wp-content/uploads/2025/02/Screenshot-2025-02-05-at-5.18.21-PM-600x403.png` | /2025-in-review-a-time-of-transition-honoring-our-founder-and-guiding-spirit-building-stronger-community-and-preparing-for-a-bright-future/, /october-2025-newsletter/ |
| 420 KB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-122852.png` | /directory-member/elias-bajalia/ |
| 371 KB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-121537.png` | /directory-member/casey-ernst/ |
| 305 KB | png | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-171946.png` | /about-us/ |
| 263 KB | png | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-171953.png` | /about-us/ |
| 240 KB | png | `/wp-content/uploads/2026/08/Screenshot-2023-04-26-at-4.58.18-PM.png` | /directory-member/astrid-harris/, /find-a-professional/ |
| 237 KB | png | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-172024.png` | /about-us/ |
| 209 KB | png | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-171937.png` | /about-us/ |
| 185 KB | png | `/wp-content/uploads/2026/08/Screenshot-2026-03-03-124126.png` | /directory-member/kevin-fretz/ |
| 179 KB | webp | `/wp-content/uploads/2026/09/Screenshot-2026-09-17-173253.png` | /how-it-works/ |
| 157 KB | jpeg | `/wp-content/uploads/2025/10/Screenshot-2025-10-22-212600.jpg` | /soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan/ |
| 106 KB | jpeg | `/wp-content/uploads/2025/10/Screenshot-2025-10-22-212600-1024x643.jpg` | /category/events/, /news/ |
| 103 KB | jpeg | `/wp-content/uploads/2026/08/Screenshot_20260124_123325_Gallery2.jpg` | /directory-member/dora-tkalec/ |
| 96 KB | jpeg | `/wp-content/uploads/2025/10/Screenshot-2025-10-22-212600-800x800.jpg` | /2025/10/, /author/admin/, /author/admin/page/1/ |
| 95 KB | jpeg | `/wp-content/uploads/2026/08/Screenshot_20210507-152741_Samsung-Internet-1024x701.jpg` | /directory-member/sarah-talia/ |
| 87 KB | jpeg | `/wp-content/uploads/2025/10/Screenshot-2025-10-22-212600-900x600.jpg` | /help-us-celebrate-food-knowledge-and-culture-in-sacramento-this-september/, /join-the-free-webinar-series-a-living-legacy-the-science-of-the-soil-food-web/ |
| 59 KB | jpeg | `/wp-content/uploads/2026/08/Screenshot_20260225_110348_Gallery.jpg` | /directory-member/dan-shazar/ |
| 52 KB | jpeg | `/wp-content/uploads/2026/08/Screenshot-2026-02-10-164537-823x1024.jpg` | /directory-member/alex-goemans/ |
| 46 KB | jpeg | `/wp-content/uploads/2025/10/Screenshot-2025-10-22-212600-600x403.jpg` | /soil-food-web-foundation-welcomes-eric-feiler/ |

The homepage hero/stat image `Screenshot-2026-09-29-161820-1024x606.png` (1.0 MB) and the `/how-it-works/` diagrams (`Screenshot-2026-09-17-172507.png`, 1.0 MB; `…173253.png`) are screenshots used as content graphics. The largest file on the site is `Daniel-Tyrkiel-adam-swam-Presentation.png` at 4.4 MB on the webinar post. All 405 responsive `srcset` variants returned 200. Images whose size is reported as 0 KB had no Content-Length header and were re-measured by downloading them. Two `<img>` tags have numeric `src` values (`http://47749`, `http://73685`) and are broken.

### 1.8 Viewport blocks zoom

410 of 412 HTML pages use `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0">`, which disables pinch-zoom (WCAG 1.4.4 failure; Lighthouse flags it). Only `/wp-login.php` uses a normal viewport. This is a Salient theme setting ('Prevent user scaling / zoom').

### 1.9 Everything is noindex

All 412 HTML pages send `<meta name='robots' content='noindex, nofollow'>` (WordPress 'Discourage search engines'). Correct for staging, but it must be switched off at launch or Google Ads cannot verify the site. Canonicals point to `new.soilfoodweb.com` on every page and will need the host swap. Canonical tags that differ from the URL: `/contact/` (canonical of its redirect target `/contact-info/`), `/news/page/2/` (→ `/news/`, so page 2 is not indexable), the three `/publications/?sfw_pub_collection=…` views (→ `/publications/`, fine), and the doubled `/directory-member/miguel-ventura-%C2%A6-permabiologic/` (canonical uses lower-case encoding).

## 2. Cache check

Every URL was fetched twice (plain, then `?nocache=12345`). For each pair the HTTP status, title, H1, canonical, robots, header-menu links, off-canvas-menu links, footer links and the main-content text were compared.

* **Result: no page is stuck in a cache.** All 689 URL pairs matched on status, title, H1, header menu, off-canvas menu and footer. Only one header-menu version (`menu-v1`), one off-canvas version (`ocm-v1`) and one footer version (`footer-v1`) exist across the whole site (see the `*_version` columns in `pages.csv`).
* Cloudflare is in front of the site. Every HTML response carried `cf-cache-status: DYNAMIC` (not cached at the edge); images were `HIT`/`REVALIDATED`/`MISS`. No page-cache plugin signature (LiteSpeed, WP Rocket, W3TC, Super Cache, SG, Breeze, Cache Enabler) was found in any HTML.
* Six pairs differed in main text, all harmlessly: the 'Related posts' block on three blog posts is randomised per request (`/obituary-for-dr-elaine-ingham/`, `/ciliates-soil-health-microscope-watermelon-crop/`, `/soil-food-web-foundation-welcomes-eric-feiler/`); the directory listing order on `/find-a-professional/` and `/sfw-directory/` is randomised; the Cloudflare e-mail-protection page changes its token. The off-canvas menu's obfuscated e-mail link also changes its hash on every request, which is why a raw HTML diff shows a difference on 436 pages. The `cache_note` column explains each case.
* **Old events:** the off-canvas 'Happening now' list shows *5 October – 24 December Permaculture Design Certificate | 2026 Cohort #3* and *16 October Community Event | Celebrating Our First Year as a Foundation!*, identical in both versions. The calendar shows 8 future events (Oct 2026 – Oct 2027) and no past events. If editors see an older menu or events in a browser, that is browser-side (or logged-in) caching, not the server.
* Two calendar events exist in the REST API but are not shown on `/calendar/` (window is 12 months): *Permaculture Design Certificate | 2027 Cohort #1* and *| 2027 Cohort #2*; both pages are live and linked from other event pages.

## 3. Comparison with the approved URL plan

| Approved address | On staging today | Address that holds the content | Real content? | Notes |
|---|---|---|---|---|
| `/about/` | **301 → `/video/about-the-soil-food-web/`** (WordPress guessed a 404 redirect to a video page) | `/about-us/` (880 words) | yes | `/about/` must become the real page or redirect to `/about-us/`; the current guess sends visitors to a video |
| `/programs/` | **301 → `/programs-carousel-preview/`** (redirect guess to a hidden preview page) | `/programs-overview/` (1,231 words) | yes | same problem; `/programs-carousel-preview/` is a 748-word component preview |
| `/scholarships/` | **404** | `/scholarship/` (291 words) + `/scholarship-opportunities/` (21 words, form) | partly | content thin, placeholder note, five fake testimonials, donate link 404 |
| `/directory/` | **301 → `/directory-portal/`** (login-code form, 38 words) | `/find-a-professional/` (625 words, 170 members) and hidden duplicate `/sfw-directory/` (449 words) | yes | `/directory/` must point at the public directory, not the member login |
| `/contact/` | **301 → `/contact-info/`** (empty page, 0 words) | contact details live inside `/about-us/#contact-legal`; footer 'Contact us' points there | no | no standalone contact page exists; `/contact-info/` is empty |
| `/case-studies/` | **404** | `/practice/#CASE-STUDIES` (264 words: video playlist titles) + 20 `/video/*` pages | partly | videos only, no written case studies |
| `/work-with-us/` | **404** | `/practice/#work-with-us` (one paragraph) | no | anchor section only |
| `/speaking/` | **404** | `/invite-us-to-speak/` (heading only, 4 words) | no | empty page |
| `/press/` | **404** | footer 'Media and press' → `/contact/` → empty | no | nothing exists |
| `/donations/` | 200 | `/donations/` (240 words) | partly | placeholder, empty CTAs, footer links to `/donate/` (404) |
| `/volunteer/` | 200 | `/volunteer/` (357 words) | partly | it is a near-copy of the About page (mission, vision, history, team anchors) with one 'Volunteer' angle; in-page links to `#team` and `#contact-legal` point at anchors that do not exist on this page; 'Read her published research →' → `#` |
| `/workshops/` | 200 | `/workshops/` (1 word) | **no** | only the H1; linked from header, footer and the homepage programs card |
| `/calendar/` | 200 | `/calendar/` (286 words, 8 events) | yes |  |
| `/news/` | 200 | `/news/` (297 words, 18 posts, 2 listing pages) | yes | title 'News and stories'; category pages `/category/school-update/`, `/spanish/`, `/uncategorized/`, `/webinars/` are empty archives; 'School Update' and 'School Updates' are duplicate categories |
| `/community/` | 200 | `/community/` (71 words + JS map) | thin | header 'Join the Community' goes to the Thinkific community, not here |
| `/how-it-works/` | 200 | `/how-it-works/` (475 words) | yes | duplicate paragraph, two H1s, screenshot diagrams |
| `/publications/` | 200 | `/publications/` (4,112 words, 134 entries) | yes | 'Start a research conversation' button has empty href; one 'citation not verified'; 82 DOI redirects unverifiable from here |
| `/login/` | 200 | `/login/` (136 words) | yes | second 'Log in' → `#`; 'Join the community' → programs |
| `/privacy/` | 200 | `/privacy/` (1,358 words) | yes | effective 16 Oct 2025; duplicated bullets |
| `/terms/` | 200 | `/terms/` (1,358 words) | yes | effective 16 Oct **2026**; says 501(c)(3) pending |

WordPress's 'redirect guess' (`redirect_guess_404_permalink`) is turning four of the planned addresses into redirects to the wrong pages. Disable it or create the real pages/redirects before launch.

## 4. Current site tree (689 URLs fetched)

Legend: words = main-content word count; `menu` = linked from header, off-canvas or footer; `REST-only` = found only through the REST API (nothing links to it); status in brackets when not 200.


### page (35)

* `/`, 1433 words — *Soil Food Web Foundation* — menu
* `/about-us/`, 880 words — *About Us – Soil Food Web Foundation* — menu
* `/calendar/`, 286 words — *Calendar – Soil Food Web Foundation* — menu
* `/community/`, 71 words — *Community – Soil Food Web Foundation* — menu
* `/contact-info/`, 0 words — *Contact Info – Soil Food Web Foundation* — REST-only (orphan)
* `/directory-portal/`, 38 words — *Directory Portal – Soil Food Web Foundation*
* `/donations/`, 240 words — *Donate – Soil Food Web Foundation* — menu
* `/find-a-professional/`, 625 words — *Find a Professional – Soil Food Web Foundation* — menu
* `/foundation-legal/`, 0 words — *Foundation legal – Soil Food Web Foundation* — REST-only (orphan)
* `/how-it-works/`, 475 words — *How It Works – Soil Food Web Foundation* — menu
* `/invite-us-to-speak/`, 4 words — *Invite us to speak – Soil Food Web Foundation* — menu
* `/login/`, 136 words — *login – Soil Food Web Foundation* — menu
* `/logo-brand-use/`, 4 words — *Logo and name use – Soil Food Web Foundation* — menu
* `/news/`, 297 words — *News and stories – Soil Food Web Foundation* — menu
* `/news/page/2/`, 156 words — *News and stories – Page 2 – Soil Food Web Foundation*
* `/nonprofit-landing/`, 572 words — *Nonprofit Landing – Soil Food Web Foundation* — REST-only (orphan)
* `/practice/`, 264 words — *Projects – Soil Food Web Foundation* — menu
* `/privacy/`, 1358 words — *Privacy – Soil Food Web Foundation* — menu
* `/programs-carousel-preview/`, 748 words — *Programs carousel preview – Soil Food Web Foundation* — REST-only (orphan)
* `/programs-overview/`, 1231 words — *Programs Overview – Soil Food Web Foundation* — menu
* `/publications/`, 4112 words — *Publications – Soil Food Web Foundation* — menu
* `/publications/?sfw_pub_collection=dr-elaines-publications`, 2642 words — *Publications – Soil Food Web Foundation*
* `/publications/?sfw_pub_collection=internet-articles`, 242 words — *Publications – Soil Food Web Foundation*
* `/publications/?sfw_pub_collection=other-relevant-publications`, 1530 words — *Publications – Soil Food Web Foundation*
* `/scholarship-opportunities/`, 21 words — *Scholarship Opportunities​​​​​​​ – Soil Food Web Foundation*
* `/scholarship/`, 291 words — *Scholarship – Soil Food Web Foundation* — menu
* `/sfw-directory/`, 449 words — *SFW Directory – Soil Food Web Foundation* — REST-only (orphan)
* `/student-map/`, 12 words — *Student Map – Soil Food Web Foundation* — REST-only (orphan)
* `/team/`, 116 words — *Team – Soil Food Web Foundation* — REST-only (orphan)
* `/templates-2/`, 3020 words — *templates 2 – Soil Food Web Foundation* — REST-only (orphan)
* `/templates/`, 2478 words — *Templates – Soil Food Web Foundation* — REST-only (orphan)
* `/terms/`, 1358 words — *Terms & Conditions – Soil Food Web Foundation* — menu
* `/timeline-preview/`, 339 words — *Timeline preview – Soil Food Web Foundation* — REST-only (orphan)
* `/volunteer/`, 357 words — *Volunteer – Soil Food Web Foundation* — menu
* `/workshops/`, 1 words — *Workshops – Soil Food Web Foundation* — menu

### post (18)

* `/2025-in-review-a-time-of-transition-honoring-our-founder-and-guiding-spirit-building-stronger-community-and-preparing-for-a-bright-future/`, 1650 words — *2025 in Review: A time of transition – honoring our founder and guidin*
* `/a-blueprint-to-return-to-the-garden-of-eden/`, 948 words — *Harnessing Ernst Gotch’s Agroecological Wisdom: A Blueprint to Return *
* `/celebrating-world-soil-day-2024/`, 663 words — *Celebrating World Soil Day 2024 – Soil Food Web Foundation*
* `/ciliates-soil-health-microscope-watermelon-crop/`, 1015 words — *How A Rare Microscope Sighting Helps Deduce The Problem With Unhealthy*
* `/exploring-soil-food-web-innovations-in-west-africa/`, 936 words — *Exploring Soil Food Web Innovations in West Africa – Soil Food Web Fou*
* `/help-us-celebrate-food-knowledge-and-culture-in-sacramento-this-september/`, 419 words — *Help us celebrate food, knowledge and culture in Sacramento this Septe*
* `/join-the-free-webinar-series-a-living-legacy-the-science-of-the-soil-food-web/`, 599 words — *🌱 Join the Free Webinar Series: A Living Legacy — The Science of the S*
* `/obituary-for-dr-elaine-ingham/`, 607 words — *Obituary for Dr. Elaine Ingham – Soil Food Web Foundation*
* `/october-2025-newsletter/`, 1271 words — *October 2025 – Newsletter – Soil Food Web Foundation*
* `/retirement-announcement-dr-elaine-ingham/`, 580 words — *Retirement Announcement: Dr. Elaine Ingham – Soil Food Web Foundation*
* `/sadhguru-and-the-soil-food-web/`, 679 words — *Sadhguru and the Soil Food Web – Soil Food Web Foundation*
* `/soil-food-web-advanced-programs-reopen-2026/`, 1148 words — *Soil Food Web School Advanced Programs Are Reopening! – Soil Food Web *
* `/soil-food-web-foundation-launches-as-nonprofit-to-carry-forward-dr-elaine-inghams-legacy/`, 670 words — *Soil Food Web Foundation Launches as Nonprofit to Carry Forward Dr. El*
* `/soil-food-web-foundation-welcomes-eric-feiler/`, 763 words — *The Soil Food Web Welcomes a New Board Member – Eric Feiler – Soil Foo*
* `/soil-food-web-school-first-permaculture-design-certificate-course/`, 1283 words — *The Soil Food Web School Launches Its First-Ever Permaculture Design C*
* `/soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan/`, 800 words — *Soil Health Week 2025: Wild Soils UK and TrashIt Bring the Soil Food W*
* `/student-profile-su-kahumbu-stephanou/`, 588 words — *Student Profile: Su Kahumbu Stephanou – Soil Food Web Foundation*
* `/unconditional-freedom-at-home-and-in-the-world/`, 1568 words — *Unconditional Freedom: At Home and in the World – Soil Food Web Founda*

### calendar-event (10)

* `/calendar-event/aw-costa-rica-2027/`, 191 words — *Accelerator Workshop \| Costa Rica – Soil Food Web Foundation*
* `/calendar-event/aw-new-mexico-usa-2027/`, 229 words — *Accelerator Workshop \| New Mexico USA – Soil Food Web Foundation*
* `/calendar-event/aw-uk-2027/`, 106 words — *Accelerator Workshop \| UK – Soil Food Web Foundation*
* `/calendar-event/biological-liquid-amendments-intensive-course/`, 116 words — *Biological Liquid Amendments Intensive Course – Soil Food Web Foundati*
* `/calendar-event/compost-intensive-course-2027-cohort-1/`, 334 words — *Compost Intensive Course \| 2027 Cohort #1 – Soil Food Web Foundation*
* `/calendar-event/compost-intensive-course-2027-cohort-2/`, 334 words — *Compost Intensive Course \| 2027 Cohort #2 – Soil Food Web Foundation*
* `/calendar-event/permaculture-design-certificate-2026-cohort-3/`, 350 words — *Permaculture Design Certificate \| 2026 Cohort #3 – Soil Food Web Foun* — menu
* `/calendar-event/permaculture-design-certificate-2027-cohort-1/`, 351 words — *Permaculture Design Certificate \| 2027 Cohort #1 – Soil Food Web Foun*
* `/calendar-event/permaculture-design-certificate-2027-cohort-2/`, 353 words — *Permaculture Design Certificate \| 2027 Cohort #2 – Soil Food Web Foun*
* `/calendar-event/sfw-turns-one/`, 411 words — *Community Event \| Celebrating Our First Year as a Foundation! – Soil * — menu

### team-member (22)

* `/team-member/alex-andreou/`, 201 words — *Alex Andreou – Soil Food Web Foundation*
* `/team-member/aysen-ustunay/`, 160 words — *Ayşen Üstünay – Soil Food Web Foundation*
* `/team-member/brian-daubenspeck/`, 88 words — *Brian Daubenspeck – Soil Food Web Foundation*
* `/team-member/casey-williams/`, 131 words — *Casey Williams – Soil Food Web Foundation*
* `/team-member/delvin-solkinson/`, 303 words — *Delvin Solkinson – Soil Food Web Foundation*
* `/team-member/dora-tkalec/`, 202 words — *Dora Tkalec – Soil Food Web Foundation*
* `/team-member/dr-carla-ribeiro-machado-e-portugal/`, 216 words — *Dr. Carla Ribeiro Machado e Portugal – Soil Food Web Foundation*
* `/team-member/dr-elaine-ingham/`, 294 words — *Dr. Elaine Ingham – Soil Food Web Foundation*
* `/team-member/elena-kalli/`, 167 words — *Elena Kalli – Soil Food Web Foundation*
* `/team-member/eric-feiler/`, 85 words — *Eric Feiler – Soil Food Web Foundation*
* `/team-member/evan-buckman/`, 342 words — *Evan Buckman – Soil Food Web Foundation*
* `/team-member/gerald-ramirez/`, 124 words — *Gerald Ramírez – Soil Food Web Foundation*
* `/team-member/ib-borup-pedersen/`, 226 words — *Ib Borup Pedersen – Soil Food Web Foundation*
* `/team-member/isadora-shmidt/`, 194 words — *Isadora Shmidt – Soil Food Web Foundation*
* `/team-member/jenna-noel/`, 105 words — *Jenna Noel – Soil Food Web Foundation*
* `/team-member/leslie-w-lewis-ph-d/`, 173 words — *Leslie W. Lewis, Ph.D. – Soil Food Web Foundation*
* `/team-member/loida-vasquez/`, 179 words — *Loida Vasquez – Soil Food Web Foundation*
* `/team-member/nick-padwick/`, 279 words — *Nick Padwick – Soil Food Web Foundation*
* `/team-member/pranjal-rajput/`, 361 words — *Pranjal Rajput – Soil Food Web Foundation*
* `/team-member/sammie-bass/`, 155 words — *Sammie Bass – Soil Food Web Foundation*
* `/team-member/stephanie-mcdaniel/`, 107 words — *Stephanie McDaniel – Soil Food Web Foundation*
* `/team-member/wesley-sander/`, 171 words — *Wesley Sander – Soil Food Web Foundation*

### testimonial (5)

* `/testimonial/amara-okafor/`, 73 words — *Amara Okafor – Soil Food Web Foundation*
* `/testimonial/david-vance/`, 71 words — *David Vance – Soil Food Web Foundation*
* `/testimonial/john-doe/`, 85 words — *John Doe – Soil Food Web Foundation*
* `/testimonial/marcus-thorne/`, 69 words — *Marcus Thorne – Soil Food Web Foundation*
* `/testimonial/yuki-tanaka/`, 68 words — *Yuki Tanaka – Soil Food Web Foundation*

### video (20)

* `/video/172-acre-park-project/`, 88 words — *172 Acre Park Project – Soil Food Web Foundation* — REST-only (orphan)
* `/video/4000-acres-norfolk-england/`, 112 words — *4,000 acres Norfolk, England – Soil Food Web Foundation* — REST-only (orphan)
* `/video/about-the-soil-food-web/`, 83 words — *About the Soil Food Web – Soil Food Web Foundation* — REST-only (orphan)
* `/video/adam-york/`, 66 words — *Adam York – Soil Food Web Foundation* — REST-only (orphan)
* `/video/alfalfa-potatoes-beans/`, 99 words — *Alfalfa, Potatoes, & Beans – Soil Food Web Foundation* — REST-only (orphan)
* `/video/compost-producers-keisha-and-casey/`, 34 words — *Compost Producers Keisha and Casey – Soil Food Web Foundation* — REST-only (orphan)
* `/video/consultants/`, 46 words — *Consultants – Soil Food Web Foundation* — REST-only (orphan)
* `/video/corn-soy-10000-acres/`, 102 words — *Corn & Soy: 10,000 Acres – Soil Food Web Foundation* — REST-only (orphan)
* `/video/cory-miller/`, 59 words — *Cory Miller – Soil Food Web Foundation* — REST-only (orphan)
* `/video/grapes-cannabis-turmeric-more/`, 103 words — *Grapes, Cannabis, Turmeric & more – Soil Food Web Foundation* — REST-only (orphan)
* `/video/jenn-sirp/`, 57 words — *Jenn Sirp – Soil Food Web Foundation* — REST-only (orphan)
* `/video/making-compost-extract-and-tea/`, 65 words — *Making Compost Extract and Tea – Soil Food Web Foundation* — REST-only (orphan)
* `/video/organic-banana-farm-south-africa/`, 130 words — *Organic Banana Farm, South Africa – Soil Food Web Foundation* — REST-only (orphan)
* `/video/renald-flores/`, 81 words — *Renald Flores – Soil Food Web Foundation* — REST-only (orphan)
* `/video/roberto-silva/`, 63 words — *Roberto Silva – Soil Food Web Foundation* — REST-only (orphan)
* `/video/sfw-consultant-brian-vagg/`, 33 words — *SFW Consultant Brian Vagg – Soil Food Web Foundation* — REST-only (orphan)
* `/video/sfw-consultant-nick-tomasini/`, 33 words — *SFW Consultant Nick Tomasini – Soil Food Web Foundation* — REST-only (orphan)
* `/video/sfw-consultant-todd-harrington/`, 33 words — *SFW Consultant Todd Harrington – Soil Food Web Foundation* — REST-only (orphan)
* `/video/students/`, 37 words — *Students – Soil Food Web Foundation* — REST-only (orphan)
* `/video/using-the-microscope/`, 87 words — *Using the Microscope – Soil Food Web Foundation* — REST-only (orphan)

### publication (134)

52 × 200, 82 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `publication`).
Publication pages with a DOI/external source redirect (301) to the source; the 52 without one are stub pages (median 33 words) such as `/publication/in-vitro-studies-on-control-of-soil-borne-plant-pathogens-by-earthworm-eudrilus-eugeniae-exudates/`.

### directory-member (170)

170 × 200, 0 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `directory-member`).

### category archive (12)

* `/category/blogposts/`, 211 words — *Blog – Soil Food Web Foundation*
* `/category/events/`, 140 words — *Events – Soil Food Web Foundation*
* `/category/features/`, 88 words — *Features – Soil Food Web Foundation*
* `/category/foundation-update/`, 88 words — *Foundation Update – Soil Food Web Foundation* — menu
* `/category/microscopy/`, 88 words — *Microscopy – Soil Food Web Foundation*
* `/category/newsletter/`, 69 words — *Newsletter – Soil Food Web Foundation*
* `/category/school-update/`, 66 words — *School Update – Soil Food Web Foundation* — REST-only (orphan)
* `/category/school-updates/`, 126 words — *School Updates – Soil Food Web Foundation*
* `/category/science-education/`, 88 words — *Science & Education – Soil Food Web Foundation*
* `/category/spanish/`, 66 words — *Spanish – Soil Food Web Foundation* — REST-only (orphan)
* `/category/uncategorized/`, 66 words — *Uncategorized – Soil Food Web Foundation* — REST-only (orphan)
* `/category/webinars/`, 66 words — *Webinars – Soil Food Web Foundation* — REST-only (orphan)

### tag archive (21)

21 × 200, 0 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `tag archive`).

### date archive (13)

13 × 200, 0 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `date archive`).

### author archive (3)

* `/author/admin/`, 377 words — *admin – Soil Food Web Foundation*
* `/author/admin/page/1/`, 377 words — *admin – Soil Food Web Foundation*
* `/author/admin/page/2/`, 201 words — *admin – Page 2 – Soil Food Web Foundation*

### attachment page (102)

20 × 200, 82 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `attachment page`).
Attachment pages (`/about-us/screenshot-…/`, `/calendar-event/…/img_1942/`, `/how-it-works/attachment/6/`, `/directory-member/<name>/<photo>/` …) 301-redirect to the image file, which is normal WordPress 6.4+ behaviour. They exist only because the REST media endpoint lists them.

### attachment (query) (8)

8 × 200, 0 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `attachment (query)`).

### non-public CPT item (query) (24)

0 × 200, 0 × redirect, 24 × 404. Full list in `pages.csv` (filter `page_type` = `non-public CPT item (query)`).
The 15 `sfw_program` and 9 `sfw_timeline` items are not publicly queryable; their REST `link` (`/?post_type=sfw_program&p=…`) returns 404. They are rendered inside other pages (programs carousel, About timeline). Harmless, but the REST API exposes them.

### media file (82)

82 × 200, 0 × redirect, 0 × 404. Full list in `pages.csv` (filter `page_type` = `media file`).
These are image files the crawler reached because attachment pages redirect to them.

### system (5)

* `/cdn-cgi/l/email-protection` [404] — *Email Protection \| Cloudflare* — menu
* `/comments/feed/`
* `/feed/`
* `/wp-login.php`, 53 words — *Log In ‹ Soil Food Web Foundation — WordPress*
* `/wp-login.php?action=lostpassword`, 39 words — *Lost Password ‹ Soil Food Web Foundation — WordPress*

### wp_navigation (1)

* `/navigation/` [404] — *Page not found – Soil Food Web Foundation* — REST-only (orphan)

### page/post (4)

* `/accessibility/` [404] — *Page not found – Soil Food Web Foundation* — menu
* `/contact/`, 0 words — *Contact Info – Soil Food Web Foundation* — menu
* `/donate-get-involved/` [404] — *Page not found – Soil Food Web Foundation*
* `/donate/` [404] — *Page not found – Soil Food Web Foundation* — menu

## 5. Hidden pages: nothing in any menu links to them

### 5.1 Pages no link on the site reaches at all (found only via the REST API)

| URL | Type | Words | Title | Comment |
|---|---|---|---|---|
| `/category/school-update/` | category archive | 66 | School Update – Soil Food Web Foundation | empty category (duplicate of 'School Updates') |
| `/category/spanish/` | category archive | 66 | Spanish – Soil Food Web Foundation | empty category |
| `/category/uncategorized/` | category archive | 66 | Uncategorized – Soil Food Web Foundation | empty category |
| `/category/webinars/` | category archive | 66 | Webinars – Soil Food Web Foundation | empty category |
| `/contact-info/` | page | 0 | Contact Info – Soil Food Web Foundation | empty; `/contact/` redirects here |
| `/foundation-legal/` | page | 0 | Foundation legal – Soil Food Web Foundation | empty |
| `/navigation/` | wp_navigation | 6 | Page not found – Soil Food Web Foundation | wp_navigation item; 404 |
| `/nonprofit-landing/` | page | 572 | Nonprofit Landing – Soil Food Web Foundation | old landing draft with demo text (see 1.3) |
| `/programs-carousel-preview/` | page | 748 | Programs carousel preview – Soil Food Web Foundation | component preview; `/programs/` redirects here by mistake |
| `/sfw-directory/` | page | 449 | SFW Directory – Soil Food Web Foundation | second copy of the directory (`/find-a-professional/` is the linked one) |
| `/student-map/` | page | 12 | Student Map – Soil Food Web Foundation | map embed only |
| `/team/` | page | 116 | Team – Soil Food Web Foundation | old team page; duplicates About › Our team |
| `/templates-2/` | page | 3020 | templates 2 – Soil Food Web Foundation | Salient demo page with Lorem ipsum |
| `/templates/` | page | 2478 | Templates – Soil Food Web Foundation | Salient demo page (see 1.3) |
| `/timeline-preview/` | page | 339 | Timeline preview – Soil Food Web Foundation | component preview; duplicates About timeline |

146 of the 170 `/directory-member/<name>/` pages have no inbound link in the static HTML: `/find-a-professional/` and `/sfw-directory/` render a random subset and load the rest with JavaScript ('Load more'), so a crawler without JavaScript (and Google's first pass) sees only a handful of members. One member URL is doubled by encoding (`/directory-member/miguel-ventura-%C2%A6-permabiologic/` and `…%c2%a6…`), and `/directory-member/alex-kellett/` has the title 'Norman Higgins'.

82 of the 134 `/publication/<slug>/` URLs have no inbound link: `/publications/` links each entry straight to its DOI or source, not to the WordPress item page. 82 of those unlinked item pages are themselves 301 redirects to the external source and 0 are stub pages with the citation only. The item pages are reachable only via the REST API.

The 20 `/video/<slug>/` canonical URLs also have zero inbound links: the site links to them only with a `?playlist=…` query string (40 URLs), so each video exists at two addresses. The attachment pages and the 3 `/publications/?sfw_pub_collection=…` filter views are likewise unlinked.

### 5.2 Pages that exist and are linked from content, but not from any menu

| URL | Words | Inbound links | Title |
|---|---|---|---|
| `/2025-in-review-a-time-of-transition-honoring-our-founder-and-guiding-spirit-building-stronger-community-and-preparing-for-a-bright-future/` | 1650 | 20 | 2025 in Review: A time of transition – honoring our founder and guidin |
| `/a-blueprint-to-return-to-the-garden-of-eden/` | 948 | 17 | Harnessing Ernst Gotch’s Agroecological Wisdom: A Blueprint to Return  |
| `/celebrating-world-soil-day-2024/` | 663 | 9 | Celebrating World Soil Day 2024 – Soil Food Web Foundation |
| `/ciliates-soil-health-microscope-watermelon-crop/` | 1015 | 12 | How A Rare Microscope Sighting Helps Deduce The Problem With Unhealthy |
| `/directory-portal/` | 38 | 2 | Directory Portal – Soil Food Web Foundation |
| `/exploring-soil-food-web-innovations-in-west-africa/` | 936 | 7 | Exploring Soil Food Web Innovations in West Africa – Soil Food Web Fou |
| `/help-us-celebrate-food-knowledge-and-culture-in-sacramento-this-september/` | 419 | 11 | Help us celebrate food, knowledge and culture in Sacramento this Septe |
| `/join-the-free-webinar-series-a-living-legacy-the-science-of-the-soil-food-web/` | 599 | 10 | 🌱 Join the Free Webinar Series: A Living Legacy — The Science of the S |
| `/news/page/2/` | 156 | 1 | News and stories – Page 2 – Soil Food Web Foundation |
| `/obituary-for-dr-elaine-ingham/` | 607 | 13 | Obituary for Dr. Elaine Ingham – Soil Food Web Foundation |
| `/october-2025-newsletter/` | 1271 | 15 | October 2025 – Newsletter – Soil Food Web Foundation |
| `/publications/?sfw_pub_collection=dr-elaines-publications` | 2642 | 4 | Publications – Soil Food Web Foundation |
| `/publications/?sfw_pub_collection=internet-articles` | 242 | 4 | Publications – Soil Food Web Foundation |
| `/publications/?sfw_pub_collection=other-relevant-publications` | 1530 | 4 | Publications – Soil Food Web Foundation |
| `/retirement-announcement-dr-elaine-ingham/` | 580 | 9 | Retirement Announcement: Dr. Elaine Ingham – Soil Food Web Foundation |
| `/sadhguru-and-the-soil-food-web/` | 679 | 6 | Sadhguru and the Soil Food Web – Soil Food Web Foundation |
| `/scholarship-opportunities/` | 21 | 1 | Scholarship Opportunities​​​​​​​ – Soil Food Web Foundation |
| `/soil-food-web-advanced-programs-reopen-2026/` | 1148 | 18 | Soil Food Web School Advanced Programs Are Reopening! – Soil Food Web  |
| `/soil-food-web-foundation-launches-as-nonprofit-to-carry-forward-dr-elaine-inghams-legacy/` | 670 | 10 | Soil Food Web Foundation Launches as Nonprofit to Carry Forward Dr. El |
| `/soil-food-web-foundation-welcomes-eric-feiler/` | 763 | 13 | The Soil Food Web Welcomes a New Board Member – Eric Feiler – Soil Foo |
| `/soil-food-web-school-first-permaculture-design-certificate-course/` | 1283 | 26 | The Soil Food Web School Launches Its First-Ever Permaculture Design C |
| `/soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan/` | 800 | 10 | Soil Health Week 2025: Wild Soils UK and TrashIt Bring the Soil Food W |
| `/student-profile-su-kahumbu-stephanou/` | 588 | 14 | Student Profile: Su Kahumbu Stephanou – Soil Food Web Foundation |
| `/testimonial/amara-okafor/` | 73 | 3 | Amara Okafor – Soil Food Web Foundation |
| `/testimonial/david-vance/` | 71 | 3 | David Vance – Soil Food Web Foundation |
| `/testimonial/john-doe/` | 85 | 3 | John Doe – Soil Food Web Foundation |
| `/testimonial/marcus-thorne/` | 69 | 3 | Marcus Thorne – Soil Food Web Foundation |
| `/testimonial/yuki-tanaka/` | 68 | 3 | Yuki Tanaka – Soil Food Web Foundation |
| `/unconditional-freedom-at-home-and-in-the-world/` | 1568 | 8 | Unconditional Freedom: At Home and in the World – Soil Food Web Founda |

### 5.3 Pages the menus link to

`/`, `/about-us/`, `/accessibility/`, `/calendar-event/permaculture-design-certificate-2026-cohort-3/`, `/calendar-event/sfw-turns-one/`, `/calendar/`, `/category/foundation-update/`, `/cdn-cgi/l/email-protection`, `/community/`, `/contact/`, `/donate/`, `/donations/`, `/find-a-professional/`, `/how-it-works/`, `/invite-us-to-speak/`, `/login/`, `/logo-brand-use/`, `/news/`, `/practice/`, `/privacy/`, `/programs-overview/`, `/publications/`, `/scholarship/`, `/terms/`, `/volunteer/`, `/workshops/`


Menu targets that are broken: `/donate/` (404, footer), `/accessibility/` (404, footer), `/contact/` (→ empty page, footer 'Media and press'), `/workshops/` (empty page, header + footer), `/invite-us-to-speak/` and `/logo-brand-use/` (heading-only pages, footer), 'Partner on Research' and 'Governance and financials' (`#`).

## 7. Analytics, tag manager and consent

Checked in the raw HTML of `https://new.soilfoodweb.com/` (plus all 901 saved staging pages) and `https://soilfoodweb.com/` for `G-` IDs, `GTM-` IDs, `UA-` IDs, `gtag(`, `googletagmanager.com`, `google-analytics.com`, Facebook pixel, and the signatures of Site Kit, MonsterInsights, GTM4WP, ExactMetrics, Analytify, WPCode and the common consent plugins.

| | Staging `new.soilfoodweb.com` | Live `soilfoodweb.com` |
|---|---|---|
| Google Tag Manager | none | `GTM-K4CC7C2X`, standard snippet hard-coded in `<head>` (after an Affirm checkout script) plus the `<noscript>` iframe at the top of `<body>` |
| GA4 | none | `G-T7N81C1KYP`, fired from inside the GTM container (a Google tag + a GA4 event tag); not in the page source |
| Universal Analytics | none | none in the page; the live cookie policy still lists the cookie `_gat_UA-150841262-1`, a UA property that stopped collecting data in 2023 |
| Facebook pixel | none | pixel `1507217424320414`, fired by a Custom HTML tag inside the GTM container on every page view |
| Loaded through a plugin? | – | No. No Site Kit, MonsterInsights, GTM4WP or headers/footers plugin is present (plugins seen: WooCommerce, LifterLMS, Ninja Forms, WP Fusion, Brave Popup, Salient Core, Student Directory, Website Toolbox Forums). The snippet sits in theme output, i.e. the Salient child theme or the theme's custom-code field. |
| Consent banner before tracking | nothing to gate (no tracking) | **No.** GTM fires immediately in `<head>`; there is no `gtag('consent', …)` default, no consent-mode tag in the container, no script-type blocking and no consent plugin loaded. The footer links to `/opt-out-preferences/?cmplz_region_redirect=true` (a Complianz-style URL) and that page's text promises a cookie banner with 'set custom permission', but the Complianz plugin is not loaded on any page fetched and no banner markup exists. |

For launch: the new site has no analytics at all today, so the Ad Grant application cannot show conversion tracking until GA4 (directly or via `GTM-K4CC7C2X`) is added. The IDs on the two sites are therefore not 'the same'; staging simply has none. If the live container is reused, the Facebook pixel in it will come along, and the privacy policy on the new site already promises Google Analytics, so a consent mechanism for EU visitors is needed.

## 8. Method and reproducibility

1. `scripts/crawl.py` – fetches sitemaps, `/wp-json/wp/v2/types` and every REST collection, then crawls every internal `<a href>` from `/` recursively (menus, footer, buttons, cards, body text), fetching each URL plain and with `?nocache=12345`. 689 URLs, 5 parallel workers, ~4 minutes.
2. `scripts/parse.py` – extracts title, H1, meta robots, canonical, viewport, main-content word count (header `#header-outer`, off-canvas `#slide-out-widget-area` and footer `#footer-outer` removed), menu/off-canvas/footer link fingerprints, all links with their section, all images; compares the two versions.
3. `scripts/checklinks.py` and `scripts/check_srcset.py` – HEAD/GET every unique link target and image (1,561 link targets + 875 images + 405 srcset variants); `scripts/recheck.py` re-ran every target that the network policy had blocked once `allowlist.txt` was applied, following redirects hop by hop so a blocked final host is recorded with the hops that did resolve.
4. `scripts/build.py` and `scripts/report.py` – produce `pages.csv`, `links.csv` and this report.

To re-run the external link check with open internet: `S=$(pwd) python3 scripts/checklinks.py` after `crawl.py` and `parse.py`.
