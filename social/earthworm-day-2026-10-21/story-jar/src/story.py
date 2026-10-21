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

def html(pics, arrows, texts, logo=True, bg='#ffffff', only=None):
    tx = []
    for t in texts:
        fam = {'title': "'Fredoka'", 'body': "'Montserrat'"}[t.get('family', 'body')]
        tx.append(f'<div class="t" style="left:{t["x"]}px;top:{t["y"]}px;width:{t["w"]}px;font-family:{fam};font-size:{t["size"]}px;'
                  f'font-weight:{t.get("weight",500)};color:{t.get("color","#5b4c46")};text-align:{t.get("align","left")};line-height:{t.get("lh",1.25)}">{t["text"]}</div>')
    ims = ''.join(f'<img src="{p["path"]}" style="position:absolute;left:{p["x"]}px;top:{p["y"]}px;width:{p["w"]}px">' for p in pics)
    arr = ''.join(arrow(*a) for a in arrows)
    lg = f'<img src="{EW}/logo.png" style="position:absolute;left:890px;top:1560px;width:150px">' if logo else ''
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
p, _ = cutout('f1-jar-t3', fade_bottom=300)
a = img(p, 0, 500, 1080)
F.append(dict(pics=[('Jar with party worm', a)], arrows=[],
              texts=[H('Is World Earthworm Day even a thing?')]))
# 2
p, _ = cutout('f2-book-t1')
a = img(p, -60, 760, 1200)
F.append(dict(pics=[('Book with worm', a)], arrows=[],
              texts=[H('Yes! Since 2016.', 112),
                     T(70, 430, 940, 'The Earthworm Society of Britain picked 21 October to honour Charles Darwin. His book on worms came out in October 1881.', 42, lh=1.36, align='center')]))
# 3
p, _ = cutout('f3-piano-t1')
a = img(p, 40, 500, 1000)
book = img(f'{HERE}/cut/f2-book-t1.png', 20, 1250, 420)
F.append(dict(pics=[('Piano with pots', a), ('Small book', book)],
              arrows=[((560, 470), at(a, 590, 250), 0.2),
                      ((660, 1225), at(a, 880, 330), -0.2),
                      ((470, 1395), at(book, 1050, 330), 0.25)],
              texts=[H('Darwin was obsessed'),
                     T(590, 420, 460, 'He played the piano to his worms', 38, 'label'),
                     T(680, 1160, 380, 'He tested how they pull leaves underground with paper triangles', 34, 'label'),
                     T(490, 1355, 560, 'His worm book outsold <i>Origin of Species</i> at his publisher’s 1881 sale', 34, 'label')]))
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
    render(html(pics, f['arrows'], f['texts']), f'{HERE}/out/frame{i}.png')
    specs.append(dict(name=f'frame{i}', html=f'{HERE}/out/frame{i}.html',
                      pics=[(n, p['path'], p['x'], p['y'], p['w'], p['h']) for n, p in f['pics']],
                      arrows=f['arrows'], texts=f['texts']))
json.dump(specs, open(f'{HERE}/layers/specs.json', 'w'))
