import random, math
from lib import *

def s2():
    R = random.Random(12)
    a = []
    X0, X1, Y0, Y1, DX, DY = 90, 760, 610, 1040, 190, -120
    front = f'M{X0},{Y0} L{X1},{Y0} L{X1},{Y1} L{X0},{Y1} Z'
    top = f'M{X0},{Y0} L{X0+DX},{Y0+DY} L{X1+DX},{Y0+DY} L{X1},{Y0} Z'
    side = f'M{X1},{Y0} L{X1+DX},{Y0+DY} L{X1+DX},{Y1+DY} L{X1},{Y1} Z'
    a.append(f'<clipPath id="front"><path d="{front}"/></clipPath><clipPath id="side"><path d="{side}"/></clipPath>')
    # side face (darker)
    a.append(wash(side, C['soil2'], 3, 1))
    a.append(f'<g clip-path="url(#side)">{glaze(X1, Y0-100, X1+DX, Y1, C["dark"], 5, 31, 0.3, 30, 60)}'
             f'<g filter="url(#wc5)" style="mix-blend-mode:multiply">{"".join(crumbs(X1+95, Y0+150, 70, 200, 26, C["dark"], 32, 5, 10))}</g></g>')
    # top face: grass
    a.append(wash(top, C['grass'], 4, 0.85))
    a.append(glaze(X0+40, Y0+DY+10, X1+DX-40, Y0-10, C['green'], 6, 33, 0.25, 30, 70))
    # front face soil
    inner = []
    inner.append(wash(front, C['soil'], 6, 1))
    inner.append(glaze(X0, Y0, X1, Y1, C['soil2'], 12, 34, 0.32, 40, 90))
    # burrow (open tunnel) from surface down
    bur = smooth([(560, Y0-5), (575, 700), (540, 800), (585, 900), (560, 1000), (575, 1060)])
    inner.append(f'<path d="{bur}" fill="none" stroke="{C["dark"]}" stroke-width="30" stroke-linecap="round" opacity="0.55" filter="url(#soft)"/>')
    # roots from plant
    roots = []
    rx = 300
    for k in range(9):
        pts = [(rx, Y0)]
        x, y = rx, Y0
        ang = math.radians(90 + R.uniform(-55, 55))
        for j in range(5):
            x += math.cos(ang) * R.uniform(40, 70); y += math.sin(ang) * R.uniform(40, 70)
            ang += math.radians(R.uniform(-25, 25)); pts.append((x, y))
        roots.append(line(smooth(pts), '#efe2c8', 3.2 - k * 0.15, 0.9))
    inner.append(''.join(roots))
    # fungal hyphae (fine branching cream threads)
    for k in range(7):
        x, y = R.uniform(120, 720), R.uniform(700, 1000)
        pts = [(x, y)]
        for j in range(6):
            x += R.uniform(-40, 40); y += R.uniform(-30, 30); pts.append((x, y))
        inner.append(line(smooth(pts), '#f7efe0', 1.3, 0.85))
    # aggregates (crumbs) and air pores
    inner.append(f'<g filter="url(#wc7)" style="mix-blend-mode:multiply">{"".join(crumbs(420, 830, 320, 200, 120, C["dark"], 35, 8, 17))}</g>')
    for k in range(34):
        x, y = R.uniform(110, 740), R.uniform(640, 1020)
        inner.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{R.uniform(6,12):.0f}" ry="{R.uniform(4,7):.0f}" fill="#fff" opacity="0.9" filter="url(#soft)"/>')
    # worms
    inner.append(worm([(565, 840), (580, 900), (560, 960), (572, 1030)], 21))
    inner.append(worm([(130, 760), (200, 730), (270, 760), (320, 800), (380, 790)], 18))
    inner.append(worm([(330, 960), (390, 990), (460, 975), (520, 1000)], 16))
    # tiny critters: nematode + mite
    inner.append(line(smooth([(640, 700), (650, 692), (660, 703), (670, 694), (680, 704)]), '#f7efe0', 2.4))
    inner.append(f'<g filter="url(#pen)"><ellipse cx="210" cy="900" rx="8" ry="6" fill="#f7efe0"/>' +
                 ''.join(f'<path d="M{210+dx},{900} l{dx*0.8:.0f},{6 if k%2 else -6}" stroke="#f7efe0" stroke-width="1.5"/>' for k, dx in enumerate([-6, -3, 3, 6])) + '</g>')
    a.append(f'<g clip-path="url(#front)">{"".join(inner)}</g>')
    # plant on top
    a.append(line(f'M300,{Y0} C300,540 296,500 306,440', C['green'], 5))
    for (lx, ly, an) in [(285, 520, -150), (322, 480, -30), (290, 455, -140), (325, 430, -50)]:
        a.append(leaf(lx, ly, 0.9, an, C['grass'], 2))
    # grass tufts on top edge
    gr = []
    for k in range(70):
        t = R.random(); u = R.random()
        bx = X0 + t * (X1 - X0) + u * DX; by = Y0 + u * DY
        h = R.uniform(14, 30)
        gr.append(f'<path d="M{bx-3:.0f},{by:.0f} Q{bx:.0f},{by-h*0.6:.0f} {bx+R.uniform(-5,5):.0f},{by-h:.0f} Q{bx+2:.0f},{by-h*0.5:.0f} {bx+3:.0f},{by:.0f} Z" fill="{C["green"]}" opacity="0.6"/>')
    a.append(f'<g filter="url(#wc9)">{"".join(gr)}</g>')
    # block outline
    a.append(line(front, INK, 2.4) + line(f'M{X0},{Y0} L{X0+DX},{Y0+DY} L{X1+DX},{Y0+DY} L{X1+DX},{Y1+DY} L{X1},{Y1} M{X1},{Y0} L{X1+DX},{Y0+DY}', INK, 2.4))
    # worm peeking out of burrow on top
    a.append(worm([(562, Y0+4), (572, 596), (600, 588), (640, 590), (670, 582)], 17, band=False))
    # labels
    a.append(arrow((842, 1100), (600, 1015), 0.15))
    a.append(arrow((185, 1108), (240, 850), -0.2))
    a.append(arrow((430, 1108), (470, 880), 0.15))
    a.append(arrow((150, 470), (262, 690), -0.25))
    texts = [T(70, 68, 940, 'Worms thriving in your soil', 66, 'title'),
             T(72, 162, 960, 'They need good structure to survive, with air pores and aggregates the biology has built. When they are present and happy, it usually means many other beneficial organisms are too.', 29, lh=1.36),
             T(110, 1110, 220, 'Air pores', 30, 'label'),
             T(360, 1110, 260, 'Aggregates', 30, 'label'),
             T(760, 1110, 200, 'Burrows', 30, 'label'),
             T(70, 395, 260, 'Roots, fungi<br>and more', 28, 'label')]
    return a, texts

