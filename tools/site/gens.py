"""Generators for tools/site/build.py: data-driven sections, item pages, /review/.

Every piece of staging text passes through fix() first, which applies the
site-wide corrections from the brief (bug numbers in comments).
"""
import json, os, re, html as H, datetime
from collections import OrderedDict
import build as B
from build import gen, img, E, A, data, repo, begin, write, fmt_date, fmt_range

TODO = '<p class="todo">%s</p>'
STAGING = "https://new.soilfoodweb.com"


# ------------------------------------------------------------------ text fixes
FIXES = [
    (re.compile(r"​|‌|‍|﻿"), ""),                       # 29 zero-width spaces
    (re.compile(r"Bio[Cc]omplete(?:™|T\b|&#8482;|&trade;)?"), "BioComplete™"),  # 22
    (re.compile(r"prerequesites|pre-requisites|prerequisits", re.I), "prerequisites"),     # 25
    (re.compile(r"\bthat that\b"), "that"),                                   # 28
    (re.compile(r"\bSpoil Sponge Workshop\b"), "Soil Sponge Workshop"),       # 26
    (re.compile(r"@soilfoodwebfoundation\.org"), "@soilfoodweb.com"),          # 21
    (re.compile(r"\bOn-line Courses\b|\bOnline courses\b(?= *<)"), "Online Courses"),       # 33
    (re.compile(r"(?:more than|approximately|over) 1[0-9]0 countries"), "100+ countries"),  # 15
    (re.compile(r"in more than 100 countries"), "in 100+ countries"),         # 15
    (re.compile(r"\s+—\s+|\s*—\s*"), ", "),                          # no em dashes
    (re.compile(r"\s+–\s+"), ", "),
    (re.compile(r",\s*,"), ","),
]


def fix(t):
    if not t:
        return t
    for rx, rep in FIXES:
        t = rx.sub(rep, t)
    return t


def staging_link(href):
    """Staging URLs -> launch URLs (and the link fixes from section 2)."""
    if not href:
        return href
    h = href.replace(STAGING, "").replace("https://www.soilfoodweb.com", "").replace("https://soilfoodweb.com", "") if ("soilfoodweb.com/" in href and "school." not in href and "webinar." not in href and "archive." not in href and "/wp-content/" not in href) else href
    table = [
        ("/about-us/", "/about/"), ("/programs-overview/", "/programs/"), ("/practice/#CASE-STUDIES", "/case-studies/"),
        ("/practice/#work-with-us", "/work-with-us/"), ("/practice/", "/case-studies/"), ("/donate/", "/donations/"),
        ("/contact-info/", "/contact/"), ("/foundation-legal/", "/governance/"), ("/sfw-directory/", "/find-a-professional/"),
        ("/team/", "/about/#team"), ("/accessibility/", "/about/#contact-legal"),
    ]
    for a, b in table:
        if h.startswith(a):
            h = b + h[len(a):]
            break
    if h.startswith("/resources/animations-videos/"):
        h = "/how-it-works/"
    elif h.startswith(("/certified-listing-directory/", "/consultants/", "/laboratory-technicians/")):
        h = "/find-a-professional/"
    elif h.startswith(("/soil-sponge-regeneration-workshop/", "/product/regenerating-the-soil-sponge/")):
        h = "/workshops/"
    h = h.replace("courses/foundation-couse-1", "courses/foundation-course-1")
    if "localhost" in h:
        h = "https://school.soilfoodweb.com/courses/permaculture-design-certification"
    if h.startswith("https://webinar.soilfoodweb.com"):
        h = "https://webinar.soilfoodweb.com"
    return h or "/"


# ------------------------------------------------------------------ html helpers
def rewrite_body(body, page_imgs=True):
    """Staging body HTML -> launch HTML: fixed text, launch links, local images."""
    body = fix(body)

    def a_sub(m):
        return 'href="%s"' % A(staging_link(H.unescape(m.group(1))))
    # WordPress tag lists have no launch address: drop them.
    body = re.sub(r"<h4>\s*Tags:\s*</h4>(\s*<a href=\"[^\"]*/tag/[^\"]*\"[^>]*>.*?</a>\s*,?)*", "", body, flags=re.S)
    body = re.sub(r'href="([^"]*)"', a_sub, body)
    # Links with no launch target keep their text and lose the link.
    body = re.sub(r'<a href="(?:/tag/[^"]*|/beneath-the-surface[^"]*|#brave_[^"]*)"[^>]*>(.*?)</a>', r"\1", body, flags=re.S)
    body = body.replace('href="/october-2025-newsletter/#gettingthewordout"', 'href="/october-2025-newsletter/"')

    def img_sub(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]*)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        if not src or not src.group(1).startswith("http") or re.match(r"https?://\d+$", src.group(1)):
            return ""  # empty or numeric src (bug 1): the picture does not exist
        try:
            return img(H.unescape(src.group(1)), H.unescape(alt.group(1)) if alt and alt.group(1) else None)
        except Exception as e:
            print("image failed", src.group(1), e)
            return ""
    if page_imgs:
        body = re.sub(r"<img[^>]*>", img_sub, body)
    # 30: a paragraph repeated later in the same page is shown once.
    seen, out = set(), []
    for part in re.split(r"(<p>.*?</p>)", body, flags=re.S):
        if part.startswith("<p>"):
            key = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", part)).strip()
            if len(key) > 40 and key in seen:
                continue
            seen.add(key)
        out.append(part)
    body = "".join(out)
    body = re.sub(r"<p>\s*</p>", "", body)
    body = re.sub(r"<(/?)h1\b", r"<\1h2", body)  # 5: the page title is the only h1
    return body


def esc_attr_text(t):
    return A(re.sub(r"\s+", " ", t.lower()))


# ------------------------------------------------------------------ courses
# Ad Grant checklist (2 Oct): sales lines toned down on the course cards.
COURSE_EDITS = [
    (", Measure the real impact of your efforts near instantly", ", Measure the real impact of your efforts"),
    (", and transforms what\u2019s possible on your land", ""),
    (", and transforms what's possible on your land", ""),
]


