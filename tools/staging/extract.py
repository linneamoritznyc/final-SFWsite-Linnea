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
    """The calendar's timeline bars carry each event's data in attributes."""
    s = page("calendar")
    out, seen = [], set()
    for a in s.select("a.sfw-blog-calendar__bar"):
        href = a.get("href", "")
        if href in seen:
            continue
        seen.add(href)
        out.append({
            "slug": href.rstrip("/").split("/")[-1],
            "title": a.get("data-title", ""),
            "start": a.get("data-start", ""),
            "end": a.get("data-end", ""),
            "staging_type": a.get("data-type", ""),
            "excerpt": a.get("data-excerpt", ""),
            "external": a.get("data-external", "0"),
            "href": href,
            "when": next((txt(li.select_one("time")) for li in s.select("li.sfw-blog-calendar__entry")
                          if li.select_one("a") and li.select_one("a")["href"] == href), ""),
        })
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
        restored = restore_images(r["slug"], m, media.get(r["featured_media"], ""))
        body = inner(m)
        out.append({
            "slug": r["slug"],
            "title": H.unescape(r["title"]["rendered"]),
            "date": r["date"][:10],
            "categories": [cats[c] for c in r["categories"] if c in cats],
            "featured": media.get(r["featured_media"], ""),
            "excerpt": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", H.unescape(r["excerpt"]["rendered"]))).strip(),
            "authors": authors,
            "body": body,
            "restored_images": restored,
        })
    out.sort(key=lambda x: x["date"], reverse=True)
    save("posts", out)
    save("categories", [{"id": k, **v} for k, v in cats.items()])


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (publications, team, directory, videos, events, courses, posts):
        f()