def s3():
    """Sidewalk after heavy rain: surface scene on top, flooded cross-section below."""
    R = random.Random(21)
    a = []
    GY = 560          # ground surface
    CY0, CY1 = 790, 860   # compaction layer
    # rain cloud + streaks
    for (cx, cy, rx, ry, s) in [(800, 330, 120, 55, 1), (700, 345, 90, 45, 2), (900, 350, 95, 42, 3), (790, 300, 80, 50, 4)]:
        a.append(blob(cx, cy, rx, ry, '#9fb3c2', s, 0.85))
    for k in range(26):
        x = R.uniform(600, 1010); y = R.uniform(400, 520)
        a.append(line(f'M{x:.0f},{y:.0f} l-9,26', C['blue'], 2.4, 0.7))
    # underground block
    ug = f'M40,{GY} L1040,{GY} L1040,1060 L40,1060 Z'
    a.append(f'<clipPath id="ug"><path d="{ug}"/></clipPath>')
    inner = [wash(ug, C['soil'], 5, 1), glaze(40, GY, 1040, 1060, C['soil2'], 10, 41, 0.3, 50, 100)]
    # saturated zone above compaction: blue glaze
    inner.append(wash(f'M40,{GY+60} C300,{GY+70} 700,{GY+50} 1040,{GY+65} L1040,{CY0} L40,{CY0+6} Z', C['sky'], 6, 0.7))
    # compaction layer: dense grey with hatching
    comp = f'M40,{CY0} C300,{CY0-8} 700,{CY0+10} 1040,{CY0-2} L1040,{CY1} C700,{CY1+8} 300,{CY1-8} 40,{CY1+4} Z'
    inner.append(wash(comp, '#6d6460', 7, 1))
    inner.append(''.join(line(f'M{x},{CY0+4} l-30,{CY1-CY0-6}', '#3c3330', 1.6, 0.45) for x in range(70, 1040, 22)))
    # burrows flooded with water, ending on the compaction layer
    for bx in (170, 470, 880):
        p = smooth([(bx, GY), (bx + 14, GY + 80), (bx - 10, GY + 160), (bx + 6, CY0 + 6)])
        inner.append(f'<path d="{p}" fill="none" stroke="{C["dark"]}" stroke-width="30" stroke-linecap="round" opacity="0.5" filter="url(#soft)"/>')
        inner.append(f'<path d="{p}" fill="none" stroke="{C["blue"]}" stroke-width="20" stroke-linecap="round" opacity="0.55" filter="url(#soft)"/>')
    # air bubbles rising in burrows
    for bx in (170, 470, 880):
        for k in range(3):
            inner.append(f'<circle cx="{bx + R.uniform(-4,6):.0f}" cy="{GY + 40 + k*55:.0f}" r="{R.uniform(3,5):.1f}" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.9"/>')
    # deeper soil crumbs below compaction
    inner.append(f'<g filter="url(#wc8)" style="mix-blend-mode:multiply">{"".join(crumbs(540, 960, 480, 80, 60, C["dark"], 42, 6, 12))}</g>')
    # a worm heading up its burrow to escape
    inner.append(worm([(462, 760), (478, 700), (466, 640), (472, GY + 10)], 17))
    a.append(f'<g clip-path="url(#ug)">{"".join(inner)}</g>')
    a.append(line(ug, INK, 2.4))
    # surface: sidewalk slab (left/middle) + lawn (right)
    slab = f'M40,{GY-34} L640,{GY-34} L640,{GY} L40,{GY} Z'
    a.append(wash(slab, '#c9c4bd', 8, 1))
    for x in (240, 440):
        a.append(line(f'M{x},{GY-34} L{x},{GY}', '#7d6f6a', 2))
    a.append(line(slab, INK, 2.4))
    # puddles on the slab top (drawn as flat ellipses just above)
    a.append(blob(150, GY - 40, 70, 9, C['sky'], 9, 0.7))
    a.append(blob(530, GY - 40, 60, 8, C['sky'], 10, 0.7))
    # grass on the right
    gr = []
    for k in range(70):
        x = 650 + k * 5.6 + R.uniform(-2, 2); h = R.uniform(24, 46)
        gr.append(f'<path d="M{x-4:.0f},{GY} Q{x:.0f},{GY-h*0.6:.0f} {x+R.uniform(-8,8):.0f},{GY-h:.0f} Q{x+2:.0f},{GY-h*0.5:.0f} {x+4:.0f},{GY} Z" fill="{C["grass"]}"/>')
    a.append(f'<g filter="url(#wc11)" style="mix-blend-mode:multiply">{"".join(gr)}</g>')
    # worms stranded on the sidewalk
    a.append(worm([(90, GY - 44), (140, GY - 52), (190, GY - 44), (240, GY - 50)], 15))
    a.append(worm([(320, GY - 46), (360, GY - 58), (400, GY - 46), (420, GY - 60)], 14, band=False))
    a.append(worm([(490, GY - 52), (530, GY - 44), (580, GY - 54)], 13, band=False))
    # labels
    a.append(arrow((1000, 1112), (900, CY1 - 20), 0.2))
    a.append(arrow((560, 1112), (480, 700), 0.15))
    a.append(arrow((160, 1112), (180, 690), -0.15))
    texts = [T(70, 68, 940, 'Worms on the sidewalk<br>after heavy rain', 66, 'title'),
             T(72, 232, 520, 'Lots of worms on the sidewalk after rain can mean water is sitting in your soil and filling their burrows.', 29, lh=1.36),
             T(60, 1118, 330, 'Water fills<br>the burrows', 28, 'label'),
             T(440, 1118, 280, 'Burrows<br>flooded', 28, 'label'),
             T(760, 1118, 280, 'Compaction<br>layer', 28, 'label', align='right'),
             T(72, 1240, 760, 'This often signals your soil needs better structure and more organic matter.', 26, color=C['green'], weight=600, lh=1.3)]
    return a, texts