# Supplied photos for the program cards on /programs/ (October 2026 image brief). Other cards keep staging's.
PROGRAM_PHOTOS = [
    ("Soil Microscopy", "R5A_4247.jpg", "Microscope objective lens focused on a slide with a soil sample."),
    ("BioComplete™ Compost Production", "R5A_3961.jpg", "Bales of hay broken open on the ground in front of compost piles and a tracked loader."),
    ("Foundation Course 1", "Ciliate, 60x obj, Patricia J Coppola.jpg", "A single oval ciliate seen under a microscope against a pale grey background. Ciliate, 60x objective. Photo: Patricia J Coppola."),
    ("Foundation Course 2", "R5A_4027.jpg", "A pitchfork standing in a large pile of dark finished compost."),
    ("Foundation Course 3", "R5A_4270.jpg", "Glass beakers, a pipette and a dropper on a sunny lab bench."),
    ("Foundation Course 4", "R5A_4261.jpg", "A microscope stage with a glass slide under the objectives."),
]


def course_card(c, scroller=False, photos=False):
    for a, b in COURSE_EDITS:
        c = dict(c, line=c["line"].replace(a, b))
    title = fix(c["title"]).replace(" : ", ": ")
    href = staging_link(c["href"])
    cta = fix(c["cta"]).replace(" →", "").replace("→", "").strip() or "Learn more"
    paths = " ".join(c["pathways"])
    text = esc_attr_text(" ".join([title, c["kicker"], c["line"], paths]))
    attrs = '' if scroller else ' data-item data-group="all %s" data-text="%s"' % (A(paths), text)
    return ('<li%s><article class="card card--link">%s<div class="card__body"><p class="card__kicker">%s</p>'
            '<h3 class="card__title"><a href="%s">%s</a></h3><p class="card__text">%s</p>'
            '<p class="card__foot"><span class="more">%s</span></p></div></article></li>') % (
        attrs, card_image(c, title, photos), E(fix(c["kicker"])), A(href), E(title), E(fix(c["line"])), E(cta))


# Repo photos for course cards that staging gives the same picture as another card.
COURSE_IMAGES = [
    ("Introduction to Ecosystem Restoration: Module 1", "img/new-2026-10/EN-ERC-Fig-M4L4P5_Natural_Capital-001-Leaf.png"),
    ("Introduction to Ecosystem Restoration: Module 2", "img/new-2026-10/EN-ERC-Fig-M2L1P8_Water_pump-001-Leaf.png"),
    ("Introduction to Ecosystem Restoration: Module 3", "img/new-2026-10/EN-ERC-Fig-M3L3P67_Erosion_Control-001-Leaf.png"),
    ("Introduction to Ecosystem Restoration: Module 4", "img/new-2026-10/EN-ERC-Fig-M4L3P2_Reforestation-001-Leaf.png"),
    ("Mini Foundation Course", "img/new-2026-10/R5A_4246.jpg"),
    ("Permaculture Design Certification", "img/new-2026-10/R5A_4016.jpg"),  # staging's card photo is from Ecosystem Restoration Camps
]


def card_image(c, title, photos):
    for start, src in COURSE_IMAGES:
        if title.startswith(start):
            if src.startswith("img/new-2026-10/"):
                return B.photo(os.path.basename(src), "", "card__img card__img--fit" if "ERC-Fig" in src else "card__img",
                               sizes="(min-width: 64em) 24rem, (min-width: 40em) 50vw, 100vw")
            return img(src, "", "card__img")
    for start, f, alt in PROGRAM_PHOTOS if photos else ():
        if title.startswith(start):
            return B.photo(f, alt, "card__img", sizes="(min-width: 64em) 24rem, (min-width: 40em) 50vw, 100vw")
    return img(c["image"], "", "card__img")


@gen
def courses(args):
    if args.strip():  # a short selection reads as a row of cards, no scroller
        return '<ul class="grid">%s</ul>' % "".join(course_card(c, True, photos=True) for c in data("courses")[:int(args)])
    cs = data("courses")
    return ('<div data-scroller><div class="scroller-head"><h3 class="sr-only">Programs</h3>'
            '<div class="scroller-nav"><button type="button" data-scroll="-1" aria-label="Previous programs">&lsaquo;</button>'
            '<button type="button" data-scroll="1" aria-label="Next programs">&rsaquo;</button></div></div>'
            '<ul class="scroller">%s</ul></div>') % "".join(course_card(c, True) for c in cs)


PATHS = [("all", "All"), ("composter", "Composter"), ("consultant", "Consultant"), ("designer", "Designer"),
         ("ecosystem-restorationist", "Ecosystem Restorationist"), ("farmer", "Farmer"), ("gardener", "Gardener"),
         ("lab-tech", "Lab Tech"), ("scientist", "Scientist")]


@gen
def courses_grid(args):
    cs = data("courses")
    chips = "".join('<li><button class="chip" type="button" data-chip="%s" aria-pressed="%s">%s</button></li>' % (k, "true" if k == "all" else "false", E(v)) for k, v in PATHS)
    return ('<div data-filter><ul class="chips" aria-label="Filter by path">%s</ul>'
            '<form class="searchbar" role="search"><label class="sr-only" for="prog-q">Search programs</label>'
            '<input id="prog-q" type="search" data-q placeholder="Search programs"></form>'
            '<p class="count" data-count data-one="program" data-many="programs" aria-live="polite"></p>'
            '<ul class="grid grid--3">%s</ul><p data-empty hidden>No programs match. Try another path.</p></div>') % (
        chips, "".join(course_card(c, photos=True) for c in cs))


@gen
def funding(args):
    """The School line and the funding sentence, for Home, About, Programs, Donate, Scholarship."""
    return '<p class="funding">%s %s <a href="/funding/">How we\u2019re funded</a></p>' % (E(B.SCHOOL_LINE), E(B.FUNDING_LINE))


# ------------------------------------------------------------------ video facade
def facade(vimeo, h, thumb, title, alt=""):
    """Thumbnail + play button; site.js swaps in the player on click.
    Without JavaScript the link opens the video on Vimeo."""
    embed = "https://player.vimeo.com/video/%s?dnt=1%s" % (vimeo, "&h=" + h if h else "")
    page = "https://vimeo.com/%s%s" % (vimeo, "/" + h if h else "")
    return '<a class="vfacade" href="%s" data-embed="%s" data-title="%s">%s<span class="sr-only">Play video: %s</span></a>' % (
        A(page), A(embed), A(title), img(thumb, alt), E(title))


@gen
def video(args):
    kv = dict(re.findall(r'(\w+)="([^"]*)"', args))
    return facade(kv["id"], kv.get("h", ""), kv["thumb"], kv["title"], kv.get("alt", ""))


