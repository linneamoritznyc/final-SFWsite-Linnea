#!/usr/bin/env python3
"""Build the launch preview: every page at its launch address as folder/index.html.

    python3 tools/site/build.py

Sources:
  src/pages/*.html      one fragment per page, with a front-matter block
  content/staging/*.json  data snapshot of new.soilfoodweb.com (tools/staging/)
  content/*.json        this repo's own copy, used where staging is thin

Front matter (between --- lines at the top of a page source):
  path:        /about/                     launch address
  title:       About us | Soil Food Web Foundation
  description: one sentence for search results
  source:      staging | repo | new        where the copy came from
  bugs:        5, 15, 17                   bug numbers from the brief fixed here
  notes:       free text shown on /review/

Tags inside a fragment:
  {{img src="URL or repo path" alt="..." class="..." eager}}
  {{name args}}   any generator in GEN below (team, courses, news, events, ...)

Output is plain static HTML; nothing here runs on the server.
"""
import html, json, os, re, shutil, sys, datetime
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import images  # noqa: E402

SRC = os.path.join(ROOT, "src", "pages")
STG = os.path.join(ROOT, "content", "staging")
E = lambda t: html.escape(str(t), quote=False)
A = lambda t: html.escape(str(t), quote=True)
SITE = "Soil Food Web Foundation"
TODAY = datetime.date(2026, 10, 3)

PAGES = OrderedDict()      # path -> review record
MISSING_ALT = []
EXTRA_FLAG = None           # set by a generator to flag every image it places (e.g. partner photos)
_current = None            # review record of the page being built


def data(name):
    return json.load(open(os.path.join(STG, name + ".json"), encoding="utf-8"))


def repo(name):
    return json.load(open(os.path.join(ROOT, "content", name + ".json"), encoding="utf-8"))


# ----------------------------------------------------------------- images
def img(src, alt=None, cls="", eager=False, sizes=None, name=None):
    rec = images.resolve(src, name=name)
    a = rec["alt"] if alt is None else alt
    if a is None or (alt is None and not a):
        MISSING_ALT.append((_current["path"] if _current else "?", src))
        a = ""
    if _current is not None:
        flags = list(rec["flags"])
        # A small portrait or thumbnail is fine at low resolution; flag only large slots.
        small = (a or "").startswith(("Portrait of", "Photo of")) or "card__img" in cls or (not cls and not a)
        if small:
            flags = [f for f in flags if not f.startswith("low resolution")]
        if EXTRA_FLAG:
            flags.append(EXTRA_FLAG)
        _current["images"].append({"src": src, "file": rec["file"], "from": rec["source"], "flags": flags})
    attrs = ['src="/%s"' % rec["file"], 'width="%d"' % rec["w"], 'height="%d"' % rec["h"], 'alt="%s"' % A(a)]
    if cls:
        attrs.append('class="%s"' % cls)
    attrs.append('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"')
    attrs.append('decoding="async"')
    return "<img %s>" % " ".join(attrs)


NEW_SRC = os.path.join(ROOT, "img", "new-2026-10")   # originals, kept out of the deploy (.vercelignore)
NEW_OUT = os.path.join(ROOT, "img", "new")
NEW_FLAGS = {}  # R5A shoot rights confirmed by Linnea, 4 October 2026


def _loose(name):
    return re.sub(r"[\s_]+", " ", os.path.splitext(name)[0]).strip().lower()