def s4():
    """Worm bins: a bowl of casts and three uses."""
    R = random.Random(31)
    a = []
    # bowl
    bowl = 'M80,560 C90,700 190,770 320,770 C450,770 550,700 560,560 Z'
    # heap of casts above bowl rim
    heap = []
    for k in range(260):
        ang = R.uniform(math.pi, 2 * math.pi)
        rr = math.sqrt(R.random())
        x = 320 + math.cos(ang) * 230 * rr
        y = 562 + math.sin(ang) * 170 * rr
        heap.append((x, y))
    heap.sort(key=lambda p: p[1])
    a.append(wash('M95,565 C120,420 240,385 320,385 C410,385 520,420 545,565 Z', C['soil2'], 3, 0.9))
    pel = []
    for (x, y) in heap:
        col = R.choice(['#5e3e30', '#6a4535', '#4F3433', '#7a5240'])
        pel.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{R.uniform(9,13):.0f}" ry="{R.uniform(7,10):.0f}" fill="{col}" stroke="{INK}" stroke-width="1.3" stroke-opacity="0.55" transform="rotate({R.uniform(-30,30):.0f} {x:.0f} {y:.0f})"/>')
    a.append(f'<g filter="url(#pen)">{"".join(pel)}</g>')
    a.append(wash(bowl, C['wood'], 4, 1))
    a.append(glaze(100, 580, 540, 750, C['soil'], 4, 51, 0.35, 40, 80))
    a.append(line(bowl, INK, 2.6))
    for yy in (610, 660, 705):
        a.append(line(f'M{110 + (yy-600)*0.5:.0f},{yy} Q320,{yy+18} {530 - (yy-600)*0.5:.0f},{yy}', INK, 1.4, 0.35))
    # a worm on the heap
    a.append(worm([(230, 452), (280, 430), (330, 440), (380, 420)], 15))
    # three uses
    cx = [190, 540, 890]; base = 1080
    # 1 pot with seedling and casts on top
    pot = f'M{cx[0]-85},{base-150} L{cx[0]+85},{base-150} L{cx[0]+65},{base} L{cx[0]-65},{base} Z'
    a.append(wash(pot, C['leaf2'], 5, 0.9))
    a.append(wash(f'M{cx[0]-95},{base-175} L{cx[0]+95},{base-175} L{cx[0]+95},{base-145} L{cx[0]-95},{base-145} Z', C['leaf2'], 6, 1))
    a.append(line(pot, INK, 2.4) + line(f'M{cx[0]-95},{base-175} L{cx[0]+95},{base-175} L{cx[0]+95},{base-145} L{cx[0]-95},{base-145} Z', INK, 2.4))
    a.append(cast(cx[0], base - 182, 0.9, '#5e3e30', 8))
    a.append(line(f'M{cx[0]},{base-200} C{cx[0]},{base-240} {cx[0]-4},{base-270} {cx[0]+4},{base-300}', C['green'], 4))
    a.append(leaf(cx[0] - 26, base - 265, 0.8, -150, C['grass'], 2) + leaf(cx[0] + 28, base - 290, 0.8, -30, C['grass'], 3))
    # 2 compost pile with casts sprinkled in
    pile = f'M{cx[1]-140},{base} C{cx[1]-110},{base-150} {cx[1]-40},{base-210} {cx[1]},{base-210} C{cx[1]+50},{base-210} {cx[1]+110},{base-150} {cx[1]+140},{base} Z'
    a.append(wash(pile, C['tan'], 7, 1))
    a.append(glaze(cx[1]-110, base-180, cx[1]+110, base-20, C['soil'], 6, 52, 0.4, 25, 50))
    for k in range(9):
        a.append(leaf(cx[1] + R.uniform(-90, 90), base - R.uniform(30, 160), 0.45, R.uniform(0, 180), R.choice([C['leaf'], C['grass'], C['yellow']]), 1 + k % 9, 0.85, vein=False))
    a.append(line(pile, INK, 2.4))
    a.append(cast(cx[1] - 10, base - 214, 0.8, '#5e3e30', 9))
    # 3 bucket of tea with bubbles
    bk = f'M{cx[2]-85},{base-190} L{cx[2]+85},{base-190} L{cx[2]+68},{base} L{cx[2]-68},{base} Z'
    a.append(wash(bk, '#a9b8bf', 8, 1))
    a.append(blob(cx[2], base - 190, 85, 16, '#8a6a4a', 9, 1))
    a.append(line(bk, INK, 2.4) + line(f'M{cx[2]-85},{base-190} C{cx[2]-85},{base-290} {cx[2]+85},{base-290} {cx[2]+85},{base-190}', INK, 2.4))
    for k in range(6):
        a.append(f'<circle cx="{cx[2] + R.uniform(-55,55):.0f}" cy="{base - 200 - R.uniform(0,60):.0f}" r="{R.uniform(5,10):.0f}" fill="none" stroke="{C["blue"]}" stroke-width="2" opacity="0.7" filter="url(#pen)"/>')
    texts = [T(70, 64, 940, 'What about worm bins?', 36, 'kicker'),
             T(70, 112, 940, 'Handfuls of small, crumbly casts', 64, 'title'),
             T(600, 470, 420, 'You can make vermicompost year-round indoors.', 29, lh=1.36, weight=600, color=C['green']),
             T(cx[0]-150, base + 22, 300, 'Direct<br>compost', 30, 'label', align='center'),
             T(cx[1]-150, base + 22, 300, 'An inoculant<br>for piles', 30, 'label', align='center'),
             T(cx[2]-150, base + 22, 300, 'Teas and<br>extracts', 30, 'label', align='center')]
    return a, texts