# ------------------------------------------------------------------ team
# Portraits supplied in October 2026 (staff folder on Drive and soilfoodweb.com/about), square crops.
TEAM_PHOTOS = {n: "img/new-2026-10/team-%s.jpg" % f for n, f in [
    ("Loida Vasquez", "loida-vasquez"), ("Delvin Solkinson", "delvin-solkinson"), ("Ib Borup Pedersen", "ib-borup-pedersen"),
    ("Elena Kalli", "elena-kalli"), ("Dora Tkalec", "dora-tkalec"), ("Ay\u015fen \u00dcst\u00fcnay", "aysen-ustunay"),
    ("Isadora Shmidt", "isadora-shmidt"), ("Brian Daubenspeck", "brian-daubenspeck"), ("Casey Williams", "casey-williams"),
    ("Kavi Reddy", "kavi-reddy")]}


def all_team():
    """Staging's team list, then the people soilfoodweb.com/about lists that staging leaves out
    (content/repo-team.json, copy from this repo's earlier team page)."""
    extra = os.path.join(B.ROOT, "content", "repo-team.json")
    return data("team") + (json.load(open(extra, encoding="utf-8")) if os.path.exists(extra) else [])


def team_photo(t, cls=""):
    if t["name"] in TEAM_PHOTOS:
        t = dict(t, photo=TEAM_PHOTOS[t["name"]])
    if t["photo"].startswith("img/new-2026-10/"):
        return B.photo(os.path.basename(t["photo"]), "Portrait of %s" % t["name"], cls, sizes="(min-width: 64em) 12rem, 40vw")
    return img(t["photo"], "Portrait of %s" % t["name"], cls) if t["photo"] else '<span class="person__ph">%s</span>' % E(t["name"][:1])


@gen
def team(args):
    out = []
    for t in all_team():
        role = fix(t["role"])
        out.append('<li><a class="person" href="/team-member/%s/">%s<p class="person__name">%s</p>%s</a></li>' % (
            t["slug"], team_photo(t), E(t["name"]), '<p class="person__role">%s</p>' % E(role) if role else ""))
    return '<ul class="people">%s</ul>' % "".join(out)


# ------------------------------------------------------------------ news
# Card photos chosen for the launch, in place of staging's featured image.
POST_IMAGES = {"obituary-for-dr-elaine-ingham": "Elaine Flower Shirt Microscope.png"}


def post_card(p):
    cat = p["categories"][0]["name"] if p["categories"] else ""
    if p["slug"] in POST_IMAGES:
        pic = B.photo(POST_IMAGES[p["slug"]], "", "card__img card__img--square", sizes="(min-width: 64em) 18rem, 50vw")
    else:
        pic = None
    pic = pic or (img(p["featured"], "", "card__img card__img--square") if p.get("featured") else '<div class="card__img card__img--square"></div>')
    return ('<li><article class="card card--link card--plain">%s<div class="card__body"><p class="card__kicker">%s &middot; '
            '<time datetime="%s">%s</time></p><h3 class="card__title"><a href="/%s/">%s</a></h3></div></article></li>') % (
        pic, E(cat), p["date"], fmt_date(p["date"]), p["slug"], E(fix(p["title"])))


def all_posts():
    ps = data("posts")
    extra = os.path.join(B.ROOT, "content", "repo-posts.json")
    if os.path.exists(extra):
        ps = ps + json.load(open(extra, encoding="utf-8"))
    return sorted(ps, key=lambda p: p["date"], reverse=True)


@gen
def news(args):
    n = int(args or 4)
    return '<ul class="grid">%s</ul>' % "".join(post_card(p) for p in all_posts()[:n])


@gen
def news_all(args):
    ps = all_posts()
    cats = OrderedDict()
    for p in ps:
        for c in p["categories"]:
            cats[c["slug"]] = c["name"]
    chips = '<li><button class="chip" type="button" data-chip="" aria-pressed="true">All</button></li>' + "".join(
        '<li><button class="chip" type="button" data-chip="%s" aria-pressed="false">%s</button></li>' % (k, E(v)) for k, v in cats.items())
    items = []
    for p in ps:
        card = post_card(p).replace("<li>", '<li data-item data-group="%s" data-text="%s">' % (
            " ".join(c["slug"] for c in p["categories"]), esc_attr_text(p["title"] + " " + p.get("excerpt", ""))), 1)
        items.append(card)
    return ('<div data-filter><ul class="chips" aria-label="Filter by category">%s</ul>'
            '<form class="searchbar" role="search"><label class="sr-only" for="news-q">Search news</label>'
            '<input id="news-q" type="search" data-q placeholder="Search posts"></form>'
            '<p class="count" data-count data-one="post" data-many="posts" aria-live="polite"></p>'
            '<ul class="grid">%s</ul><p data-empty hidden>No posts match.</p></div>') % (chips, "".join(items))


# ------------------------------------------------------------------ events (bug 24)
EVENT_TYPES = OrderedDict([("workshop", "Workshop"), ("course", "Courses and intensives"),
                           ("community", "Community event"), ("webinar", "Webinar")])


def event_type(e):
    t = e["title"].lower()
    if t.startswith("community event"):
        return "community"
    if "workshop" in t:
        return "workshop"
    if "intensive" in t or "cohort" in t or "certificate" in t or "course" in t:
        return "course"
    if "webinar" in t:
        return "webinar"
    return "workshop"


def all_events():
    evs = []
    for e in data("events"):
        e = dict(e)
        e["type"] = event_type(e)
        e["title"] = fix(e["title"]).replace(" | ", ": ")
        if e["type"] == "community":
            e["title"] = e["title"].replace("Community Event: ", "")
        evs.append(e)
    cal = repo("calendar")["indiaWorkshop"]
    evs.append({"slug": "accelerator-workshop-india-2026", "title": "Accelerator Workshop: India", "start": "2026-10-19",
                "end": "2026-10-30", "type": "workshop", "when": cal["dated"], "repo": True,
                "href": "https://school.soilfoodweb.com/courses/india-workshop-2026"})
    evs.append({"slug": "soil-health-week-pakistan-2026", "title": "Soil Health Week Pakistan 2026", "start": "2026-12-01",
                "end": "2026-12-07", "type": "community", "when": "1 to 7 December 2026", "repo": "pakistan",
                "href": "/soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan/"})
    return sorted(evs, key=lambda e: e["start"])


REPO_EVENT_TEXT = {
    # From this repo's calendar page (_dev/legacy-pages/calendar.html).
    "pakistan": ("The second year of Soil Health Week in Pakistan. Co-led by Wild Soils UK (Nick Padwick) and TrashIt, a woman- and youth-led "
                 "compost enterprise in Pakistan. The Soil Food Web Foundation is a supporting partner. Last year's event reached more than 600 "
                 "participants across 60 districts.",
                 [("Read about last year's Soil Health Week", "/soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan/"),
                  ("TrashIt", "https://www.trashit.pk")]),
}


