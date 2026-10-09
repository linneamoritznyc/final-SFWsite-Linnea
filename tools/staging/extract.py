#!/usr/bin/env python3
"""Turn a saved copy of new.soilfoodweb.com into data files in content/staging/.

    python3 tools/staging/extract.py <cache-dir>

<cache-dir> holds the REST API dumps (pages.json, posts.json, team_member.json,
...) and html/<slug>.html, one rendered page per URL, written by fetch.sh. The
output is a snapshot dated in content/staging/README.md; the site build reads
only the snapshot, never the network.
"""
import json, os, re, sys, html as H
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "content", "staging")
SRC = sys.argv[1] if len(sys.argv) > 1 else "."
STG = "https://new.soilfoodweb.com"


def page(name):
    p = os.path.join(SRC, "html", name + ".html")
    return BeautifulSoup(open(p, encoding="utf-8", errors="ignore"), "lxml") if os.path.exists(p) else None


def rest(t):
    return json.load(open(os.path.join(SRC, t + ".json")))


def txt(n):
    return re.sub(r"\s+", " ", n.get_text(" ", strip=True)).strip() if n else ""


def img_src(n):
    if not n:
        return ""
    for k in ("data-src", "src"):
        v = n.get(k, "")
        if v and not v.startswith("data:"):
            return v
    return ""


def inner(n):
    """Body HTML with theme attributes stripped: p, h2-h4, ul/ol/li, a, strong, em, blockquote, img."""
    if not n:
        return ""
    # Cloudflare email obfuscation: put the real address back.
    for sp in n.select("[data-cfemail]"):
        sp.replace_with(cf_email(sp["data-cfemail"]))
    for a in n.select('a[href*="/cdn-cgi/l/email-protection"]'):
        h = a["href"].split("#", 1)
        a["href"] = "mailto:" + (cf_email(h[1]) if len(h) == 2 and h[1] else a.get_text(strip=True))
    for x in n.select("script,style,svg"):
        x.decompose()
    for t in n.find_all(True):
        keep = {}
        if t.name == "a" and t.get("href"):
            keep["href"] = t["href"]
        if t.name == "img":
            s = img_src(t)
            if s:
                keep["src"] = s
            if t.get("alt"):
                keep["alt"] = t["alt"]
        t.attrs = keep
    for t in n.find_all(["div", "span", "section", "font"]):
        t.unwrap()
    h = n.decode_contents()
    h = re.sub(r"<p>\s*(&nbsp;| )?\s*</p>", "", h)
    return re.sub(r"\n\s*\n+", "\n", h).strip()


def cf_email(hexs):
    k = int(hexs[:2], 16)
    return "".join(chr(int(hexs[i:i + 2], 16) ^ k) for i in range(2, len(hexs), 2))