def photo(file, alt, cls="", eager=False, caption=None, sizes="(min-width: 64em) 50vw, 100vw", name=None, full=True):
    """A supplied photo or diagram from img/new-2026-10/: WebP at up to 2400 px on the long
    side plus a 1200 px version for phones, no upscaling, never cropped (BioRender credits
    stay visible). File names match loosely (underscores or spaces, any case). HEIC is read
    via pillow-heif; phone photos are turned upright from their EXIF orientation. name sets
    the output file name; full=False (cards) stops at 1200 px."""
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    want = _loose(file)
    hits = [f for f in os.listdir(NEW_SRC) if _loose(f) == want]
    slug = name or re.sub(r"[^a-z0-9]+", "-", want).strip("-")
    if not hits:
        # Some originals are gitignored (phone HEICs, the R5A shoot), so a fresh
        # clone has only the committed outputs. Use those rather than stop.
        made = sorted((f for f in os.listdir(NEW_OUT) if re.fullmatch(re.escape(slug) + r"-\d+w\.jpg", f)),
                      key=lambda f: -int(f.rsplit("-", 1)[1][:-5])) if os.path.isdir(NEW_OUT) else []
        if not made:
            raise SystemExit("photo: %s not found in img/new-2026-10/" % file)
        return _photo_tag([(os.path.relpath(os.path.join(NEW_OUT, f[:-4]), ROOT),) + Image.open(os.path.join(NEW_OUT, f)).size
                           for f in made], "img/new-2026-10/" + file, want, alt, cls, eager, caption, sizes)
    srcf = os.path.join(NEW_SRC, hits[0])
    os.makedirs(NEW_OUT, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(srcf))
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    variants = []
    # 1600 and 800 px wide, never upscaled, each written as WebP and as JPG, under 300 KB, no EXIF.
    for width in (1600, 800):
        scale = min(1.0, width / im.size[0])
        w, h = round(im.size[0] * scale), round(im.size[1] * scale)
        if variants and w >= variants[-1][1]:
            continue  # source no wider than 800 px: one size serves both
        stem = os.path.join(NEW_OUT, "%s-%dw" % (slug, w))
        if not os.path.exists(stem + ".jpg") or os.path.getmtime(stem + ".jpg") < os.path.getmtime(srcf):
            r = im.resize((w, h), Image.LANCZOS) if scale < 1 else im
            for ext, fmt in ((".webp", "WEBP"), (".jpg", "JPEG")):
                rr = r.convert("RGB") if fmt == "JPEG" else r
                rr, q = rr, 82
                while True:
                    if fmt == "JPEG":
                        rr.save(stem + ext, fmt, quality=q, optimize=True, progressive=True)
                    else:
                        rr.save(stem + ext, fmt, quality=q, method=6)
                    if os.path.getsize(stem + ext) <= 300 * 1024:
                        break
                    if q > 70:
                        q -= 4
                    else:  # still heavy at a decent quality: make it smaller rather than blurrier
                        rr = rr.resize((round(rr.size[0] * .9), round(rr.size[1] * .9)), Image.LANCZOS)
        actual = Image.open(stem + ".jpg").size
        variants.append((os.path.relpath(stem, ROOT), actual[0], actual[1]))
    return _photo_tag(variants, "img/new-2026-10/" + hits[0], want, alt, cls, eager, caption, sizes)


def _photo_tag(variants, src, want, alt, cls, eager, caption, sizes):
    """variants: (path without extension, width, height), largest first."""
    small = variants[-1]
    if _current is not None:
        flags = [why for k, why in NEW_FLAGS.items() if want.startswith(k.replace("_", " "))]
        _current["images"].append({"src": src, "file": small[0] + ".jpg", "from": "supplied (Google Drive)", "flags": flags})
    big = variants[0]
    attrs = ['src="/%s.jpg"' % big[0], 'width="%d"' % big[1], 'height="%d"' % big[2], 'alt="%s"' % A(alt)]
    srcset = lambda ext: ", ".join("/%s%s %dw" % (f, ext, w) for f, w, _ in reversed(variants))
    if len(variants) > 1:
        attrs.append('srcset="%s"' % srcset(".jpg"))
        attrs.append('sizes="%s"' % A(sizes))
    if cls:
        attrs.append('class="%s"' % cls)
    attrs.append('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"')
    attrs.append('decoding="async"')
    source = '<source type="image/webp" srcset="%s"%s>' % (srcset(".webp"), ' sizes="%s"' % A(sizes) if len(variants) > 1 else "")
    tag = "<picture>%s<img %s></picture>" % (source, " ".join(attrs))
    if caption:
        return '<figure class="photo">%s<figcaption>%s</figcaption></figure>' % (tag, E(caption))
    return tag


def flag_image(src, why):
    """Extra review flag for an image, e.g. a partner photo with no permission on file."""
    rec = images.resolve(src)
    if why not in rec["flags"]:
        rec["flags"].append(why)


