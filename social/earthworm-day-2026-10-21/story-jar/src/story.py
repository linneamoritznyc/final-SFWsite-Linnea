"""World Earthworm Day story, 1080x1920, 5 frames. Replicate (nano-banana) watercolours + code-drawn arrows, text in Fredoka/Montserrat."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); EW = os.path.dirname(HERE)
sys.path.insert(0, EW)
import lib
from lib import T, INK, C, defs, arrow
W, H = 1080, 1920
os.makedirs(f'{HERE}/cut', exist_ok=True); os.makedirs(f'{HERE}/out', exist_ok=True); os.makedirs(f'{HERE}/layers', exist_ok=True)

def cutout(name, fade_bottom=0):
    """White paper -> transparent, so each painting is a clean movable object on the white slide."""
    im = Image.open(f'{HERE}/raw/{name}.png').convert('RGB'); a = np.array(im).astype(float)
    d = 255 - a.min(axis=2)
    al = np.clip((d - 6) * 4.0, 0, 255)
    alf = np.maximum(al / 255, 1e-3)[..., None]
    rgb = np.clip((a - 255 * (1 - alf)) / alf, 0, 255)
    if fade_bottom:
        h = a.shape[0]; ramp = np.ones(h); ramp[h - fade_bottom:] = np.linspace(1, 0, fade_bottom) ** 1.4
        al = al * ramp[:, None]
    out = Image.fromarray(np.dstack([rgb, al]).astype('uint8'), 'RGBA')
    p = f'{HERE}/cut/{name}.png'; out.save(p); return p, im.size

def img(path, x, y, w):
    im = Image.open(path); h = w * im.height / im.width
    return dict(path=path, x=x, y=y, w=w, h=h, sx=w / im.width)

def html(pics, arrows, texts, logo=True, bg='#ffffff', only=None, logo_xy=(890, 1560)):
    tx = []
    for t in texts:
        fam = {'title': "'Fredoka'", 'body': "'Montserrat'"}[t.get('family', 'body')]
        tx.append(f'<div class="t" style="left:{t["x"]}px;top:{t["y"]}px;width:{t["w"]}px;font-family:{fam};font-size:{t["size"]}px;'
                  f'font-weight:{t.get("weight",500)};color:{t.get("color","#5b4c46")};text-align:{t.get("align","left")};line-height:{t.get("lh",1.25)}">{t["text"]}</div>')
    ims = ''.join(f'<img src="{p["path"]}" style="position:absolute;left:{p["x"]}px;top:{p["y"]}px;width:{p["w"]}px">' for p in pics)
    arr = ''.join(arrow(*a) for a in arrows)
    lg = f'<img src="{EW}/logo.png" style="position:absolute;left:{logo_xy[0]}px;top:{logo_xy[1]}px;width:150px">' if logo else ''
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Fredoka';src:url('{EW}/fonts/Fredoka.ttf');font-weight:300 700}}
@font-face{{font-family:'Montserrat';src:url('{lib.REPO_FONTS}/montserrat-latin-variable.woff2');font-weight:100 900}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}} .t{{position:absolute;text-wrap:balance}}
svg{{position:absolute;left:0;top:0}}</style></head><body>{ims}
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{defs()}{arr}</svg>{''.join(tx)}{lg}</body></html>'''

def at(p, rx, ry):  # raw image coords -> slide coords
    return (round(p['x'] + rx * p['sx']), round(p['y'] + ry * p['sx']))

F = []
TEXT_Y, SIZE, LH = 290, 50, 1.4
def story_text(text, y=TEXT_Y):
    return T(60, y, 960, text, SIZE, lh=LH, align='center', color='#4a3b36')

def n_lines(text):
    """Line count from a real Chromium render, so the picture always starts below the text."""
    probe = f'{HERE}/out/_probe.html'
    open(probe, 'w').write(html([], [], [story_text(text)], logo=False))
    out = json.loads(subprocess.run(['node', f'{EW}/lines.js', probe], capture_output=True, text=True, check=True).stdout)
    return len(out[probe][0])

def below(text, name, box_bottom=1540, w_max=960, x0=60, gap=70):
    """Fit a painting into the space under the text, centred."""
    top = TEXT_Y + n_lines(text) * SIZE * LH + gap
    im = Image.open(f'{HERE}/cut/{name}.png'); bb = im.getbbox()
    cw, ch = bb[2] - bb[0], bb[3] - bb[1]
    sc = min(w_max / cw, (box_bottom - top) / ch)
    w = im.width * sc
    x = x0 + (w_max - cw * sc) / 2 - bb[0] * sc
    y = top - bb[1] * sc
    return img(f'{HERE}/cut/{name}.png', x, y, w)

TX = [
 'Is World Earthworm Day even a thing?',
 'It is! In 2016 the Earthworm Society of Britain picked 21 October, to honour Charles Darwin. His book on worms came out in October 1881.',
 'Darwin studied worms for over 40 years. At one point he wanted to know if they can hear.',
 'So his son played the bassoon at them. Darwin whistled and shouted. His wife played the piano loudly right next to their pots. The worms didn’t react at all.',
 'Then he put the pots on top of the piano. One note, and the worms shot back into their burrows. They felt the music through the wood.',
 'He also left about 300 paper triangles by their burrows, to see how worms drag leaves underground. Most went in pointed end first, just like leaves.',
 'People loved it. At his publisher’s sale that November, the worm book sold 3,500 copies. <i>Origin of Species</i> sold 600.',
 'Worms are still doing the same work in your garden. There are three kinds.',
 'Which worm are you today?',
]
for name in ['f1-jar-t3', 'f2-book-t1', 'f3-note-b', 'f4-stool-a', 'f3-piano-keys-k2', 'f6-triangles-a', 'f7-books-a', 'f4-jar-t2', 'f5-jars-t1']:
    cutout(name)
# 1: jar sits on the bottom edge (no fade), logo beside it on white
a = img(f'{HERE}/cut/f1-jar-t3.png', 40, 1920 - 880 * 1184 / 864, 880)
F.append(dict(pics=[('Jar with party worm', a)], arrows=[], texts=[story_text(TX[0])]))
# 2 to 7: painting under the text
for k, (name, label) in enumerate([('f2-book-t1', 'Open book with worm'), ('f3-note-b', 'Worm and music note'),
                                   ('f4-stool-a', 'Piano with pots on a stool'), ('f3-piano-keys-k2', 'Pots on the piano'),
                                   ('f6-triangles-a', 'Paper triangle pulled into a burrow'), ('f7-books-a', 'Stack of old books')], start=1):
    F.append(dict(pics=[(label, below(TX[k], name))], arrows=[], texts=[story_text(TX[k])]))
# 8: the three-worm jar with its labels
top8 = TEXT_Y + n_lines(TX[7]) * SIZE * LH + 40
a = img(f'{HERE}/cut/f4-jar-t2.png', -30, top8 - 40, 690)
L = dict(kind='label', weight=400, lh=1.2)
ly = [top8 + 30, top8 + 470, top8 + 760]
F.append(dict(pics=[('Jar with three worms', a)],
              arrows=[((688, ly[0] + 22), at(a, 440, 380), -0.15),
                      ((688, ly[1] + 22), at(a, 250, 700), 0.15),
                      ((688, ly[2] + 22), at(a, 560, 900), -0.1)],
              texts=[story_text(TX[7]),
                     T(700, ly[0], 360, '<b>The Composter</b> (epigeic). Small and red. Lives in the leaves and turns them into compost.', 32, **L),
                     T(700, ly[1], 360, '<b>The Mixer</b> (endogeic). Pale. Eats its way through the topsoil.', 32, **L),
                     T(700, ly[2], 360, '<b>The Engineer</b> (anecic). Big and dark-headed. Digs deep tunnels and pulls leaves down at night.', 32, **L)]))
# 9: three jars, names, poll space 1250 to 1500
a = img(f'{HERE}/cut/f5-jars-t1.png', -40, 470, 1160)
cx = [at(a, x, 0)[0] for x in (255, 680, 1090)]
F.append(dict(pics=[('Three party jars', a)], arrows=[],
              texts=[story_text(TX[8])] + [T(c - 180, 1110, 360, n, 44, 'title', align='center') for c, n in zip(cx, ['The Composter', 'The Mixer', 'The Engineer'])]))

def render(h, png, transp=False):
    hp = png.replace('.png', '.html'); open(hp, 'w').write(h)
    subprocess.run(['node', f'{HERE}/render.js', hp, png] + (['t'] if transp else []), check=True)

specs = []
for i, f in enumerate(F, 1):
    pics = [p for _, p in f['pics']]
    render(html(pics, f['arrows'], f['texts'], logo_xy=f.get('logo', (890, 1560))), f'{HERE}/out/frame{i}.png')
    specs.append(dict(name=f'frame{i}', html=f'{HERE}/out/frame{i}.html',
                      pics=[(n, p['path'], p['x'], p['y'], p['w'], p['h']) for n, p in f['pics']],
                      arrows=f['arrows'], texts=f['texts'], logo=f.get('logo', (890, 1560))))
json.dump(specs, open(f'{HERE}/layers/specs.json', 'w'))
