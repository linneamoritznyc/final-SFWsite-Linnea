import os
import random
from lib import *
R = random.Random(4)
# jar geometry
L, Rr, B, SH, NL, NR, NT = 150, 600, 1235, 540, 225, 525, 455
def jar_path(i=0):
    return (f'M{NL+i},{NT} L{NL+i},{SH-50} C{NL+i},{SH-10} {L+i},{SH-20} {L+i},{SH+60} '
            f'L{L+i},{B-60-i} Q{L+i},{B-i} {L+60},{B-i} L{Rr-60},{B-i} Q{Rr-i},{B-i} {Rr-i},{B-60-i} '
            f'L{Rr-i},{SH+60} C{Rr-i},{SH-20} {NR-i},{SH-10} {NR-i},{SH-50} L{NR-i},{NT} Z')
art = []
art.append(f'<clipPath id="jar"><path d="{jar_path(10)}"/></clipPath>')
# glass tint
art.append(wash(jar_path(0), '#cfe0e6', 2, 0.55))
layers = []
# bottom pebbles
y0 = 1110
layers.append(wash(f'M100,{y0} L650,{y0+6} L650,1260 L100,1260 Z', C['grey'], 3, 0.6))
for k in range(16):
    x = 175 + (k % 8) * 55 + R.uniform(-8, 8); y = 1140 + (k // 8) * 48 + R.uniform(-6, 6)
    layers.append(blob(x, y, R.uniform(22, 30), R.uniform(15, 20), C['stone'], 1 + k % 6, 0.9))
# soil 1 (dark)
layers.append(wash(f'M100,1000 C250,990 400,1012 650,995 L650,{y0+10} L100,{y0+4} Z', C['soil2'], 4, 1))
# sand with dots
layers.append(wash(f'M100,900 C260,912 420,890 650,905 L650,1004 C400,1015 250,992 100,1004 Z', C['sand'], 5, 0.95))
for k in range(70):
    x, y = R.uniform(165, 590), R.uniform(915, 990)
    layers.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{R.uniform(1.8,3.6):.1f}" fill="{C["soil"]}" opacity="0.6"/>')
# soil 2 with crumbs and pores
layers.append(wash('M100,730 C260,720 430,742 650,728 L650,908 C420,893 260,914 100,903 Z', C['soil'], 6, 1))
layers.append(f'<g filter="url(#wc7)" opacity="0.9" style="mix-blend-mode:multiply">{"".join(crumbs(375, 815, 220, 70, 55, C["soil2"], 11, 6, 13))}</g>')
for k in range(14):  # air pores: little white gaps
    x, y = R.uniform(175, 580), R.uniform(752, 885)
    layers.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{R.uniform(5,9):.0f}" ry="{R.uniform(3,5):.0f}" fill="#fff" opacity="0.85" filter="url(#soft)"/>')
# leaves / food layer
layers.append(wash('M100,640 C260,650 430,628 650,642 L650,734 C430,746 260,724 100,736 Z', C['soil'], 8, 0.55))
for k in range(16):
    x, y = 180 + k * 27 + R.uniform(-10, 10), R.uniform(655, 712)
    a = R.uniform(-40, 40); col = [C['leaf'], C['leaf2'], C['yellow'], C['grass']][k % 4]
    layers.append(f'<g transform="translate({x:.0f},{y:.0f}) rotate({a:.0f})">'
                  + wash('M-30,0 C-14,-16 14,-16 30,0 C14,16 -14,16 -30,0 Z', col, 1 + k % 9, 0.9) + '</g>')
# top soil + grass
layers.append(wash('M100,575 C260,584 420,566 650,578 L650,648 C430,634 260,656 100,646 Z', C['soil2'], 9, 0.9))
grass = []
for k in range(60):
    x = 165 + k * 7.4 + R.uniform(-3, 3); h = R.uniform(40, 85); lean = R.uniform(-14, 14)
    grass.append(f'<path d="M{x-5:.0f},585 Q{x+lean*0.4:.0f},{585-h*0.6:.0f} {x+lean:.0f},{585-h:.0f} Q{x+lean*0.3+3:.0f},{585-h*0.5:.0f} {x+5:.0f},585 Z" fill="{C["grass"]}"/>')
layers.append(f'<g filter="url(#wc10)" style="mix-blend-mode:multiply">{"".join(grass)}</g>')
layers.append(glaze(160, 1010, 590, 1100, C['dark'], 7, 21, 0.35))
layers.append(glaze(160, 740, 590, 900, C['soil2'], 8, 22, 0.3))
layers.append(glaze(160, 590, 590, 640, C['dark'], 5, 23, 0.3, 30, 60))
CASTCOL = '#a06a4e'
casts = [cast(445, 1093, 1.0, CASTCOL, 5), cast(492, 1097, 0.8, CASTCOL, 6), cast(536, 1095, 0.65, CASTCOL, 7)]
# worms inside
WF, WB = '#c98a7e', '#9c5248'
worms = [worm([(200, 860), (260, 830), (330, 850), (390, 900), (460, 960), (530, 950)], 19, fill=WF, band_color=WB),
         worm([(560, 700), (510, 735), (470, 780), (420, 790), (360, 770)], 17, fill=WF, band_color=WB),
         worm([(240, 1040), (300, 1070), (370, 1055), (420, 1080)], 15, fill=WF, band_color=WB)]
art.append(f'<g clip-path="url(#jar)">{"".join(layers)}</g>')
# glass outline + highlights
art.append(line(jar_path(0), '#7d6f6a', 3))
art.append(line(f'M{L+28},{SH+90} L{L+28},{B-120}', '#ffffff', 10, 0.75))
art.append(line(f'M{L+46},{SH+110} L{L+46},{SH+260}', '#ffffff', 5, 0.6))
# lid: band with threads
lid = f'M{NL-16},392 Q{NL-16},378 {NL-2},378 L{NR+2},378 Q{NR+16},378 {NR+16},392 L{NR+16},{NT+6} Q{NR+16},{NT+16} {NR+4},{NT+16} L{NL-4},{NT+16} Q{NL-16},{NT+16} {NL-16},{NT+6} Z'
art.append(wash(lid, '#bdb4a6', 11, 1))
for yy in (398, 418, 438):
    art.append(line(f'M{NL-12},{yy} Q375,{yy+6} {NR+12},{yy}', '#7d6f6a', 2, 0.55))
art.append(line(lid, INK, 2.6))
# labels with arrows
lab = [(700, 520, 'Fallen leaves: the<br>worms’ dinner table', (420, 668)),
       (700, 720, 'Air pores and<br>aggregates', (520, 820)),
       (700, 905, 'Worms working with<br>the microbes', (545, 945)),
       (700, 1095, 'Crumbly casts', (452, 1062))]
texts = [dict(x=70, y=70, w=950, size=86, weight=600, family='title', color=INK, lh=1.0,
              text='Happy World<br>Earthworm Day!'),
         dict(x=72, y=262, w=900, size=34, weight=500, text='What can the worms in your life<br>tell you about your soil?', color=BODY)]
arrows = []
for i, (x, y, t, tgt) in enumerate(lab):
    arrows.append(((x - 14, y + 28), tgt, 0.18 if i % 2 else -0.18))
    texts.append(dict(x=x, y=y, w=330, size=30, weight=500, family='title', color=INK, text=t, lh=1.15))

import json, subprocess
jar = ''.join(art)
arr = ''.join(arrow(*a_) for a_ in arrows)
LAYERS = {'jar': jar, 'casts': ''.join(casts), **{f'worm{i+1}': w_ for i, w_ in enumerate(worms)}}
open('s1.html', 'w').write(page(jar + ''.join(casts) + ''.join(worms) + arr, texts, logo_box=(890, 1200, 150, None)))
subprocess.run(['node', 'render.js', os.path.abspath('s1.html'), os.path.abspath('out/s1.png')], check=True)
os.makedirs('layers', exist_ok=True)
for k, v in LAYERS.items():
    open(f'layers/{k}.html', 'w').write(page(v, [], logo=False, bg='transparent'))
    subprocess.run(['node', 'render.js', os.path.abspath(f'layers/{k}.html'), os.path.abspath(f'layers/{k}.png'), 't'], check=True)
json.dump({'arrows': arrows, 'texts': texts}, open('layers/s1.json', 'w'))

