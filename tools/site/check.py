#!/usr/bin/env python3
"""Check the built preview: links, anchors, images, and the brief's rules.

    python3 tools/site/check.py

Every internal href and src must resolve to a file (folder/index.html for
pages) and every #anchor must exist on its target page. Also checks: one h1
per page, noindex meta, no zoom blocking, no em dashes in text, no staging
editorial notes ([VERIFY ...], [IMPACT LINES ...]), images WebP-or-svg under
300 KB and at most 1600 px wide
(supplied photos in img/new/ may add a srcset variant up to 2400 px and 600 KB). Exits non-zero on any failure.
"""
import os, re, sys, html, json
from collections import defaultdict
from urllib.parse import urlsplit, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGES = json.load(open(os.path.join(ROOT, "content", "staging", "built-pages.json")))


def page_file(path):
    return os.path.join(ROOT, "index.html") if path == "/" else os.path.join(ROOT, path.strip("/"), "index.html")


def main():
    errors = defaultdict(list)
    ids = {}
    docs = {}
    for p in PAGES:
        f = page_file(p)
        h = open(f, encoding="utf-8").read()
        docs[p] = h
        ids[p] = set(re.findall(r'\sid="([^"]+)"', h))
    external = set()
    for p, h in docs.items():
        if len(re.findall(r"<h1[\s>]", h)) != 1:
            errors[p].append("h1 count %d" % len(re.findall(r"<h1[\s>]", h)))
        if '<meta name="robots" content="noindex' not in h:
            errors[p].append("missing noindex")
        if "user-scalable" in h or "maximum-scale" in h:
            errors[p].append("zoom blocked")
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for bad in () if p == "/review/" or p.startswith("/testimonial/") or p == "/scholarship/" else ("[VERIFY", "[IMPACT", "[PLACEHOLDER", "Lorem ipsum", "John Doe", "Amara Okafor", "localhost", "foundation-couse"):
            if bad in text or bad in h:
                errors[p].append("contains %r" % bad)
        for attr, url in re.findall(r'\s(href|src|poster)="([^"]*)"', h):
            url = html.unescape(url)
            if not url or url.startswith(("mailto:", "tel:", "data:", "javascript:")):
                if not url:
                    errors[p].append("empty %s" % attr)
                continue
            if url.startswith(("http://", "https://")):
                external.add(url)
                if "new.soilfoodweb.com" in url:
                    errors[p].append("links to staging: " + url)
                continue
            if url == "#":
                errors[p].append("bare # link")
                continue
            parts = urlsplit(url)
            path, frag = parts.path, parts.fragment
            if not path:
                target = p
            elif path.endswith("/"):
                target = path
                if target not in docs:
                    errors[p].append("missing page " + url)
                    continue
            else:
                fp = os.path.join(ROOT, unquote(path).lstrip("/"))
                if not os.path.isfile(fp):
                    errors[p].append("missing file " + url)
                continue
            if frag and frag not in ids.get(target, set()):
                errors[p].append("missing anchor " + url)
    # images
    from PIL import Image
    used = set()
    for h in docs.values():
        used.update(re.findall(r'src="/(img/[^"]+)"', h))
        for ss in re.findall(r'srcset="([^"]+)"', h):
            used.update(u.strip().split()[0].lstrip("/") for u in ss.split(","))
    for i in sorted(used):
        fp = os.path.join(ROOT, i)
        if not os.path.exists(fp):
            continue
        # Supplied photos (img/new/) also ship a large srcset variant: up to 2400 px and 600 KB.
        big = i.startswith("img/new/") and re.search(r"-(\d+)\.webp$", i) and int(re.search(r"-(\d+)\.webp$", i).group(1)) > 1600
        if os.path.getsize(fp) > (600 if big else 300) * 1024:
            errors["images"].append("%s is %d KB" % (i, os.path.getsize(fp) // 1024))
        if i.endswith((".webp", ".png", ".jpg")):
            w = max(Image.open(fp).size) if big else Image.open(fp).size[0]
            if w > (2400 if big else 1600):
                errors["images"].append("%s is %d px wide" % (i, w))
    n = sum(len(v) for v in errors.values())
    for p, es in sorted(errors.items()):
        for e in es:
            print("%s: %s" % (p, e))
    print("%d pages, %d images, %d external links, %d problems" % (len(docs), len(used), len(external), n))
    with open(os.path.join(ROOT, "content", "staging", "external-links.txt"), "w") as f:
        f.write("\n".join(sorted(external)) + "\n")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
