"""Hand-drawn music notes rising from the piano (frame 3), drawn in code like the arrows."""
import math, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); EW = os.path.dirname(HERE)
sys.path.insert(0, EW)
from lib import defs, wash, line, INK

def head(x, y, s, seed):
    d = f'M{x-11*s:.1f},{y:.1f} C{x-11*s:.1f},{y-9*s:.1f} {x+11*s:.1f},{y-12*s:.1f} {x+11*s:.1f},{y-2*s:.1f} C{x+11*s:.1f},{y+7*s:.1f} {x-11*s:.1f},{y+10*s:.1f} {x-11*s:.1f},{y:.1f} Z'
    return wash(d, INK, seed, 1) + line(d, INK, 2)

def eighth(x, y, s, rot, seed):
    g = head(x, y, s, seed) + line(f'M{x+10*s:.1f},{y-3*s:.1f} L{x+10*s:.1f},{y-52*s:.1f} Q{x+26*s:.1f},{y-40*s:.1f} {x+28*s:.1f},{y-22*s:.1f}', INK, 3)
    return f'<g transform="rotate({rot} {x} {y})">{g}</g>'

def beamed(x, y, s, rot, seed):
    w = 40 * s
    g = (head(x, y, s, seed) + head(x + w, y - 8 * s, s, seed + 1) +
         line(f'M{x+10*s:.1f},{y-3*s:.1f} L{x+10*s:.1f},{y-52*s:.1f} L{x+w+10*s:.1f},{y-60*s:.1f} L{x+w+10*s:.1f},{y-11*s:.1f}', INK, 3) +
         line(f'M{x+10*s:.1f},{y-44*s:.1f} L{x+w+10*s:.1f},{y-52*s:.1f}', INK, 3))
    return f'<g transform="rotate({rot} {x} {y})">{g}</g>'

def notes_svg():
    out = []
    # notes drift up and to the left from the left side of the piano lid
    spec = [(250, 860, 1.5, -10, 'e'), (130, 790, 1.7, 8, 'b'), (390, 800, 1.35, 14, 'e'),
            (80, 650, 1.5, -6, 'e'), (240, 680, 1.8, -12, 'b'), (440, 680, 1.3, 10, 'e'),
            (360, 560, 1.5, -8, 'b'), (120, 520, 1.4, 12, 'e'), (540, 560, 1.2, -14, 'e'),
            (250, 470, 1.25, 6, 'e'), (480, 450, 1.1, 18, 'e')]
    for i, (x, y, s, r, k) in enumerate(spec):
        out.append((eighth if k == 'e' else beamed)(x, y, s, r, 1 + i % 12))
    # two soft sound swirls
    out.append(line('M330,930 C260,880 330,820 260,770 C200,720 270,650 210,600', INK, 2, 0.45))
    out.append(line('M190,930 C150,880 210,840 160,790', INK, 2, 0.45))
    out.append(line('M470,920 C440,870 500,830 460,780', INK, 2, 0.45))
    return ''.join(out)

if __name__ == '__main__':
    import lib
    html = f'''<!doctype html><html><head><style>html,body{{margin:0;width:1080px;height:1920px;background:transparent}}svg{{position:absolute;left:0;top:0}}</style></head><body>
<svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">{defs()}{notes_svg()}</svg></body></html>'''
    open(f'{HERE}/cut/notes.html', 'w').write(html)
    subprocess.run(['node', f'{HERE}/render.js', f'{HERE}/cut/notes.html', f'{HERE}/cut/notes.png', 't'], check=True)
