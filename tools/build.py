#!/usr/bin/env python3
"""Render static pages from content/*.json.

Authoring aid, not a runtime dependency: output is plain static HTML,
committed and served with no build step. Copy lives in content/, markup
lives here, so copy changes without touching design and design without
touching copy.

    python3 tools/build.py

Keys are the SFWF Website Copy Deck's own element names. [VERIFY] and
[PLACEHOLDER] ride as status/note fields on the object they belong to,
never as body text; templates turn them into .todo blocks hidden until
?notes=1.
"""
import json, os, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIALS = os.path.join(ROOT, "tools", "partials") + os.sep

def load(n):
    with open(os.path.join(ROOT, "content", n + ".json"), encoding="utf-8") as f:
        return json.load(f)

e = lambda t: html.escape(str(t), quote=False)
A = lambda t: html.escape(str(t), quote=True)

def note(o, cls="todo"):
    if not isinstance(o, dict) or not o.get("note"):
        return ""
    return '<p class="%s" data-status="%s">%s</p>' % (cls, A(o.get("status", "")), e(o["note"]))

def facts(rows):
    """Key and value, one per row. The questions a first-time visitor asks
    first (what is it, how long, how much) answered without a paragraph."""
    li = "".join('        <li class="fact"><span class="fact__k">%s</span>'
                 '<span class="fact__v">%s</span></li>\n' % (e(r["k"]), e(r["v"])) for r in rows)
    return '      <ul class="facts">\n%s      </ul>\n' % li


def awaiting(o):
    """The visible half of a placeholder.

    .todo is display:none for visitors, so a section whose only content was a
    note rendered as a heading over nothing. This says in the open what is
    coming, which is both truer and better looking than a void.
    """
    if not isinstance(o, dict) or not o.get("awaiting"):
        return ""
    out = '      <p class="awaiting">%s</p>\n' % e(o["awaiting"])
    if o.get("link"):
        out += '      <p><a href="%s">%s &rarr;</a></p>\n' % (A(o["link"]["href"]), e(o["link"]["label"]))
    return out


def eyebrow(t):
    return '<p class="eyebrow">%s</p>' % e(t) if t else ""

def cta(c, cls="btn"):
    if not c or not isinstance(c, dict) or "href" not in c:
        return ""
    return '<a class="%s" href="%s">%s</a>' % (cls, A(c["href"]), e(c["label"]))

def sec(inner, cls="", label=None, sid=None):
    a = ' aria-labelledby="%s"' % label if label else ""
    i = ' id="%s"' % sid if sid else ""
    k = (" " + cls) if cls else ""
    return '  <section class="stratum%s"%s%s>\n    <div class="wrap">\n%s\n    </div>\n  </section>\n' % (k, a, i, inner)

sec_ = sec


def slug(t):
    """Lowercase, drop punctuation, collapse to hyphens: "Contact & Legal" -> contact-legal."""
    t = t.replace("\u2019", "").replace("'", "")
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t


def hero(h, hid, sid=None, photo=None, depth=0):
    """The page opener.

    photo is an optional (src, alt). Given one, the hero becomes two columns
    with the photograph beside the text; without one it stays exactly as it
    was, so the pages that do not take an image are unchanged.
    """
    pills = ""
    if h.get("anchorPills"):
        pills = ('\n      <ul class="chips" aria-label="On this page">'
                 + "".join('<li><a class="chip" href="#%s">%s</a></li>' % (A(slug(p)), e(p))
                           for p in h["anchorPills"])
                 + "</ul>")
    intro = h.get("intro") or h.get("subhead") or ""
    # Every number gets a source line, including the ones inside a hero lede.
    src = '\n      <p class="source small">%s</p>' % e(h["source"]) if h.get("source") else ""
    ctas = ""
    if h.get("primaryCta"):
        ctas = ('\n      <p style="margin-top:var(--s4);display:flex;flex-wrap:wrap;gap:var(--s2);align-items:center">'
                + cta(h["primaryCta"]) + " " + cta(h.get("secondaryCta"), "btn btn--ghost") + "</p>")
    if photo:
        return ('  <section class="stratum" style="border-top:0"%s>\n    <div class="wrap">\n'
                '      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
                '        <div class="span-6">\n          %s\n          <h1 id="%s">%s</h1>\n'
                '          <p class="lede">%s</p>%s%s\n        </div>\n'
                '        <div class="span-6">\n          %s\n        </div>\n'
                '      </div>\n    </div>\n  </section>\n'
                % (' id="%s"' % sid if sid else "", eyebrow(h.get("eyebrow")), hid, e(h["h1"]),
                   e(intro), src + pills, ctas, shot(photo[0], photo[1], cap=True, depth=depth)))
    return ('  <section class="stratum" style="border-top:0"%s>\n    <div class="wrap">\n'
            '      <div class="head" style="margin-bottom:0">\n        %s\n        <h1 id="%s">%s</h1>\n'
            '        <p class="lede">%s</p>\n      </div>%s%s\n    </div>\n  </section>\n'
            % (' id="%s"' % sid if sid else "", eyebrow(h.get("eyebrow")), hid, e(h["h1"]), e(intro),
               src + pills, ctas))

def tabs(items, target, aria="Filter"):
    li = "".join('<li><button class="chip" type="button" data-filter="%s" aria-pressed="%s">%s</button></li>'
                 % (A("all" if i == 0 else t.lower().replace(" ", "-").replace("&", "and")),
                    "true" if i == 0 else "false", e(t)) for i, t in enumerate(items))
    return ('      <ul class="chips" data-filter-for="%s" aria-label="%s">%s'
            '<li class="small" data-filter-status style="align-self:center;color:var(--ink-faint)"></li></ul>\n'
            % (A(target), A(aria), li))

def cards(items, kind=None):
    out = '      <ul class="cards">\n'
    for c in items:
        k = '        <li class="card"%s>\n' % (' data-kind="%s"' % A(kind) if kind else "")
        if c.get("tag"):
            k += '          <div class="card__kind"><span>%s</span></div>\n' % e(c["tag"])
        title = e(c.get("title", c.get("name", "")))
        if isinstance(c.get("cta"), dict):
            title = '<a href="%s">%s</a>' % (A(c["cta"]["href"]), title)
        k += '          <h3 class="card__title">%s</h3>\n' % title
        if c.get("tagline"):
            k += '          <p class="card__line" style="color:var(--soil);font-weight:600">%s</p>\n' % e(c["tagline"])
        if c.get("body"):
            k += '          <p class="card__line">%s</p>\n' % e(c["body"])
        if isinstance(c.get("cta"), dict):
            k += '          <p class="card__line"><a href="%s">%s &rarr;</a></p>\n' % (A(c["cta"]["href"]), e(c["cta"]["label"]))
        n = note(c)
        if n:
            k += "          " + n + "\n"
        out += k + "        </li>\n"
    return out + "      </ul>\n"

def steps(items, icon="i-cycle"):
    """A numbered sequence, one column per step.

    It used to be a two-across grid of half-width cells, which put step three
    on a second row under step one and left a hole beside it, and it repeated
    the same icon against all three. The numeral is the information here, so
    the numeral carries it, the way the homepage approach already does.
    """
    li = "".join(
        '        <li class="step">\n          <p class="step__n">%s</p>\n'
        '          <h3>%s</h3>\n          <p>%s</p>\n%s        </li>\n'
        % (e(s["n"]), e(s.get("title", "")), e(s["body"]),
           ("          " + note(s) + "\n") if s.get("note") else "")
        for s in items)
    return '      <ol class="steps">\n%s      </ol>\n' % li


# ------------------------------------------------------ photographs and motion
# Added 11 September 2026 for the visual-language proposal.
#
# Every photograph on the site is the Foundation's own, from the asset library
# in img/. Each one below was opened and looked at before it was placed: the
# filenames describe almost nothing.
#
# CAPTION is deliberately a constant. Captions are the Foundation's to write,
# and an invented one would be a claim about a real place and real people.
CAPTION = "the place, the people and the date. Foundation to supply."



def web(src):
    """Point at the web-sized derivative, not the original.

    img/ holds the Foundation's originals at the sizes they arrived with, some
    of them several megabytes. tools/images.py writes a capped progressive JPEG
    for each one into img/w/, and every page references those. The originals
    stay exactly as they are, filenames included, as the library.
    """
    # img/cut/ holds the cut-out specimens, which are PNGs with an alpha
    # channel. They are already web-sized, and a JPEG derivative would fill
    # the transparency with black, so they are served exactly as they are.
    if src.startswith("img/cut/"):
        return src
    if not src.startswith("img/") or src.startswith("img/w/"):
        return src
    name = src[len("img/"):]
    if name.lower().endswith(".svg"):
        return src
    # must match tools/images.py safe_stem: srcset is space delimited, so a
    # filename with a space in it would break the attribute silently.
    stem = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(name)[0].lower()).strip("-")
    return "img/w/" + stem + ".jpg"



def img(src, alt, sizes="(max-width: 48em) 100vw, 33vw", depth=0, eager=False, cls=""):
    """One <img>, pointed at the derivatives and told how wide it will be drawn.

    Without sizes the browser assumes 100vw and pulls the 1600px file into a
    300px box. The homepage was shipping 4.3 MB of photographs that way.
    """
    b = "../" * depth
    w = web(src)
    small = w[:-4] + "-800.jpg"
    c = ' class="%s"' % A(cls) if cls else ""
    return ('<img%s src="%s%s" srcset="%s%s 800w, %s%s 1600w" sizes="%s" alt="%s"'
            ' loading="%s" decoding="async">'
            % (c, b, A(w), b, A(small), b, A(w), A(sizes), A(alt),
               "eager" if eager else "lazy"))


def shot(src, alt, cls="", cap=False, depth=0):
    """One photograph, shown whole. Caption only where the layout wants one."""
    c = ("shot " + cls).strip()
    f = '<figure class="%s">\n        %s\n' % (
        A(c), img(src, alt, sizes="(max-width: 48em) 100vw, 50vw", depth=depth))
    if cap:
        f += '        <figcaption class="cap--todo">%s</figcaption>\n' % e(CAPTION)
    return f + "      </figure>"


