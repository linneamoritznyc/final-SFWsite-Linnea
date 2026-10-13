#!/usr/bin/env python3
"""Inventory every image, graphic, GIF, video and button on the live WordPress
site and match each file to its source in this repo or the SFW Drive.

    python3 tools/asset-inventory.py                       # crawls new.soilfoodweb.com
    python3 tools/asset-inventory.py --base http://127.0.0.1:8000   # any other host

Writes asset-inventory.csv (one row per asset per placement, pages in menu
order) and asset-inventory-links.csv (every non-button link that is broken or
points at the old site). Prints the count per page, the files with no source
found, and the broken buttons and links.

Standard library only; pixel sizes come from ffprobe, which reads images and
video alike. Downloads are cached in --cache so a rerun is cheap.

Drive links: only the SFW Drive list below (Stephanie's image log and Linnea).
Never add a link to anyone's personal Drive here.
"""
import argparse, collections, csv, hashlib, html, json, os, re, subprocess, sys
import urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser
from xml.etree import ElementTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_DIRS = ("img", "video", "exports", "tools/blog-cards/photos")
OLD_HOSTS = ("soilfoodweb.com", "www.soilfoodweb.com")
OLD_PATHS = ("/foundation-courses-2", "/shop", "/product/", "/cart", "/checkout", "/my-account")
LOCAL = re.compile(r"^(?:https?://)?(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(?::\d+)?", re.I)
SKIP_PATH = re.compile(r"/(?:cdn-cgi|wp-admin|wp-login\.php|wp-json|feed|xmlrpc\.php|comments/feed)\b|/feed/?$|[?&](?:replytocom|share)=", re.I)
MEDIA_EXT = re.compile(r"\.(?:jpe?g|png|gif|webp|avif|svg|bmp|tiff?|ico|mp4|webm|mov|m4v|ogv)(?:$|\?)", re.I)
VIDEO_EXT = re.compile(r"\.(?:mp4|webm|mov|m4v|ogv)(?:$|\?)", re.I)
GRAPHIC_HINT = re.compile(r"logo|icon|badge|graphic|diagram|illustration|infographic|chart|map|seal|qr", re.I)
BUTTON_CLASS = re.compile(r"\b(?:wp-block-button__link|wp-element-button|elementor-button|button|btn|cta)\b", re.I)
WP_SUFFIX = re.compile(r"(?:-\d+x\d+|-scaled|-rotated|-e\d{10,}|@2x)$", re.I)
REPO_SUFFIX = re.compile(r"-(?:240|512|640|800)$")
UPLOAD_DATE = re.compile(r"/wp-content/uploads/(\d{4})/(\d{2})/")
CSS_URL = re.compile(r"url\(\s*([\"']?)([^)\"']+)\1\s*\)", re.I)
YOUTUBE = re.compile(r"(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|shorts/)|youtu\.be/)([\w-]{11})", re.I)
VIMEO = re.compile(r"(?:player\.)?vimeo\.com/(?:video/)?(\d{6,})", re.I)

