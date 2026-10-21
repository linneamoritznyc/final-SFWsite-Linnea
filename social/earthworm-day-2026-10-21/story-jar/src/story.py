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
TEXT_Y, SIZE, LH, PGAP = 280, 42, 1.36, 26

def para(text, y, size=SIZE):
    return T(60, y, 960, text, size, lh=LH, align='center', color=INK)

def n_lines(t):
    """Line count from a real Chromium render."""
    probe = f'{HERE}/out/_probe.html'
    open(probe, 'w').write(html([], [], [t], logo=False))
    out = json.loads(subprocess.run(['node', f'{EW}/lines.js', probe], capture_output=True, text=True, check=True).stdout)
    return len(out[probe][0])

def stack(paras, size=SIZE):
    """One text box per paragraph, stacked from TEXT_Y. Returns boxes and the y where the text ends."""
    y, out = TEXT_Y, []
    for p in paras:
        t = para(p, y, size); out.append(t)
        y += n_lines(t) * size * LH + PGAP
    return out, y - PGAP

def fit(name, top, box_bottom=1530, w_max=960, x0=60):
    """Fit a whole painting (bottom edge included) into the box under the text, centred."""
    im = Image.open(f'{HERE}/cut/{name}.png'); bb = im.getbbox()
    cw, ch = bb[2] - bb[0], bb[3] - bb[1]
    sc = min(w_max / cw, (box_bottom - top) / ch)
    x = x0 + (w_max - cw * sc) / 2 - bb[0] * sc
    return img(f'{HERE}/cut/{name}.png', x, top - bb[1] * sc, im.width * sc)

FR = [
 (['Is World Earthworm Day even a thing?',
   'It is! In 2016 the Earthworm Society of Britain picked 21 October, to honour Charles Darwin. His book on worms came out in October 1881, after more than 40 years of studying them.'],
  'g1-jar-a', 'Jar with party worm'),
 (['Darwin wanted to know if worms can hear. His son played the bassoon at them, Darwin whistled and shouted, and his wife played the piano right next to their pots. The worms didn’t react at all.',
   'Then he put the pots on top of the piano. One note, and the worms shot back into their burrows. Worms have no ears. They feel music through the ground with their whole body.'],
  'g4-piano-c', 'Piano with pot and diving worm'),
 (['Dr. Elaine Ingham, who founded our school, taught that worms are part of the soil food web.',
   'When a worm eats a fallen leaf, it also eats the bacteria and fungi growing on it. They broke the leaf down first. The worm passes those nutrients on in a form plant roots can take up, and lines its tunnels with slime full of nutrients and microbes.',
   'So when you find worms, the life under them is doing well too.'],
  'g6-bite-b', 'Worm biting a leaf, magnified'),
]
for paras, name, label in FR:
    cutout(name)
    texts, end = stack(paras)
    F.append(dict(pics=[(label, fit(name, end + 50))], arrows=[], texts=texts))
# 4: three jars, a description under each, empty space for the poll sticker
cutout('f5-jars-t1')
texts, end = stack(['Which worm are you today?'], 56)
a = fit('f5-jars-t1', end + 50, box_bottom=end + 50 + 560, w_max=1040, x0=20)
cx = [at(a, x, 0)[0] for x in (255, 680, 1090)]
jb = at(a, 0, 715)[1]
D = [('The Composter', 'small and red, lives in the leaves and turns them into compost'),
     ('The Mixer', 'pale, eats its way through the topsoil'),
     ('The Engineer', 'big and dark-headed, digs deep tunnels and pulls leaves down at night')]
for c, (n, d) in zip(cx, D):
    x = min(max(c - 170, 12), 1068 - 340)
    texts.append(T(x, jb + 24, 340, f'<b>{n}:</b> {d}', 31, lh=1.28, align='center', color=INK))
F.append(dict(pics=[('Three party jars', a)], arrows=[], texts=texts))

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