def event_when(e):
    w = fmt_range(e["start"], e["end"])
    m = re.search(r"(\d{1,2}):(\d{2}) ([ap])\.m\. UTC", e.get("when", ""))
    if m:
        w += ", %d:%s %sm UTC" % (int(m.group(1)), m.group(2), m.group(3))
    return w


@gen
def events(args):
    evs = all_events()
    chips = '<li><button class="chip" type="button" data-chip="" aria-pressed="true">All</button></li>' + "".join(
        '<li><button class="chip" type="button" data-chip="%s" aria-pressed="false">%s</button></li>' % (k, v)
        for k, v in EVENT_TYPES.items() if any(e["type"] == k for e in evs))
    rows = []
    for e in evs:
        rows.append('<li class="event" data-item data-group="%s"><p class="event__date"><time datetime="%s">%s</time></p>'
                    '<h3 class="event__title"><a href="/calendar-event/%s/">%s</a></h3><span class="event__type">%s</span></li>' % (
                        e["type"], e["start"], E(event_when(e)), e["slug"], E(e["title"]), EVENT_TYPES[e["type"]]))
    return ('<div data-filter><ul class="chips" aria-label="Filter by type">%s</ul>'
            '<ul class="events">%s</ul><p data-empty hidden>No events of this type in the next twelve months.</p></div>') % (chips, "".join(rows))


@gen
def workshop_events(args):
    evs = [e for e in all_events() if e["type"] == "workshop"]
    return '<ul class="events">%s</ul>' % "".join(
        '<li class="event"><p class="event__date"><time datetime="%s">%s</time></p><h3 class="event__title"><a href="/calendar-event/%s/">%s</a></h3>'
        '<span class="event__type">Workshop</span></li>' % (e["start"], E(event_when(e)), e["slug"], E(e["title"])) for e in evs)


# ------------------------------------------------------------------ publications
START_HERE = [
    ("The Soil Biology Primer, chapters 1 to 5", "1999", "USDA NRCS, 1999", 1064,
     "Dr. Ingham’s free, plain-language introduction to soil bacteria, fungi, protozoa and nematodes, written for the US Department of Agriculture. The best first read for anyone new to soil biology."),
    ("Interactions of bacteria, fungi and their nematode grazers", "1985", "Ecological Monographs, 1985", 1017,
     "Shows that nematodes grazing on bacteria and fungi release nitrogen that plants then take up. This is the core idea behind the soil food web approach."),
    ("The detrital food web in a short grass prairie", "1987", "Biology and Fertility of Soils, 1987", 1024,
     "One of the first studies to map and measure a whole soil food web, organism group by organism group. Later soil food web models build on it."),
    ("Review of the effects of twelve selected biocides on target and non-target soil organisms", "1985", "Crop Protection, 1985", 1018,
     "Reviews what common pesticides do to the soil life they were never meant to hit. Useful for anyone weighing chemical inputs."),
    ("The Compost Tea Brewing Manual", "2000", "2000", 1066,
     "Dr. Ingham’s practical guide to making aerobic compost tea, the method taught in the Soil Food Web School courses."),
    ("Fungal-bacterial diversity and microbiome complexity predict ecosystem functioning", "2019", "Nature Communications, 2019, Wagg et al.", 1135,
     "A recent large study from outside our network. Soils with more diverse and better-connected fungi and bacteria performed more ecosystem functions."),
]


def pubs():
    ps = data("publications")
    blurbs = {}
    bf = os.path.join(B.STG, "publication-blurbs.json")
    if os.path.exists(bf):
        blurbs = {b["id"]: b for b in json.load(open(bf, encoding="utf-8"))}
    for p in ps:
        p["title"] = fix(p["title"])
        if p["id"] == 1064:  # 27 and section 7: one USDA label, typed as a government publication
            p["kind"] = "Government publication"
        p["hide_citation"] = p["citation"] == "Journal citation not verified"  # 11
        b = blurbs.get(p["id"])
        text = fix(b["blurb"]).strip() if b else ""
        p["blurb_title_only"] = text.endswith("[from title]")  # no abstract found; Carla checks these first
        p["blurb"] = text.replace("[from title]", "").strip()
        p["blurb_source"] = b["source"] if b else ""
    return ps


def pub_links(p):
    """Dr. Elaine's own papers: Google Scholar first, DOI second (section 7)."""
    href = p["href"]
    own = p["collection"].startswith("Dr. Elaine")
    doi = href if "doi.org/" in href else ""
    if not doi and "doi.org/" in p.get("blurb_source", ""):
        doi = p["blurb_source"]
    links = []
    if own:
        scholar = href if "scholar.google" in href else "https://scholar.google.com/scholar?q=" + H.escape(re.sub(r"\s+", "+", '"%s"' % p["title"]), quote=True)
        links.append(("Google Scholar", scholar))
        if doi:
            links.append(("DOI", doi))
        elif href and "scholar.google" not in href and "soilfoodweb.com" not in href:
            links.append(("Publisher", href))
    else:
        if href and "soilfoodweb.com" not in href:
            links.append(("DOI" if doi else "Read it", href))
    return links


@gen
def start_here(args):
    by = {p["id"]: p for p in pubs()}
    cards = []
    for title, year, cite, pid, blurb in START_HERE:
        p = by.get(pid)
        href = "/publication/%s/" % p["slug"] if p else "#"
        cards.append('<li><article class="card card--link"><div class="card__body"><p class="card__kicker">%s</p>'
                     '<h3 class="card__title"><a href="%s">%s</a></h3><p class="meta">%s</p><p class="card__text draft">%s</p></div></article></li>' % (
                         year, href, E(title), E(cite), E(blurb)))
    return '<ul class="grid grid--3">%s</ul>' % "".join(cards)


