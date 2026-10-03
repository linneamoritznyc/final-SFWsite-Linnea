"""Soil Health Week 2025, tablet: the two strongest brochure layouts in the
brand's full palette (css/site.css tokens and their --accent-deep pairs).
Legacy Purple stays for Dr. Elaine only, Harvest Gold for Donate only."""
import os, sys
OUT = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], OUT]
import variants2 as V
B = V.B
from pptx import Presentation
from pptx.util import Emu

# name, accent, deep, eyebrow colour on it
PAIRS = [
 ('Food Web Green', '#156826', '#22371F', '#DBE6A7'),
 ('Education Blue', '#3780B8', '#1F4E73', '#FFFFFF'),
 ('Violet (science)', '#6E5C99', '#4C3E70', '#DBE6A7'),
 ('Rust (practice)', '#9C4A24', '#7A3818', '#F4F1EA'),
 ('Soil Brown', '#4F3433', '#231F1D', '#C89B7B'),
 ('Scope', '#3C3841', '#231F1D', '#9E8FC2'),
 ('Olive', '#5F6A3C', '#22371F', '#DBE6A7'),
]
W, H = V.W, V.H

def side(s, name, c1, c2, eye):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    V.band(s, 0, 0, 430, H, c1, c2)
    V.eyebrow(s, 48, 150, V.POST['cat'], eye)
    y = V.headline(s, 48, 180, 340, '#FFFFFF')
    V.deck(s, 48, y + 20, 330, '#FFFFFF')
    V.photo(s, 'p3-' + name, 400, 0, 624, H, curve='left')
    V.read_post(s, 48, 560, url_colour='#FFFFFF')
    V.caption(s, 48, 690, 330, '#FFFFFF')

def foot(s, name, c1, c2, eye):
    V.band(s, 0, 0, W, H, c1, c2, 'Colour')
    V.photo(s, 'p3f-' + name, 0, 0, W, 450, curve='bottom')
    V.eyebrow(s, 56, 486, V.POST['cat'], eye)
    y = V.headline(s, 56, 514, 600, '#FFFFFF')
    V.deck(s, 56, y + 12, 560, '#FFFFFF')
    V.read_post(s, 780, 520, url_colour='#FFFFFF')
    V.caption(s, 780, 636, 220, '#FFFFFF')

def light(s, name, ground, text, eye):
    # the specimen-case colours as a light ground: Living Green, Glow, Membrane
    B.rect(s, 0, 0, W, H, ground, 'Ground')
    V.photo(s, 'p3l-' + name, 400, 0, 624, H, curve='left')
    V.eyebrow(s, 48, 150, V.POST['cat'], eye)
    y = V.headline(s, 48, 180, 340, text)
    V.deck(s, 48, y + 20, 330, text)
    V.read_post(s, 48, 560, url_colour=text)
    V.caption(s, 48, 690, 330, text)

SLIDES = [(side, p) for p in PAIRS] + [(foot, PAIRS[1]), (foot, PAIRS[3]), (foot, PAIRS[5])] + [
 (light, ('Glow', '#DBE6A7', '#3C3841', '#156826')),
 (light, ('Living Green', '#A2AE77', '#22371F', '#22371F')),
 (light, ('Membrane Violet', '#9E8FC2', '#231F1D', '#231F1D')),
 (light, ('Tan', '#C89B7B', '#231F1D', '#4F3433')),
]
prs = Presentation(); prs.slide_width, prs.slide_height = Emu(W * B.PX), Emu(H * B.PX)
for fn, p in SLIDES:
    sl = prs.slides.add_slide(prs.slide_layouts[6]); fn(sl, *p)
    sl.notes_slide.notes_text_frame.text = f'{fn.__name__}: {p[0]}'
out = os.path.join(OUT, 'Tablet-headers-soil-health-week-colours.pptx'); prs.save(out); print(out)
