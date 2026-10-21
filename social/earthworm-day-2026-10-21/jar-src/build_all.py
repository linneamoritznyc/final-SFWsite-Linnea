"""Render the Earthworm Day carousel (watercolour on white, drawn in code) and write an editable PPTX.
Each slide: illustration picture, each worm its own picture, arrows as editable lines, text boxes, logo."""
import json, os, re, subprocess
import lib, slides
from lib import page, arrow as draw_arrow
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/user/final-sfwsite-linnea/social/earthworm-day-2026-10-21'
os.makedirs(f'{HERE}/layers', exist_ok=True)

def render(html, png, transp=False):
    open(png.replace('.png', '.html'), 'w').write(html)
    subprocess.run(['node', f'{HERE}/render.js', png.replace('.png', '.html'), png] + (['t'] if transp else []), check=True)

specs = []
# slide 1 comes from s1.py (already layered)
subprocess.run(['python3', f'{HERE}/s1.py'], check=True, cwd=HERE)
s1 = json.load(open(f'{HERE}/layers/s1.json'))
specs.append(dict(name='s1', pics=[('Jar', 'layers/jar.png'), ('Worm casts', 'layers/casts.png')] +
                  [(f'Worm {i}', f'layers/worm{i}.png') for i in (1, 2, 3)], arrows=s1['arrows'], texts=s1['texts']))

for n in range(2, 9):
    name = f's{n}'
    worms, arrows = [], []
    slides.worm = lambda *a, **k: (worms.append(lib.worm(*a, **k)), '')[1]
    slides.arrow = lambda p0, p1, bend=0.25, **k: (arrows.append((p0, p1, bend)), '')[1]
    art, texts = getattr(slides, name)()
    art = ''.join(art)
    full = art + ''.join(worms) + ''.join(draw_arrow(*a) for a in arrows)
    render(page(full, texts, logo_box=(890, 1200, 150, None)), f'{HERE}/out/{name}.png')
    render(page(art, [], logo=False, bg='transparent'), f'{HERE}/layers/{name}-art.png', True)
    pics = [('Illustration', f'layers/{name}-art.png')]
    for i, w in enumerate(worms):
        render(page(w, [], logo=False, bg='transparent'), f'{HERE}/layers/{name}-worm{i+1}.png', True)
        pics.append((f'Worm {i+1}', f'layers/{name}-worm{i+1}.png'))
    specs.append(dict(name=name, pics=pics, arrows=arrows, texts=texts))
json.dump(specs, open(f'{HERE}/layers/specs.json', 'w'))