@gen
def publications(args):
    ps = pubs()
    colls = OrderedDict()
    for p in ps:
        colls.setdefault(p["collection"], []).append(p)
    topics = sorted({t for p in ps for t in p["topics"]})
    slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower().replace("’", "")).strip("-")
    chips = '<li><button class="chip" type="button" data-chip="" aria-pressed="true">All (%d)</button></li>' % len(ps) + "".join(
        '<li><button class="chip" type="button" data-chip="%s" aria-pressed="false">%s (%d)</button></li>' % (slug(c), E(c), len(v)) for c, v in colls.items())
    opts = '<option value="">Topic: any</option>' + "".join('<option value="%s">%s</option>' % (A(t.replace(" ", "-")), E(t)) for t in topics)
    groups = []
    for c, items in colls.items():
        rows = []
        for p in items:
            line = p["authors"] + ("" if p["hide_citation"] or not p["citation"] else " · " + p["citation"])
            links = " ".join('<a href="%s" rel="noopener">%s</a>' % (A(h), l) for l, h in pub_links(p))
            why = ('<p class="entry__why"><b>Why read it:</b> <span class="draft"%s>%s</span></p>' % (' data-from="title"' if p["blurb_title_only"] else "", E(p["blurb"]))) if p["blurb"] else \
                '<p class="entry__why"><b>Why read it:</b> <span class="todo">one-sentence summary from the abstract; Carla Portugal checks</span></p>'
            rows.append('<li class="entry" data-item data-group="%s" data-topics="%s" data-text="%s"><span class="entry__year">%s</span>'
                        '<div><p class="entry__title"><a href="/publication/%s/">%s</a></p><p class="entry__line">%s</p>%s%s</div>'
                        '<span class="entry__kind">%s</span></li>' % (
                            slug(c), A(" ".join(t.replace(" ", "-") for t in p["topics"])),
                            esc_attr_text(" ".join([p["title"], p["authors"], p["citation"], p["year"], " ".join(p["topics"])])),
                            E(p["year"]), p["slug"], E(p["title"]), E(line), why,
                            '<p class="entry__links">%s</p>' % links if links else "", E(p["kind"])))
        groups.append('<section data-group-block><h3>%s</h3><ul class="entries">%s</ul></section>' % (E(c), "".join(rows)))
    return ('<div data-filter id="all"><ul class="chips" aria-label="Collections">%s</ul>'
            '<form class="searchbar" role="search"><label class="sr-only" for="pub-q">Search publications</label>'
            '<input id="pub-q" type="search" data-q placeholder="Search by title, author, topic, or year">'
            '<label class="sr-only" for="pub-topic">Topic</label><select id="pub-topic" data-topic>%s</select></form>'
            '<p class="count" data-count data-one="publication" data-many="publications" aria-live="polite"></p>%s'
            '<p data-empty hidden>No publications match. Try a different word or topic.</p></div>') % (chips, opts, "".join(groups))


# ------------------------------------------------------------------ videos
def playlists_data():
    pl = OrderedDict()
    for v in data("videos"):
        pl.setdefault(v["playlist"], []).append(v)
    return pl


def vcard(v):
    thumb = img(v["thumb"], "", "") if v["thumb"] else ""
    return '<li><a class="vcard" href="/video/%s/"><span class="vcard__thumb">%s</span><p class="vcard__title">%s</p></a></li>' % (
        v["slug"], thumb, E(fix(v["title"])))


@gen
def playlists(args):
    order = [x.strip() for x in args.split("|")] if args else list(playlists_data())
    pl = playlists_data()
    out = []
    for name in order:
        if name not in pl:
            continue
        vid = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        out.append('<section class="playlist" id="%s"><h3>%s</h3><ul class="grid">%s</ul></section>' % (vid, E(name), "".join(vcard(v) for v in pl[name])))
    return "".join(out)


# ------------------------------------------------------------------ directory
def dir_slug(d):
    """Launch slug: plain letters, digits and hyphens (staging has one with an encoded broken bar)."""
    if d["slug"] == "alex-kellett":
        return "norman-higgins"
    from urllib.parse import unquote
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9-]+", "-", unquote(d["slug"]).lower())).strip("-")


def country_of(area):
    c = area.split(",")[-1].strip() if area else ""
    return {"Netherlands The": "Netherlands", "USA": "United States", "UK": "United Kingdom"}.get(c, c)


@gen
def directory(args):
    ds = data("directory")
    slug = lambda t: re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    roles = OrderedDict([("consultant", "Consultant"), ("lab-tech", "Lab Tech")])
    chips = '<li><button class="chip" type="button" data-chip="" aria-pressed="true">All (%d)</button></li>' % len(ds) + "".join(
        '<li><button class="chip" type="button" data-chip="%s" aria-pressed="false">%s (%d)</button></li>' % (
            k, v, sum(1 for d in ds if any(r.lower() == k for r in d["roles"]))) for k, v in roles.items())
    countries = sorted({country_of(d["area"]) for d in ds if country_of(d["area"])})
    opts = '<option value="">All countries</option>' + "".join('<option value="%s">%s</option>' % (slug(c), E(c)) for c in countries)
    cards = []
    for d in ds:
        rk = " ".join(r.lower() for r in d["roles"])
        name = d["name"].strip()
        pic = img(d["photo"], "Photo of %s" % name, "card__img card__img--square") if d["photo"] else '<div class="card__img card__img--square"></div>'
        cards.append('<li data-item data-group="%s" data-topics="%s" data-text="%s"><article class="card card--link card--plain">%s<div class="card__body">'
                     '<p class="card__kicker">%s</p><h3 class="card__title"><a href="/directory-member/%s/">%s</a></h3>%s<p class="meta">%s</p></div></article></li>' % (
                         A(rk), slug(country_of(d["area"])), esc_attr_text(" ".join([name, d["company"], d["area"], " ".join(d["roles"])])), pic,
                         E(" \u00b7 ".join(r.replace("Lab-Tech", "Lab Tech") for r in d["roles"])), dir_slug(d), E(name),
                         '<p class="card__text">%s</p>' % E(d["company"]) if d["company"] else "", E(d["area"])))
    return ('<div data-filter><ul class="chips" aria-label="Filter by category">%s</ul>'
            '<form class="searchbar" role="search"><label class="sr-only" for="dir-q">Search the directory</label>'
            '<input id="dir-q" type="search" data-q placeholder="Name, company, location">'
            '<label class="sr-only" for="dir-country">Country</label><select id="dir-country" data-topic>%s</select></form>'
            '<p class="count" data-count data-one="practitioner" data-many="practitioners" aria-live="polite"></p>'
            '<ul class="grid">%s</ul><p data-empty hidden>No practitioners match. Try another country or a nearby region.</p></div>') % (chips, opts, "".join(cards))


# ------------------------------------------------------------------ item pages
def back(href, label):
    return '<a class="back" href="%s">%s</a>' % (href, E(label))


# Ad Grant checklist: past tense for Dr. Elaine; no relative dates that age.
TEAM_EDITS = {
    "dr-elaine-ingham": [
        ("In addition to starting Soil Foodweb Inc. 26 years ago,", "In addition to starting Soil Foodweb Inc. in 1996,"),
        ("Dr. Ingham\u2019s research is global, and her scientific papers date as far back as 1982",
         "Dr. Ingham\u2019s research was global, and her scientific papers date as far back as 1982"),
        ("Dr. Ingham has written 6 book chapters for published books, participated in research teams publishing 17 technical reports, and has been a speaker",
         "Dr. Ingham wrote 6 book chapters for published books, took part in research teams publishing 17 technical reports, and was a speaker"),
    ],
}