# ----------------------------------------------------------------- chrome
# Menus copied from new.soilfoodweb.com (9 October 2026): same labels, same addresses.
# Staging links "Partner on Research" and "Governance and financials" to "#" and "Media and
# press" to /contact/ (which redirects to /contact-info/); here they go to the page that exists.
NAV = [
    ("Home", "/", None),
    ("About Us", "/about-us/", [
        ("Mission, Vision & Story", "/about-us/#mission"),
        ("Our Team", "/about-us/#team"),
        ("Dr. Elaine’s Research", "/about-us/#dr-elaine"),
        ("Foundation News", "/category/foundation-update/"),
        ("Contact & Legal", "/about-us/#contact-legal"),
    ]),
    ("Learn", "/programs-overview/", [
        ("Programs Overview", "/programs-overview/"),
        ("Online Courses", "/programs-overview/#path"),
        ("Workshops", "/workshops/"),
        ("Free Webinars", "https://webinar.soilfoodweb.com"),
        ("Scholarship", "/scholarship/"),
        ("Student Login", "/login/"),
    ]),
    ("Science", "/how-it-works/", [
        ("How the Soil Food Web Works", "/how-it-works/"),
        ("Research Database", "/publications/"),
        ("Partner on Research", "/practice/#work-with-us"),
    ]),
    ("Practice", "/practice/", [
        ("Case Studies", "/practice/#CASE-STUDIES"),
        ("Find a Professional", "/find-a-professional/"),
        ("Work With Us", "/practice/#work-with-us"),
    ]),
    ("Community", "/community/", [
        ("Community Map", "/community/#community-map"),
        ("News & Blog", "/news/"),
        ("Calendar", "/calendar/"),
        ("Join the Community", "https://school.soilfoodweb.com/products/communities/SFW-public-community"),
    ]),
]

FOOTER = [
    ("Foundation", [("About us", "/about-us/"), ("Our team and board", "/about-us/#team"),
                    ("Dr. Elaine’s research", "/publications/"),
                    ("Governance and financials", "/foundation-legal/"), ("Contact us", "/about-us/#contact-legal")]),
    ("Learn", [("Explore our programs", "/programs-overview/"), ("On-line Courses", "/programs-overview/#path"),
               ("Workshops and events", "/workshops/"), ("Calendar", "/calendar/"),
               ("Free webinars", "https://webinar.soilfoodweb.com/"), ("Scholarships", "/scholarship/")]),
    ("Resources", [("How the soil food web works", "/how-it-works/"),
                   ("Research and publications", "/publications/"), ("Case studies", "/practice/#CASE-STUDIES"),
                   ("Media and press", "/contact-info/"),
                   ("sMApp on soilmapp.com", "https://www.soilmapp.com/")]),
    ("Get involved", [("Donate", "/donations/"), ("Volunteer with us", "/volunteer/"),
                      ("Invite us to speak", "/invite-us-to-speak/"),
                      ("Find a professional", "/find-a-professional/"),
                      ("Logo and name use", "/logo-brand-use/")]),
]

SCHOOL_LINE = "The Soil Food Web School is a program of the Soil Food Web Foundation."
# The funding sentence from docs/copy-deck-v2.md (section 5), shown site-wide
# so a reviewer landing on any page sees how course fees serve the mission.
FUNDING_LINE = ("Course fees are program revenue; after the cost of delivering the courses "
                "they fund scholarships, open research and field projects.")
LEGAL = ("Soil Food Web Foundation is a 501(c)(3) nonprofit organization, EIN 39-4439236, "
         "Oregon DOJ registration #71264. Registered office: 5441 S Macadam Ave Ste N, Portland, Oregon 97239.")


def ext(href):
    return href.startswith("http")


def link(label, href, cur=""):
    a = ' aria-current="page"' if href == cur else ""
    return '<a href="%s"%s>%s</a>' % (A(href), a, E(label))