def s5():
    """Worms climbing out of the bin."""
    R = random.Random(41)
    a = []
    # bin in 3/4: front face, right side, top opening
    F = (400, 560, 900, 1150); D = (110, -80)
    x0, y0, x1, y1 = F
    front = f'M{x0},{y0} L{x1},{y0} L{x1-20},{y1} L{x0+20},{y1} Z'
    side = f'M{x1},{y0} L{x1+D[0]},{y0+D[1]} L{x1+D[0]-18},{y1+D[1]} L{x1-20},{y1} Z'
    opening = f'M{x0},{y0} L{x0+D[0]},{y0+D[1]} L{x1+D[0]},{y0+D[1]} L{x1},{y0} Z'
    # lid leaning behind
    lid = f'M{x0+D[0]+10},{y0+D[1]} L{x0+D[0]+60},{y0+D[1]-130} L{x1+D[0]+40},{y0+D[1]-130} L{x1+D[0]},{y0+D[1]} Z'
    a.append(wash(lid, '#7f9aa6', 2, 0.9) + line(lid, INK, 2.4))
    a.append(wash(opening, C['soil2'], 3, 1))
    # food heap inside: green scraps
    for k in range(14):
        a.append(leaf(x0 + 140 + R.uniform(0, 330), y0 - 25 + R.uniform(-20, 20), 0.75, R.uniform(0, 180), R.choice([C['grass'], '#8cbf5a', C['green'], C['yellow']]), 1 + k % 11, 0.95, vein=False))
    a.append(wash(side, '#6e8a96', 4, 1))
    a.append(wash(front, C['bin'], 5, 0.95))
    a.append(glaze(x0 + 20, y0 + 20, x1 - 20, y1 - 20, '#4f6b77', 5, 61, 0.3, 50, 90))
    a.append(line(front, INK, 2.6) + line(side, INK, 2.6) + line(opening, INK, 2.6))
    # air holes
    for k in range(6):
        a.append(f'<circle cx="{x0 + 90 + k*64}" cy="{y0 + 60}" r="7" fill="#fff" stroke="{INK}" stroke-width="1.6" filter="url(#pen)"/>')
    # heat squiggles
    for k, hx in enumerate((540, 640, 740)):
        a.append(line(f'M{hx},{y0-70} q14,-22 0,-44 q-14,-22 0,-44 q14,-22 0,-44', '#d65a3a', 3.2, 0.85))
    # worms climbing over the front rim
    a.append(worm([(470, y0 - 30), (480, y0 - 4), (470, y0 + 40), (480, y0 + 110), (468, y0 + 170)], 17))
    a.append(worm([(640, y0 - 26), (660, y0 + 2), (650, y0 + 60), (664, y0 + 120)], 16, band=False))
    a.append(worm([(820, y0 - 20), (845, y0 + 6), (856, y0 + 70), (840, y0 + 150), (860, y0 + 220)], 17))
    # one already escaped on the floor
    a.append(worm([(300, 1170), (240, 1150), (180, 1170), (120, 1160)], 16, band=False))
    texts = [T(70, 68, 940, 'Worms climbing out<br>of the worm bin?', 66, 'title'),
             T(72, 250, 330, 'Low oxygen or too much heat from fresh, high-nitrogen food added in high quantities is sending them looking for an exit.', 29, lh=1.36),
             T(72, 760, 300, 'Slow down the feeding and let them cool off.', 36, 'title', color=C['green'], lh=1.1)]
    return a, texts