def mmss(sec):
    """743 -> 12:23. Nothing is invented: no duration, no label."""
    try:
        sec = int(sec)
    except (TypeError, ValueError):
        return ""
    return "%d:%02d" % (sec // 60, sec % 60)


def thumb_src(v, b):
    """A local file if we have one, the old site's if we do not, nothing if
    neither. remoteThumb still points at soilfoodweb.com: run
    tools/thumbs.py to bring those in and stop the new site depending on the
    old one. Until that is done, vercel.json has to keep soilfoodweb.com in
    the Content-Security-Policy's img-src or these load as broken images."""
    t = v.get("thumb") or ""
    if t:
        return b + t
    return v.get("remoteThumb") or ""


def pic(v, b):
    src = thumb_src(v, b)
    return ('<img src="%s" alt="" loading="lazy" decoding="async">' % A(src)) if src else ""


def theatre(only=(), depth=0):
    """The video theatre: one player, a rail of videos, no page reloads.

    Reads content/videos.json, which tools/playlist.py writes and verifies.
    Returns "" when there is nothing verified to show, so the page falls back
    to whatever it said before rather than showing an empty player. That is
    the third of the five old bugs, the canonical URL with no video in it,
    and the fix is to render nothing rather than an empty box.

    The private hash goes in the data, once, where no link can drop it.
    """
    c = load("videos")
    items, seen = [], set()
    for pl in c["playlists"]:
        if only and pl["id"] not in only:
            continue
        for it in pl["items"]:
            # An id and a hash, or it cannot play. The duration used to be
            # required too, as a way of spotting showcase ids in a scrape.
            # That test threw out 21 real videos: plenty of these return no
            # duration from oembed and embed perfectly well. It now applies
            # only to raw scraped data, never to a curated file.
            if not (it.get("id") and it.get("hash")):
                continue
            if not c.get("curated") and not it.get("duration"):
                continue
            if it["id"] in seen:                       # the same video in two playlists
                continue
            seen.add(it["id"])
            items.append(it)
    if not items:
        return ""

    b = "../" * depth
    rows = ""
    for n, v in enumerate(items):
        thumb = ('<span class="theatre__thumb">%s</span>\n' % pic(v, b)) if True else ""
        sub = e(v.get("subtitle", ""))
        rows += ('        <li data-active="%s">\n'
                 '          <button class="theatre__item" type="button" data-i="%d" aria-current="%s">\n'
                 '            %s'
                 '            <span class="theatre__t">%s</span>\n'
                 '            <span class="theatre__s">%s</span>\n'
                 '            <span class="theatre__d">%s</span>\n'
                 '          </button>\n        </li>\n'
                 % ("true" if n == 0 else "false", n, "true" if n == 0 else "false",
                    thumb, e(v["title"]), sub, e(mmss(v.get("duration")))))

    first = items[0]
    payload = json.dumps([dict({k: v.get(k, "") for k in
                                ("slug", "id", "hash", "title", "subtitle")},
                               thumb=thumb_src(v, b))
                          for v in items], ensure_ascii=False)
    # a JSON island cannot be allowed to close the script element early
    payload = payload.replace("</", "<\\/")

    # Titles are whatever the playlist markup or Vimeo gave us. Several are
    # upload names rather than display titles, because the playlist pages
    # render their titles with JavaScript and a scrape of the HTML does not
    # see them. Flagged rather than rewritten: inventing a title for a named
    # grower's case study is exactly the thing not to do.
    flag = ""
    if any(re.search(r"_[A-Z]{2,}|_\d{4}|CTA[A-Z]?\d", v.get("title", "")) for v in items):
        flag = ('      <p class="todo">Some titles below are Vimeo upload names, not display '
                'titles: the playlist pages write their titles with JavaScript, which the scrape '
                'does not see. Run tools/playlist.py --save-raw and the real titles can be read '
                'from the saved pages. Nothing here has been renamed by hand.</p>\n')

    return (flag + '      <div class="theatre" data-theatre>\n'
            '        <div class="theatre__stage">\n'
            '          <div class="theatre__frame" data-frame hidden></div>\n'
            '          <button class="theatre__poster" type="button" data-poster>\n'
            '            %s\n'
            '            <span class="theatre__go" aria-hidden="true">\n'
            '              <svg viewBox="0 0 24 24" width="34" height="34"><path d="M8 5.5 19 12 8 18.5z"/></svg>\n'
            '            </span>\n'
            '            <span class="visually-hidden">Play</span>\n'
            '          </button>\n'
            '          <div class="theatre__panel" data-next hidden>\n'
            '            <p class="theatre__panel-t">Up next: <b data-next-title></b></p>\n'
            '            <p class="theatre__panel-c">Starting in <span data-next-count>8</span></p>\n'
            '            <p class="theatre__panel-b">\n'
            '              <button class="btn" type="button" data-next-go>Play now</button>\n'
            '              <button class="btn btn--ghost" type="button" data-next-cancel>Cancel</button>\n'
            '            </p>\n          </div>\n'
            '          <div class="theatre__panel" data-check hidden>\n'
            '            <p class="theatre__panel-t">Are you still watching?</p>\n'
            '            <p class="theatre__panel-b">\n'
            '              <button class="btn" type="button" data-check-go>Continue</button>\n'
            '            </p>\n          </div>\n        </div>\n'
            '        <p class="theatre__now"><b data-now-title>%s</b> <span data-now-sub></span></p>\n'
            '        <p class="visually-hidden" data-live aria-live="polite"></p>\n'
            '        <ol class="theatre__list">\n%s        </ol>\n'
            '        <script type="application/json" data-theatre-data>%s%s\n'
            '      </div>\n'
            % (pic(first, b), e(first["title"]), rows, payload,
               # written in two halves so this file never contains the literal
               # closing tag inside a Python string that produces one
               "</" + "script>"))


def specimen(src, alt, size="", label="Illustration", depth=0):
    """One cut-out specimen, floating on the page.

    No frame, no ground, no shadow: the transparency is the point, so the
    paper shows through and the object sits on the page the way a specimen
    sits on a museum sweep.

    label defaults to "Illustration" and is not decoration. These assets are
    generated images of real-looking organisms and soil, and the site must
    never present one as a photograph of something the Foundation holds. The
    Foundation's own microscopy stays the only thing shown as real.
    """
    c = ("specimen " + size).strip()
    return ('<figure class="%s">\n        <img src="%s" alt="%s" loading="lazy" decoding="async">\n'
            '        <figcaption><span class="fig-n">%s</span>%s</figcaption>\n      </figure>'
            % (A(c), A(("../" * depth) + web(src)), A(alt), e(label), e(CAPTION)))


def filmstrip(items, depth=0):
    """Photographs running edge to edge. Faces of the people doing the work."""
    li = "".join(
        '        <li>%s</li>\n'
        % img(src, alt, sizes="(max-width: 60em) 60vw, 20vw", depth=depth) for src, alt in items)
    return '      <ul class="filmstrip">\n%s      </ul>\n' % li


def ledger(items, depth=0):
    """A tidy grid of photographs, each with a small caption underneath.

    Items are (src, alt) or (src, alt, label). The label is optional and left
    off wherever naming the place or the people in a frame would be a claim
    the Foundation has not made.
    """
    li = ""
    for it in items:
        src, alt = it[0], it[1]
        label = it[2] if len(it) > 2 else ""
        cap = ('<b>%s</b>' % e(label) if label else "") + '<span class="cap--todo">%s</span>' % e(CAPTION)
        li += ('        <li>\n          <figure>\n            %s\n'
               '            <figcaption>%s</figcaption>\n'
               '          </figure>\n        </li>\n'
               % (img(src, alt, sizes="(max-width: 48em) 50vw, 30vw", depth=depth), cap))
    return '      <ul class="ledger">\n%s      </ul>\n' % li


def films(items, depth=0):
    """Films from the field, as facades.

    A still with a play button, and nothing from Vimeo until somebody presses
    it: an iframe per card would pull a player and its cookies onto the page
    for every visitor who never watches. The privacy hash rides in data-h,
    because these are unlisted videos and the player refuses them without it.
    """
    li = ""
    for f in items:
        src = "https://player.vimeo.com/video/%s?h=%s&badge=0&byline=0&portrait=0&title=0" % (
            f["vimeo"], f["hash"])
        li += ('        <li>\n'
               '          <figure class="film">\n'
               '            <button class="film__go" type="button" data-film="%s"\n'
               '                    aria-label="Play the film with %s, %s">\n'
               '              %s\n'
               '              <span class="film__play" aria-hidden="true">\u25b6</span>\n'
               '            </button>\n'
               '            <figcaption>\n              <b>%s</b>\n'
               '              <span>%s</span>\n              <span>%s</span>\n'
               '            </figcaption>\n          </figure>\n        </li>\n'
               % (A(src), A(f["name"]), A(f["place"]),
                  img(f["poster"], f["posterAlt"], sizes="(max-width: 52em) 100vw, 32vw", depth=depth),
                  e(f["name"]), e(f["place"]), e(f["kind"])))
    return '      <ul class="films">\n%s      </ul>\n' % li


def banner(src, alt, h2, hid, lede="", ctas="", depth=0, tag="h2", eyeb="", source=""):
    """One landscape photograph carrying a whole screen, with one line over it.

    Landscape only and never a face: type sits on the image, so it needs a
    scrim, and a scrim across somebody's face is exactly what was ruled out.
    """
    inner = ""
    if eyeb:
        inner += "          %s\n" % eyebrow(eyeb)
    inner += '          <%s id="%s">%s</%s>\n' % (tag, A(hid), e(h2), tag)
    if lede:
        inner += '          <p class="lede">%s</p>\n' % e(lede)
    if source:
        inner += '          <p class="source small">%s</p>\n' % e(source)
    if ctas:
        inner += '          <p style="margin-top:var(--s4);display:flex;flex-wrap:wrap;gap:var(--s2)">%s</p>\n' % ctas
    return ('  <section class="banner bleed" aria-labelledby="%s">\n    %s\n'
            '    <div class="banner__in">\n      <div class="wrap">\n%s      </div>\n    </div>\n'
            '  </section>\n' % (A(hid), img(src, alt, sizes="100vw", depth=depth), inner))


def slides(depth=0):
    """Three live circles, one drop of water, each one a way in.

    All three run the same reel from the Foundation's archive, framed on
    different parts of the slide and entered at different seconds of the loop,
    so they read as three moments rather than three copies. Positions were
    measured off the square still: the two organisms meet at the centre of the
    frame, and the dark body sits at 24% across, 27% down.

    Each circle is a link. The label says where it goes, and every one of them
    is a label that already exists in the site navigation, so nothing here is
    new copy. An earlier version labelled them by which part of the frame they
    showed, which described the crop rather than the content and meant nothing
    to a reader.

    The attribution belongs to the material, which all three share, so it is
    printed once for the group rather than repeated under every circle.

    Nothing here is colour graded. The rest of the site stretches this reel
    hard because it is nearly flat; these are meant to look like the footage
    looks, so legibility comes from framing instead.
    """
    b = "../" * depth
    # (label, href, zoom, point of interest as %, seconds in, reel)
    # Three different reels, not three crops of one: the same footage at three
    # zooms read as one clip repeated, which is what it was.
    views = [
        ("How the soil food web works",  "science.html",  1.0, 50, 50, 0.0, "sfw-amoeba-loop-square"),
        ("Every program and its price",  "learn.html",    1.6, 50, 50, 2.0, "sfw-amoeba-lab-640"),
        ("Research and publications",    "research.html", 2.4, 24, 27, 6.6, "sfw-amoeba-loop-hero"),
    ]
    li = ""
    for label, href, z, px, py, t, reel in views:
        tx, ty = 50 - px, 50 - py
        transform = "scale(%s)" % z if z == 1.0 else "scale(%s) translate(%d%%, %d%%)" % (z, tx, ty)
        li += ('        <li>\n          <a class="slide" href="%s%s">\n'
               '            <span class="slide__disc">\n'
               '              <video data-loop data-start="%s" muted loop playsinline preload="none"\n'
               '                     style="transform:%s"\n'
               '                     poster="%simg/w/sfw-amoeba-still-square.jpg"\n'
               '                     aria-hidden="true" tabindex="-1"\n'
               '                     data-src="%svideo/%s.webm,%svideo/%s.mp4"></video>\n'
               '            </span>\n'
               '            <span class="slide__n">%s <span class="slide__go" aria-hidden="true">&rarr;</span></span>\n'
               '          </a>\n        </li>\n'
               % (b, A(href), t, transform, b, b, A(reel), b, A(reel), e(label)))
    return ('      <ul class="slides">\n%s      </ul>\n'
            '      <p class="source small" style="margin-top:var(--s4)">'
            'Brightfield microscopy, Soil Food Web Foundation archive</p>\n' % li)


def partners(items):
    """The organizations named so far. A name and a line each: the Foundation
    has not supplied logo files, and a name is worth more than a grey box."""
    if not items:
        return ""
    li = "".join('        <li>\n          <a href="%s"><b>%s</b></a>\n          <span>%s</span>\n        </li>\n'
                 % (A(x["href"]), e(x["name"]), e(x["line"])) for x in items)
    return '      <ul class="partners">\n%s      </ul>\n' % li


def doors(items, depth=0):
    """Three audience doorways. The photograph is the target, type sits under."""
    li = ""
    for it in items:
        src, alt, href, title, body = it[:5]
        # The link text names the destination: a doorway that says only
        # "Farm with biology" does not tell you where pressing it lands you.
        label = ('            <span class="door__go">%s &rarr;</span>\n' % e(it[5])) if len(it) > 5 else ""
        li += ('        <li>\n          <a class="door" href="%s">\n            %s\n'
               '            <h3>%s</h3>\n            <p>%s</p>\n%s'
               '          </a>\n        </li>\n'
               % (A(href), img(src, alt, sizes="(max-width: 52em) 100vw, 32vw", depth=depth),
                  e(title), e(body), label))
    return '      <ul class="doors">\n%s      </ul>\n' % li



# ------------------------------------------------------------------ chrome
# The approved mark. Drop the artwork into img/ named logo.svg, logo.png or
# logo.webp and the header, the overlay menu and the footer all pick it up on
# the next build; the type-set wordmark becomes the accessible name. Nothing
# else to edit: the file being there is the switch.
#
# It stays absent rather than approximated. A hand-traced copy of a brand mark
# is not the brand mark. Decision 16.
def _find_logo():
    """Any image in img/ with "logo" in its name, vector first.

    The canonical names win if they exist, but nobody should have to remember
    a naming rule to change the logo: sfwlogo-240.png works as well as
    logo.svg does.
    """
    d = os.path.join(ROOT, "img")
    if not os.path.isdir(d):
        return None
    for name in ("logo.svg", "logo.png", "logo.webp", "logo.jpg"):
        if os.path.exists(os.path.join(d, name)):
            return "img/" + name
    rank = {".svg": 0, ".png": 1, ".webp": 2, ".jpg": 3, ".jpeg": 3}
    found = [f for f in os.listdir(d)
             if "logo" in f.lower() and os.path.splitext(f)[1].lower() in rank]
    if not found:
        return None
    found.sort(key=lambda f: (rank[os.path.splitext(f)[1].lower()], f.lower()))
    return "img/" + found[0]


LOGO = _find_logo()
LOGO_ALT = "Soil Food Web Foundation"


def wordmark(depth=0, tag="a", href="/", cls=""):
    """The mark in the header, the overlay and the footer.

    One function so the logo lands in all three the moment the file exists.
    The name and the 501(c)(3) line stay in the markup either way: they are
    the accessible name when the logo is an image, and the whole mark until
    the artwork arrives.
    """
    b = "../" * depth
    inner = ""
    if LOGO:
        # Never through web(). That pipeline writes JPEGs, and a JPEG has no
        # alpha channel: a transparent logo would gain a solid box behind it.
        # The mark is small enough that it needs no derivative anyway.
        inner = ('<img class="wordmark__logo" src="%s%s" alt="%s" decoding="async">'
                 % (b, A(LOGO), A(LOGO_ALT)))
    inner += ('<span class="wordmark__name">Soil Food Web Foundation</span>'
              '<span class="wordmark__status">A 501(c)(3) nonprofit</span>')
    k = ("wordmark" + (" " + cls if cls else "")) + (" wordmark--image" if LOGO else "")
    if tag == "a":
        return '<a class="%s" href="%s%s">%s</a>' % (k, b, A(href), inner)
    return '<span class="%s">%s</span>' % (k, inner)


def chrome(depth=0):
    g = load("global")
    b = "../" * depth
    def h(x):
        if x.startswith(("http", "mailto:", "#")):
            return x
        # "/" is the site root, so at depth it is "../", not "..//".
        return (b or "/") if x == "/" else b + x
    u = g["utilityBar"]
    util = "".join('<li><a href="%s">%s</a></li>' % (A(h(a["href"])), e(a["label"])) for a in u["actions"])
    acc = ""
    for it in g["nav"]["items"]:
        if not it.get("children"):
            continue
        sid = it["label"].lower().replace(" ", "-")
        links = "".join('                <li><a href="%s">%s</a></li>\n' % (A(h(c["href"])), e(c["label"]))
                        for c in it["children"])
        desc = it.get("pillar") or "Who we are and how we are governed"
        acc += ('          <li class="acc__item" data-acc-item data-open="false">\n'
                '            <button class="acc__btn" type="button" data-acc-btn aria-controls="acc-%s">\n'
                '              <span class="acc__name">%s</span><span class="acc__desc">%s</span>\n'
                '            </button>\n'
                '            <div class="acc__panel" id="acc-%s" data-acc-panel><div>\n'
                '              <ul class="acc__links">\n%s              </ul>\n'
                '            </div></div>\n          </li>\n' % (sid, e(it["label"]), e(desc), sid, links))
    # The header repeats each section's children as a hover dropdown. Same data
    # as the overlay accordion above, so a link added to global.json reaches
    # both menus: before this, the desktop dropdowns lived only in the committed
    # HTML and every run of this script deleted them.
    tn = ""
    for i in g["nav"]["items"][1:]:
        kids = i.get("children")
        if not kids:
            tn += '\n      <li><a href="%s">%s</a></li>' % (A(h(i["href"])), e(i["label"]))
            continue
        drop = "".join('\n          <li><a href="%s">%s</a></li>' % (A(h(c["href"])), e(c["label"]))
                       for c in kids)
        tn += ('\n      <li class="has-drop"><a href="%s">%s</a>'
               '\n        <ul class="drop">%s\n        </ul>\n      </li>'
               % (A(h(i["href"])), e(i["label"]), drop))
    topnav = tn + "\n    "

    # Happening now, from content/global.json. Every dated item shows its date,
    # and an unconfirmed one says so on the line itself (Decision 12).
    n = g["happeningNow"]
    now_li = "".join(
        '          <li><span class="dated"><time datetime="%s">%s</time></span>'
        '<a href="%s">%s</a></li>\n'
        % (A(it["datetime"]), e(it["dated"]), A(h(it["href"])), e(it["label"]))
        for it in n["items"])
    hdr = ('<!-- ============ UTILITY BAR + HEADER (every page) ============ -->\n'
           '<div class="utility">\n  <div class="wrap">\n'
           '    <p class="utility__tagline">%s</p>\n'
           '    <ul class="utility__links">%s</ul>\n  </div>\n</div>\n'
           '<header class="site-header">\n  <div class="wrap%s">\n'
           '    %s\n'
           '    <ul class="site-header__links">%s</ul>\n'
           '    <a class="btn btn--donate" href="%s">Donate</a>\n'
           '    <button class="menu-btn" type="button" data-menu-open aria-controls="overlay" aria-expanded="false">\n'
           '      <svg class="icon" aria-hidden="true"><use href="#i-menu"/></svg><span class="menu-btn__label">Menu</span>\n'
           '    </button>\n  </div>\n</header>\n\n'
           '<div class="overlay" id="overlay" data-open="false" role="dialog" aria-modal="true" aria-label="Site menu">\n'
           '  <div class="wrap">\n    <div class="overlay__top">\n'
           '      %s\n'
           '      <button class="menu-btn" type="button" data-menu-close>\n'
           '        <svg class="icon" aria-hidden="true"><use href="#i-close"/></svg>Close\n'
           '      </button>\n    </div>\n'
           '    <div class="overlay__body">\n      <nav class="overlay__nav" aria-label="Sections">\n'
           '        <ul class="acc" data-accordion>\n%s        </ul>\n'
           '        <ul class="overlay__utility">%s</ul>\n      </nav>\n'
           '      <aside class="overlay__now" aria-labelledby="now-h">\n'
           '        <h2 id="now-h">%s</h2>\n        <ul class="now-list">\n%s        </ul>\n'
           '        <a class="more" href="%s">%s</a>\n'
           '      </aside>\n    </div>\n'
           '  </div>\n</div>\n\n'
           % (e(u["tagline"]), util, " wrap--logo" if LOGO else "", wordmark(depth), topnav, A(h("donate")),
              wordmark(depth, tag="span"),
              acc, util, e(n["heading"]), now_li, A(h(n["more"]["href"])), e(n["more"]["label"])))

    f = g["footer"]
    navs = ""
    for i, col in enumerate(f["columns"]):
        hn = col["head"]
        li = "".join('          <li><a href="%s">%s</a></li>\n' % (A(h(x["href"])), e(x["label"]))
                     for x in col["links"])
        # 4 wordmark + four 2-wide columns from track 5 = 12 exactly.
        span = "span-2 start-5" if i == 0 else "span-2"
        navs += ('      <nav class="%s" aria-labelledby="f-%d">\n        <h2 id="f-%d">%s</h2>\n'
                 '        <ul>\n%s        </ul>\n      </nav>\n' % (span, i, i, e(hn), li))
    ftr = ('<!-- ============ FOOTER (every page) ============ -->\n'
           '<footer class="site-footer">\n  <div class="wrap">\n    <div class="grid">\n'
           '      <div class="span-4">\n'
           '        %s\n'
           '        <p class="footer__tag">%s</p>\n'
           '        <form class="footer__news" action="#" method="post" aria-label="Newsletter" data-newsletter>\n'
           '          <label for="footer-email" class="visually-hidden">Email address</label>\n'
           '          <input class="input" id="footer-email" type="email" name="email" placeholder="Email for the newsletter" required>\n'
           '          <button class="btn" type="submit">Subscribe</button>\n        </form>\n'
           '        <p class="caption" style="color:rgba(255,255,255,.75)">One email a month. Unsubscribe with one click.</p>\n'
           '      </div>\n%s    </div>\n'
           '    <div class="footer__legal">\n'
           '      <p>EIN 39-4439236. Registered office: 5441 S Macadam Ave Ste N, Portland, Oregon 97239. '
           'Our Form 990 and financial statements are available on the <a href="%s">governance page</a> and on request.</p>\n'
           '      %s\n      <ul>\n        <li>%s</li>\n'
           '        <li><a href="%s">Privacy</a></li>\n        <li><a href="%s">Terms</a></li>\n'
           '        <li><a href="%s">Accessibility</a></li>\n      </ul>\n    </div>\n  </div>\n</footer>\n\n'
           % (wordmark(depth, tag="span"), e(f["brandLine"]), navs, A(h("about-governance")),
              note(f.get("social", {})), e(f["legalLine"]),
              A(h("privacy")), A(h("terms")), A(h("accessibility"))))
    return hdr, ftr


SITE = "https://soilfoodweb.org"   # VERIFY: the production hostname at cutover.


def render(path, title, desc, main, depth=0, share=None, tone=""):
    hdr, ftr = chrome(depth)
    b = "../" * depth
    # og:image has to be absolute: a relative path is useless to a link
    # unfurler, which is not on this origin. Each page shares its own hero.
    img_abs = SITE + "/" + web(share or "img/hand-soil-roots-fungi.jpg")
    sprite = open(PARTIALS + "sprite.html", encoding="utf-8").read()
    head = ('<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '  <title>%s</title>\n  <meta name="description" content="%s">\n'
            '  <meta property="og:site_name" content="Soil Food Web Foundation">\n'
            '  <meta property="og:type" content="website">\n'
            '  <meta property="og:title" content="%s">\n'
            '  <meta property="og:description" content="%s">\n'
            '  <meta property="og:url" content="%s">\n'
            '  <meta property="og:image" content="%s">\n'
            '  <meta name="twitter:card" content="summary_large_image">\n'
            '  <meta name="twitter:title" content="%s">\n'
            '  <meta name="twitter:description" content="%s">\n'
            '  <meta name="twitter:image" content="%s">\n'
            '  <link rel="preload" href="%sfonts/montserrat-latin-variable.woff2" as="font" type="font/woff2" crossorigin>\n'
            '  <link rel="preload" href="%sfonts/source-sans-3-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
            '  <link rel="stylesheet" href="%scss/site.css">\n</head>\n<body%s>\n'
            '<a class="skip" href="#main">Skip to content</a>\n\n'
            '<!-- Icon sprite, inlined so the page works over file:// -->\n'
            % (e(title), A(desc),
               A(title), A(desc), A(SITE + "/" + path), A(img_abs),
               A(title), A(desc), A(img_abs),
               b, b, b,
               # The page's accent family. One colour per section of the site,
               # set once here and read by every component through --accent.
               (' class="%s"' % A(tone)) if tone else ""))
    out = head + sprite + "\n\n" + hdr + main + "\n\n" + ftr + '<script src="%sjs/site.js"></script>\n</body>\n</html>\n' % b
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
        f.write(out)
    print("  rendered", path)

MAIN = lambda s: '<main id="main">\n\n' + s + '\n</main>'


# ------------------------------------------------------------------- pages
def p_home():
    """The homepage.

    Evan asked for a community-led page with the faces of the movement up
    front, more biology, depth and layering, and real photographs of people
    doing the hands-on work. So: the specimen first, the people immediately
    after, and the Foundation's own microscopy running silently before any
    claim is made about what lives in soil.

    Copy is untouched. Every string still comes from content/home.json.
    """
    c = load("home"); o = []

    # -- hero. The image note in home.json asks for hands holding living soil
    #    with roots and fungal strands visible; this photograph is exactly that.
    h = c["hero"]
    o.append('  <section class="stratum" style="border-top:0">\n    <div class="wrap">\n'
             '      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
             '        <div class="span-6">\n          %s\n          <h1>%s</h1>\n'
             '          <p class="lede">%s</p>\n'
             '          <p style="margin-top:var(--s4);display:flex;flex-wrap:wrap;gap:var(--s2);align-items:center">%s %s</p>\n'
             '        </div>\n        <div class="span-6">\n          %s\n        </div>\n'
             '      </div>\n    </div>\n  </section>\n'
             % (eyebrow(h["eyebrow"]), e(h["h1"]), e(h["subhead"]),
                cta(h["primaryCta"]), cta(h["secondaryCta"], "btn btn--ghost"),
                shot("img/hand-soil-roots-fungi.jpg",
                     "An open palm holding a clump of soil bound together by roots and pale fungal strands",
                     cap=True)))

    # -- the faces, immediately. No copy of its own: the photographs are the
    #    argument. Edge to edge so the page opens out before the figures.
    o.append('  <section class="stratum" aria-label="The community at work">\n'
             '    <div class="bleed">\n%s    </div>\n  </section>\n'
             % filmstrip([
                 ("img/Carla-Nicks Son-Nick-ERI-Wild Soils Event-11-2024.jpg",
                  "A group of people laughing as they work together outdoors with brushes and rakes"),
                 ("img/ctpfw-student-moving-compost-1.jpg",
                  "A student lifting an armful of finished compost while others watch and a hose is played over the pile"),
                 ("img/erc-panchamana-treeplanting-3-fb-img-1666271008784.jpg",
                  "A young man crouching to plant a seedling, with others planting along the same row behind him"),
                 ("img/hvdb-inplanten-002.jpg",
                  "A group planting young trees across an open field on a grey day"),
                 ("img/el-nino-2017-tractor-in-mud-w-crew.jpg",
                  "A crew digging a tractor out of deep mud under a wide sky"),
             ]))

    # -- the figures
    s_ = c["stats"]; cells = ""
    for k in [k for k in ("stat1", "stat2", "stat3") if k in s_]:
        st = s_[k]
        src_ = '<p class="source small">%s</p>' % e(st["source"]) if st.get("source") else ""
        cells += ('        <div class="span-5">\n          <p class="stat">%s</p>\n'
                  '          <p class="stat__label">%s</p>\n          %s\n        </div>\n'
                  % (e(st["value"]), e(st["label"]), src_))
    o.append(sec('      <h2 id="stats-h" class="visually-hidden">The Foundation in figures</h2>\n'
                 '      <div class="grid">\n%s      </div>\n      %s' % (cells, note(s_)),
                 label="stats-h"))

    # -- the three doorways. Evan's Work With Us copy, on the homepage, each
    #    one leading to the page that serves that person first.
    dr = c["doors"]
    o.append(sec('      <div class="head">\n        %s\n        <h2 id="doors-h">%s</h2>\n      </div>\n%s'
                 % (eyebrow(dr["eyebrow"]), e(dr["h2"]),
                    doors([(x["img"], x["alt"], x["href"], x["title"], x["body"], x["cta"])
                           for x in dr["cards"]])), label="doors-h", sid="doors"))

    # -- the slide. The most valuable material the Foundation owns, given the
    #    quietest treatment on the page: silent, contained, endless.
    o.append(sec('      <h2 id="slide-h" class="visually-hidden">One drop of soil water, under the microscope</h2>\n'
                 '%s' % slides(), label="slide-h"))

    # -- who we are, with the one legacy moment the homepage gets
    w = c["whoWeAre"]
    o.append(sec('      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
                 '        <div class="span-7">\n          %s\n          <h2 id="who-h">%s</h2>\n'
                 '          %s\n          <p><a href="%s">%s</a></p>\n        </div>\n'
                 '        <div class="span-5">\n          %s\n        </div>\n      </div>\n      %s'
                 % (eyebrow(w["eyebrow"]), e(w["h2"]),
                    "\n          ".join("<p>%s</p>" % e(p) for p in w["body"]),
                    A(w["link"]["href"]), e(w["link"]["label"]),
                    shot("img/hand-wet-dirt-worm.jpg",
                         "A hand holding a broken clod of wet dark soil over freshly turned ground",
                         cap=True), note(w)), label="who-h"))

    # -- the approach. Four steps, four photographs, numerals instead of the
    #    drawn branch icons: the steps are a real sequence, so a numeral is
    #    information. Nothing here is drawn.
    a = c["howItWorks"]
    # One treatment across all four: a hand, soil, close, warm. The clinical
    # blue lab bench and the wide garden aerial were the two that broke the
    # set, so the group now reads as four plates from one collection.
    step_shots = [
        ("img/soil-sample-close-up-test-tube.jpg",
         "A gloved hand holding a sample tube and a probe over dark soil"),
        ("img/hand-of-compost.jpg",
         "A hand lifting a fistful of dark finished compost above the pile it came from"),
        ("img/hand-scooping-planter-bed-soil.jpg",
         "A hand lifting a scoop of dark crumbly soil from a planting bed"),
        ("img/handling-loose-soil.jpg",
         "Hands letting dry crumbs of soil fall back to the ground in low sunlight"),
    ]
    cells = ""
    for i, st in enumerate(a["steps"]):
        src, alt = step_shots[i]
        cells += ('        <div class="span-3">\n          <div class="step">\n            %s\n'
                  '            <span class="fig-n">Fig. %02d</span>\n            <h3>%s</h3>\n            <p>%s</p>\n'
                  '          </div>\n        </div>\n'
                  % (shot(src, alt, cls="shot--crop"), st["n"],
                     e(st.get("title", "")), e(st["body"])))
    o.append(sec('      <div class="head">\n        %s\n        <h2 id="approach-h">%s</h2>\n      </div>\n'
                 '      <div class="case">\n        <div class="grid" style="row-gap:var(--s5)">\n%s        </div>\n      </div>\n'
                 '      <p style="margin-top:var(--s5)"><a href="%s">%s</a></p>\n      %s'
                 % (eyebrow(a["eyebrow"]), e(a["h2"]), cells,
                    A(a["link"]["href"]), e(a["link"]["label"]), note(a)), label="approach-h"))

    # -- learn with us. The existing card takes a photograph in .card__media.
    l = c["learnWithUs"]
    card_shots = [
        ("img/2-dirty-hands.jpg", "Two open palms held out, thickly covered in wet soil"),
        ("img/Test tubes with sample_.jpg", "Sample tubes racked in front of a microscope, shallow focus"),
        ("img/erc-rancho-cacachilas-agro8.jpg", "Rows of flowering crops and low tunnels seen from directly above"),
        ("img/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg",
         "People spread across a clearing planting seedlings among standing trees"),
        ("img/ctpfw-student-squeezing-compost-1.jpg",
         "A student in gloves squeezing a handful of compost to test it, with a group watching"),
    ]
    out = '      <ul class="cards">\n'
    for i, cd in enumerate(l["cards"]):
        src, alt = card_shots[i] if i < len(card_shots) else (None, "")
        k = '        <li class="card">\n'
        if src:
            k += ('          <div class="card__media">%s</div>\n'
                  % img(src, alt, sizes="(max-width: 48em) 100vw, 30vw"))
        if cd.get("tag"):
            k += '          <div class="card__kind"><span>%s</span></div>\n' % e(cd["tag"])
        title = e(cd.get("title", ""))
        if isinstance(cd.get("cta"), dict):
            title = '<a href="%s">%s</a>' % (A(cd["cta"]["href"]), title)
        k += '          <h3 class="card__title">%s</h3>\n' % title
        if cd.get("body"):
            k += '          <p class="card__line">%s</p>\n' % e(cd["body"])
        if isinstance(cd.get("cta"), dict):
            k += ('          <p class="card__line"><a href="%s">%s &rarr;</a></p>\n'
                  % (A(cd["cta"]["href"]), e(cd["cta"]["label"])))
        n_ = note(cd)
        if n_:
            k += "          " + n_ + "\n"
        out += k + "        </li>\n"
    out += "      </ul>\n"
    o.append(sec('      <div class="head">\n        %s\n        <h2 id="learn-h">%s</h2>\n      </div>\n%s      %s'
                 % (eyebrow(l["eyebrow"]), e(l["h2"]), out,
                    '<p class="todo">%s</p>' % e(l["layoutNote"])), label="learn-h"))

    # -- what's new, as an index list: thumbnail, date, line, category right.
    n = c["whatsNew"]
    links = " &middot; ".join('<a href="%s">%s</a>' % (A(x["href"]), e(x["label"])) for x in n["links"])
    rows = "".join(
        '        <li class="entry entry--thumb">\n'
        '          <span class="entry__thumb"><img src="%s" alt="%s" loading="lazy" decoding="async"></span>\n'
        '          <span class="dated"><time datetime="%s">%s</time></span>\n'
        '          <h3 class="entry__t"><a href="%s">%s</a></h3>\n'
        '          <span class="entry__kind">%s</span>\n        </li>\n'
        % (A(it["img"]), A(it["alt"]), A(it["datetime"]), e(it["dated"]),
           A(it["href"]), e(it["label"]), e(it["kind"])) for it in n["items"])
    o.append(sec('      <div class="head">\n        %s\n        <h2 id="new-h">%s</h2>\n      </div>\n'
                 '      <ul class="rule-list rule-list--thumb">\n%s      </ul>\n'
                 '      <p style="margin-top:var(--s4)">%s</p>\n      %s'
                 % (eyebrow(n["eyebrow"]), e(n["h2"]), rows, links, note(n)),
                 label="new-h"))

    # -- the testimonial. A real one, named, with its source under it.
    t = c["testimonial"]
    if isinstance(t.get("quote"), str):
        o.append(sec('      <h2 id="say-h" class="visually-hidden">What people say</h2>\n'
                     '      <figure class="testimonial">\n        <blockquote><p>%s</p></blockquote>\n'
                     '        <figcaption>%s</figcaption>\n      </figure>\n'
                     '      <p class="source small">%s</p>\n      %s'
                     % (e(t["quote"]), e(t["attribution"]), e(t["source"]), note(t)), label="say-h"))
    else:
        o.append(sec("      %s\n      %s" % (note(t["quote"]), note(t["attribution"])), "notes-only"))

    # .head puts the h2 left and the lede right; this section's h2 is
    # visually hidden, which left the lede stranded in an empty right column.
    ec = c["ecosystem"]
    o.append(sec('      <h2 id="eco-h" class="visually-hidden">Our ecosystem</h2>\n      %s\n'
                 '      <p class="lede" style="max-width:44ch;margin-top:var(--s2)">%s</p>\n%s'
                 '      <p style="margin-top:var(--s4)">%s</p>\n      %s'
                 % (eyebrow(ec["eyebrow"]), e(ec["line"]), partners(ec.get("partners", [])),
                    cta(ec["cta"], "btn btn--ghost"), note(ec)),
                 label="eco-h"))

    # -- the close. One landscape photograph carrying the whole screen, with
    #    the join line over it. No people in the frame, so the scrim the type
    #    needs falls on land and sky only.
    j = c["joinBand"]
    btns = " ".join(cta(x, "btn" if i == 0 else "btn btn--ghost")
                    for i, x in enumerate(j["ctas"]) if x.get("type") != "email")
    o.append(banner("img/erc-rancho-cacachilas-agro.jpg",
                    "Long rows of crops running to a line of trees under a wide clouded sky",
                    j["h2"], "join-h", j["body"], btns))
    return MAIN("\n".join(o))


def p_about():
    c = load("about"); o = []

    # hero, with one photograph beside it
    h = c["hero"]
    o.append('  <section class="stratum" style="border-top:0">\n    <div class="wrap">\n'
             '      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
             '        <div class="span-6">\n          %s\n          <h1 id="about-h">%s</h1>\n'
             '          <p class="lede">%s</p>\n        </div>\n'
             '        <div class="span-6">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n'
             % (eyebrow(h.get("eyebrow")), e(h["h1"]), e(h.get("intro") or h.get("subhead") or ""),
                shot("img/handling-loose-soil.jpg",
                     "Hands letting dry crumbs of soil fall back to the ground in low sunlight, a green field behind",
                     cap=True)))

    m = c["missionVision"]
    o.append(sec('      <div class="grid">\n        <div class="span-6"><h2 id="mission-h">Mission</h2><p class="lede">%s</p></div>\n'
                 '        <div class="span-6"><h2>Vision</h2><p class="lede">%s</p></div>\n      </div>'
                 % (e(m["mission"]), e(m["vision"])), "", "mission-h", "mission"))

    hi = c["history"]
    rows = "".join('        <li class="entry">\n          <span class="dated">%s</span>\n'
                   '          <div><h3 class="entry__t">%s</h3><p class="entry__line">%s</p>%s</div>\n'
                   '          <span></span>\n        </li>\n'
                   % (e(x["year"]), e(x["title"]), e(x["body"]),
                      (('<p class="entry__line"><a href="%s">%s</a></p>' % (A(x["link"]), A(x["link"]))) if x.get("link") else "")
                      # a number in a timeline entry still names where it came from
                      + (('<p class="entry__line"><span class="source small"><a href="%s">%s</a>, %s</span></p>'
                          % (A(x["sourceLink"]["href"]), e(x["sourceLink"]["label"]), e(x["source"])))
                         if x.get("source") else ""))
                   for x in hi["entries"])
    o.append(sec('      <div class="head"><h2 id="story-h">%s</h2></div>\n      <ul class="rule-list">\n%s      </ul>'
                 % (e(hi["h2"]), rows), label="story-h", sid="our-story"))

    # The four pillars. The drawn web-diagram icon is gone: circles joined by
    # lines is exactly the thing that was ruled out. Photographs and numerals
    # instead, because the pillars are four real kinds of work.
    wd = c["whatWeDo"]
    pillar_shots = [
        ("img/ctpfw-student-squeezing-compost-1.jpg",
         "A student in gloves squeezing a handful of compost to test it while a group watches"),
        ("img/soil-sample-close-up-test-tube.jpg",
         "Gloved hands holding a sample tube and a probe over dark soil"),
        ("img/erc-panchmana-treeplanting-fb-img-1666270907385.jpg",
         "A long line of people planting seedlings through a stand of tall trees"),
        ("img/Carla-Nicks Son-Nick-ERI-Wild Soils Event-11-2024.jpg",
         "A group of people laughing as they work together outdoors with brushes and rakes"),
    ]
    cells = ""
    for i, pl in enumerate(wd["pillars"]):
        src, alt = pillar_shots[i]
        cells += ('        <div class="span-3">\n          <div class="step">\n            %s\n'
                  '            <p class="step__n">%s</p>\n            <h3>%s</h3>\n            <p>%s</p>\n'
                  '          </div>\n        </div>\n'
                  % (shot(src, alt, cls="shot--crop"), e(str(pl["n"])), e(pl["title"]), e(pl["body"])))
    o.append(sec('      <div class="head"><h2 id="wd-h">%s</h2></div>\n'
                 '      <div class="grid" style="row-gap:var(--s5)">\n%s      </div>'
                 % (e(wd["h2"]), cells), "", "wd-h", "what-we-do"))

    t = c["team"]
    o.append(sec('      <div class="head"><h2 id="team-h">%s</h2></div>\n'
                 '      <p>The full roster, taken from soilfoodweb.com, lives on the team page.</p>\n'
                 '      <p><a class="btn btn--ghost" href="about-team">Our team and board</a></p>\n      %s'
                 % (e(t["h2"]), note(t)), label="team-h", sid="team"))

    # The legacy section. Legacy Purple appears here and on her own page, and
    # nowhere else on the site. Her face is shown whole and untouched.
    el = c["elaine"]
    o.append(sec('      <div class="grid legacy" style="align-items:center;row-gap:var(--s5)">\n'
                 '        <div class="span-5">\n          %s\n        </div>\n'
                 '        <div class="span-6 start-7">\n          %s\n          <h2 id="el-h">%s</h2>\n          %s\n'
                 '          <p><a href="%s">%s</a></p>\n        </div>\n      </div>'
                 % (shot("img/copy-of-9.jpg",
                         "Dr. Elaine Ingham outdoors in a blue patterned shirt, looking towards the camera",
                         cls="shot--legacy", cap=True),
                    eyebrow(el["eyebrow"]), e(el["h2"]),
                    "\n          ".join("<p>%s</p>" % e(p) for p in el["body"]),
                    A(el["link"]["href"]), e(el["link"]["label"])), "", "el-h", "dr-elaines-legacy"))

    cl = c["contactLegal"]
    o.append(sec('      <div class="grid">\n        <div class="span-6"><h2 id="cl-h">Contact &amp; Legal</h2>\n'
                 '          <p>%s</p><p><a class="btn btn--ghost" href="contact">Contact us</a></p></div>\n'
                 '        <div class="span-5 start-8"><p class="small">%s</p><p class="small">%s</p>%s</div>\n      </div>'
                 % (e(cl["contact"]), e(cl["legal"]), e(cl["brandUse"]),
                    note({"note": cl["brandUseNote"], "status": "note"})), label="cl-h", sid="contact-legal"))
    return MAIN("\n".join(o))


def p_learn():
    """Learn. The programs list becomes the index list: a thumbnail beside each
    line, the tagline on the left, the category on the right, thin rules
    between. One photograph per program, chosen for what the program actually
    involves rather than for decoration.
    """
    c = load("learn"); o = []

    h = c["hero"]
    o.append('  <section class="stratum" style="border-top:0">\n    <div class="wrap">\n'
             '      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
             '        <div class="span-6">\n          %s\n          <h1 id="learn-h">%s</h1>\n'
             '          <p class="lede">%s</p>\n        </div>\n'
             '        <div class="span-6">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n'
             % (eyebrow(h.get("eyebrow")), e(h["h1"]), e(h.get("intro") or h.get("subhead") or ""),
                shot("img/Elaine Flower Shirt Microscope.png",
                     "A researcher at a microscope in a laboratory, reading from a screen beside her",
                     cap=True)))

    ps = c["pathSelector"]
    o.append(sec('      <div class="head"><h2 id="path-h">%s</h2></div>\n'
                 '      <ul class="chips" aria-label="Paths">%s</ul>'
                 % (e(ps["h2"]), "".join('<li><a class="chip" href="%s">%s</a></li>'
                                        % (A(x["href"]), e(x["label"])) for x in ps["chips"])),
                 "", "path-h"))

    program_shots = {
        "foundation-courses": ("img/2-dirty-hands.jpg",
                               "Two open palms held out, thickly covered in wet soil"),
        "complete-practicum": ("img/Sampling equipment.jpg",
                               "A microscope on a bench beside racked sample tubes and bottles"),
        "permaculture": ("img/erc-panchamana-garden.jpg",
                         "A planted garden of curved beds seen from above, dense with green growth"),
        "restoration": ("img/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg",
                        "People spread across a clearing planting seedlings among standing trees"),
        "workshops": ("img/ctpfw-student-squeezing-compost-1.jpg",
                      "A student in gloves squeezing a handful of compost to test it, with a group watching"),
        "webinars": ("img/soil-sample-close-up-test-tube.jpg",
                     "Gloved hands holding a sample tube and a probe over dark soil"),
    }
    missing = [pr["id"] for pr in c["programs"] if pr["id"] not in program_shots]
    if missing:
        raise SystemExit("no thumbnail for program id(s): " + ", ".join(missing)
                         + ". Add one to program_shots, or the row renders an empty box.")
    rows = ""
    for pr in c["programs"]:
        src, alt = program_shots[pr["id"]]
        thumb = '          <span class="entry__thumb">%s</span>\n' % img(src, alt, sizes="10rem")
        rows += ('        <li class="entry entry--thumb" id="%s">\n%s'
                 '          <span class="entry__kind" style="text-align:left">%s</span>\n'
                 '          <div><h3 class="entry__t">%s</h3>\n'
                 '            <p class="entry__line">%s</p>\n            <p class="entry__line">%s</p>%s</div>\n'
                 '          <span></span>\n        </li>\n'
                 % (A(pr["id"]), thumb, e(pr["tagline"]), e(pr["name"]), e(pr["body"]),
                    '<a href="%s">%s &rarr;</a>' % (A(pr["cta"]["href"]), e(pr["cta"]["label"])), note(pr)))
    o.append(sec('      <div class="head"><h2 id="prog-h" class="visually-hidden">Programs</h2></div>\n'
                 '      <ul class="rule-list rule-list--thumb">\n%s      </ul>\n'
                 '      <p class="ribbon">%s</p>\n      %s'
                 % (rows, e(c["guarantee"]["ribbon"]), note(c["guarantee"])), label="prog-h", sid="programs"))

    t = c["testimonials"]
    o.append(sec('      <div class="head"><h2 id="tq-h">%s</h2></div>\n%s      %s'
                 % (e(t["h2"]), awaiting(t), "\n      ".join(note(q) for q in t["quotes"])),
                 "", "tq-h"))

    f = c["faq"]
    rows = "".join('        <li class="entry">\n          <span></span>\n'
                   '          <div><h3 class="entry__t">%s</h3><p class="entry__line">%s</p>%s</div>\n'
                   '          <span></span>\n        </li>\n' % (e(q["q"]), e(q["a"]), note(q)) for q in f["items"])
    o.append(sec('      <div class="head"><h2 id="faq-h">%s</h2></div>\n      <ul class="rule-list">\n%s      </ul>'
                 % (e(f["h2"]), rows), "", "faq-h"))
    return MAIN("\n".join(o))


def p_science():
    """How the soil food web works.

    Six mechanisms. The first one IS the microscopy, so it gets the rack:
    scroll drives the playhead and the focus together, and reading the page
    becomes the act of looking down a microscope. Study 14 from /motion.

    The other five carry the Foundation's own animation for that mechanism,
    embedded from Vimeo and lazy-loaded, so nothing is fetched until the
    reader scrolls to it. The animations explain the mechanism; a photograph
    of somebody holding soil never did.
    """
    c = load("science"); o = []

    h = c["hero"]
    o.append('  <section class="stratum" style="border-top:0">\n    <div class="wrap">\n'
             '      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
             '        <div class="span-6">\n          %s\n          <h1 id="sci-h">%s</h1>\n'
             '          <p class="lede">%s</p>\n        </div>\n'
             '        <div class="span-6">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n'
             % (eyebrow(h.get("eyebrow")), e(h["h1"]), e(h.get("intro") or h.get("subhead") or ""),
                shot("img/fungal-spores-in-suspension.jpg",
                     "A brightfield microscope view of a pale green field scattered with dark spores and debris",
                     cap=True)))

    body = ""
    for m in c["mechanisms"]:
        n = m["n"]
        if True:
            # the Foundation's own animation for this mechanism. loading="lazy"
            # keeps it off the wire until the reader scrolls to it.
            an = m["animation"]
            media = ('        <figure class="plate span-6 start-7">\n'
                     '          <div class="plate__film">\n'
                     '            <iframe src="https://player.vimeo.com/video/%s?badge=0&amp;byline=0&amp;portrait=0&amp;title=0"\n'
                     '                    title="%s" loading="lazy"\n'
                     '                    allow="fullscreen; picture-in-picture" allowfullscreen></iframe>\n'
                     '          </div>\n'
                     '          <figcaption><span class="plate__n">Plate %d.</span> <span class="plate__t">%s</span></figcaption>\n'
                     '        </figure>\n'
                     % (A(an["vimeo"]), A("Animation: " + an["title"]), n, e(an["title"])))
        body += ('      <div class="grid" style="padding-block:var(--s6);border-top:var(--hairline) solid var(--rule);align-items:center" id="mechanism-%d">\n'
                 '        <div class="span-5">\n          <p class="small" style="color:var(--ink-faint)">%d of 6</p>\n'
                 '          <h3>%s</h3>\n          <p>%s</p>\n          <p class="todo">%s</p>\n        </div>\n%s      </div>\n'
                 % (n, n, e(m["title"]), e(m["body"]), e(m["animation"]["note"]), media))

    o.append('  <section class="stratum" aria-labelledby="mech-h" style="border-top:0">\n    <div class="wrap">\n'
             '      <h2 id="mech-h" class="visually-hidden">The six mechanisms</h2>\n%s    </div>\n  </section>\n' % body)

    br = c["bridge"]
    o.append(sec('      <div class="head"><h2 id="br-h">%s</h2><p>%s</p></div>\n'
                 '      <p><a class="btn" href="practice#case-studies">Case studies</a> '
                 '<a class="btn btn--ghost" href="learn">Explore our programs</a></p>'
                 % (e(br["title"]), e(br["body"])), "", "br-h"))

    cs = c["cases"]
    o.append(sec('      <div class="head"><h2 id="cs-h">%s</h2><p>%s</p></div>\n%s      %s\n'
                 '      <p class="small">%s</p>'
                 % (e(cs["h2"]), e(cs["intro"]), awaiting(cs), note(cs["cards"]), e(c["honestFooter"])),
                 label="cs-h"))
    return MAIN("\n".join(o))


def app_band(a):
    """A web app, offered honestly.

    sMApp has no App Store or Google Play listing, so there are no store
    buttons here. Read the _note in content/practice.json before adding any:
    the "SoilMapp" in both stores is a different organisation's app, and
    searching the stores by name lands on it.

    What a store install would really have bought is an icon on the home
    screen, so this offers that route instead, spelled out for both phones in
    plain HTML. No user agent sniffing: the string lies, sniffing fingerprints
    the reader, it breaks with scripting off, and it hides the desktop path
    from someone on a phone who wants it. The band needs no JavaScript at all.

    The address is a literal absolute https URL carried in the content file,
    never assembled at runtime, so there is no way to steer it with a query
    parameter. It opens in the same tab, like all 144 other outbound links on
    this site, which leaves no window.opener handle behind for the far end to
    reach back through. The host is printed next to the button so a reader can
    check it against the address bar before signing in.
    """
    plats = ""
    for pl in a["install"]["platforms"]:
        li = "".join("            <li>%s</li>\n" % e(x) for x in pl["steps"])
        plats += ('        <li>\n          <h4>%s</h4>\n          <ol>\n%s          </ol>\n        </li>\n'
                  % (e(pl["name"]), li))
    return ('      <div class="head">\n        %s\n        <h2 id="app-h">%s</h2>\n      </div>\n'
            '      <div class="getapp">\n'
            '      <p class="lede">%s</p>\n      <p>%s</p>\n      %s\n'
            '        <p class="getapp__go">\n'
            '          <a class="btn" href="%s">'
            '<svg class="icon" aria-hidden="true" focusable="false"><use href="#i-web"/></svg>%s</a>\n'
            '          <span class="getapp__host">%s Opens <b>%s</b></span>\n'
            '        </p>\n        <p class="getapp__limit">%s</p>\n'
            '        <div class="getapp__install">\n          <h3>%s</h3>\n          <p>%s</p>\n'
            '          <ul class="getapp__steps">\n%s          </ul>\n        </div>\n'
            '      </div>\n      <p class="source small">%s</p>\n'
            % (eyebrow(a.get("eyebrow")), e(a["h2"]),
               e(a["what"]), e(a["detail"]), note(a.get("access", {})),
               A(a["cta"]["href"]), e(a["cta"]["label"]),
               e(a["free"]), e(a["host"]), e(a["limit"]),
               e(a["install"]["h3"]), e(a["install"]["lede"]), plats,
               e(a["source"])))


def p_practice():
    """Practice. Carries the three audience doorways Evan approved.

    A doorway is a photograph you walk through, so the whole cell is the link
    and the type sits under the image rather than on it.
    """
    c = load("practice"); o = []

    h = c["hero"]
    o.append('  <section class="stratum" style="border-top:0">\n    <div class="wrap">\n'
             '      <div class="grid" style="align-items:center;row-gap:var(--s5)">\n'
             '        <div class="span-6">\n          %s\n          <h1 id="pr-h">%s</h1>\n'
             '          <p class="lede">%s</p>\n        </div>\n'
             '        <div class="span-6">\n          %s\n        </div>\n      </div>\n    </div>\n  </section>\n'
             % (eyebrow(h.get("eyebrow")), e(h["h1"]), e(h.get("intro") or ""),
                shot("img/red-soil-hand.jpg",
                     "An open palm resting on deep red soil, the same soil caught in the creases of the fingers",
                     cap=True)))

    o.append(sec("      " + note(c["projects"]), "notes-only"))

    # Evan, Sep 7: until the three written case studies exist, the Consultant
    # and Farmer Case Studies playlists run here as stories from the field.
    # The theatre renders itself only when content/videos.json holds videos
    # that have been verified as playable; until then this section says
    # exactly what it said before.
    cs = c["caseStudies"]
    # The eleven case-study films run in the theatre: one player that stays on
    # the page, autoplay into the next, and a shareable ?v= link for each.
    # Everything around it, the source line, the notes and the link to the
    # written Sweden study, is as the base branch wrote it.
    stage = theatre(only=load("videos")["onPractice"])
    o.append(sec('      <div class="head">\n        %s\n        <h2 id="csx-h">%s</h2>\n        <p>%s</p>\n      </div>\n%s'
                 '      <p class="source small">%s</p>\n'
                 '      <p style="margin-top:var(--s4)"><a class="btn btn--ghost" href="projects/market-garden-sweden">Read the Sweden market garden case study</a></p>\n'
                 '      %s%s'
                 % (eyebrow(cs["eyebrow"]), e(cs["h2"]), e(cs["lede"]), stage,
                    e(cs["source"]), note(cs), note(cs["more"])),
                 label="csx-h", sid="case-studies"))

    o.append(sec(app_band(c["app"]), "", "app-h", "app"))

    w = c["workWithUs"]
    door_shots = [
        ("img/hand-scooping-planter-bed-soil.jpg",
         "A hand lifting a scoop of dark crumbly soil from a planting bed, green growth behind"),
        ("img/erc-rancho-cacachilas-aerial-shot.jpg",
         "An aerial view along a wooded valley floor with mountains beyond"),
        ("img/ctpfw-student-moving-compost-1.jpg",
         "A student lifting an armful of finished compost while a group looks on"),
    ]
    items = []
    for i, cd in enumerate(w["cards"]):
        src, alt = door_shots[i]
        items.append((src, alt, cd["href"], cd["title"], cd["body"], cd["cta"]))

    fields = "".join('          <p><label for="w-%d">%s</label><br><input class="input" id="w-%d" type="text"></p>\n'
                     % (i, e(f), i) for i, f in enumerate(w["form"]["fields"]))
    o.append(sec('      <div class="head">\n        <p class="eyebrow">%s</p>\n        <h2 id="ww-h">%s</h2>\n        <p>%s</p>\n      </div>\n%s'
                 '      <div class="grid" style="margin-top:var(--s6)">\n'
                 '        <div class="span-6">\n          <h3>%s</h3>\n          <form action="mailto:info@soilfoodweb.com" method="post">\n%s'
                 '            <p><button class="btn" type="submit">Send</button></p>\n          </form>\n          %s\n        </div>\n'
                 '        <div class="span-5 start-8"><p>%s</p></div>\n      </div>'
                 % (e(w["h2"]), e(w["tagline"]), e(w["lede"]), doors(items),
                    e(w["form"]["title"]), fields, note(w["form"]),
                    " &middot; ".join('<a href="%s">%s</a>' % (A(x["href"]), e(x["label"])) for x in w["crossLinks"])),
                 "", "ww-h", "work-with-us"))
    return MAIN("\n".join(o))


def optional_img(src, alt, depth=0, cls="", sizes=""):
    """A photograph that has not been uploaded yet.

    Everything under public/assets/ is referenced at its final path before the
    real file arrives. These are not in img/, so they have no img/w/ derivative
    and no srcset: they are uploaded at the size the README asks for. The
    data-optional flag is what site.js job 13 looks for, so a file that is not
    there yet prints its own alt text in a toned box instead of a broken icon.
    """
    b = "../" * depth
    c = ' class="%s"' % A(cls) if cls else ""
    s = ' sizes="%s"' % A(sizes) if sizes else ""
    return ('<img%s src="%s%s" alt="%s"%s loading="lazy" decoding="async" data-optional>'
            % (c, b, A(src), A(alt), s))


MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")
MON3 = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _when(date, today):
    """Which period chips a post answers to: "year month", "year", or nothing.

    Space separated, because a post from this month is also a post from this
    year and has to survive both filters. site.js matches on tokens.
    """
    y, m, _d = (int(x) for x in date.split("-"))
    ty, tm, _td = (int(x) for x in today.split("-"))
    if y != ty:
        return ""
    return "year month" if m == tm else "year"


def p_community():
    """Community. Built to the approved mockup, docs/sfw-community-mockup.html.

    An intro, the newest story carried large, then the log: every post the
    Foundation has published about its own community, newest first, ruled off
    by month and filtered by period and by kind. Then the form for sending a
    story in, the directory, and the join band.

    The mockup rendered the log from an array in a <script> tag. It is written
    out as static HTML here instead: a WordPress developer inherits a list of
    <article> elements with dates on them, not a template in JavaScript, and
    the page reads the same with JavaScript switched off. The only script this
    page needs is the filter that site.js already carries for every other index.
    """
    c = load("community"); o = []
    today = c["_today"]
    h = c["hero"]

    o.append(sec('      <h1 id="com-h">%s</h1>\n'
                 '      <p class="lede">%s</p>\n'
                 '      <p class="source small">%s</p>'
                 % (e(h["h1"]), e(h["intro"]), e(h["source"])),
                 label="com-h"))

    posts = sorted(c["posts"], key=lambda p: p["date"], reverse=True)

    # The newest story that has a photograph to carry, which is what the mockup
    # puts in the feature block. No photograph, no feature: the block is a
    # picture and a panel, and half of it empty is worse than not having it.
    lead = next((p for p in posts if p.get("imgs")), None)
    if lead:
        lt = c["latest"]
        d = lead["date"].split("-")
        when = "%d %s %s" % (int(d[2]), MONTHS[int(d[1]) - 1], d[0])
        # The date is the <time>; the place is not, so it sits outside it.
        panel = ('        <p class="latest__when"><time datetime="%s">%s</time>, %s</p>\n'
                 '        <h2 id="latest-h">%s</h2>\n        <p>%s</p>\n'
                 % (A(lead["date"]), e(when), e(lead["place"]), e(lead["title"]), e(lead["body"])))
        if lead.get("people"):
            panel += '        <p class="latest__people">%s</p>\n' % e(lead["people"])
        panel += ('        <p class="latest__row">'
                  '<a class="btn btn--ghost" href="%s">%s</a>'
                  ' <a class="btn btn--ghost" href="#news">%s</a></p>\n'
                  % (A(lead.get("href", "#" + lead["id"])), e(lt["readMore"]), e(lt["allNews"])))
        o.append(sec('      <div class="latest">\n'
                     '        <figure class="latest__img">%s</figure>\n'
                     '        <div class="latest__panel">\n%s        </div>\n      </div>'
                     % (optional_img(lead["imgs"][0]["src"], lead["imgs"][0]["alt"],
                                     sizes="(max-width: 52em) 100vw, 58vw"), panel),
                     label="latest-h"))

    # ---- the log ---------------------------------------------------------
    g = c["log"]
    kn = g["kindNames"]

    def chips(items, target, aria, attr=None):
        li = "".join('<li><button class="chip" type="button" data-filter="%s" aria-pressed="%s">%s</button></li>'
                     % (A(x["key"]), "true" if i == 0 else "false", e(x["label"]))
                     for i, x in enumerate(items))
        # No "N shown" counter here: the list carries month rules as well as
        # posts, so a count off it would say twenty when ten posts are on the
        # page. The empty state below says the one thing worth saying.
        return ('        <ul class="chips" data-filter-for="%s" aria-label="%s"%s>%s</ul>\n'
                % (A(target), A(aria), ' data-filter-attr="%s"' % A(attr) if attr else "", li))

    feed = '      <ul class="feed" id="community-feed">\n'
    seen = ""
    for p in posts:
        d = p["date"].split("-")
        y, mi = d[0], int(d[1]) - 1
        month = "%s %s" % (MONTHS[mi], y)
        when = _when(p["date"], today)
        if month != seen:
            # The rule takes the attributes of the posts under it so the filter
            # hides it with them. See the note in site.css section 14.
            same = [q for q in posts if q["date"][:7] == p["date"][:7]]
            kinds = " ".join(sorted({q["kind"] for q in same}))
            whens = " ".join(sorted({t for q in same for t in _when(q["date"], today).split()}))
            feed += ('        <li class="feed__month" data-kind="%s" data-when="%s">%s</li>\n'
                     % (A(kinds), A(whens), e(month)))
            seen = month

        if p.get("monthOnly"):
            date_block = '<span class="post__m">%s</span>' % e(month)
        else:
            date_block = ('<span class="post__d">%s</span><span class="post__m">%s %s</span>'
                          % (e(str(int(d[2]))), e(MON3[mi]), e(y)))

        art = ('        <li class="post" id="%s" data-kind="%s" data-when="%s">\n'
               '          <p class="post__date"><time datetime="%s">%s</time></p>\n'
               '          <div>\n'
               % (A(p["id"]), A(p["kind"]), A(when), A(p["date"]), date_block))
        art += '            <p class="post__place">%s</p>\n' % e(p["place"])
        art += '            <h3 class="post__t">%s</h3>\n' % e(p["title"])

        if p.get("imgs"):
            two = " post__pics--two" if len(p["imgs"]) > 1 else ""
            art += '            <ul class="post__pics%s">\n' % two
            for i in p["imgs"]:
                art += ('              <li><figure>%s</figure></li>\n'
                        % optional_img(i["src"], i["alt"],
                                       sizes="(max-width: 36em) 100vw, 30vw"))
            art += "            </ul>\n"

        art += '            <p>%s</p>\n' % e(p["body"])
        if p.get("people"):
            art += '            <p class="post__people">%s</p>\n' % e(p["people"])
        if p.get("note"):
            art += "            " + note({"note": p["note"], "status": p.get("noteStatus", "")}) + "\n"

        acts = '<span class="post__kind">%s</span>' % e(kn.get(p["kind"], p["kind"]))
        if p.get("link") and p.get("href"):
            ext = ' target="_blank" rel="noopener"' if p["href"].startswith("http") else ""
            acts += ' <a href="%s"%s>%s</a>' % (A(p["href"]), ext, e(p["link"]))
        if p.get("src"):
            acts += ' <a href="%s" target="_blank" rel="noopener">Source</a>' % A(p["src"])
        art += '            <p class="post__acts">%s</p>\n' % acts
        art += "          </div>\n        </li>\n"
        feed += art

    feed += ('        <li class="feed__empty" data-filter-empty hidden>%s '
             '<a href="#share">%s</a>.</li>\n'
             % (e(g["emptyLead"]), e(g["emptyLink"])))
    feed += "      </ul>\n"

    cu = c["comingUp"]
    coming = '        <div class="sidecard">\n          <h3>%s</h3>\n          <ul class="sidelist">\n' % e(cu["h3"])
    for x in cu["items"]:
        coming += ('            <li><span class="sidelist__when">%s</span>'
                   '<a href="%s">%s</a></li>\n' % (e(x["when"]), A(x["href"]), e(x["label"])))
    coming += "          </ul>\n        </div>\n"

    rg = c["regions"]
    # One row per region the Foundation has actually posted from, with the date
    # of its most recent post. Nothing is claimed that is not on this page.
    latest_by_region = {}
    for p in posts:
        r = p.get("region")
        if r and p["date"] > latest_by_region.get(r, ""):
            latest_by_region[r] = p["date"]
    rows = ""
    for r, dt in sorted(latest_by_region.items(), key=lambda kv: kv[1], reverse=True):
        d = dt.split("-")
        rows += ('            <li><span>%s</span><span>Latest %s %s</span></li>\n'
                 % (e(r), e(MON3[int(d[1]) - 1]), e(d[0])))
    # The overlay menu on every page links to community.html#community-map.
    # The mockup replaced the map with this list of regions, so the anchor
    # lands here, on the regions and the note saying the map is still to come.
    regions = ('        <div class="sidecard" id="community-map" style="scroll-margin-top:var(--s4)">\n          <h3>%s</h3>\n'
               '          <ul class="sidelist sidelist--split">\n%s          </ul>\n'
               '          %s\n        </div>\n'
               % (e(rg["h3"]), rows, note({"note": rg["note"], "status": rg["noteStatus"]})))

    o.append(sec('      <div class="grid">\n        <div class="span-8">\n'
                 '          <h2 id="news-h" style="margin-bottom:var(--s3)">%s</h2>\n'
                 '%s          <p class="small">%s</p>\n%s        </div>\n'
                 '        <div class="span-4">\n%s%s        </div>\n      </div>'
                 % (e(g["h2"]),
                    chips(g["time"], "#community-feed", g["timeLabel"], "data-when")
                    + chips(g["kinds"], "#community-feed", g["kindLabel"]),
                    e(g["sourceLine"]), feed, coming, regions),
                 label="news-h", sid="news"))

    # ---- send us a story -------------------------------------------------
    s = c["share"]
    fields = ""
    for i, f in enumerate(s["fields"]):
        fid = "share-" + slug(f["label"])
        full = " full" if f.get("full") else ""
        if f["type"] == "drop":
            # One wrapping label, so the field is named by its own words and the
            # whole dashed box is the target that opens the file picker.
            fields += ('        <label class="full" for="%s">%s\n'
                       '          <span class="drop">%s</span>\n'
                       '          <input class="visually-hidden" id="%s" type="file" name="%s" multiple accept="image/*,video/*">\n'
                       '        </label>\n'
                       % (A(fid), e(f["label"]), e(f["placeholder"]), A(fid), A(fid)))
        elif f["type"] == "textarea":
            fields += ('        <label class="%s" for="%s">%s\n'
                       '          <textarea class="input" id="%s" name="%s" placeholder="%s"></textarea>\n        </label>\n'
                       % (full.strip(), A(fid), e(f["label"]), A(fid), A(fid), A(f.get("placeholder", ""))))
        else:
            ph = ' placeholder="%s"' % A(f["placeholder"]) if f.get("placeholder") else ""
            fields += ('        <label%s for="%s">%s\n'
                       '          <input class="input" id="%s" type="%s" name="%s"%s>\n        </label>\n'
                       % (' class="full"' if f.get("full") else "", A(fid), e(f["label"]),
                          A(fid), A(f["type"]), A(fid), ph))

    o.append(sec('      <div class="grid">\n        <div class="span-5">\n'
                 '          <h2 id="share-h">%s</h2>\n          <p>%s</p>\n'
                 '          <p class="small">%s</p>\n          %s\n        </div>\n'
                 '        <form class="span-7" action="#" method="post">\n'
                 '          <fieldset style="border:0;padding:0;margin:0;min-width:0">\n'
                 '            <legend class="visually-hidden">%s</legend>\n'
                 '            <div class="form-grid">\n%s'
                 '        <p class="full"><button class="btn" type="submit">%s</button></p>\n'
                 '            </div>\n          </fieldset>\n        </form>\n      </div>'
                 % (e(s["h2"]), e(s["body"]), e(s["fine"]),
                    note({"note": s["note"], "status": s["noteStatus"]}),
                    e(s["legend"]), fields, e(s["cta"])),
                 label="share-h", sid="share"))

    # ---- the directory ---------------------------------------------------
    w = c["work"]
    o.append(sec('      <div class="panel">\n        <div class="grid">\n'
                 '          <div class="span-8">\n            <h2 id="work-h">%s</h2>\n            <p>%s</p>\n'
                 '            %s\n          </div>\n'
                 '          <p class="span-4" style="align-self:center">%s</p>\n'
                 '        </div>\n      </div>'
                 % (e(w["h2"]), e(w["body"]),
                    note({"note": w["note"], "status": w["noteStatus"]}), cta(w["cta"])),
                 label="work-h", sid="find-a-professional"))

    j = c["joinBand"]
    o.append(sec('      <h2 id="cj-h">%s</h2>\n      <p class="lede" style="color:var(--paper)">%s</p>\n'
                 '      <p style="display:flex;flex-wrap:wrap;gap:var(--s2);margin-top:var(--s4)">%s</p>'
                 % (e(j["h2"]), e(j["body"]),
                    " ".join(cta(x, "btn" if i == 0 else "btn btn--ghost") for i, x in enumerate(j["ctas"]))),
                 "stratum--moss", "cj-h", "join"))
    return MAIN("\n".join(o))


def p_calendar():
    c = load("calendar"); o = [hero(c["hero"], "cal-h", photo=(
        "img/ctpfw-student-moving-compost-1.jpg",
        "A student lifting an armful of finished compost at a workshop while a group looks on"))]
    f = c["featured"]
    iw = c["indiaWorkshop"]
    rows = ('        <li class="cal__row">\n          <div class="cal__rail">\n'
            '            <svg class="icon icon--olive" aria-hidden="true"><use href="#i-scholarship"/></svg>\n'
            '            <span><span class="cal__name">Permaculture Design Certification</span>'
            '<span class="cal__when">16 September to 20 December 2026</span></span>\n          </div>\n'
            '          <div class="cal__track"><a class="cal__bar" href="learn#permaculture"'
            ' aria-label="Permaculture Design Certification, 16 September to 20 December 2026"'
            ' style="--l:4.11%;--w:26.301%"></a></div>\n        </li>\n'
            '        <li class="cal__row">\n          <div class="cal__rail">\n'
            '            <svg class="icon icon--olive" aria-hidden="true"><use href="#i-workshop"/></svg>\n'
            '            <span><span class="cal__name">' + e(iw["title"]) + '</span>'
            '<span class="cal__when">' + e(iw["dated"]) + '</span></span>\n          </div>\n'
            '          <div class="cal__track"><a class="cal__bar" href="#workshops"'
            ' aria-label="' + A(iw["title"]) + ', ' + A(iw["dated"]) + '"'
            ' style="--l:13.151%;--w:3.288%"></a></div>\n        </li>\n'
            '        <li class="cal__row">\n          <div class="cal__rail">\n'
            '            <svg class="icon icon--olive" aria-hidden="true"><use href="#i-calendar"/></svg>\n'
            '            <span><span class="cal__name">The rest of 2027</span><span class="cal__when">Not yet scheduled</span></span>\n'
            '          </div>\n          <div class="cal__track">'
            '<span class="cal__bar cal__bar--todo" style="--l:33.425%;--w:66.575%"><span>dates not set</span></span></div>\n        </li>\n')
    months = ""
    grid = ""
    import calendar as _c
    y, mo = 2026, 9
    for _ in range(12):
        w = round(_c.monthrange(y, mo)[1] / 365 * 100, 3)
        months += '<li style="flex:0 0 %s%%">%s <span style="color:var(--ink-faint)">%s</span></li>' % (w, _c.month_abbr[mo], str(y)[2:])
        grid += '<span style="flex:0 0 %s%%"></span>' % w
        mo += 1
        if mo > 12:
            mo = 1; y += 1
    o.append(sec('      <h2 id="cal-h2" class="visually-hidden">Events</h2>\n'
                 + tabs(c["filterTabs"], "#cal-list", "Event type")
                 + '      <div class="cal-wrap" role="region" aria-label="Year calendar" tabindex="0">\n'
                   '        <div class="cal" data-cal data-cal-start="2026-09-01" data-cal-end="2027-08-31">\n'
                   '          <div class="cal__grid" aria-hidden="true">%s<span class="cal__today" data-cal-today hidden></span></div>\n'
                   '          <ol class="cal__months" aria-hidden="true">%s</ol>\n'
                   '          <ol class="cal__rows">\n%s          </ol>\n        </div>\n      </div>\n'
                   '      <p class="small">Bars are placed by their real dates across September 2026 to August 2027. '
                   'A solid bar is a confirmed run, the dashed band is time that is not scheduled yet, and the green line marks today.</p>\n'
                   '      <ul class="rule-list" id="cal-list">\n'
                   '        <li class="entry" data-kind="workshops" id="workshops">\n'
                   '          <span class="dated"><time datetime="%s">%s</time></span>\n'
                   '          <div><h3 class="entry__t">%s</h3><p class="entry__line">%s</p>\n          <p class="entry__line">%s</p></div>\n'
                   '          <span class="entry__kind">Workshop</span>\n        </li>\n'
                   '        <li class="entry" data-kind="public-webinars">\n'
                   '          <span class="dated">Monthly</span>\n'
                   '          <div><h3 class="entry__t"><a href="learn-webinars">Free educational webinar</a></h3></div>\n'
                   '          <span class="entry__kind">Public webinar</span>\n        </li>\n      </ul>\n      %s\n'
                   '      <p class="small">%s</p>'
                   % (grid, months, rows, A(iw["datetime"]), e(iw["dated"]),
                      e(f["title"]), e(f["body"]),
                      cta(f["cta"], "btn btn--ghost") + " "
                      + " &middot; ".join('<a href="%s">%s</a>' % (A(x["href"]), e(x["label"]))
                                          for x in c["links"]),
                      '<p class="source small">%s</p>' % e(f["source"])
                      + note(f) + note(c["otherListings"]), e(c["footerLine"])), label="cal-h"))
    return MAIN("\n".join(o))


def p_news():
    c = load("news"); o = [hero(c["hero"], "news-h", photo=(
        "img/Carla-Nicks Son-Nick-ERI-Wild Soils Event-11-2024.jpg",
        "A group of people laughing as they work together outdoors with brushes and rakes"))]
    posts = [("14 Aug 2026", "2026-08-14", "Learning to see: what is your soil test really telling you?", "blog", ""),
             ("14 Jul 2026", "2026-07-14", "A brief history of the fungi-to-bacteria ratio", "blog", "Wes Sander"),
             ("1 May 2026", "2026-05-01", "Ciliates, cysts and the clues in a struggling watermelon crop", "blog", "Wes Sander"),
             ("13 Apr 2026", "2026-04-13", "The School launches its first Permaculture Design Certificate course", "foundation-news", ""),
             ("23 Feb 2026", "2026-02-23", "Advanced Programs are reopening", "foundation-news", "Evan Buckman"),
             ("18 Feb 2026", "2026-02-18", "Obituary for Dr. Elaine Ingham", "foundation-news", "")]
    rows = "".join('        <li class="entry" data-kind="%s">\n          <span class="dated"><time datetime="%s">%s</time></span>\n'
                   '          <div><h3 class="entry__t">%s</h3></div>\n          <span class="entry__kind">%s</span>\n        </li>\n'
                   % (k, dt, d, e(t), e(a or k.replace("-", " ").title())) for d, dt, t, k, a in posts)
    o.append(sec('      <h2 id="news-list-h" class="visually-hidden">All posts</h2>\n'
                 + tabs(c["filterTabs"], "#news-list", "Category")
                 + '      <ul class="rule-list" id="news-list">\n%s      </ul>\n'
                   '      <p class="todo">the six posts above carry no link until the blog is migrated to /news/[slug], '
                   'and all earlier posts still need pulling from the archive. Run crawl.py locally, keep every date and author. Linnea.</p>\n'
                   '      <p class="small">%s</p>' % (rows, e(c["featuredSlotRule"])), label="news-h", sid="foundation"))
    nl = c["newsletter"]
    o.append(sec('      <h2 id="nl-h">%s</h2>\n      <p>%s</p>\n'
                 '      <form action="#" method="post" aria-label="Newsletter" style="display:flex;gap:var(--s1);max-width:26rem">\n'
                 '        <label for="news-email" class="visually-hidden">Email address</label>\n'
                 '        <input class="input" id="news-email" type="email" placeholder="Email for the newsletter" required>\n'
                 '        <button class="btn" type="submit">%s</button>\n      </form>\n'
                 '      <p class="todo">form action: which service receives the email field (Ontraport?). DECISION 14. Evan.</p>'
                 % (e(nl["title"]), e(nl["body"]), e(nl["cta"])), "stratum--deep", "nl-h", "subscribe"))
    return MAIN("\n".join(o))


def p_research():
    c = load("research"); o = []
    o.append(hero({"eyebrow": "RESEARCH", "h1": "The research behind living soil",
                   "intro": "A growing database of soil food web science: Dr. Elaine Ingham's publications, research from the wider field, and, as our open-research program matures, studies from the Foundation and its partners."},
                  "res-h", photo=("img/soil-sample-shovel-and-bag.jpg",
                                  "Gloved hands easing a trowel of red soil into a sample bag")))

    # Sections, order and entry numbering come from the Foundation's own
    # publications document: her papers, then book chapters, then the two kinds
    # of technical report, then the wider literature and the internet articles.
    # Oldest first inside each section, as the document has it, and the numbers
    # are stable so an entry can be cited by one.
    d = c["database"]

    def entry(x):
        title = e(x["title"])
        if x.get("url"):
            # The arrow must not be able to fall to a line of its own under the
            # title, so the last word and the arrow travel together.
            head, _, last = title.rpartition(" ")
            mark = ('<span style="white-space:nowrap">%s<svg class="icon" aria-hidden="true">'
                    '<use href="#i-external"/></svg></span>' % last)
            title = '<a href="%s">%s</a>' % (A(x["url"]), (head + " " + mark) if head else mark)
        line = " · ".join(e(x[k]) for k in ("authors", "citation") if x.get(k))
        return ('        <li class="entry" id="p%d-%d">\n'
                '          <span class="dated"><span class="entry__n">%d</span>'
                '<time datetime="%d">%d</time></span>\n'
                '          <div><h3 class="entry__t">%s</h3>%s</div>\n'
                '          <span class="entry__kind">%s</span>\n        </li>\n'
                % (x["_sec"], x["n"], x["n"], x["year"], x["year"], title,
                   ('<p class="entry__line">%s</p>' % line) if line else "", e(x["type"])))

    body = ('      <h2 id="res-list-h">%s</h2>\n      <p class="lede">%s</p>\n'
            '      <p><a class="btn" href="%s">%s</a></p>\n'
            % (e(d["h2"]),
               e(d["lede"]).replace("info@soilfoodweb.com",
                                    '<a href="%s">info@soilfoodweb.com</a>' % A(d["ledeMailto"])),
               A(d["scholar"]["href"]), e(d["scholar"]["label"])))

    # A contents list rather than filter chips: the sections are the structure
    # now, and filtering a numbered bibliography leaves holes in the numbering.
    body += ('      <ul class="chips" aria-label="Sections">%s</ul>\n'
             % "".join('<li><a class="chip" href="#sec-%s">%s (%d)</a></li>'
                       % (A(x["slug"]), e(x["name"]), len(x["entries"])) for x in d["sections"]))
    body += "".join('      <p class="todo">%s</p>\n' % e(n) for n in d["notes"])

    for i, sec in enumerate(d["sections"], 1):
        for x in sec["entries"]:
            x["_sec"] = i
        body += ('      <h3 id="sec-%s">%s</h3>\n      <ul class="rule-list">\n%s      </ul>\n'
                 % (A(sec["slug"]), e(sec["name"]),
                    "".join(entry(x) for x in sec["entries"])))
        if sec["slug"] == "reports":
            n = d["columnNote"]
            body += ('      <h3>%s</h3>\n      <p>%s</p>\n      <p>%s</p>\n'
                     % (e(n["h3"]), e(n["body"]), e(n["after"])))

    o.append(sec_(body, label="res-list-h"))
    w = c["workWithUs"]
    o.append(sec_('      <h2 id="rw-h">%s</h2>\n      <p class="lede">%s</p>\n      <p>%s</p>'
                  % (e(w["h2"]), e(w["body"]), cta(w["cta"])), "stratum--deep", "rw-h", "work-with-us"))
    return MAIN("\n".join(o))


def p_login():
    c = load("login"); o = [hero(c["hero"], "log-h")]
    items = []
    for ch in c["choosers"]:
        nm = ch["name"]["note"] if isinstance(ch["name"], dict) else ch["name"]
        pg = ch["programs"]["note"] if isinstance(ch["programs"], dict) else ch["programs"]
        items.append({"title": nm, "body": pg, "cta": ch["cta"] if ch["cta"]["href"] != "#" else None})
    o.append(sec('      <h2 id="lms-h" class="visually-hidden">Choose your platform</h2>\n'
                 + cards(items) + '      <p>%s</p>\n      <p class="source small">%s</p>'
                 % (e(c["helpLine"]), e(c["source"])), "stratum--deep", "lms-h"))
    return MAIN("\n".join(o))


def p_donate():
    c = load("donate"); o = [hero(c["hero"], "don-h", photo=(
        "img/2-hands-planting-shrub.jpg",
        "Two hands firming red soil around the base of a newly planted shrub"))]
    g = c["makeGift"]
    o.append(sec('      <div class="grid">\n        <div class="span-6">\n          <h2 id="gift-h">Make a gift</h2>\n'
                 '          <form action="#" method="post" aria-label="Donate">\n'
                 '            <p role="group" aria-label="Frequency">%s</p>\n'
                 '            <p role="group" aria-label="Amount">%s</p>\n'
                 '            <p><button class="btn btn--donate" type="submit">%s</button></p>\n          </form>\n'
                 '          <p class="small">%s</p>\n          %s\n        </div>\n'
                 '        <div class="span-5 start-8">\n          <h2>%s</h2>\n          %s\n'
                 '          <p>%s <a href="%s">%s</a></p>\n        </div>\n      </div>'
                 % (" ".join('<button class="chip" type="button" aria-pressed="%s">%s</button>' % ("true" if i == 0 else "false", e(x)) for i, x in enumerate(g["frequencies"])),
                    " ".join('<button class="chip" type="button" aria-pressed="%s">%s</button>' % ("true" if i == 1 else "false", e(x)) for i, x in enumerate(g["amounts"])),
                    e(g["cta"]), e(g["finePrint"]), note(c["impactLines"]),
                    e(c["whyMonthly"]["h2"]), note(c["whyMonthly"]),
                    e(c["otherGiving"]["body"]), A(c["otherGiving"]["link"]["href"]), e(c["otherGiving"]["link"]["label"])),
                 label="gift-h"))
    # Volunteering has its own page now, so this is a signpost rather than a
    # second form. Two forms for one thing is how a nonprofit ends up with two
    # inboxes and half the replies going to neither.
    v = c["volunteer"]
    o.append(sec('      <div class="head">\n        %s\n        <h2 id="vol-h">%s</h2>\n        <p>%s</p>\n      </div>\n'
                 '      <p><a class="btn" href="%s">%s</a></p>\n      %s'
                 % (eyebrow(v["eyebrow"]), e(v["h2"]), e(v["lede"]),
                    A(v["link"]["href"]), e(v["link"]["label"]), note(v)),
                 "stratum--deep", "vol-h", "volunteer"))
    return MAIN("\n".join(o))


def p_scholarships():
    c = load("scholarships"); o = [hero(c["hero"], "sch-h", photo=(
        "img/ctpfw-student-squeezing-compost-1.jpg",
        "A student in gloves squeezing a handful of compost to test it, with a group watching"))]
    st = c["stories"]
    o.append(sec('      <div class="head"><h2 id="st-h">%s</h2></div>\n%s      %s'
                 % (e(st["h2"]), awaiting(st), note(st)), "stratum--deep", "st-h"))
    ap = c["apply"]
    o.append(sec('      <div class="head"><h2 id="ap-h">%s</h2></div>\n%s'
                 '      <p style="margin-top:var(--s5)">%s</p>'
                 % (e(ap["h2"]), steps(ap["steps"], "i-scholarship"), cta(ap["cta"])), label="ap-h"))
    d = c["donorPanel"]
    o.append(sec('      <h2 id="dp-h">%s</h2>\n      <p class="lede">%s</p>\n      <p>%s</p>'
                 % (e(d["title"]), e(d["body"]), cta(d["cta"], "btn btn--donate")), "stratum--deep", "dp-h"))
    return MAIN("\n".join(o))


def p_webinars():
    c = load("webinars"); o = [hero(c["hero"], "web-h", photo=(
        "img/Test tubes with sample_.jpg",
        "Sample tubes racked in front of a microscope, shallow focus"))]
    fa = c["facts"]
    o.append(sec('      <div class="head">\n        <h2 id="fa-h">%s</h2>\n        <p>%s</p>\n      </div>\n%s'
                 '      <p class="source small">%s</p>'
                 % (e(fa["h2"]), e(fa["lede"]), facts(fa["rows"]), e(fa["source"])), label="fa-h"))

    ns = c["nextSession"]
    o.append(sec('      <div class="head"><h2 id="ns-h">Next session</h2></div>\n%s      %s\n'
                 '      <p><a class="btn" href="https://webinar.soilfoodweb.com">%s</a></p>'
                 % (awaiting(ns), note(ns), e(ns["cta"])), "stratum--deep", "ns-h"))
    se = c["series"]
    o.append(sec('      <div class="head">\n        <h2 id="se-h">%s</h2>\n        <p>%s</p>\n      </div>\n%s      %s'
                 % (e(se["h2"]), e(se["lede"]),
                    cards([{"title": x["title"], "body": x["body"]} for x in se["items"]]), note(se)),
                 label="se-h"))

    r = c["recordings"]
    o.append(sec('      <div class="head"><h2 id="rec-h">%s</h2></div>\n%s      %s\n'
                 '      <p>%s <a href="%s">our community space</a></p>'
                 % (e(r["h2"]), awaiting(r), note({"note": r["note"], "status": "placeholder"}),
                    e(r["backlogLine"]), A(r["backlogHref"])), label="rec-h"))
    # Free resources: each one is a way somewhere else on the site, so each one
    # is a link that says where it goes.
    res = c["resources"]
    o.append(sec('      <div class="head">\n        <h2 id="fr-h">%s</h2>\n        <p>%s</p>\n      </div>\n%s'
                 % (e(res["h2"]), e(res["lede"]),
                    cards([{"title": x["title"], "body": x["body"],
                            "cta": {"label": x["cta"], "href": x["href"]},
                            "note": x.get("note"), "status": x.get("status")}
                           for x in res["items"]])),
                 "stratum--deep", "fr-h"))

    nx = c["next"]
    o.append(sec('      <div class="head">\n        <h2 id="nx-h">%s</h2>\n        <p>%s</p>\n      </div>\n%s'
                 % (e(nx["h2"]), e(nx["lede"]), cards(nx["cards"])), label="nx-h"))
    return MAIN("\n".join(o))


# (file, <title>, content key, renderer, og:image). The share image is the
# page's own hero photograph: a link to the Learn page should not unfurl with
# the homepage's picture.
PAGES = [
    # path, <title>, content file, builder, the image a shared link shows,
    # and the page's accent family. The accent is one colour per section:
    # education blue on the Learn pages, the microscopy violet on Science,
    # oxidised rust on Practice. Everything else keeps Food Web Green.
    ("index.html", "Soil Food Web Foundation, a nonprofit teaching the science of living soil", "home", p_home,
     "img/hand-soil-roots-fungi.jpg"),
    ("about.html", "About the Foundation, Soil Food Web Foundation", "about", p_about,
     "img/Dr Elaine Ingham with Microscope.jpg"),
    ("learn.html", "Learn with us, Soil Food Web Foundation", "learn", p_learn,
     "img/ctpfw-student-squeezing-compost-1.jpg", "t-learn"),
    ("science.html", "How the soil food web works, Soil Food Web Foundation", "science", p_science,
     "img/fungal-spores-in-suspension.jpg", "t-science"),
    ("practice.html", "Practice, Soil Food Web Foundation", "practice", p_practice,
     "img/red-soil-hand.jpg", "t-practice"),
    ("news.html", "News and stories, Soil Food Web Foundation", "news", p_news,
     "img/Carla-Nicks Son-Nick-ERI-Wild Soils Event-11-2024.jpg"),
    ("research.html", "Research, Soil Food Web Foundation", "research", p_research,
     "img/Test tubes with sample_.jpg", "t-science"),
    ("login.html", "Student access, Soil Food Web Foundation", "login", p_login,
     "img/hand-soil-roots-fungi.jpg", "t-learn"),
    ("donate.html", "Donate and get involved, Soil Food Web Foundation", "donate", p_donate,
     "img/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg"),
    ("learn-scholarships.html", "Scholarships, Soil Food Web Foundation", "scholarships", p_scholarships,
     "img/hvdb-inplanten-002.jpg", "t-learn"),
]

# Pages written by hand rather than rendered from content/. They carry the same
# header and footer, so the chrome is re-stamped into them here: without this the
# nav drifts out of step with the generated pages every time a label changes.
# calendar, community and learn-webinars were rendered from content/ until
# their pages were edited by hand and the builders were not kept up. Running
# build.py rebuilt them from the stale templates and silently deleted the
# newer work: 25, 34 and 46 lines of it. p_calendar, p_community and
# p_webinars are still here and still correct as far as they go, so moving a
# page back is a matter of reconciling its builder with the page and putting
# its row back in PAGES.
HAND_WRITTEN = [
    "index.html", "about.html", "learn.html", "science.html", "practice.html",
    "news.html", "research.html", "login.html", "donate.html",
    "learn-scholarships.html",
    "calendar.html", "community.html", "app.html", "learn-webinars.html",
    "about-elaine.html", "about-governance.html", "about-team.html",
    "accessibility.html", "contact.html", "directory.html", "privacy.html",
    "terms.html", "volunteer.html", "projects/market-garden-sweden.html",
    "news/wild-ken-hill-2026.html",
]

HDR_RE = re.compile(
    r"<!-- =+ UTILITY BAR \+ HEADER \(every page\) =+ -->.*?(?=<main id=\"main\">)", re.S)
FTR_RE = re.compile(
    r"<!-- =+ FOOTER \(every page\) =+ -->.*?</footer>\n", re.S)


SHARE_RE = re.compile(r'<img[^>]+src="((?:\.\./)*img/[^"]+)"')
OG_RE = re.compile(r'\n?  <meta (?:property="og:|name="twitter:)[^>]*>', re.S)


def clean(path):
    """The URL a page is served at, which is not its filename: vercel.json sets
    cleanUrls, so index.html is / and terms.html is /terms. og:url has to match
    the canonical tag, or a shared link unfurls to a URL the site does not serve.
    """
    p = path[:-len(".html")] if path.endswith(".html") else path
    return "" if p == "index" else p


def restamp_head(path, doc):
    """Give a hand-written page the same share tags the generated ones get."""
    title = re.search(r"<title>(.*?)</title>", doc, re.S).group(1).strip()
    d = re.search(r'<meta name="description" content="([^"]*)"', doc)
    desc = d.group(1) if d else title
    # A page may name its own share image with <!-- share: img/x.jpg -->.
    # Without that the first photograph in the document is used, which is
    # right until the first thing in the document is a decorative cut-out
    # in a margin, and then the page unfurls as a piece of moss.
    # Not [^\s>]: several photographs in img/ have spaces in their filenames,
    # and stopping at the first space silently picked a path that does not
    # exist, so the page fell back to the logo.
    pick = re.search(r"<!--\s*share:\s*(.+?)\s*-->", doc)
    m = SHARE_RE.search(doc)
    if pick:
        rel = pick.group(1)
    else:
        rel = re.sub(r"^(\.\./)+", "", m.group(1)) if m else "img/hand-soil-roots-fungi.jpg"
    img_abs = SITE + "/" + web(rel)
    tags = ('\n  <meta property="og:type" content="website">'
            '\n  <meta property="og:title" content="%s">'
            '\n  <meta property="og:description" content="%s">'
            '\n  <meta property="og:url" content="%s">'
            '\n  <meta property="og:image" content="%s">'
            '\n  <meta name="twitter:card" content="summary_large_image">'
            '\n  <meta name="twitter:title" content="%s">'
            '\n  <meta name="twitter:description" content="%s">'
            '\n  <meta name="twitter:image" content="%s">'
            % (A(title), A(desc), A(SITE + "/" + clean(path)), A(img_abs),
               A(title), A(desc), A(img_abs)))
    doc = OG_RE.sub("", doc)
    anchor = '  <meta property="og:site_name" content="Soil Food Web Foundation">'
    if anchor not in doc:
        doc = doc.replace("</title>", "</title>\n" + anchor, 1)
    return doc.replace(anchor, anchor + tags, 1)


def restamp(path):
    """Replace the header and footer blocks of a hand-written page in place."""
    full = os.path.join(ROOT, path)
    with open(full, encoding="utf-8") as fh:
        doc = fh.read()
    depth = path.count("/")
    hdr, ftr = chrome(depth)
    doc, nh = HDR_RE.subn(lambda m: hdr, doc, count=1)
    doc, nf = FTR_RE.subn(lambda m: ftr.rstrip("\n") + "\n", doc, count=1)
    if not (nh and nf):
        raise SystemExit("chrome markers missing in " + path)
    doc = restamp_head(path, doc)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print("  re-stamped", path)


if __name__ == "__main__":
    for path in HAND_WRITTEN:
        restamp(path)
    print("done:", len(HAND_WRITTEN), "re-stamped")