def header(path, active):
    items = []
    for i, (label, href, sub) in enumerate(NAV):
        if not sub:
            items.append("<li>%s</li>" % link(label, href, path))
            continue
        cur = ' aria-current="page"' if active == href else ""
        subs = "".join("<li>%s</li>" % link(l, h, path) for l, h in sub)
        items.append('<li><button class="nav__top" type="button" aria-expanded="false" aria-controls="sub-%d"%s>%s</button>'
                     '<ul class="sub" id="sub-%d"><li>%s</li>%s</ul></li>' % (i, cur, E(label), i, link(label + " overview" if False else label, href, path), subs))
    items.append('<li><a class="btn btn--donate" href="/donations/">Donate</a></li>')
    ocm = []
    for label, href, sub in NAV:
        if not sub:
            ocm.append("<li>%s</li>" % link(label, href, path))
        else:
            subs = "".join("<li>%s</li>" % link(l, h, path) for l, h in sub)
            ocm.append("<li><details><summary>%s</summary><ul><li>%s</li>%s</ul></details></li>" % (E(label), link(label, href, path), subs))
    return """<a class="skip" href="#main">Skip to content</a>
<p class="preview-flag">Review preview of the launch site, not public. <a href="/review/">What changed on each page</a></p>
<div class="utility"><div class="wrap"><span class="utility__name">The Soil Food Web Foundation 501(c)(3)</span><nav aria-label="Account"><a href="/login/">Student login</a><a href="#newsletter">Subscribe</a></nav></div></div>
<header class="site-header"><div class="wrap">
<a class="logo" href="/"><img src="/img/sfwlogo-240.webp" width="80" height="69" alt="Soil Food Web Foundation, home"></a>
<nav class="nav" aria-label="Main"><ul>%s</ul></nav>
<button class="menu-btn" type="button" data-menu-open aria-expanded="false" aria-controls="ocm"><span aria-hidden="true"></span>Menu</button>
</div></header>
<div class="ocm" id="ocm" hidden><div class="ocm__scrim"></div><div class="ocm__panel" role="dialog" aria-modal="true" aria-label="Menu">
<div class="ocm__top"><p class="ocm__name">Soil Food Web Foundation<small>A 501(c)(3) nonprofit</small></p><button class="ocm__close" type="button" data-menu-close>&times; Close</button></div>
<nav aria-label="Main"><ul>%s</ul></nav><a class="btn btn--donate" href="/donations/">Donate</a></div></div>
""" % ("".join(items), "".join(ocm))


def footer(path):
    cols = "".join('<div class="footer-col"><h2>%s</h2><ul>%s</ul></div>' % (E(h), "".join("<li>%s</li>" % link(l, u, path) for l, u in ls)) for h, ls in FOOTER)
    return """<footer class="site-footer" role="contentinfo"><div class="wrap">
<div class="footer-top">
<div class="footer-brand"><p class="footer-brand__name">Soil Food Web Foundation</p><p class="footer-brand__status">A 501(c)(3) nonprofit</p>
<p class="footer-brand__line">Healing soil. Feeding humanity. Restoring the living world.</p>
<form class="newsletter" id="newsletter" data-newsletter action="#" method="post"><label class="sr-only" for="newsletter-email">Email for the newsletter</label>
<input id="newsletter-email" type="email" name="email" placeholder="Email for the newsletter" autocomplete="email"><button class="btn" type="submit">Subscribe</button></form>
<small>One email a month. Unsubscribe with one click.</small></div>
<div class="footer-cols">%s</div>
</div>
<div class="footer-legal"><p>EIN 39-4439236. Registered office: 5441 S Macadam Ave Ste N, Portland, Oregon 97239. Our Form 990 and financial statements are available on the <a href="/foundation-legal/">governance page</a> and on request.</p></div>
<div class="footer-bottom"><p>&copy; 2026 Soil Food Web Foundation, a 501(c)(3) nonprofit organization. Soil Food Web School is a program of the Soil Food Web Foundation.</p>
<ul><li><a href="/privacy/">Privacy</a></li><li><a href="/terms/">Terms</a></li><li><a href="/about-us/#contact-legal">Accessibility</a></li></ul></div>
</div></footer>""" % (cols,)