def s6():
    """Smaller worms in cooler months: a ruler for scale, babies and cocoons, snow."""
    R = random.Random(51)
    a = []
    # snowflakes
    for k in range(16):
        x, y = R.uniform(80, 1000), R.uniform(390, 600)
        s = R.uniform(8, 18)
        flake = ''.join(f'M{x - math.cos(t)*s:.1f},{y - math.sin(t)*s:.1f} L{x + math.cos(t)*s:.1f},{y + math.sin(t)*s:.1f} ' for t in (0, math.pi/3, 2*math.pi/3))
        a.append(line(flake, C['blue'], 2.2, 0.7))
    # ground with frost: low wash strip
    a.append(wash('M40,1010 C300,995 700,1020 1040,1000 L1040,1110 L40,1110 Z', C['soil'], 3, 0.9))
    a.append(glaze(60, 1010, 1020, 1100, C['soil2'], 6, 71, 0.35, 40, 80))
    a.append(wash('M40,1000 C300,988 700,1012 1040,994 L1040,1016 C700,1030 300,1006 40,1020 Z', '#dfeaf1', 4, 1))
    # ruler
    rul = 'M80,700 L1000,700 L1000,770 L80,770 Z'
    a.append(wash(rul, C['yellow'], 5, 0.85) + line(rul, INK, 2.4))
    ticks = ''.join(f'M{80 + k*23},700 l0,{22 if k % 5 == 0 else 12} ' for k in range(1, 40))
    a.append(line(ticks, INK, 1.6, 0.8))
    # adult worm resting on the ruler
    a.append(worm([(110, 680), (220, 664), (330, 682), (440, 664), (560, 680)], 24))
    # babies on the ruler, right side
    for (x, y) in [(660, 682), (780, 680), (890, 684)]:
        a.append(worm([(x, y), (x + 22, y - 8), (x + 46, y), (x + 66, y - 6)], 10, band=False))
    # cocoons on the ground
    for (x, y, rot) in [(260, 960, -20), (420, 970, 15), (840, 960, -10)]:
        a.append(f'<g transform="rotate({rot} {x} {y})">' + blob(x, y, 20, 13, '#d8b25a', 6, 1) + f'<ellipse cx="{x}" cy="{y}" rx="20" ry="13" fill="none" stroke="{INK}" stroke-width="2" filter="url(#pen)"/>' + line(f'M{x+20},{y} l10,0 M{x-20},{y} l-10,0', INK, 2) + '</g>')
    a.append(worm([(560, 975), (580, 965), (600, 975), (616, 968)], 9, band=False))
    a.append(arrow((330, 870), (275, 940), -0.2))
    a.append(arrow((780, 870), (620, 955), 0.2))
    a.append(arrow((780, 800), (780, 700), 0.15))
    texts = [T(70, 68, 940, 'Smaller worms<br>in cooler months', 66, 'title'),
             T(72, 232, 900, 'This isn’t an issue. Many are babies that have just hatched, and they grow slowly until warm weather speeds them up.', 30, lh=1.36),
             T(200, 820, 300, 'Cocoons', 30, 'label'),
             T(800, 800, 240, 'Just<br>hatched', 30, 'label'),
             ]
    return a, texts

