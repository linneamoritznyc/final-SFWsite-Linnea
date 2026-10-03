#!/usr/bin/env python3
"""Every internal link points at a file that exists and an anchor that exists.

    python3 tools/linkcheck.py

Exits non-zero on the first failure, so it can gate a deploy. External links
are listed, not fetched: this build environment has no outbound access to
soilfoodweb.com or doi.org, and a checker that silently passes what it cannot
reach is worse than one that says so.
"""
import re, os, sys, glob, html, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = ("lovable",)

A = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.S | re.I)
HREF = re.compile(r'href="([^"]*)"')
TAGS = re.compile(r'<[^>]+>')
IDS = re.compile(r'\sid="([^"]+)"')


def pages():
    out = sorted(glob.glob(os.path.join(ROOT, "*.html")))
    out += sorted(glob.glob(os.path.join(ROOT, "news", "*.html")))
    out += sorted(glob.glob(os.path.join(ROOT, "projects", "*.html")))
    return [p for p in out if not any(s in p for s in SKIP_DIRS)]


def main():
    ids, links = {}, collections.OrderedDict()
    for p in pages():
        rel = os.path.relpath(p, ROOT)
        s = open(p, encoding="utf-8").read()
        ids[rel] = set(IDS.findall(s))
        rows = []
        for attrs, inner in A.findall(s):
            m = HREF.search(attrs)
            if not m:
                continue
            label = re.sub(r"\s+", " ", html.unescape(TAGS.sub(" ", inner))).strip()
            rows.append((m.group(1), label))
        links[rel] = rows

    bad, external = [], collections.defaultdict(set)
    for rel, rows in links.items():
        for href, label in rows:
            if href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            if href.startswith("http"):
                external[href].add(rel)
                continue
            if href.startswith("#"):
                if len(href) > 1 and href[1:] not in ids[rel]:
                    bad.append((rel, href, label, "no such anchor on this page"))
                continue
            path, _, frag = href.partition("#")
            if not path:
                continue
            if path == "/":
                target = "index.html"
            else:
                target = os.path.normpath(os.path.join(os.path.dirname(rel), path))
                if target.endswith("/"):
                    target += "index.html"
            resolved = None
            for candidate in (target, target + ".html", os.path.join(target, "index.html")):
                if os.path.isfile(os.path.join(ROOT, candidate)):
                    resolved = candidate
                    break
            if resolved is None:
                bad.append((rel, href, label, "no such file: " + target))
            elif frag and frag not in ids.get(resolved, set()):
                bad.append((rel, href, label, "no such anchor: #%s on %s" % (frag, target)))

    print("%d pages, %d links, %d external URLs"
          % (len(links), sum(len(v) for v in links.values()), len(external)))
    if bad:
        print("\n%d broken internal links:" % len(bad))
        for rel, href, label, why in bad:
            print("  %s: %r (%s) -> %s" % (rel, href, label[:50], why))
        return 1
    print("no broken internal links")
    print("\n%d external URLs, not fetched (no outbound access here, see docs/link-map.md):" % len(external))
    for u in sorted(external):
        print("  %s" % u)
    return 0


if __name__ == "__main__":
    sys.exit(main())