def save(name, data):
    with open(os.path.join(OUT, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(name, len(data))


# ---------------------------------------------------------------- publications
def publications():
    s = page("publications")
    out = []
    for g in s.select(".sfw-pub-group"):
        coll = txt(g.select_one(".sfw-pub-group__title"))
        for li in g.select("li.sfw-pub-entry"):
            cls = li.get("class", [])
            a = li.select_one(".sfw-pub-entry__title a")
            line = txt(li.select_one(".sfw-pub-entry__line"))
            authors, _, cite = line.partition(" · ")
            pid = next((c[5:] for c in cls if c.startswith("post-")), "")
            href = a["href"] if a else ""
            out.append({
                "id": int(pid) if pid else None,
                "collection": coll,
                "year": txt(li.select_one("time")),
                "title": txt(a),
                "href": href,
                "authors": authors.strip(),
                "citation": cite.strip(),
                "kind": txt(li.select_one(".sfw-pub-entry__kind")),
                "topics": sorted(c[18:].replace("-", " ") for c in cls if c.startswith("publication_topic-")),
            })
    slugs = {p["id"]: p["slug"] for p in rest("sfw_publication")}
    for p in out:
        p["slug"] = slugs.get(p["id"], "")
    save("publications", out)


# ---------------------------------------------------------------- team
def team():
    about = page("about-us")
    order = []
    for a in about.select('a[href*="/team-member/"]'):
        slug = a["href"].rstrip("/").split("/")[-1]
        if slug not in order:
            order.append(slug)
    out = []
    for r in rest("team_member"):
        s = page("team-member__" + r["slug"])
        m = s.select_one(".sfw-team-single") if s else None
        out.append({
            "slug": r["slug"],
            "name": H.unescape(r["title"]["rendered"]),
            "role": txt(m.select_one(".sfw-team-single__title")) if m else "",
            "photo": img_src(m.select_one("img.sfw-team-single__photo")) if m else "",
            "bio": inner(m.select_one(".sfw-team-single__bio")) if m else "",
            "order": order.index(r["slug"]) if r["slug"] in order else 999,
        })
    out.sort(key=lambda x: (x["order"], x["name"]))
    save("team", out)


# ---------------------------------------------------------------- directory
def directory():
    out = []
    for r in rest("directory_member"):
        s = page("directory-member__" + r["slug"])
        if not s:
            continue
        m = s.select_one(".sfw-directory-single")
        links = []
        for a in m.select(".sfw-directory-single__contact a"):
            label = txt(a.select_one(".sfw-directory-single__link-label"))
            val = txt(a.select_one(".sfw-directory-single__link-value"))
            href = a.get("href", "")
            em = a.select_one("[data-cfemail]")
            if em:
                val = cf_email(em["data-cfemail"])
                href = "mailto:" + val
            links.append({"label": label, "value": val, "href": href})
        meta = {txt(r_.select_one("dt")): txt(r_.select_one("dd")) for r_ in m.select(".sfw-directory-single__meta-row")}
        out.append({
            "slug": r["slug"],
            "name": H.unescape(r["title"]["rendered"]),
            "company": txt(m.select_one(".sfw-directory-single__company")),
            "roles": [txt(x) for x in m.select(".sfw-directory-pill")],
            "photo": img_src(m.select_one("img.sfw-directory-single__photo")),
            "bio": inner(m.select_one(".sfw-directory-single__bio")),
            "area": meta.get("Area", ""),
            "links": links,
            "social": [{"label": txt(a), "href": a.get("href", "")} for a in m.select(".sfw-directory-single__social a")],
            "staging_title": txt(s.title).replace("– Soil Food Web Foundation", "").strip(),
        })
    out.sort(key=lambda x: x["name"].lower())
    save("directory", out)


# ---------------------------------------------------------------- videos
def videos():
    out = []
    for r in rest("sfw_video"):
        s = page("video__" + r["slug"])
        m = s.select_one(".sfw-video-single") if s else None
        fr = m.select_one("iframe") if m else None
        src = (fr.get("data-src") or fr.get("src", "")) if fr else ""
        vid = re.search(r"vimeo\.com/video/(\d+)", src)
        hsh = re.search(r"[?&]h=([0-9a-f]+)", src)
        yt = re.search(r"youtube(?:-nocookie)?\.com/embed/([\w-]+)", src)
        thumb = ""
        for row in s.select(".sfw-video-playlist__row") if s else []:
            if row.get("href", "").split("?")[0].rstrip("/").endswith(r["slug"]):
                thumb = img_src(row.select_one("img"))
        out.append({
            "slug": r["slug"],
            "title": H.unescape(r["title"]["rendered"]),
            "playlist": txt(m.select_one(".sfw-video-single__kicker")) if m else "",
            "vimeo": vid.group(1) if vid else "",
            "vimeo_h": hsh.group(1) if hsh else "",
            "youtube": yt.group(1) if yt else "",
            "thumb": thumb,
            "body": inner(m.select_one(".sfw-video-single__content, .sfw-video-single__body")) if m else "",
        })
    # Thumbnails appear on the other videos' playlists; fill in from there.
    thumbs = {}
    for f in os.listdir(os.path.join(SRC, "html")):
        if f.startswith("video__"):
            for row in page(f[:-5]).select(".sfw-video-playlist__row"):
                thumbs[row.get("href", "").split("?")[0].rstrip("/").split("/")[-1]] = img_src(row.select_one("img"))
    for v in out:
        v["thumb"] = v["thumb"] or thumbs.get(v["slug"], "")
    save("videos", out)


# ---------------------------------------------------------------- events
def events():
    """All ten sfw_calendar_event posts. Dates come from the calendar's timeline
    bars (data attributes); the two 2027 PDC cohorts sit outside its twelve-month
    window, so their dates are read from the event text ("Runs April 19- July 3rd").
    Body text and the sign-up link come from each event page."""
    import datetime
    cal = page("calendar")
    bars = {}
    for a in cal.select("a.sfw-blog-calendar__bar"):
        slug = a.get("href", "").rstrip("/").split("/")[-1]
        when = next((txt(li.select_one("time")) for li in cal.select("li.sfw-blog-calendar__entry")
                     if li.select_one("a") and li.select_one("a")["href"] == a.get("href")), "")
        bars.setdefault(slug, {"start": a.get("data-start", ""), "end": a.get("data-end", ""),
                               "staging_type": a.get("data-type", ""), "when": when})
    out = []
    for r in rest("sfw_calendar_event"):
        slug = r["slug"]
        s = page("calendar-event__" + slug)
        m = (s.select_one(".post-content .content-inner") or s.select_one(".post-content")) if s else None
        body = inner(m) if m else ""
        text = txt(m) if m else ""
        b = bars.get(slug, {})
        e = {"slug": slug, "title": H.unescape(r["title"]["rendered"]), "start": b.get("start", ""), "end": b.get("end", ""),
             "staging_type": b.get("staging_type", ""), "when": b.get("when", ""), "body": body, "text_dates": ""}
        mm = re.search(r"Runs ([A-Z][a-z]+ \d{1,2})(?:st|nd|rd|th)?\s*-\s*([A-Z][a-z]+ \d{1,2})(?:st|nd|rd|th)?", text)
        if mm:
            e["text_dates"] = mm.group(0)
            if not e["start"]:
                year = re.search(r"(20\d\d)", e["title"]).group(1)
                d = lambda t: datetime.datetime.strptime(t + " " + year, "%B %d %Y").date().isoformat()
                e["start"], e["end"] = d(mm.group(1)), d(mm.group(2))
        links = [x["href"] for x in m.select("a[href]")] if m else []
        e["signup"] = next((l for l in links if "school.soilfoodweb.com" in l or "webinar.soilfoodweb.com" in l), "")
        out.append(e)
    out.sort(key=lambda e: e["start"])
    save("events", out)


# ---------------------------------------------------------------- courses
def courses():
    """Program cards on /programs-overview/, with their pathway tags."""
    s = page("programs-overview")
    out = []
    for li in s.select("li[data-sfw-program-item]"):
        a = li.select_one(".sfw-programs__name a")
        out.append({
            "title": txt(a),
            "href": a.get("href", "") if a else "",
            "kicker": txt(li.select_one(".sfw-programs__kicker")),
            "line": txt(li.select_one(".sfw-programs__line")),
            "cta": txt(li.select_one(".sfw-programs__cta a")),
            "image": img_src(li.select_one("img")),
            "pathways": li.get("data-pathways", "").split(),
        })
    save("courses", out)


# ---------------------------------------------------------------- posts
def restore_images(slug, m, featured):
    """Staging lost the src of images migrated from the old site (src="").
    The live soilfoodweb.com post still has them, in the same order, so fill
    each empty one from the old page by position. Returns what was restored."""
    empty = [i for i in m.select("img.img-with-animation") if not img_src(i)]
    oldp = os.path.join(SRC, "old", slug + ".html")
    if not empty or not os.path.exists(oldp):
        return []
    o = BeautifulSoup(open(oldp, encoding="utf-8", errors="ignore"), "lxml")
    feat = re.sub(r"(-scaled)?(-\d)?$", "", os.path.basename(featured).rsplit(".", 1)[0])
    olds = [img_src(i) for i in o.select("img.img-with-animation")]
    if len(olds) != len(empty):
        olds = [u for u in olds if not (u and feat and feat in u)]
    done = []
    if len(olds) != len(empty):
        return []
    for i, u in zip(empty, olds):
        if u:
            i["src"] = u
            done.append(u)
    return done


def posts():
    cats = {c["id"]: {"slug": c["slug"], "name": H.unescape(c["name"])} for c in rest("categories")}
    media = {m["id"]: m["source_url"] for m in rest("media")}
    out = []
    for r in rest("posts"):
        s = page(r["slug"])
        m = s.select_one(".post-content .content-inner") or s.select_one(".post-content")
        # Testimonial shortcodes render as quote blocks; keep them as blockquotes.
        for q in m.select(".nectar_single_testimonial"):
            bq = s.new_tag("blockquote")
            p = s.new_tag("p"); p.string = txt(q.select_one("p")); bq.append(p)
            nm = txt(q.select_one(".wrap, .title, span"))
            if nm:
                c = s.new_tag("cite"); c.string = nm.lstrip("—– ").strip(); bq.append(c)
            q.replace_with(bq)
        # Author boxes (team_member shortcode) become a byline block, src kept verbatim.
        authors = []
        for tm in m.select(".team-member"):
            im = tm.select_one("img")
            authors.append({"name": txt(tm.select_one("h4")) or (im.get("title", "") if im else ""),
                            "role": txt(tm.select_one(".position, p")),
                            "photo": im.get("src", "") if im else ""})
            tm.decompose()
        hw = s.select_one(".page-header-bg-image img")
        header = img_src(hw) if hw else ""
        if header.startswith("data:"):
            header = ""
        if hw and not header:
            header = media.get(r["featured_media"], "")
        by = s.select_one("#page-header-bg .meta-author a, .page-header-meta .meta-author a, .meta-author a")
        restored = restore_images(r["slug"], m, media.get(r["featured_media"], ""))
        body = inner(m)
        out.append({
            "slug": r["slug"],
            "title": H.unescape(r["title"]["rendered"]),
            "date": r["date"][:10],
            "categories": [cats[c] for c in r["categories"] if c in cats],
            "featured": media.get(r["featured_media"], ""),
            "header": header,
            "wp_author": txt(by) if by else "",
            "excerpt": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", H.unescape(r["excerpt"]["rendered"]))).strip(),
            "authors": authors,
            "body": body,
            "restored_images": restored,
        })
    out.sort(key=lambda x: x["date"], reverse=True)
    save("posts", out)
    save("categories", [{"id": k, **v} for k, v in cats.items()])


# ---------------------------------------------------------------- workshops, testimonials
def mirror_main(s, sel):
    """The staging <main> of a plugin page, kept as HTML (plugin classes kept, scripts out)."""
    m = s.select_one(sel)
    if not m:
        return ""
    for x in m.select("script, style, noscript"):
        x.decompose()
    for i in m.select("img"):
        src = img_src(i)
        for k in list(i.attrs):
            if k not in ("alt", "class", "width", "height"):
                del i[k]
        i["src"] = src
    for f in m.select("iframe"):
        f["src"] = f.get("data-src") or f.get("src", "")
        for k in list(f.attrs):
            if k not in ("src", "title", "allow", "allowfullscreen"):
                del f[k]
    return str(m)


def workshops():
    out = []
    for r in rest("sfw_workshop"):
        s = page("workshop__" + r["slug"])
        if not s:
            continue
        out.append({"slug": r["slug"], "title": H.unescape(r["title"]["rendered"]), "date": r["date"],
                    "html": mirror_main(s, "main.sfw-workshop-single")})
    save("workshops", out)


def testimonials():
    out = []
    for r in rest("sfw_testimonial"):
        s = page("testimonial__" + r["slug"])
        if not s:
            continue
        m = s.select_one("main") or s.select_one(".container-wrap")
        out.append({"slug": r["slug"], "title": H.unescape(r["title"]["rendered"]), "menu_order": r.get("menu_order", 0),
                    "html": mirror_main(s, "main") if s.select_one("main") else mirror_main(s, ".container-wrap .container.main-content")})
    save("testimonials", out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (publications, team, directory, videos, events, courses, posts, workshops, testimonials):
        f()
