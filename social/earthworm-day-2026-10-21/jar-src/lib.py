"""Watercolour-on-white drawing kit (SVG filters rendered in Chromium). No AI images."""
import math, os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_FONTS = '/home/user/final-sfwsite-linnea/fonts'

INK = '#4F3433'      # Soil Brown: titles, outlines, arrows
BODY = '#5b4c46'     # body text
C = dict(soil='#7a5240', soil2='#5e3e30', dark='#4F3433', sand='#d8b98a', tan='#C89B7B',
         grass='#59A66C', green='#156826', grey='#a9a39c', stone='#8d8781', sky='#8db7d6',
         blue='#3780B8', leaf='#d98a3c', leaf2='#c25b33', yellow='#e8c25a', pink='#e9a6a0',
         purple='#6B4C7A', cream='#F4F1EA', white='#ffffff', bin='#6f8f9e', wood='#b07a4f')

def defs(n=12):
    out = []
    for s in range(1, n + 1):
        out.append(f'''
<filter id="wc{s}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="3" seed="{s}" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="17" xChannelSelector="R" yChannelSelector="G" result="shape"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="4" seed="{s+40}" result="n2"/>
 <feColorMatrix in="n2" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  2.6 0 0 0 -0.9" result="mottle"/>
 <feComposite in="shape" in2="mottle" operator="in" result="pig"/>
 <feComponentTransfer in="pig" result="pig2"><feFuncA type="linear" slope="0.5"/></feComponentTransfer>
 <feComponentTransfer in="shape" result="base"><feFuncA type="linear" slope="0.42"/></feComponentTransfer>
 <feMorphology in="shape" operator="erode" radius="2.2" result="er"/>
 <feComposite in="shape" in2="er" operator="out" result="edge"/>
 <feGaussianBlur in="edge" stdDeviation="0.7" result="edgeb"/>
 <feComponentTransfer in="edgeb" result="edge2"><feFuncA type="linear" slope="0.55"/></feComponentTransfer>
 <feMerge result="m"><feMergeNode in="base"/><feMergeNode in="pig2"/><feMergeNode in="edge2"/></feMerge>
 <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="2" seed="{s+7}" result="g"/>
 <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1.4 0 0 0 0.35" result="gm"/>
 <feComposite in="m" in2="gm" operator="in"/>
</filter>''')
    out.append('''
<filter id="pen" x="-10%" y="-10%" width="120%" height="120%">
 <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="3" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="3.5" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
 <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="9" result="n"/>
 <feDisplacementMap in="SourceGraphic" in2="n" scale="8" xChannelSelector="R" yChannelSelector="G" result="d"/>
 <feGaussianBlur in="d" stdDeviation="1.2"/>
</filter>''')
    return '<defs>' + ''.join(out) + '</defs>'

def wash(d, color, seed=1, op=1.0, tag='path', extra=''):
    """A watercolour wash. d is a path 'd' (tag=path) or raw attributes for other tags."""
    shape = f'<path d="{d}" fill="{color}"/>' if tag == 'path' else f'<{tag} {d} fill="{color}"/>'
    return f'<g filter="url(#wc{seed})" opacity="{op}" style="mix-blend-mode:multiply" {extra}>{shape}</g>'

def blob(cx, cy, rx, ry, color, seed=1, op=1.0):
    return wash(f'cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"', color, seed, op, tag='ellipse')

def smooth(pts, closed=False):
    """Catmull-Rom through points -> cubic bezier path."""
    p = list(pts)
    if closed:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    d = f'M{p[1][0]:.1f},{p[1][1]:.1f}'
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        c1 = (p1[0] + (p2[0]-p0[0])/6, p1[1] + (p2[1]-p0[1])/6)
        c2 = (p2[0] - (p3[0]-p1[0])/6, p2[1] - (p3[1]-p1[1])/6)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d + (' Z' if closed else '')

