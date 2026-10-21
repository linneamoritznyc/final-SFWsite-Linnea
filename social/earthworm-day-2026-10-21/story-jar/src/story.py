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
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}} .t{{position:absolute}}
svg{{position:absolute;left:0;top:0}}</style></head><body>{ims}
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{defs()}{arr}</svg>{''.join(tx)}{lg}</body></html>'''

def at(p, rx, ry):  # raw image coords -> slide coords
    return (round(p['x'] + rx * p['sx']), round(p['y'] + ry * p['sx']))

F = []
def H(text, size=104, y=270):
    return T(40, y, 1000, text, size, 'title', lh=1.04, align='center')
# 1
p, _ = cutout('f1-jar-t3')
a = img(p, 60, 1920 - 860 * 1184 / 864, 860)   # bottom of the painting sits on the frame edge, no fade
F.append(dict(pics=[('Jar with party worm', a)], arrows=[],
              texts=[H('Is World Earthworm Day even a thing?', y=400)]))
# 2
p, _ = cutout('f2-book-t1')
a = img(p, 110, 1000, 860)
B2 = dict(lh=1.36, align='center')
F.append(dict(pics=[('Book with worm', a)], arrows=[],
              texts=[H('Yes! Since 2016.', 112),
                     T(60, 420, 960, 'The Earthworm Society of Britain picked 21 October to honour Charles Darwin. His book on worms came out in October 1881.', 38, **B2),
                     T(60, 620, 960, 'Darwin studied worms for over 40 years. The worm book was his last, published a year before he died.', 38, **B2),
                     T(60, 820, 960, 'He weighed the casts worms left on the ground and found they bring up 7 to 18 tons of soil per acre every year.', 38, **B2)]))
# 3
p, _ = cutout('f3-piano-keys-k2')
a = img(p, 90, 600, 900)
notes = dict(path=f'{HERE}/cut/notes.png', x=0, y=0, w=1080, h=1920, sx=1)
book = img(f'{HERE}/cut/f2-book-t1.png', 40, 1390, 300)
LB = dict(kind='label', weight=500, lh=1.2)
F.append(dict(pics=[('Piano with pots', a), ('Music notes', notes), ('Small book', book)],
              arrows=[((600, 450), at(a, 590, 255), 0.2),
                      ((650, 1235), at(a, 870, 330), -0.15),
                      ((250, 1338), (215, 1448), 0.25)],
              texts=[H('Darwin was obsessed'),
                     T(620, 400, 430, 'Loud music didn’t bother them. But with their pots on the piano, one struck note sent them diving into their burrows. Worms feel vibrations.', 28, **LB),
                     T(660, 1200, 400, 'He scattered about 300 paper triangles near their burrows. Most were pulled in by the pointed end, the same way they pull leaves in tip first.', 28, **LB),
                     T(60, 1200, 520, 'At his publisher’s November 1881 sale, the worm book sold 3,500 copies. <i>Origin of Species</i> sold 600.', 28, **LB)]))
# 4
p, _ = cutout('f4-jar-t2')
a = img(p, -20, 390, 740)
L = dict(kind='label', weight=400, lh=1.2)
F.append(dict(pics=[('Jar with three worms', a)],
              arrows=[((690, 470), at(a, 440, 380), -0.15),
                      ((690, 900), at(a, 250, 700), 0.15),
                      ((688, 1222), at(a, 560, 900), -0.1)],
              texts=[H('Meet the three worms', 96),
                     T(700, 420, 360, '<b>The Composter</b> (epigeic). Small and red. Lives in the leaves and turns them into compost.', 34, **L),
                     T(700, 860, 360, '<b>The Mixer</b> (endogeic). Pale. Eats its way through the topsoil.', 34, **L),
                     T(700, 1200, 360, '<b>The Engineer</b> (anecic). Big and dark-headed. Digs deep tunnels and pulls leaves down at night.', 34, **L)]))
# 5
p, _ = cutout('f5-jars-t1')
a = img(p, -40, 520, 1160)
cx = [at(a, x, 0)[0] for x in (255, 680, 1090)]
F.append(dict(pics=[('Three party jars', a)], arrows=[],
              texts=[H('Which worm are you today?')] +
                    [T(c - 180, 1150, 360, n, 44, 'title', align='center') for c, n in zip(cx, ['The Composter', 'The Mixer', 'The Engineer'])]))

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
