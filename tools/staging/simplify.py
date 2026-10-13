#!/usr/bin/env python3
"""Reduce a saved staging page (WordPress + Salient) to plain semantic HTML.

    python3 tools/staging/simplify.py page.html > page.simple.html

Keeps headings, paragraphs, lists, links, images, blockquotes, tables and
iframes, drops every theme wrapper. Used once, to read staging copy and lay it
into this repo's own markup; the site never loads WordPress markup.
"""
import sys, re
from bs4 import BeautifulSoup, NavigableString, Tag

KEEP = {"h1","h2","h3","h4","h5","h6","p","ul","ol","li","a","img","blockquote",
        "table","thead","tbody","tr","th","td","iframe","strong","em","b","i","br",
        "figure","figcaption","time","details","summary","video","source","form",
        "label","input","select","option","textarea","button","section"}
DROP = "script,style,noscript,#footer-outer,#slide-out-widget-area,#slide-out-widget-area-bg,#header-outer,#header-space,.sfw-utility-bar,#search-outer,svg,.nectar-social,#ajax-loading-screen"

def clean(node):
    for c in list(node.children):
        if isinstance(c, NavigableString):
            continue
        if not isinstance(c, Tag):
            c.extract(); continue
        clean(c)
        if c.name not in KEEP:
            c.unwrap(); continue
        keep = {}
        for k in ("href","src","alt","id","datetime","title","data-src","type","name","placeholder","value"):
            if c.get(k):
                keep[k] = c[k]
        if c.name == "section" and not keep.get("id"):
            c.unwrap(); continue
        if c.get("class"):
            cls = [x for x in c["class"] if x.startswith("sfw")]
            if cls: keep["class"] = " ".join(cls)
        c.attrs = keep

def simplify(path):
    s = BeautifulSoup(open(path, encoding="utf-8", errors="ignore"), "lxml")
    for x in s.select(DROP): x.decompose()
    # Section ids live on the WPBakery row wrappers; carry them as anchors.
    for row in s.select("[id]"):
        if row.name not in ("section",) and not row["id"].startswith(("fws_","ajax","post-","block-","sidebar")) and row.name not in KEEP:
            a = s.new_tag("section"); a["id"] = row["id"]; row.wrap(a)
    m = s.select_one(".container-wrap") or s.select_one("main") or s.select_one("#ajax-content-wrap") or s.body
    clean(m)
    h = m.decode_contents()
    h = re.sub(r"[ \t]*\n\s*\n+", "\n", h)
    return h

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(simplify(p))