def s7():
    """Fun fact: a lens on the leaf surface shows what the worm is really eating."""
    R = random.Random(61)
    a = []
    LX, LY, LR = 640, 820, 300
    # big leaf lower-left with a bite taken, worm taking a bite
    lf = 'M60,1250 C120,1040 300,960 470,980 C440,1150 260,1260 60,1250 Z'
    a.append(wash(lf, C['leaf'], 3, 1) + line('M60,1250 C200,1130 330,1040 470,980', INK, 1.8, 0.5))
    a.append(f'<circle cx="300" cy="1150" r="34" fill="#fff"/>')
    a.append(line(lf, INK, 2.2))
    a.append(worm([(80, 1010), (140, 1060), (200, 1090), (262, 1140)], 22))
    # lens contents
    a.append(f'<clipPath id="lens"><circle cx="{LX}" cy="{LY}" r="{LR}"/></clipPath>')
    inner = [wash(f'M{LX-LR-30},{LY-LR-30} L{LX+LR+30},{LY-LR-30} L{LX+LR+30},{LY+LR+30} L{LX-LR-30},{LY+LR+30} Z', '#f0c58a', 4, 1),
             glaze(LX-LR, LY-LR, LX+LR, LY+LR, C['leaf'], 9, 81, 0.45, 50, 110)]
    # leaf veins
    inner.append(line(f'M{LX-LR},{LY+120} C{LX-100},{LY+60} {LX+100},{LY-20} {LX+LR},{LY-120}', '#b8742f', 6, 0.6))
    # fungi: branching hyphae
    for k in range(5):
        x, y = LX - 220 + k * 60, LY + 160 - k * 30
        pts = [(x, y)]
        for j in range(6):
            x += R.uniform(15, 45); y -= R.uniform(10, 40); pts.append((x, y))
            if j in (2, 4):
                inner.append(line(f'M{x:.0f},{y:.0f} l{R.uniform(-40,40):.0f},{R.uniform(-40,-10):.0f}', '#ffffff', 2.6, 0.95))
        inner.append(line(smooth(pts), INK, 5, 0.35))
        inner.append(line(smooth(pts), '#ffffff', 3, 1))
    # bacteria: tiny rods and dots
    for k in range(60):
        x, y = R.uniform(LX - 140, LX + 260), R.uniform(LY - 260, LY - 60)
        ang = R.uniform(0, 180)
        inner.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="13" height="6" rx="3" fill="{C["purple"]}" opacity="0.8" transform="rotate({ang:.0f} {x:.0f} {y:.0f})"/>')
    # protozoa: amoeba + ciliate
    am = [(LX + 120 + math.cos(t) * r_, LY + 120 + math.sin(t) * r_ * 0.8) for t, r_ in zip([k * math.pi / 4 for k in range(8)], [52, 38, 60, 34, 56, 40, 64, 36])]
    inner.append(wash(smooth(am, True), C['blue'], 7, 0.7) + line(smooth(am, True), INK, 2))
    inner.append(f'<circle cx="{LX+120}" cy="{LY+120}" r="11" fill="{C["blue"]}" opacity="0.8"/>')
    inner.append(wash(f'cx="{LX-150}" cy="{LY-60}" rx="46" ry="28"', '#8fb8a0', 8, 0.9, tag='ellipse') +
                 f'<ellipse cx="{LX-150}" cy="{LY-60}" rx="46" ry="28" fill="none" stroke="{INK}" stroke-width="2" filter="url(#pen)"/>' +
                 line(''.join(f'M{LX-150 + 46*math.cos(t):.0f},{LY-60 + 28*math.sin(t):.0f} l{8*math.cos(t):.0f},{8*math.sin(t):.0f} ' for t in [k * math.pi / 9 for k in range(18)]), INK, 1.3))
    # nematode
    nem = smooth([(LX - 40, LY + 240), (LX + 10, LY + 200), (LX + 60, LY + 240), (LX + 110, LY + 200), (LX + 160, LY + 230)])
    inner.append(f'<path d="{nem}" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" filter="url(#pen)"/><path d="{nem}" fill="none" stroke="#f6efe2" stroke-width="9" stroke-linecap="round" filter="url(#pen)"/>')
    a.append(f'<g clip-path="url(#lens)">{"".join(inner)}</g>')
    # lens rim + handle
    a.append(f'<circle cx="{LX}" cy="{LY}" r="{LR}" fill="none" stroke="{INK}" stroke-width="12" filter="url(#pen)"/>')
    a.append(f'<circle cx="{LX}" cy="{LY}" r="{LR-9}" fill="none" stroke="#fff" stroke-width="3" opacity="0.7"/>')
    a.append(line(f'M{LX-LR*0.66:.0f},{LY+LR*0.72:.0f} L{LX-LR*0.66-70:.0f},{LY+LR*0.72+70:.0f}', INK, 0.1))  # anchor
    # labels around the lens
    a.append(arrow((150, 600), (520, 880), 0.15))
    a.append(arrow((950, 485), (800, 600), -0.2))
    a.append(arrow((940, 1120), (790, 970), 0.2))
    a.append(arrow((560, 1225), (650, 1050), -0.2))
    texts = [T(70, 64, 940, 'Fun fact', 36, 'kicker'),
             T(70, 112, 960, 'Worms lean on microbes to break down leaves', 56, 'title'),
             T(72, 290, 940, 'They take a bite and feed on the bacteria, fungi, protozoa and nematodes living on the surface of those foods.', 29, lh=1.36),
             T(860, 440, 200, 'Bacteria', 30, 'label'),
             T(870, 1125, 180, 'Protozoa', 30, 'label'),
             T(450, 1230, 220, 'Nematodes', 30, 'label'),
             T(70, 560, 220, 'Fungi', 30, 'label')]
    return a, texts