def team_pages():
    for t in all_team():
        for a, b in TEAM_EDITS.get(t["slug"], []):
            t = dict(t, bio=t["bio"].replace(a, b))
        path = "/team-member/%s/" % t["slug"]
        begin(path, "staging", [], "", "Team member")
        role = fix(t["role"])
        bio = rewrite_body(t["bio"]) or TODO % ("Bio for %s; supplied by %s." % (t["name"], t["name"]))
        body = ('<section class="band"><div class="wrap">%s<div class="profile"><div class="profile__photo">%s</div><div>'
                '<h1>%s</h1>%s<div class="prose">%s</div></div></div></div></section>') % (
            back("/about/#team", "Back to the team"), team_photo(t), E(t["name"]),
            '<p class="profile__role">%s</p>' % E(role) if role else TODO % "Role or title for %s; Stephanie McDaniel supplies." % t["name"], bio)
        write(path, t["name"], "%s, %s at the Soil Food Web Foundation." % (t["name"], role or "team member"), body, "/about/")


def directory_pages():
    for d in data("directory"):
        slug = dir_slug(d)
        path = "/directory-member/%s/" % slug
        name = d["name"].strip()
        bugs, note = [], ""
        if d["slug"] == "alex-kellett":
            # 32: staging's alex-kellett page holds Norman Higgins's whole listing
            # (name, email, bio). The title now matches the person on the page,
            # the URL follows the name, and /directory-member/alex-kellett/ redirects.
            bugs, note = ["32"], ("Staging serves this listing at /directory-member/alex-kellett/ with the title Norman Higgins; name, email and bio are all "
                                  "Norman Higgins's. Moved to his own address, with a redirect from the old one. Alex Kellett's own listing seems to be missing: Stephanie McDaniel checks.")
        begin(path, "staging", bugs, note, "Directory member")
        bio = rewrite_body(d["bio"])
        notes = []
        if re.search(r"^\s*<p>\s*test bio\s*</p>\s*$", d["bio"], re.I) or not bio:
            bio = TODO % ("Bio for %s; the member supplies it through the directory portal." % name)
        links = []
        for l in d["links"]:
            v = l["value"]
            if l["label"] == "Phone" and re.fullmatch(r"\d{2,4}0{6,}", v):
                links.append("<dt>Phone</dt><dd>%s</dd>" % (TODO % "phone number looks like a placeholder; member confirms"))
                continue
            links.append('<dt>%s</dt><dd><a href="%s">%s</a></dd>' % (E(l["label"]), A(l["href"]), E(v.rstrip("/"))))
        own = [s for s in d["social"] if "facebook.com/soilfoodweb" in s["href"]]
        social = [s for s in d["social"] if s not in own]
        if social:
            links.append("<dt>Social</dt><dd>%s</dd>" % " &middot; ".join('<a href="%s" rel="noopener">%s</a>' % (A(s["href"]), E(s["label"])) for s in social))
        if own:
            links.append("<dt>Social</dt><dd>%s</dd>" % (TODO % "social links on staging point to the Foundation's own Facebook page; member supplies their own"))
        pic = img(d["photo"], "Photo of %s" % name) if d["photo"] else ""
        body = ('<section class="band"><div class="wrap">%s<div class="profile"><div class="profile__photo">%s</div><div>'
                '<ul class="pills">%s</ul><h1>%s</h1>%s<h2>About</h2><div class="prose">%s</div>'
                '<h2>Location</h2><p>%s</p><h2>Contact</h2><dl class="kv">%s</dl></div></div></div></section>') % (
            back("/find-a-professional/", "Back to the directory"), pic,
            "".join("<li>%s</li>" % E(r.replace("Lab-Tech", "Lab Tech")) for r in d["roles"]), E(name),
            '<p class="profile__role">%s</p>' % E(d["company"]) if d["company"] else "", bio,
            E(d["area"]) or TODO % "Area; member supplies", "".join(links) or "<dt>Contact</dt><dd>Through the Foundation</dd>")
        role = " and ".join(r.replace("Lab-Tech", "Lab Tech") for r in d["roles"])
        write(path, name, "%s, Soil Food Web %s%s." % (name, role, (", " + d["area"]) if d["area"] else ""), body, "/case-studies/")


def video_pages():
    pl = playlists_data()
    for name, vids in pl.items():
        for v in vids:
            path = "/video/%s/" % v["slug"]
            begin(path, "staging", [], "", "Video")
            if v["vimeo"]:
                src = "https://player.vimeo.com/video/%s?dnt=1%s" % (v["vimeo"], "&h=" + v["vimeo_h"] if v["vimeo_h"] else "")
            else:
                src = "https://www.youtube-nocookie.com/embed/%s" % v["youtube"]
            if v["vimeo"] and v["thumb"]:
                player = facade(v["vimeo"], v["vimeo_h"], v["thumb"], fix(v["title"]))
            else:
                player = '<div class="embed"><iframe src="%s" title="%s" allow="fullscreen; picture-in-picture" loading="lazy"></iframe></div>' % (A(src), A(fix(v["title"])))
            items = "".join('<li><a href="/video/%s/"%s><span>%d</span>%s<span>%s</span></a></li>' % (
                o["slug"], ' aria-current="page"' if o is v else "", i + 1, img(o["thumb"], "") if o["thumb"] else "<span></span>", E(fix(o["title"])))
                for i, o in enumerate(vids))
            body = ('<section class="band"><div class="wrap">%s<div class="video-layout"><div>%s'
                    '<p class="eyebrow" style="margin-top:1.25rem">%s</p><h1>%s</h1>%s</div>'
                    '<aside aria-label="%s"><h2 class="h3">%s</h2><p class="meta">%d videos</p><ol class="plist">%s</ol></aside></div></div></section>') % (
                back("/case-studies/", "Back to case studies and videos"), player, E(name), E(fix(v["title"])),
                rewrite_body(v["body"]) if v["body"] else TODO % ("150 to 300 words about this film, written from its Vimeo transcript: who, where, what they did and what changed. Stephanie McDaniel."),
                A(name), E(name), len(vids), items)
            write(path, fix(v["title"]), "%s: a video from the Soil Food Web Foundation’s %s playlist." % (fix(v["title"]), name), body, "/case-studies/")