def shell(path, title, desc, body, active=None):
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>%s</title>
<meta name="description" content="%s">
<link rel="icon" href="/img/favicon.png" type="image/png">
<link rel="preload" href="/fonts/montserrat-latin-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
<script src="/js/site.js" defer></script>
</head>
<body>
%s
<main id="main">
%s
</main>
%s
</body>
</html>
""" % (E(title), A(desc), header(path, active), body.strip(), footer(path))


# ----------------------------------------------------------------- page writing
def out_path(path):
    p = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def begin(path, source, bugs=(), notes="", kind="page"):
    global _current
    _current = {"path": path, "source": source, "bugs": list(bugs), "notes": notes, "images": [], "todos": [], "kind": kind, "title": ""}
    PAGES[path] = _current
    return _current


def write(path, title, desc, body, active=None):
    full = title if title.endswith(SITE) else "%s | %s" % (title, SITE)
    h1s = len(re.findall(r"<h1[\s>]", body))
    if h1s != 1:
        print("WARNING: %s has %d h1" % (path, h1s))
    _current["title"] = full
    _current["todos"] = [re.sub(r"<[^>]+>", "", t).strip() for t in re.findall(r'<(?:p|span|li|div) class="todo"[^>]*>(.*?)</(?:p|span|li|div)>', body, re.S)]
    open(out_path(path), "w", encoding="utf-8").write(shell(path, full, desc, body, active))


TAG = re.compile(r"\{\{\s*(\w+)(.*?)\}\}", re.S)
ATTR = re.compile(r'(\w+)(?:="([^"]*)")?')


def render(text):
    def sub(m):
        name, args = m.group(1), m.group(2).strip()
        if name == "img":
            kv = {k: (v if v is not None else True) for k, v in ATTR.findall(args)}
            kv = {k: (True if v == "" and k in ("eager",) else v) for k, v in kv.items()}
            return img(kv["src"], kv.get("alt"), kv.get("class", ""), bool(kv.get("eager")))
        if name == "photo":
            kv = {k: v for k, v in ATTR.findall(args)}
            extra = {"sizes": kv["sizes"]} if kv.get("sizes") else {}
            if kv.get("name"):
                extra["name"] = kv["name"]
            return photo(kv["file"], kv["alt"], kv.get("class", ""), "eager" in kv, kv.get("caption") or None,
                         full="card" not in kv, **extra)
        return GEN[name](args)
    prev = None
    while prev != text:
        prev, text = text, TAG.sub(sub, text)
    return text


def page_source(f):
    raw = open(f, encoding="utf-8").read()
    meta, body = {}, raw
    if raw.startswith("---"):
        head, body = raw[3:].split("\n---", 1)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body


def build_pages():
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".html"):
            continue
        meta, body = page_source(os.path.join(SRC, f))
        bugs = [b.strip() for b in meta.get("bugs", "").split(",") if b.strip()]
        begin(meta["path"], meta.get("source", ""), bugs, meta.get("notes", ""))
        write(meta["path"], meta["title"], meta.get("description", ""), render(body), meta.get("nav"))


# ----------------------------------------------------------------- generators
GEN = {}


def gen(fn):
    GEN[fn.__name__] = fn
    return fn


def fmt_date(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return "%d %s %d" % (d.day, d.strftime("%B"), d.year)


def fmt_range(a, b):
    da, db = datetime.date.fromisoformat(a), datetime.date.fromisoformat(b)
    if da == db:
        return fmt_date(a)
    if da.year == db.year and da.month == db.month:
        return "%d to %d %s %d" % (da.day, db.day, db.strftime("%B"), db.year)
    if da.year == db.year:
        return "%d %s to %d %s %d" % (da.day, da.strftime("%B"), db.day, db.strftime("%B"), db.year)
    return "%s to %s" % (fmt_date(a), fmt_date(b))


sys.modules.setdefault("build", sys.modules[__name__])  # gens.py imports this module by name
import gens  # noqa: E402,F401  (registers generators and item pages)


def main():
    # Remove only the index.html files the last build wrote, then any folder
    # that is left empty, so a renamed page does not linger and nothing else
    # in the repo (video/, img/, ...) is ever touched.
    record = os.path.join(STG, "built-pages.json")
    for p in (json.load(open(record)) if os.path.exists(record) else []):
        f = out_path(p)
        if os.path.exists(f):
            os.remove(f)
        d = os.path.dirname(f)
        while d != ROOT and os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
            d = os.path.dirname(d)
    build_pages()
    gens.item_pages()
    gens.review_page()
    images.save_manifest()
    json.dump(sorted(PAGES), open(record, "w"), indent=0)
    print("pages:", len(PAGES))
    if MISSING_ALT:
        print("MISSING ALT (%d):" % len(MISSING_ALT))
        for p, s in MISSING_ALT:
            print("  ", p, s)


if __name__ == "__main__":
    main()