def _sample(pts, n=200):
    """Sample the Catmull-Rom curve densely (for segment marks)."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        for k in range(n // (len(pts) - 1)):
            t = k / (n // (len(pts) - 1))
            t2, t3 = t*t, t*t*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    out.append(pts[-1])
    return out

def worm(pts, w=20, fill='#ffffff', band=True, segs=True, line=2.6, ink=INK, band_color=None):
    """Simple white worm with a brown outline, like the worksheet reference."""
    d = smooth(pts)
    g = [f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{w+line*2}" stroke-linecap="round" stroke-linejoin="round"/>',
         f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>']
    s = _sample(pts, 400)
    L = [0.0]
    for a, b in zip(s, s[1:]):
        L.append(L[-1] + math.dist(a, b))
    total = L[-1]
    def at(frac):
        tgt = frac * total
        for i in range(1, len(L)):
            if L[i] >= tgt:
                a, b = s[i-1], s[i]
                return a, (b[0]-a[0], b[1]-a[1])
        a, b = s[-2], s[-1]
        return b, (b[0]-a[0], b[1]-a[1])
    if band:
        bd = []
        for k in range(9):
            (x, y), _ = at(0.24 + k * 0.012)
            bd.append((x, y))
        g.append(f'<path d="{smooth(bd)}" fill="none" stroke="{band_color or C["pink"]}" stroke-width="{w*0.78}" stroke-linecap="round" opacity="0.9"/>')
    if segs:
        step = max(w * 0.75, 11)
        n = int(total / step)
        for k in range(2, n - 1):
            (x, y), (dx, dy) = at(k / n)
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy/ln, dx/ln
            h = w * 0.36
            tx, ty = dx/ln*2.2, dy/ln*2.2
            g.append(f'<path d="M{x+nx*h:.1f},{y+ny*h:.1f} Q{x+tx:.1f},{y+ty:.1f} {x-nx*h:.1f},{y-ny*h:.1f}" fill="none" stroke="{ink}" stroke-width="1.5" opacity="0.55" stroke-linecap="round"/>')
    return f'<g filter="url(#pen)">{"".join(g)}</g>'

def arrow(p0, p1, bend=0.25, ink=INK, sw=2.6, head=14):
    """Thin hand-drawn arrow from p0 to p1 (head at p1)."""
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    cx, cy = mx - dy*bend, my + dx*bend
    ang = math.atan2(p1[1]-cy, p1[0]-cx)
    h1 = (p1[0] - head*math.cos(ang-0.45), p1[1] - head*math.sin(ang-0.45))
    h2 = (p1[0] - head*math.cos(ang+0.45), p1[1] - head*math.sin(ang+0.45))
    return (f'<g filter="url(#pen)" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M{p0[0]},{p0[1]} Q{cx:.1f},{cy:.1f} {p1[0]},{p1[1]}"/>'
            f'<path d="M{h1[0]:.1f},{h1[1]:.1f} L{p1[0]},{p1[1]} L{h2[0]:.1f},{h2[1]:.1f}"/></g>')

def line(d, ink=INK, sw=2.4, op=1, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}" filter="url(#pen)" {extra}/>'

def crumbs(cx, cy, rx, ry, n, color, seed=1, rmin=7, rmax=15, rng=None):
    """Aggregates: little irregular crumbs scattered in an ellipse."""
    import random
    r = rng or random.Random(seed)
    out = []
    for _ in range(n):
        a = r.random() * 2 * math.pi
        rr = math.sqrt(r.random())
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        s = r.uniform(rmin, rmax)
        pts = [(x + math.cos(t) * s * r.uniform(0.7, 1.15), y + math.sin(t) * s * r.uniform(0.6, 1.0)) for t in [k * 2 * math.pi / 6 for k in range(6)]]
        out.append(f'<path d="{smooth(pts, True)}" fill="{color}"/>')
    return out

def page(art, texts, logo=True, logo_box=(870, 1215, 170, None), bg='#ffffff'):
    """art: SVG inner markup; texts: list of dict(x,y,w,size,weight,family,color,align,text,lh)."""
    tx = []
    for t in texts:
        fam = {'title': "'Fredoka'", 'body': "'Montserrat'"}[t.get('family', 'body')]
        tx.append(f'<div class="t" style="left:{t["x"]}px;top:{t["y"]}px;width:{t["w"]}px;'
                  f'font-family:{fam};font-size:{t["size"]}px;font-weight:{t.get("weight",500)};'
                  f'color:{t.get("color",BODY)};text-align:{t.get("align","left")};line-height:{t.get("lh",1.25)};'
                  f'letter-spacing:{t.get("ls",0)}px">{t["text"]}</div>')
    lg = ''
    if logo:
        x, y, w, _ = logo_box
        lg = f'<img src="{HERE}/logo.png" style="position:absolute;left:{x}px;top:{y}px;width:{w}px">'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Fredoka';src:url('{HERE}/fonts/Fredoka.ttf');font-weight:300 700}}
@font-face{{font-family:'Montserrat';src:url('{REPO_FONTS}/montserrat-latin-variable.woff2');font-weight:100 900}}
html,body{{margin:0;padding:0;width:1080px;height:1350px;overflow:hidden;background:{bg}}}
.t{{position:absolute}} .t b{{font-weight:700;color:{INK}}} .t em{{font-style:normal;color:{C["green"]};font-weight:600}}
svg{{position:absolute;left:0;top:0}}
</style></head><body>
<svg width="1080" height="1350" viewBox="0 0 1080 1350" xmlns="http://www.w3.org/2000/svg">{defs()}{art}</svg>
{''.join(tx)}{lg}</body></html>'''

def glaze(x0, y0, x1, y1, color, n, seed=1, op=0.35, rmin=30, rmax=80):
    """Loose darker blooms inside an area, for layered watercolour depth."""
    import random
    r = random.Random(seed)
    out = []
    for k in range(n):
        cx, cy, rx, ry = r.uniform(x0, x1), r.uniform(y0, y1), r.uniform(rmin, rmax), r.uniform(rmin*0.5, rmax*0.6)
        n_ = 7
        pts = [(cx + math.cos(t*2*math.pi/n_) * rx * r.uniform(0.55, 1.1), cy + math.sin(t*2*math.pi/n_) * ry * r.uniform(0.55, 1.1)) for t in range(n_)]
        out.append(wash(smooth(pts, True), color, 1 + (seed + k) % 12, op * 0.7))
    return ''.join(out)

def cast(x, y, s=1.0, color=None, seed=1):
    """A small pile of worm casts: stacked rounded pellets."""
    import random
    r = random.Random(seed)
    color = color or C['soil2']
    pel = []
    rows = [(0, 5), (-1, 4), (-2, 3), (-3, 2)]
    for row, n in rows:
        for k in range(n):
            px = x + (k - (n - 1) / 2) * 13 * s + r.uniform(-2, 2) * s
            py = y + row * 10 * s + r.uniform(-2, 2) * s
            pel.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{8*s:.1f}" ry="{6*s:.1f}" fill="{color}" stroke="{INK}" stroke-width="1.6" stroke-opacity="0.6"/>')
    return f'<g filter="url(#pen)">{"".join(pel)}</g>'

def leaf(x, y, s, ang, color, seed=1, op=0.95, vein=True):
    d = f'M{-30*s:.1f},0 C{-14*s:.1f},{-17*s:.1f} {14*s:.1f},{-17*s:.1f} {30*s:.1f},0 C{14*s:.1f},{17*s:.1f} {-14*s:.1f},{17*s:.1f} {-30*s:.1f},0 Z'
    v = line(f'M{-34*s:.1f},0 L{24*s:.1f},0', INK, 1.4, 0.45) if vein else ''
    return f'<g transform="translate({x:.0f},{y:.0f}) rotate({ang:.0f})">{wash(d, color, seed, op)}{v}</g>'

def T(x, y, w, text, size=30, kind='body', weight=None, color=None, lh=None, align='left'):
    if kind == 'title':
        return dict(x=x, y=y, w=w, size=size, weight=weight or 600, family='title', color=color or INK, lh=lh or 1.02, text=text, align=align)
    if kind == 'label':
        return dict(x=x, y=y, w=w, size=size, weight=weight or 500, family='title', color=color or INK, lh=lh or 1.15, text=text, align=align)
    if kind == 'kicker':
        return dict(x=x, y=y, w=w, size=size, weight=weight or 600, family='title', color=color or C['green'], lh=lh or 1.1, text=text, align=align)
    return dict(x=x, y=y, w=w, size=size, weight=weight or 500, family='body', color=color or BODY, lh=lh or 1.38, text=text, align=align)