DRIVE = {
    "2 dirty hands": "https://drive.google.com/file/d/1hRjWUxoN2QhsFvNWk8jG1VPz6BU0QcF-/view",
    "2 hands clasped holding plant roots": "https://drive.google.com/file/d/1vsyp3Tle-3yP13uY-RMLluDewyoA4Egx/view",
    "2 hands planting shrub": "https://drive.google.com/file/d/193uuZ1E_MPlXv-N2e5bwF-0O5sj3v7IT/view",
    "Fist of dry soil": "https://drive.google.com/file/d/1U4Yl3q1-61vgV1I0StnXPziCxIxYyZRC/view",
    "Gloved hands": "https://drive.google.com/file/d/13_OX4a7KEUMeC3PF5tQfEmIV0Y3D0Unh/view",
    "Hand, soil, roots, fungi": "https://drive.google.com/file/d/1BmPi6todBxz8zFRnmXBlhDeQZUMJmXPb/view",
    "Hands, wet dirt, worms": "https://drive.google.com/file/d/1Y4FG3s-F9BQitNWlkw-3Hhw1JwHzm0Tm/view",
    "Hand of compost": "https://drive.google.com/file/d/162s49QwIFM7sdb62JFTEBy29SAERPPyE/view",
    "Hand scooping planter bed soil": "https://drive.google.com/file/d/13OId4KvmonHvcIqSeEYfvMNOAmzqkAyK/view",
    "Handling loose soil": "https://drive.google.com/file/d/1tOnit5YCWPpXakvN5wZHlwCGMv7LZsn2/view",
    "Red soil, hand": "https://drive.google.com/file/d/1p5P5oAbTIbEP0dqhLldxeTxM733RHbbp/view",
    "Soil sample, shovel and bag": "https://drive.google.com/file/d/1JNakdMJOybMXNzUAKQ_V_Ka5PwWWLx0T/view",
    "Soil sample, close up": "https://drive.google.com/file/d/1SLhY-6iQYagD4ljr4_CnXMZWYtI9_WCz/view",
    "Soil and hand": "https://drive.google.com/file/d/1RnoG4rcm47ywZiVZQp2QzN0MPcv56rlw/view",
    "People digging": "https://drive.google.com/file/d/114RoSnKyQAGrNvbpmrdzPFApSZhEaQnf/view",
    "Dr Elaine Ingham with microscope": "https://drive.google.com/file/d/1k03t56f3igfui6TbohmgPeaRJVjWKKPZ/view",
    "Elaine with sample bag": "https://drive.google.com/file/d/1tQg_VtI8iBwVr_M7cmr372R2oP8mX-l0/view",
    "Elaine flower shirt microscope": "https://drive.google.com/file/d/1EvvyKI9A7oOC0RrbFsAu4ktck6hDJh9A/view",
    "Elaine and nematode extraction": "https://drive.google.com/file/d/1APd8fe7ftVA9bwxNBLa-YC3QveE7a01L/view",
    "Elaine smile talking": "https://drive.google.com/file/d/1Frx9mpqhKYzcgpJPEq-ktJZ_zXqyEqOl/view",
    "Sampling equipment": "https://drive.google.com/file/d/1IcowYSdUfYKcY01dfpARhXIn-GR7pi4l/view",
    "Test tubes with sample": "https://drive.google.com/file/d/1_CI4ZiXFvjg4_1NfkiOHkk_kQQvswMzV/view",
    "Carla, Nick's son, Wild Soils event Nov 2024": "https://drive.google.com/file/d/1Hcn-5lvVmFWzHcDbaLWLa2m7dTpCP1_s/view",
}
# Drive titles that differ from the file names the photos were saved under.
DRIVE_ALIASES = {
    "Gloved hands": ["gloved hands red bucket mulch"],
    "Hand, soil, roots, fungi": ["hand soil roots fungi"],
    "Hands, wet dirt, worms": ["hand wet dirt worm"],
    "Soil sample, close up": ["soil sample close up test tube"],
    "Carla, Nick's son, Wild Soils event Nov 2024": ["Carla-Nicks Son-Nick-ERI-Wild Soils Event-11-2024"],
}

COLUMNS = ["Page slug", "Section", "Type", "Current file name", "WordPress media URL", "Links to",
           "Pixel size", "File size", "Repo path", "SFW Drive link", "Also used on", "Notes"]


# ---------------------------------------------------------------- names

def stem(name):
    name = urllib.parse.unquote(name.split("?")[0].rstrip("/").rsplit("/", 1)[-1])
    return re.sub(r"\.[A-Za-z0-9]{2,5}$", "", name)


def original_stem(name):
    """File stem with WordPress size variants removed: foo-1024x683 -> foo."""
    s = stem(name)
    while True:
        t = WP_SUFFIX.sub("", s)
        if t == s:
            return s
        s = t


def key(name, repo=False):
    """Compare names ignoring case, spaces, hyphens, punctuation and size suffixes."""
    s = original_stem(name)
    if repo:
        s = REPO_SUFFIX.sub("", s)
    return re.sub(r"[^a-z0-9]", "", s.lower())


def repo_index():
    idx = collections.defaultdict(list)
    for d in REPO_DIRS:
        for dirpath, _, files in os.walk(os.path.join(ROOT, d)):
            for f in files:
                if MEDIA_EXT.search(f):
                    rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
                    idx[key(f, repo=True)].append(rel)
                    idx[key(f)].append(rel)
    return {k: sorted(set(v), key=lambda p: (REPO_SUFFIX.search(stem(p)) is not None, len(p), p))
            for k, v in idx.items()}


def label_key(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def repo_buttons():
    """Buttons on the static prototype pages that Alex rebuilt in WordPress:
    label key -> [(page, href)]."""
    import glob
    idx = collections.defaultdict(list)
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "projects", "*.html"))
                   + glob.glob(os.path.join(ROOT, "news", "*.html")))
    for path in files:
        pg = Page("https://repo.local/" + os.path.relpath(path, ROOT))
        try:
            pg.feed(open(path, encoding="utf-8", errors="replace").read())
        except Exception:
            continue
        for ln in pg.links:
            if ln["is_button"] and ln["text"]:
                idx[label_key(ln["text"])].append((os.path.relpath(path, ROOT), ln.get("abs") or (ln.get("raw_href") or "").strip()))
    return idx