EVENT_TEXT = {
    "community": "A celebration of the Foundation’s first year.",
}


def event_pages():
    for e in all_events():
        path = "/calendar-event/%s/" % e["slug"]
        bugs = ["24"] if e["type"] in ("community", "course") or ":" in e.get("when", "") else []
        begin(path, "repo" if e.get("repo") else "staging", bugs, "", "Calendar event")
        detail = []
        if e.get("repo") == "pakistan":
            text, links = REPO_EVENT_TEXT["pakistan"]
            detail.append("<p>%s</p>" % E(text))
            detail.append('<p class="source">Source: this repo\u2019s calendar page. The 600 participants and 60 districts come from last year\u2019s event report.</p>')
            detail.append("<p>%s</p>" % " &middot; ".join('<a href="%s">%s</a>' % (A(h), E(l)) for l, h in links))
            detail.append(TODO % "Confirm the 2026 dates and the Foundation's role with Nick Padwick before publishing.")
        elif e.get("repo"):
            cal = repo("calendar")["featured"]
            detail.append("<p>%s</p>" % E(fix(cal["body"])))
            detail.append('<p class="source">Source: %s</p>' % E(cal["source"]))
            detail.append('<p class="actions"><a class="btn" href="%s">%s</a></p>' % (A(cal["cta"]["href"]), E(cal["cta"]["label"])))
        else:
            if e.get("body"):
                detail.append('<div class="prose">%s</div>' % rewrite_body(e["body"]))
            else:
                detail.append(TODO % ("Description, place and how to sign up for %s; the staging event page is empty. Evan or Stephanie McDaniel supplies." % e["title"]))
            if e.get("text_dates") and e["start"] and fmt_range(e["start"], e["end"]).split(" to ")[-1] not in e["text_dates"].replace("rd", "").replace("th", "") \
                    and e["slug"].endswith("2026-cohort-3"):
                detail.append(TODO % ("Dates disagree on staging: the calendar says %s, the event text says \u201c%s\u201d. Confirm the end date." % (fmt_range(e["start"], e["end"]), e["text_dates"])))
            if e["type"] == "community":
                detail.append(TODO % "Start time: staging shows 3:27 pm UTC, which looks like a placeholder. Confirm the time and time zone.")
            if e.get("signup"):
                label = {"workshop": "Register interest", "course": "Enroll on the school site", "community": "Join on the webinar site"}.get(e["type"], "Sign up")
                detail.append('<p class="actions"><a class="btn" href="%s">%s</a></p>' % (A(staging_link(e["signup"])), label))
            more = {"workshop": ('/workshops/', "About our workshops"), "course": ('/programs/#path', "See all Online Courses"),
                    "community": ('/year-one-report/', "Read the year one report")}.get(e["type"])
            if more:
                detail.append('<p><a class="more" href="%s">%s</a></p>' % more)
        body = ('<section class="band"><div class="wrap wrap--narrow">%s<p class="eyebrow">%s</p><h1>%s</h1>'
                '<dl class="kv"><dt>When</dt><dd><time datetime="%s">%s</time></dd><dt>Type</dt><dd>%s</dd></dl>%s</div></section>') % (
            back("/calendar/", "Back to the calendar"), EVENT_TYPES[e["type"]], E(e["title"]), e["start"], E(event_when(e)),
            EVENT_TYPES[e["type"]], "".join(detail))
        write(path, e["title"], "%s, %s." % (e["title"], event_when(e)), body, "/community/")


def publication_pages():
    for p in pubs():
        path = "/publication/%s/" % p["slug"]
        bugs = ["11"] if p["hide_citation"] else (["27"] if p["id"] == 1064 else [])
        begin(path, "staging", bugs, "", "Publication")
        links = " ".join('<a class="btn btn--ghost btn--small" href="%s" rel="noopener">%s</a>' % (A(h), l) for l, h in pub_links(p))
        rows = [("Year", p["year"]), ("Type", p["kind"]), ("Authors", p["authors"])]
        if p["citation"] and not p["hide_citation"]:
            rows.append(("Published in", p["citation"]))
        rows.append(("Collection", p["collection"]))
        if p["topics"]:
            rows.append(("Topics", ", ".join(p["topics"])))
        why = '<p class="lead"><b>Why read it:</b> <span class="draft"%s>%s</span></p>' % (' data-from="title"' if p["blurb_title_only"] else "", E(p["blurb"])) if p["blurb"] else TODO % "Why read it: one sentence from the abstract; Carla Portugal checks."
        extra = TODO % "Journal citation for this entry; Carla Portugal verifies it." if p["hide_citation"] else ""
        body = ('<section class="band"><div class="wrap wrap--narrow">%s<p class="eyebrow">%s</p><h1>%s</h1>%s'
                '<dl class="kv">%s</dl>%s%s</div></section>') % (
            back("/publications/", "Back to publications"), E(p["kind"]), E(p["title"]), why,
            "".join("<dt>%s</dt><dd>%s</dd>" % (E(k), E(v)) for k, v in rows), extra,
            '<p class="actions">%s</p>' % links if links else "")
        write(path, p["title"], "%s (%s). %s" % (p["title"], p["year"], p["authors"]), body, "/how-it-works/")


def post_pages():
    for p in all_posts():
        path = "/%s/" % p["slug"]
        bugs = []
        if p["slug"] in ("unconditional-freedom-at-home-and-in-the-world", "a-blueprint-to-return-to-the-garden-of-eden"):
            bugs.append("1")
        if p["slug"] == "obituary-for-dr-elaine-ingham":
            bugs.append("30")
        broken = len([1 for t in re.findall(r"<img[^>]*>", p["body"]) if not re.search(r'src="https?://(?!\d+")', t)])
        note = []
        if p.get("restored_images"):
            note.append("%d image(s) were empty on staging and are restored from the same post on soilfoodweb.com." % len(p["restored_images"]))
        if broken:
            note.append("%d image(s) are broken on staging and on the old site; left out." % broken)
        if p["slug"] == "obituary-for-dr-elaine-ingham":
            note.append("Bug 30: the repeated paragraph reported on 2 October was already gone from staging on 3 October; the build still drops any repeated paragraph.")
        begin(path, p.get("source", "staging"), bugs, " ".join(note), "Blog post")
        B.EXTRA_FLAG = PARTNER_POSTS.get(p["slug"])
        cats = " &middot; ".join('<a href="/category/%s/">%s</a>' % (c["slug"], E(c["name"])) for c in p["categories"])
        hero = img(p["featured"], p.get("featured_alt", ""), "article-hero", eager=True) if p.get("featured") else ""
        body_html = B.render(p["body"]) if p.get("source") == "repo" else rewrite_body(p["body"])
        by = ""
        for a in p.get("authors", []):
            photo = AUTHOR_PHOTOS.get(a["name"])
            pic = img(photo, "Portrait of %s" % a["name"]) if photo else ""
            missing = "" if photo else TODO % ("Photo of %s; the old site’s image is broken and no copy exists. Ask %s." % (a["name"], a["name"]))
            by += '<div class="byline">%s<p><strong>%s</strong><br>%s</p></div>%s' % (pic, E(a["name"]), E(fix(a["role"])), missing)
        body = ('<article class="band"><div class="wrap"><header class="article-head"><a class="back" href="/news/">All news</a>'
                '<p class="eyebrow">%s</p><h1>%s</h1><p class="meta"><time datetime="%s">%s</time></p></header>%s'
                '<div class="prose">%s</div>%s</div></article>') % (
            cats, E(fix(p["title"])), p["date"], fmt_date(p["date"]), hero, body_html, by)
        B.EXTRA_FLAG = None
        write(path, fix(p["title"]), (fix(p.get("excerpt", "")) or fix(p["title"]))[:200], body, "/community/")


