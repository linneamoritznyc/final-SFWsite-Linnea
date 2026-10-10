"""Linnea's workshop page copy (content/workshop-copy.md, 10 October 2026) as blog-style
page HTML for every /workshop/<slug>/ page.

The copy is used word for word, with two exceptions: "(photo)" source links are left
out because the photo itself sits next to the paragraph, and every <mark>[...]</mark>
note becomes a visible to-do under the paragraph it belongs to. Photos come from
img/new-2026-10/ through build.photo()."""
import os, re, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "content", "workshop-copy.md")

LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
MARK = re.compile(r"\s*<mark>\[(.*?)\]</mark>", re.S)
PHOTO_CITE = re.compile(r"\s*\(\[photo\]\([^)]*\)\)")
URL = re.compile(r"(https?://\S+)$")


def load():
    text = re.sub(r"<!--.*?-->", "", open(SRC, encoding="utf-8").read(), flags=re.S)
    out = []
    for block in re.split(r"^# ", text, flags=re.M)[1:]:
        lines = block.strip("\n").split("\n")
        w = {"slug": lines[0].strip(), "details": [], "body": [], "sources": []}
        i = 1
        while i < len(lines) and lines[i].strip():
            k, _, v = lines[i].partition(":")
            w[k.strip()] = v.strip()
            i += 1
        section, para = None, []

        def flush():
            if para:
                w["body"].append(("p", " ".join(para)))
                para.clear()
        for ln in lines[i:]:
            s = ln.strip()
            if not s:
                flush()
            elif s.startswith("## "):
                flush()
                section = s[3:]
                if section != "Sources":
                    w["body"].append(("h", section))
            elif s.startswith("!photo "):
                flush()
                w["body"].append(("photo", [x.strip() for x in s[7:].split("|")]))
            elif s.startswith("- ") and section == "Sources":
                w["sources"].append(s[2:])
            elif s.startswith("- ") and not w["body"]:
                k, _, v = s[2:].partition(":")
                w["details"].append((k.strip(), v.strip()))
            else:
                para.append(s)
        flush()
        out.append(w)
    return out


def inline(t):
    """Markdown links to <a>, everything else escaped."""
    t = PHOTO_CITE.sub("", t)
    parts, last = [], 0
    for m in LINK.finditer(t):
        parts.append(H.escape(t[last:m.start()], quote=False))
        parts.append('<a href="%s" rel="noopener">%s</a>' % (H.escape(m.group(2)), H.escape(m.group(1), quote=False)))
        last = m.end()
    parts.append(H.escape(t[last:], quote=False))
    return "".join(parts)


def split_marks(t):
    return MARK.sub("", t).strip(), [m.strip() for m in MARK.findall(t)]


def todo(t, tag="p"):
    return '<%s class="todo">%s</%s>' % (tag, inline(t), tag)


def details(w):
    rows = []
    for k, v in w["details"]:
        txt, marks = split_marks(v)
        rows.append("<dt>%s</dt><dd>%s%s</dd>" % (H.escape(k), inline(txt), "".join(" " + todo(m, "span") for m in marks)))
    return '<dl class="kv">%s</dl>' % "".join(rows)


def figure(photo, args, alts):
    f, cap = args[0], args[1] if len(args) > 1 else ""
    note = args[2] if len(args) > 2 else ""
    alt = alts.get(f, "")
    html = photo(f, alt, "", False, cap, "(min-width: 64em) 22rem, 100vw")
    if note:
        html += "".join(todo(m) for m in split_marks(note)[1])
    return html


def article(w, photo, alts, cover=False):
    """The write-up: details list, paragraphs with photos between them, sources."""
    h = []
    if w.get("new"):
        h += [todo(m) for m in split_marks(w["new"])[1]]
    if cover and w.get("cover"):
        f, alt, cap = (w["cover"].split("|") + ["", ""])[:3]
        note = w["cover"].split("|")[3] if w["cover"].count("|") >= 3 else ""
        h.append(photo(f.strip(), alt.strip(), "", True, cap.strip(), "(min-width: 64em) 44rem, 100vw"))
        h += [todo(m) for m in split_marks(note)[1]]
    h.append(details(w))
    body, i = w["body"], 0
    while i < len(body):
        kind, val = body[i]
        if kind == "h":
            h.append("<h3>%s</h3>" % H.escape(val))
        elif kind == "photo":
            run = [val]
            while i + 1 < len(body) and body[i + 1][0] == "photo":
                i += 1
                run.append(body[i][1])
            # Two or more photos in a row sit side by side, like a blog post's photo pair.
            h.append(figure(photo, run[0], alts) if len(run) == 1 else
                     '<ul class="grid">%s</ul>' % "".join("<li>%s</li>" % figure(photo, r, alts) for r in run))
        else:
            txt, marks = split_marks(val)
            if txt:
                h.append("<p>%s</p>" % inline(txt))
            h += [todo(m) for m in marks]
        i += 1
    if w["sources"]:
        refs = []
        for s in w["sources"]:
            m = URL.search(s)
            refs.append('<li>%s<a href="%s" rel="noopener">%s</a></li>' % (H.escape(s[:m.start()], quote=False), H.escape(m.group(1)), H.escape(m.group(1), quote=False)) if m else "<li>%s</li>" % H.escape(s))
        h.append('<h3>Sources</h3><ul class="source">%s</ul>' % "".join(refs))
    return '<div class="workshop-copy">%s</div>' % "\n".join(h)