def href_key(h):
    """Compare a live href with a prototype href: path only, .html and index dropped."""
    p = urllib.parse.urlsplit(h or "")
    host = p.netloc.lower().replace("www.", "")
    path = re.sub(r"(?:index)?\.html$", "", p.path).strip("/")
    if host in ("", "new.soilfoodweb.com", "repo.local"):
        host = ""
    return host + "/" + path + ("#" + p.fragment if p.fragment else "")


def drive_index():
    idx = {}
    for title, link in DRIVE.items():
        for t in [title] + DRIVE_ALIASES.get(title, []):
            idx[key(t)] = link
    return idx


def repo_videos():
    """Vimeo and YouTube IDs the repo already knows, from content/videos.json."""
    out = {}
    p = os.path.join(ROOT, "content", "videos.json")
    if os.path.exists(p):
        for m in re.finditer(r'"slug":\s*"([^"]+)"[^{}]*?"id":\s*"(\w+)"|"id":\s*"(\w+)"[^{}]*?"slug":\s*"([^"]+)"', open(p).read()):
            slug, vid = (m.group(1), m.group(2)) if m.group(1) else (m.group(4), m.group(3))
            out[vid] = "content/videos.json (" + slug + ")"
    return out


# ---------------------------------------------------------------- fetching

class SameHostRedirects(urllib.request.HTTPRedirectHandler):
    """Follow redirects on the same host only. Publication entries redirect to
    doi.org or Google Scholar; those are papers, not pages on this site."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).netloc.lower() != urllib.parse.urlsplit(req.full_url).netloc.lower():
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(SameHostRedirects)


class Fetcher:
    def __init__(self, cache, timeout=30):
        self.cache, self.timeout = cache, timeout
        os.makedirs(cache, exist_ok=True)
        self.memo = {}

    def get(self, url, body=True):
        """(status, headers dict, bytes or None, local path or None)."""
        if (url, body) in self.memo:
            return self.memo[(url, body)]
        path = os.path.join(self.cache, hashlib.sha1(url.encode()).hexdigest())
        meta = path + ".json"
        if os.path.exists(meta) and (not body or os.path.exists(path)):
            m = json.load(open(meta))
            res = (m["status"], m["headers"], open(path, "rb").read() if body and os.path.exists(path) else None,
                   path if os.path.exists(path) else None)
            self.memo[(url, body)] = res
            return res
        safe_url = urllib.parse.quote(url, safe=":/?&=%#@+,;~!$'()*[]")  # file names with "×" etc.
        req = urllib.request.Request(safe_url, method="GET" if body else "HEAD",
                                     headers={"User-Agent": "sfw-asset-inventory/1.0"})
        status, headers, data = 0, {}, None
        try:
            with OPENER.open(req, timeout=self.timeout) as r:
                status, headers = r.status, {k.lower(): v for k, v in r.headers.items()}
                data = r.read() if body else None
        except urllib.error.HTTPError as e:
            status, headers = e.code, {k.lower(): v for k, v in e.headers.items()}
        except Exception as e:
            headers = {"error": str(e)}
        if not body and status in (403, 405, 501):  # some hosts refuse HEAD
            return self.get(url, body=True)
        if data is not None:
            open(path, "wb").write(data)
        if status:
            json.dump({"status": status, "headers": headers}, open(meta, "w"))
        res = (status, headers, data, path if data is not None else None)
        self.memo[(url, body)] = res
        return res


def probe(path):
    if not path:
        return ""
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height", "-of", "csv=p=0:s=x", path],
                             capture_output=True, text=True, timeout=60).stdout.strip().splitlines()
        return out[0] if out and re.match(r"^\d+x\d+$", out[0]) else ""
    except Exception:
        return ""


def svg_size(data):
    head = data[:2000].decode("utf-8", "ignore") if data else ""
    w, h = re.search(r'\bwidth="([\d.]+)', head), re.search(r'\bheight="([\d.]+)', head)
    if w and h:
        return "%sx%s" % (w.group(1), h.group(1))
    vb = re.search(r'viewBox="[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)', head)
    return "%sx%s (viewBox)" % vb.groups() if vb else ""


def human(n):
    if n in (None, ""):
        return ""
    n = int(n)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


# ---------------------------------------------------------------- parsing

def largest_srcset(srcset):
    best, best_w = None, -1
    for part in srcset.split(","):
        bits = part.strip().split()
        if not bits:
            continue
        w = 1
        if len(bits) > 1:
            m = re.match(r"([\d.]+)([wx])", bits[1])
            if m:
                w = float(m.group(1)) * (1 if m.group(2) == "w" else 10000)
        if w > best_w:
            best, best_w = bits[0], w
    return best


class Page(HTMLParser):
    HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self, url):
        super().__init__(convert_charrefs=True)
        self.url = url
        self.section = "(top of page)"
        self.region = []            # header / nav / footer stack
        self.items = []             # dicts: kind, src, section, ...
        self.links = []             # (href, label, region, section, is_button)
        self.styles, self.stylesheets = [], []
        self._heading, self._htext = None, []
        self._anchor = None         # open <a> or <button>: dict
        self._in_style = False
        self._video = None

    def abs(self, u):
        return urllib.parse.urljoin(self.url, html.unescape(u.strip())) if u is not None else u

    def add(self, kind, src, **kw):
        if src and not src.startswith("data:"):
            self.items.append(dict(kind=kind, src=self.abs(src), section=self.section,
                                   region="/".join(self.region), **kw))

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag in ("header", "footer", "nav"):
            self.region.append(tag)
        if tag in self.HEADINGS:
            self._heading, self._htext = tag, []
        if tag == "style":
            self._in_style = True
        if tag == "link" and "stylesheet" in a.get("rel", "").lower() and a.get("href"):
            self.stylesheets.append(self.abs(a["href"]))
        for m in CSS_URL.finditer(a.get("style", "")):
            self.add("css", m.group(2), via="inline style")
        for attr in ("data-bg", "data-background", "data-background-image", "data-bg-image"):
            if a.get(attr):
                self.add("css", a[attr], via=attr)
        if tag == "img":
            src = a.get("data-src") or a.get("data-lazy-src") or a.get("src")
            srcset = a.get("data-srcset") or a.get("data-lazy-srcset") or a.get("srcset")
            self.add("img", src, srcset_max=self.abs(largest_srcset(srcset)) if srcset else "", alt=a.get("alt"))
            if self._anchor is not None:
                self._anchor["text"].append(a.get("alt", ""))
        if tag == "source":
            if self._video is not None or VIDEO_EXT.search(a.get("src", "")):
                self.add("video", a.get("src"))
            elif a.get("srcset"):
                self.add("img", largest_srcset(a["srcset"]), srcset_max="", alt="(picture source)")
        if tag == "video":
            self._video = a
            if a.get("src"):
                self.add("video", a["src"])
            if a.get("poster"):
                self.add("img", a["poster"], srcset_max="", alt="(video poster)")
        if tag == "iframe":
            src = a.get("data-src") or a.get("src") or ""
            yt, vm = YOUTUBE.search(src), VIMEO.search(src)
            if yt or vm:
                self.add("embed", src, provider="YouTube" if yt else "Vimeo", vid=(yt or vm).group(1))
        if tag == "a" and a.get("href"):
            h = a["href"]
            yt, vm = YOUTUBE.search(h), VIMEO.search(h)
            if yt or vm:
                self.add("embed", h, provider="YouTube" if yt else "Vimeo", vid=(yt or vm).group(1), via="video link")
            elif VIDEO_EXT.search(h):
                self.add("video", h, via="video link")
        if tag == "a" or tag == "button":
            cls = a.get("class", "") + " " + a.get("role", "")
            self._anchor = dict(href=None if tag == "button" and "href" not in a else a.get("href"),
                                tag=tag, is_button=(tag == "button" or bool(BUTTON_CLASS.search(cls))),
                                text=[a.get("aria-label", "")] if a.get("aria-label") else [],
                                onclick=a.get("onclick", ""), section=self.section,
                                region="/".join(self.region))
            if "href" in a or tag == "a":
                self._anchor["raw_href"] = a.get("href", "")
        if tag == "input" and a.get("type", "").lower() in ("submit", "button"):
            self.links.append(dict(href=None, tag="input", is_button=True, text=a.get("value", ""),
                                   section=self.section, region="/".join(self.region)))

    def handle_endtag(self, tag):
        if tag in ("header", "footer", "nav") and tag in self.region:
            while self.region and self.region.pop() != tag:
                pass
        if tag == self._heading:
            t = " ".join("".join(self._htext).split())
            if t:
                self.section = t
            self._heading = None
        if tag == "style":
            self._in_style = False
        if tag == "video":
            self._video = None
        if tag in ("a", "button") and self._anchor is not None and self._anchor["tag"] == tag:
            an = self._anchor
            an["text"] = " ".join(" ".join(an["text"]).split())
            if an.get("raw_href"):
                an["abs"] = self.abs(an["raw_href"])
            self.links.append(an)
            self._anchor = None

    def handle_data(self, data):
        if self._heading:
            self._htext.append(data)
        if self._anchor is not None:
            self._anchor["text"].append(data)
        if self._in_style:
            self.styles.append(data)


# ---------------------------------------------------------------- crawl

def css_backgrounds(text, base_url, via, section_prefix=""):
    out = []
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", text):
        for m in CSS_URL.finditer(rule.group(2)):
            u = urllib.parse.urljoin(base_url, html.unescape(m.group(2).strip()))
            if MEDIA_EXT.search(u) and not u.startswith("data:"):
                sel = " ".join(rule.group(1).split())
                sel = sel.rsplit(";", 1)[-1].strip()[:120]
                out.append(dict(kind="css", src=u, section=section_prefix + sel, region="", via=via))
    return out


def same_host(u, host):
    return urllib.parse.urlsplit(u).netloc.lower() == host


def clean(u):
    p = urllib.parse.urlsplit(u)
    # Query strings (?playlist=, ?sfw_pub_collection=) are filtered views of
    # the same page and would only repeat its rows. WordPress paging is /page/2/.
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path or "/", "", ""))


def sitemap_urls(f, url, seen=None):
    seen = seen or set()
    if url in seen:
        return []
    seen.add(url)
    status, _, data, _ = f.get(url)
    if status != 200 or not data:
        print("  sitemap %s -> %s" % (url, status), file=sys.stderr)
        return []
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError:
        return []
    locs = [e.text.strip() for e in root.iter() if e.tag.endswith("loc") and e.text]
    if root.tag.endswith("sitemapindex"):
        out = []
        for loc in locs:
            out += sitemap_urls(f, loc, seen)
        return out
    return locs


def rest_links(f, base):
    """Every public page, post, event and custom post, from the REST API.
    WordPress turns wp-sitemap.xml off when the site is set to noindex."""
    out = []
    status, _, data, _ = f.get(base + "/wp-json/wp/v2/types")
    if status != 200:
        return out
    types = json.loads(data)
    first = ["page", "post", "sfw_calendar_event"]
    names = first + sorted(t for t in types if t not in first)
    for t in names:
        info = types.get(t) or {}
        rb = info.get("rest_base")
        if not rb or t in ("attachment", "nav_menu_item", "wp_block", "wp_template", "wp_template_part",
                           "wp_global_styles", "wp_navigation", "wp_font_family", "wp_font_face"):
            continue
        for n in range(1, 100):
            st, hd, d, _ = f.get("%s/wp-json/wp/v2/%s?per_page=100&page=%d&_fields=link&orderby=menu_order&order=asc" % (base, rb, n)
                                 if t == "page" else "%s/wp-json/wp/v2/%s?per_page=100&page=%d&_fields=link" % (base, rb, n))
            if st != 200 or not d:
                break
            try:
                batch = json.loads(d)
            except ValueError:
                break
            if not isinstance(batch, list) or not batch:
                break
            out += [clean(b["link"]) for b in batch if b.get("link")]
            if n >= int(hd.get("x-wp-totalpages", "1") or 1):
                break
    return out


def slug(u, base):
    p = urllib.parse.urlsplit(u).path.strip("/")
    return p or "home"


def classify(src, kind):
    name = stem(src)
    if kind in ("video", "embed") or VIDEO_EXT.search(src):
        return "Video"
    if re.search(r"\.gif(?:$|\?)", src, re.I):
        return "GIF"
    if re.search(r"\.svg(?:$|\?)", src, re.I) or GRAPHIC_HINT.search(name):
        return "Graphic"
    return "Image"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://new.soilfoodweb.com")
    ap.add_argument("--out", default=os.path.join(ROOT, "asset-inventory.csv"))
    ap.add_argument("--links-out", default=os.path.join(ROOT, "asset-inventory-links.csv"))
    ap.add_argument("--cache", default=os.path.join(ROOT, "_dev", "asset-inventory-cache"))
    ap.add_argument("--max-pages", type=int, default=2000)
    args = ap.parse_args()

    base = args.base.rstrip("/")
    host = urllib.parse.urlsplit(base).netloc.lower()
    f = Fetcher(args.cache)

    # 1. Menu order: header links, then footer links, then the sitemap.
    status, _, data, _ = f.get(base + "/")
    if status != 200:
        sys.exit("Cannot read %s/ (status %s %s). Is the host reachable from here?"
                 % (base, status, f.get(base + "/")[1].get("error", "")))
    home = Page(base + "/")
    home.feed(data.decode("utf-8", "replace"))
    order = [base + "/"]
    for region in ("header", "footer"):
        for ln in home.links:
            href = ln.get("raw_href")
            if href and region in ln["region"].split("/"):
                u = clean(home.abs(href))
                if same_host(u, host) and not SKIP_PATH.search(u) and not MEDIA_EXT.search(u):
                    order.append(u)
    order += [clean(u) for u in sitemap_urls(f, base + "/wp-sitemap.xml")]
    order += rest_links(f, base)
    order = [u for u in order if same_host(u, host)]
    queue = list(dict.fromkeys(order))
    seeds = set(queue)
    seen_pages = set(queue)

    # 2. Crawl. Same-host links found on pages (posts, events, paged archives)
    #    are appended after the sitemap, so menu order stays first.
    pages, css_files = [], collections.OrderedDict()
    i = 0
    while i < len(queue) and len(pages) < args.max_pages:
        u = queue[i]; i += 1
        status, headers, data, _ = f.get(u)
        ctype = headers.get("content-type", "")
        if 300 <= status < 400:
            continue  # redirects off the site, e.g. a publication pointing at its paper
        if status != 200 or "html" not in ctype or not data:
            if u in seeds:  # a dead menu or sitemap entry; dead discovered links go to the links file
                pages.append((u, status, None))
            continue
        pg = Page(u)
        pg.feed(data.decode("utf-8", "replace"))
        pg.items += css_backgrounds("".join(pg.styles), u, "page <style> block", "CSS ")
        pages.append((u, status, pg))
        print("  %3d %s (%d assets)" % (len(pages), u, len(pg.items)), file=sys.stderr)
        for s in pg.stylesheets:
            if same_host(s, host):
                css_files.setdefault(s, None)
        for ln in pg.links:
            href = ln.get("raw_href")
            if not href:
                continue
            v = clean(pg.abs(href))
            if (same_host(v, host) and v not in seen_pages and not SKIP_PATH.search(v)
                    and not MEDIA_EXT.search(v) and not re.search(r"\.(?:pdf|zip|docx?|xlsx?|pptx?|ics)$", v, re.I)):
                seen_pages.add(v)
                queue.append(v)

    # 3. Theme stylesheets: every background image, under the selector using it.
    css_items = []
    for s in css_files:
        status, _, data, _ = f.get(s)
        if status != 200 or not data:
            continue
        css_items += css_backgrounds(data.decode("utf-8", "replace"), s, "stylesheet " + stem(s) + ".css")

    # 4. WordPress media library, when the REST API is open: true upload dates
    #    and original sizes even for files only seen as size variants.
    library = {}
    for n in range(1, 200):
        status, _, data, _ = f.get(base + "/wp-json/wp/v2/media?per_page=100&page=%d" % n)
        if status != 200 or not data:
            break
        try:
            batch = json.loads(data)
        except ValueError:
            break
        if not batch:
            break
        for m in batch:
            det = m.get("media_details") or {}
            library[key(m.get("source_url", ""))] = dict(date=m.get("date", "")[:10], url=m.get("source_url"),
                                                         size=det.get("filesize"), w=det.get("width"), h=det.get("height"))

    # 5. Rows.
    repo, drive, vids, rbuttons = repo_index(), drive_index(), repo_videos(), repo_buttons()
    rows, placements = [], collections.defaultdict(set)
    media_meta = {}

    def meta(url):
        if url in media_meta:
            return media_meta[url]
        status, headers, data, path = f.get(url)
        size = (headers.get("content-length") or (len(data) if data else "")) if status == 200 else ""
        px = svg_size(data) if re.search(r"\.svg(?:$|\?)", url, re.I) else probe(path)
        media_meta[url] = dict(status=status, size=size, px=px, error=headers.get("error", ""))
        return media_meta[url]

    page_rows = collections.OrderedDict()
    for u, status, pg in pages:
        ps = slug(u, base)
        page_rows[ps] = []
        if pg is None:
            page_rows[ps].append({**dict.fromkeys(COLUMNS, ""), "Page slug": ps,
                                  "Notes": "PAGE NOT READ: status %s" % status, "_count": False})
            continue
        for it in pg.items:
            if it["kind"] == "css" and not MEDIA_EXT.search(it["src"]):
                continue
            url = it.get("srcset_max") or it["src"]
            row = {c: "" for c in COLUMNS}
            row.update({"Page slug": ps, "Section": it["section"], "_item": it, "_url": url})
            if it.get("region"):
                row["Section"] = "%s (%s)" % (it["section"], it["region"])
            page_rows[ps].append(row)
            placements[key(url) if it["kind"] != "embed" else it["vid"]].add(ps)
        for ln in pg.links:
            if not ln["is_button"]:
                continue
            row = {c: "" for c in COLUMNS}
            row.update({"Page slug": ps, "Section": ln["section"] + (" (%s)" % ln["region"] if ln["region"] else ""),
                        "Type": "Button", "Current file name": ln["text"] or "(no label)",
                        "Links to": ln.get("raw_href", "") if ln["tag"] == "a" or "raw_href" in ln else "(button, no href)",
                        "_link": ln})
            page_rows[ps].append(row)
    if css_items:
        page_rows["(theme stylesheet)"] = []
        for it in css_items:
            row = {c: "" for c in COLUMNS}
            row.update({"Page slug": "(theme stylesheet)", "Section": it["section"], "_item": it, "_url": it["src"]})
            page_rows["(theme stylesheet)"].append(row)

    for ps, rs in page_rows.items():
        for row in rs:
            notes = []
            it = row.get("_item")
            if it:
                url = row["_url"]
                if it["kind"] == "embed":
                    row.update({"Type": "Video", "Current file name": "%s %s" % (it["provider"], it["vid"]),
                                "WordPress media URL": it["src"]})
                    row["Repo path"] = vids.get(it["vid"], "No source found")
                    others = sorted(placements[it["vid"]] - {ps})
                else:
                    m = meta(url)
                    row.update({"Type": classify(url, it["kind"]), "Current file name": urllib.parse.unquote(url.split("?")[0].rsplit("/", 1)[-1]),
                                "WordPress media URL": url, "Pixel size": m["px"], "File size": human(m["size"])})
                    if it.get("srcset_max") and it["srcset_max"] != it["src"]:
                        notes.append("largest srcset entry; src is " + stem(it["src"]))
                    if it.get("via"):
                        notes.append("CSS background, " + it["via"])
                    if m["status"] == 0:
                        notes.append("NOT CHECKED: could not connect (%s)" % m["error"])
                    elif m["status"] != 200:
                        notes.append("BROKEN: image returns %s" % m["status"])
                    k = key(url)
                    lib = library.get(k)
                    d = UPLOAD_DATE.search(url)
                    date = (lib or {}).get("date") or (d and "%s-%s" % d.groups()) or ""
                    if date and date[:4] < "2026":
                        notes.append("uploaded %s (before 2026)" % date)
                    if original_stem(url) != stem(url):
                        notes.append("WordPress size variant of %s" % original_stem(url))
                    if lib and lib.get("w"):
                        notes.append("original %sx%s%s" % (lib["w"], lib["h"], (", " + human(lib["size"])) if lib.get("size") else ""))
                    if re.match(r"^https?://\d+/?$", url):
                        notes.append("image field holds an attachment ID instead of a URL")
                    if not same_host(url, host):
                        notes.append("hosted off-site on " + urllib.parse.urlsplit(url).netloc)
                    if urllib.parse.urlsplit(url).netloc.lower() in OLD_HOSTS:
                        notes.append("OLD SITE: file served from soilfoodweb.com")
                    hits = repo.get(key(url)) or repo.get(key(url, repo=True))
                    if hits and len(key(url)) < 4:
                        hits = None  # 2.jpg, 6.jpg: too generic to match by name
                        notes.append("name too generic to match by name")
                    if not hits:
                        dup = re.sub(r"-\d$", "", original_stem(url))
                        if dup != original_stem(url):
                            hits = repo.get(re.sub(r"[^a-z0-9]", "", dup.lower()))
                            if hits:
                                notes.append("matched after dropping WordPress re-upload suffix")
                    row["Repo path"] = hits[0] if hits else ""
                    if hits and os.path.splitext(hits[0])[1].lower() != os.path.splitext(url.split("?")[0])[1].lower():
                        notes.append("repo match is a different format, check by eye")
                    if hits and len(hits) > 1:
                        notes.append("other repo copies: " + "; ".join(hits[1:4]) + (" ..." if len(hits) > 4 else ""))
                    dl = drive.get(key(url)) or next((drive[key(h)] for h in (hits or []) if key(h) in drive), None) \
                        or next((drive[key(h, repo=True)] for h in (hits or []) if key(h, repo=True) in drive), None)
                    row["SFW Drive link"] = dl or ""
                    if not hits and not dl:
                        row["Repo path"] = "No source found"
                    others = sorted(placements[k] - {ps})
                    same_page = sum(1 for r in rs if r.get("_item") and r["_item"]["kind"] != "embed" and key(r["_url"]) == k)
                    if same_page > 1:
                        notes.append("DUPLICATE: %d slots on this page" % same_page)
                if others:
                    notes.append("DUPLICATE: also on %d other page(s)" % len(others))
                    row["Also used on"] = "; ".join(others[:15]) + (" ... (+%d)" % (len(others) - 15) if len(others) > 15 else "")
            ln = row.get("_link")
            if ln:
                href = (ln.get("raw_href") or "").strip()
                if ln["tag"] == "input" or ("raw_href" not in ln):
                    notes.append("form or script button" + (" (onclick)" if ln.get("onclick") else ""))
                elif href == "" or href == "#":
                    notes.append("BROKEN: href is %s" % ("empty" if not href else '"#"'))
                elif LOCAL.match(href):
                    notes.append("BROKEN: points to localhost")
                else:
                    absu = ln.get("abs") or href
                    net = urllib.parse.urlsplit(absu).netloc.lower()
                    if net in OLD_HOSTS:
                        notes.append("OLD SITE: points to soilfoodweb.com")
                    if any(p in urllib.parse.urlsplit(absu).path for p in OLD_PATHS):
                        notes.append("OLD SITE: WordPress shop or foundation-courses-2")
                    if href.lower().startswith("javascript:"):
                        notes.append("BROKEN: javascript href")
                    if net == host and "/cdn-cgi/" not in absu:
                        st = f.get(clean(absu), body=False)[0]
                        if st >= 400:
                            notes.append("BROKEN: target returns %s" % st)
                        elif 300 <= st < 400:
                            notes.append("redirects off the site")
                        elif st == 0:
                            notes.append("NOT CHECKED: could not connect")
                if not ln["text"]:
                    notes.append("no visible label")
                hits = rbuttons.get(label_key(ln["text"])) if ln["text"] else None
                if hits:
                    pages_ = sorted({h[0] for h in hits})
                    row["Repo path"] = ("shared header/footer on %d prototype pages" % len(pages_) if len(pages_) > 8
                                        else "; ".join(pages_))
                    live = href_key(ln.get("abs") or ln.get("raw_href") or "")
                    proto = sorted({h[1] for h in hits})
                    if any(href_key(h) == live for h in proto):
                        notes.append("same label and link in the repo prototype")
                    else:
                        notes.append("same label in the repo prototype, link there: "
                                     + "; ".join(sorted({href_key(h) for h in proto})[:3]))
                else:
                    row["Repo path"] = "No source found"
            if notes:
                row["Notes"] = ("; ".join(notes) + ("; " + row["Notes"] if row["Notes"] else "")).strip("; ")

    # 6. Non-button links that are broken or go to the old site.
    link_rows = []
    for u, status, pg in pages:
        if pg is None:
            continue
        for ln in pg.links:
            if ln["is_button"] or "raw_href" not in ln:
                continue
            href = (ln.get("raw_href") or "").strip()
            absu = pg.abs(href) if href else ""
            net = urllib.parse.urlsplit(absu).netloc.lower()
            why = []
            if href in ("", "#"):
                why.append('href is %s' % ("empty" if not href else '"#"'))
            elif LOCAL.match(href):
                why.append("points to localhost")
            else:
                if net in OLD_HOSTS:
                    why.append("points to the old site")
                if any(p in urllib.parse.urlsplit(absu).path for p in OLD_PATHS):
                    why.append("WordPress shop or foundation-courses-2")
                if net == host and not href.startswith("#") and "/cdn-cgi/" not in absu:
                    st = f.get(clean(absu), body=False)[0]
                    if st >= 400:
                        why.append("target returns %s" % st)
            if why:
                link_rows.append([slug(u, base), ln["section"], ln["text"] or "(no label)", href, "; ".join(why)])

    with open(args.out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for rs in page_rows.values():
            for r in rs:
                w.writerow([r.get(c, "") for c in COLUMNS])
    with open(args.links_out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Page slug", "Section", "Link text", "Href", "Problem"])
        w.writerows(link_rows)

    # 7. Report.
    print("\nCount per page (images, graphics, GIFs, videos, buttons):")
    for ps, rs in page_rows.items():
        c = collections.Counter(r["Type"] for r in rs if r["Type"])
        print("  %-50s %4d  %s" % (ps, sum(c.values()), ", ".join("%s %d" % kv for kv in sorted(c.items()))))
    nosrc = sorted({r["Current file name"] for rs in page_rows.values() for r in rs if r.get("Repo path") == "No source found"})
    print("\nNo source found (%d files):" % len(nosrc))
    for n in nosrc:
        print("  " + n)
    broken = [(r["Page slug"], r["Current file name"], r["Links to"], r["Notes"]) for rs in page_rows.values() for r in rs
              if "BROKEN" in r.get("Notes", "") or "OLD SITE" in r.get("Notes", "")]
    print("\nBroken or old-site assets and buttons (%d):" % len(broken))
    for b in broken:
        print("  %s | %s | %s | %s" % b)
    print("\nBroken or old-site links (%d), see %s" % (len(link_rows), os.path.relpath(args.links_out, ROOT)))
    for l in link_rows[:200]:
        print("  %s | %s | %s | %s" % (l[0], l[2], l[3], l[4]))


if __name__ == "__main__":
    main()