def s8():
    """Leave the leaves + comment prompt."""
    R = random.Random(71)
    a = []
    # falling leaves through the middle
    for k in range(9):
        x, y = 120 + k * 105 + R.uniform(-30, 30), R.uniform(560, 760)
        a.append(leaf(x, y, R.uniform(0.7, 1.1), R.uniform(0, 360), R.choice([C['leaf'], C['leaf2'], C['yellow']]), 1 + k % 11, 0.9))
    # ground
    a.append(wash('M40,1090 C300,1080 700,1100 1040,1085 L1040,1180 L40,1180 Z', C['soil'], 3, 0.95))
    # leaf pile
    pile = []
    for k in range(70):
        x = R.uniform(120, 960); y = 1080 - abs(R.gauss(0, 1)) * 60 - (1 - abs(x - 540) / 460) * 110 * R.random()
        pile.append(leaf(x, y, R.uniform(0.8, 1.2), R.uniform(0, 360), R.choice([C['leaf'], C['leaf2'], C['yellow'], '#b5823d']), 1 + k % 12, 0.95))
    a.append(''.join(pile))
    # worm peeking out of the pile
    a.append(worm([(560, 1060), (565, 990), (590, 945), (630, 930)], 22))
    texts = [T(70, 68, 940, 'Leave the leaves<br>where they land', 66, 'title'),
             T(72, 232, 920, 'Worms are part of the soil food web, working alongside the microbes. That makes the fallen leaves in your yard their dinner table.', 30, lh=1.36),
             T(72, 420, 920, 'Next time you rake, leave a corner of leaves for the worms.', 34, 'title', weight=500, color=C['green'], lh=1.2)]
    return a, texts
