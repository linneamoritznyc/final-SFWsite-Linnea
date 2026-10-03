"""Blog headers in the Foundation's existing soil design (Linnea's Canva headers
Certified / Transfer / Growing / Scholarship Opportunities): dark soil photograph
edge to edge, a crumbling white soil edge along the foot, the words on tilted
paper labels (one coloured, then white ones), and a white line icon in a circle
on the right. One editable .pptx per size, one slide per post."""
import os, sys, math, random, re, io
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
ONLY_SIZES = sys.argv[2:]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], OUT]
import build as B
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import cairosvg
PX = B.PX
REPO = B.REPO
TMP = os.path.join(OUT, '_soil'); os.makedirs(TMP, exist_ok=True)

MINT, ORANGE, VIOLET, WHITE, INK = '#A9CFB1', '#E1752B', '#B9A9DA', '#F6F5F1', '#161514'
ELAINE = {'obituary-dr-elaine-ingham', 'living-legacy-webinar-series', 'retirement-dr-elaine-ingham', 'foundation-launches-as-nonprofit'}
ICON = {'Microscopy': 'i-microscope', 'Education': 'i-scholarship', 'School Updates': 'i-scholarship', 'Events': 'i-calendar',
        'Blog': 'i-web', 'In Memoriam': 'logo', 'Foundation Update': 'logo'}

SIZES = {
 'desktop-header-1920x720':  dict(W=1920, H=720,  font=86, x=150, y=0, maxw=1150, icon=(1560, 0, 240), edge=170),
 'feature-social-1400x1400': dict(W=1400, H=1400, font=96, x=100, y=0, maxw=1150, icon=(1060, 90, 240), edge=240),
 'tablet-header-1024x768':   dict(W=1024, H=768,  font=56, x=56, y=0, maxw=700, icon=(840, 40, 140), edge=140),
 'mobile-header-750x1000':   dict(W=750,  H=1000, font=56, x=44, y=0, maxw=640, icon=(560, 40, 150), edge=170),
}

# --- the soil: the compost photograph, mirrored out to any size -----------------
_SRC = None
def soil(w, h, seed=7):
    """Random patches of the compost photograph, feathered together, so the
    texture never repeats or mirrors."""
    global _SRC
    import numpy as np
    if _SRC is None:
        src = Image.open(os.path.join(REPO, 'img', 'hand-of-compost.jpg')).convert('RGB').crop((0, 0, 1640, 560))
        src = ImageEnhance.Color(src).enhance(.55)
        _SRC = ImageEnhance.Brightness(src).enhance(.72)
    src = _SRC
    rnd = random.Random(seed)
    P = 420
    out = Image.new('RGB', (w, h))
    # base: the photograph scaled to cover
    k = max(w / src.width, h / src.height)
    base = src.resize((int(src.width * k) + 1, int(src.height * k) + 1), Image.LANCZOS).crop((0, 0, w, h))
    out.paste(base, (0, 0))
    feather = Image.new('L', (P, P), 0); ImageDraw.Draw(feather).ellipse((40, 40, P - 40, P - 40), fill=255)
    feather = feather.filter(ImageFilter.GaussianBlur(45))
    for yy in range(-P // 2, h, P // 2):
        for xx in range(-P // 2, w, P // 2):
            sx, sy = rnd.randint(0, src.width - P), rnd.randint(0, src.height - P)
            patch = src.crop((sx, sy, sx + P, sy + P))
            if rnd.random() < .5: patch = patch.rotate(180)
            out.paste(patch, (xx + rnd.randint(-40, 40), yy + rnd.randint(-40, 40)), feather)
    return out

def crumble_edge(w, h, seed=1):
    """White soil crumbling up from the foot: the soil photograph's own grain,
    thresholded against a rising gradient, so the particles are real texture."""
    g = ImageOps.grayscale(soil(w, h, seed=seed))
    g = ImageOps.autocontrast(g)
    import numpy as np
    a = np.asarray(g).astype(np.float32) / 255
    rnd = np.random.default_rng(seed)
    ys = np.linspace(0, 1, h)[:, None]
    wave = (np.sin(np.linspace(0, 9, w) + seed) * .05 + np.sin(np.linspace(0, 31, w)) * .03)[None, :]
    level = ys + wave - .35
    alpha = ((a * .75 + rnd.random(a.shape) * .45 + level * 1.7) > 1.0).astype(np.uint8) * 255
    alpha[int(h * .72):, :] = 255
    m = Image.fromarray(alpha).filter(ImageFilter.MedianFilter(3))
    out = Image.new('RGBA', (w, h), (255, 255, 255, 0)); out.putalpha(m)
    return out

# --- icons: the site's own line icons, white, in a white ring ------------------
SVG = open(os.path.join(REPO, 'img', 'icons.svg')).read()
def icon_png(name, size):
    if name == 'logo':
        lg = Image.open(os.path.join(REPO, 'img', 'sfwlogo-240.png')).convert('RGBA')
        white = Image.new('RGBA', lg.size, (255, 255, 255, 0)); white.putalpha(lg.split()[3])
        return white
    m = re.search(r'<symbol id="%s" viewBox="([^"]+)">(.*?)</symbol>' % name, SVG, re.S)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-7 -7 38 38" width="{size}" height="{size}">'
           f'<circle cx="12" cy="12" r="17.5" fill="none" stroke="#fff" stroke-width="1.1"/>'
           f'<g fill="none" stroke="#fff" stroke-width="1.05" stroke-linecap="round" stroke-linejoin="round">{m.group(2)}</g></svg>')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)))