# Posts whose pictures come from partners or guest authors: no permission on file.
PARTNER_POSTS = {
    "unconditional-freedom-at-home-and-in-the-world": "partner photo (Unconditional Freedom), no permission on file",
    "a-blueprint-to-return-to-the-garden-of-eden": "guest author photo (Philip Barton), no permission on file",
    "sadhguru-and-the-soil-food-web": "partner photo (Isha / Save Soil), no permission on file",
    "soil-health-week-2025-wild-soils-uk-and-trashit-bring-the-soil-food-web-approach-to-pakistan": "partner photo (Wild Soils UK, TrashIt), no permission on file",
    "october-2025-newsletter": "event photos (Groundswell and partners), no permission on file",
    "exploring-soil-food-web-innovations-in-west-africa": "partner photo, no permission on file",
}


AUTHOR_PHOTOS = {
    # bug 1: the Garden of Eden post's author photo, from the live soilfoodweb.com post
    "Philip Barton": "https://soilfoodweb.com/wp-content/uploads/2024/02/Webinar-picture--150x150.jpg",
}


def category_pages():
    ps = all_posts()
    cats = OrderedDict()
    for p in ps:
        for c in p["categories"]:
            cats.setdefault(c["slug"], (c["name"], []))[1].append(p)
    for slug, (name, items) in cats.items():
        path = "/category/%s/" % slug
        begin(path, "staging", [], "", "Category")
        body = ('<section class="pagehead"><div class="wrap"><a class="back" href="/news/">All news</a><p class="eyebrow">News &amp; blog</p>'
                '<h1>%s</h1><p>%d post%s.</p></div></section><section class="band"><div class="wrap"><ul class="grid">%s</ul></div></section>') % (
            E(name), len(items), "" if len(items) == 1 else "s", "".join(post_card(p) for p in items))
        write(path, name, "Posts filed under %s." % name, body, "/community/")


def item_pages():
    team_pages()
    directory_pages()
    video_pages()
    event_pages()
    publication_pages()
    post_pages()
    category_pages()


# ------------------------------------------------------------------ /review/
SOURCE_LABEL = {"staging": "staging copy with fixes", "repo": "this repo's version", "new": "new page", "": "generated"}


def review_page():
    begin("/review/", "new", [], "", "Review")
    main, items = [], OrderedDict()
    for path, r in B.PAGES.items():
        if path == "/review/":
            continue
        if r["kind"] == "page":
            main.append((path, r))
        else:
            items.setdefault(r["kind"], []).append((path, r))

    def flags(r):
        out = []
        for i in r["images"]:
            if i["flags"]:
                out.append("<li>%s: %s</li>" % (E(os.path.basename(i["src"].split("?")[0])), E("; ".join(i["flags"]))))
        return "<ul>%s</ul>" % "".join(sorted(set(out))) if out else ""

    def img_sources(r):
        n_repo = sum(1 for i in r["images"] if i["from"].startswith("repo") or i["from"] == "replacement")
        n_stg = sum(1 for i in r["images"] if i["from"] == "staging download")
        return "%d from repo, %d from staging" % (n_repo, n_stg) if r["images"] else ""

    def row(path, r):
        todos = "<ul>%s</ul>" % "".join("<li>%s</li>" % E(t) for t in r["todos"]) if r["todos"] else ""
        notes = '<p>%s</p>' % E(r["notes"]) if r["notes"] else ""
        return "<tr><td><a href=\"%s\">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s%s</td><td>%s</td></tr>" % (
            path, path, SOURCE_LABEL.get(r["source"], r["source"]), ", ".join(r["bugs"]), img_sources(r), flags(r), "", todos + notes)

    table = ('<div class="table-wrap"><table class="table"><thead><tr><th>Launch URL</th><th>Source</th><th>Bugs fixed</th>'
             '<th>Images</th><th>Flagged images</th><th>Placeholders left and notes</th></tr></thead><tbody>%s</tbody></table></div>')
    item_tables = []
    for kind, rows in items.items():
        n_todo = sum(len(r["todos"]) for _, r in rows)
        bugrows = [(p, r) for p, r in rows if r["bugs"] or r["todos"] or flags(r)]
        item_tables.append('<details class="faq"><summary>%s pages: %d (%d with placeholders, bug fixes or flags; %d placeholders)</summary><div>%s</div></details>' % (
            kind, len(rows), len(bugrows), n_todo, table % "".join(row(p, r) for p, r in bugrows) if bugrows else "<p>Nothing to flag.</p>"))
    notes = open(os.path.join(B.ROOT, "src", "review-notes.html"), encoding="utf-8").read() if os.path.exists(os.path.join(B.ROOT, "src", "review-notes.html")) else ""
    body = ('<section class="pagehead"><div class="wrap"><p class="eyebrow">Review</p><h1>What changed on each page</h1>'
            '<p>This preview rebuilds new.soilfoodweb.com at its launch addresses with the fixes from the 3 October 2026 brief. '
            'Yellow boxes on any page are placeholders that still need a fact from someone. Add <code>?review</code> to any address to highlight draft text.</p></div></section>'
            '<section class="band"><div class="wrap"><h2>Main pages</h2>%s<h2 style="margin-top:3rem">Item pages</h2>%s%s</div></section>') % (
        table % "".join(row(p, r) for p, r in main), "".join(item_tables), notes)
    write("/review/", "Review", "What changed on each page of the launch preview.", body)
