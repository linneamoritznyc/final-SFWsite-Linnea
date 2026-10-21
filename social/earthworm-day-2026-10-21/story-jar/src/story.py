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
# 1
p, _ = cutout('f1-jar-t3', fade_bottom=260)
a = img(p, 150, 500, 800)
F.append(dict(pics=[('Jar with party worm', a)], arrows=[],
              texts=[T(70, 270, 940, 'Is World Earthworm Day even a thing?', 84, 'title', lh=1.05)]))
# 2
p, _ = cutout('f2-book-t1')
a = img(p, 40, 640, 1000)
F.append(dict(pics=[('Book with worm', a)], arrows=[],
              texts=[T(70, 270, 940, 'Yes! Since 2016.', 84, 'title'),
                     T(72, 400, 930, 'The Earthworm Society of Britain picked 21 October to honour Charles Darwin. His book on worms came out in October 1881.', 34, lh=1.38)]))
# 3
p, _ = cutout('f3-piano-t1')
a = img(p, 40, 440, 1000)
book = img(f'{HERE}/cut/f2-book-t1.png', 40, 1150, 340)
F.append(dict(pics=[('Piano with pots', a), ('Small book', book)],
              arrows=[((560, 455), at(a, 590, 250), 0.2),
                      ((830, 1165), at(a, 880, 330), -0.2),
                      ((470, 1300), at(book, 1060, 300), 0.25)],
              texts=[T(70, 270, 940, 'Darwin was obsessed', 84, 'title'),
                     T(590, 395, 450, 'He played the piano to his worms', 32, 'label'),
                     T(590, 1180, 450, 'He tested how they pull leaves underground with paper triangles', 32, 'label'),
                     T(490, 1340, 520, 'His worm book outsold <i>Origin of Species</i> at his publisher’s 1881 sale', 32, 'label')]))
# 4
p, _ = cutout('f4-jar-t2')
a = img(p, 10, 400, 640)
F.append(dict(pics=[('Jar with three worms', a)],
              arrows=[((630, 470), at(a, 440, 380), -0.15),
                      ((630, 880), at(a, 250, 700), 0.15),
                      ((630, 1230), at(a, 560, 900), 0.2)],
              texts=[T(70, 270, 940, 'Meet the three worms', 84, 'title'),
                     T(650, 410, 410, '<b>The Composter</b> (epigeic). Small and red. Lives in the leaves and turns them into compost.', 31, 'label', weight=400, lh=1.22),
                     T(650, 840, 410, '<b>The Mixer</b> (endogeic). Pale. Eats its way through the topsoil.', 31, 'label', weight=400, lh=1.22),
                     T(650, 1180, 410, '<b>The Engineer</b> (anecic). Big and dark-headed. Digs deep tunnels and pulls leaves down at night.', 31, 'label', weight=400, lh=1.22)]))
# 5
p, _ = cutout('f5-jars-t1')
a = img(p, 20, 440, 1040)
cx = [at(a, x, 0)[0] for x in (255, 680, 1090)]
F.append(dict(pics=[('Three party jars', a)], arrows=[],
              texts=[T(70, 270, 940, 'Which worm are you today?', 84, 'title', lh=1.05)] +
                    [T(c - 170, 1060, 340, n, 38, 'title', align='center') for c, n in zip(cx, ['The Composter', 'The Mixer', 'The Engineer'])]))

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