def put_png(slide, im, name, x, y, w, h, rot=0):
    p = os.path.join(TMP, f'{name}.png'); im.save(p)
    pic = slide.shapes.add_picture(p, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
    pic.name = name
    if rot: pic.rotation = rot
    return pic

def label(slide, text, x, y, size, fill, name, rot):
    """A paper label: a flat rectangle, slightly tilted, text set in it."""
    f = B.font('Montserrat-Regular.ttf', size)
    tw = f.getlength(text)
    padx, h = size * .42, size * 1.28
    w = tw + 2 * padx
    sh = slide.shapes.add_shape(1, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
    sh.name = name + ' paper'; sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(*B.hexrgb(fill)); sh.line.fill.background(); sh.shadow.inherit = False
    sh.rotation = rot
    tf = sh.text_frame; tf.margin_left = tf.margin_right = Emu(int(padx * PX)); tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE; tf.word_wrap = False
    p = tf.paragraphs[0]; p.text = text; p.alignment = PP_ALIGN.LEFT
    r = p.runs[0]; r.font.name = 'Montserrat'; r.font.size = Pt(size * .75); r.font.bold = False
    r.font.color.rgb = RGBColor(*B.hexrgb(INK))
    return w, h

def card(prs, post, key, cfg):
    W, H = cfg['W'], cfg['H']
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = soil(W, H, seed=len(key)); p = os.path.join(TMP, f'soil-{key}.jpg'); bg.save(p, quality=90)
    s.shapes.add_picture(p, 0, 0, Emu(W * PX), Emu(H * PX)).name = 'Soil'
    eh = cfg['edge']
    put_png(s, crumble_edge(W, eh, seed=hash(post['slug']) % 97), f'edge-{key}-{post["slug"]}', 0, H - eh, W, eh)
    # the words: category on the coloured label, headline on white ones
    size = cfg['font']
    colour = VIOLET if post['slug'] in ELAINE else (ORANGE if post['cat'] == 'Events' else MINT)
    maxw = cfg['maxw']
    while True:
        lines = B.wrap(post['head'], B.font('Montserrat-Regular.ttf', size), maxw - size * .9)
        if len(lines) <= 3 or size < 30: break
        size -= 2
    small = size * .92
    x = cfg['x']
    block = small * 1.34 + size * 1.3 * len(lines)
    y = (H - cfg['edge'] * .6 - block) / 2
    rnd = random.Random(post['slug'] + key)
    label(s, post['cat'], x + size * .35, y, small, colour, 'Category', -2.6)
    y += small * 1.34
    for i, ln in enumerate(lines):
        label(s, ln, x - (size * .1 if i % 2 == 0 else -size * .25), y, size, WHITE, f'Headline {i+1}', rnd.uniform(1.0, 2.0) * (1 if i % 2 == 0 else .5))
        y += size * 1.3
    ix, iy, isz = cfg['icon']
    if W / H > 1.2: iy = (H - cfg['edge'] * .6 - isz) / 2
    ic = icon_png(ICON.get(post['cat'], 'i-web') if post['slug'] not in ELAINE else 'logo', isz * 2)
    ih = isz * ic.height / ic.width
    put_png(s, ic, f'icon-{key}-{post["slug"]}', ix, iy, isz, ih)
    s.notes_slide.notes_text_frame.text = f"{post['slug']} ({post['date']})"

only = ONLY_SIZES or list(SIZES)
for key in only:
    cfg = SIZES[key]
    prs = Presentation(); prs.slide_width, prs.slide_height = Emu(cfg['W'] * PX), Emu(cfg['H'] * PX)
    for post in B.POSTS: card(prs, post, key, cfg)
    out = os.path.join(OUT, f'soil-blog-headers--{key}.pptx'); prs.save(out); print(out)
