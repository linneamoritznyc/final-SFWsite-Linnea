"""Ten tablet (1024x768) designs for one post, Soil Health Week 2025.

Linnea's type on all ten: the category as a big bold Montserrat word, the
headline in Source Sans 3, the line under it, the black READ POST box in
EB Garamond with the cursor, and www.soilfoodweb.com. What changes is the
art direction around it. One slide per design, every piece its own layer.
"""
import os, sys, math
OUT = sys.argv[1]
sys.argv = [sys.argv[0], OUT]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from PIL import Image, ImageOps, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.util import Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

W, H = 1024, 768
PX = B.PX
POST = next(p for p in B.POSTS if p['slug'] == 'soil-health-week-pakistan')
B._CURRENT['slug'] = POST['slug']
SRC = ImageOps.exif_transpose(Image.open(B.photo_for(POST))).convert('RGB')
TMP = B.TMP
BIG, SMALL = 50, 20          # the whole set uses these two sizes
GREEN, MOSS, GLOW, CREAM, SAGE, TAN, INK = '#156826', '#22371F', '#DBE6A7', '#F4F1EA', '#A7B097', '#C89B7B', B.INK

def photo(slide, name, x, y, w, h, focus=(.5, .45), treat=None, border=0, rot=0):
    k = max(1, min(2, min(SRC.width / w, SRC.height / h)))
    im = B.cover(SRC, int(w * k), int(h * k), focus)
    if treat: im = treat(im)
    if border:
        b = int(border * k)
        framed = Image.new('RGB', (im.width + 2 * b, im.height + 2 * b), (255, 255, 255))
        framed.paste(im, (b, b)); im = framed
        x, y, w, h = x - border, y - border, w + 2 * border, h + 2 * border
    path = os.path.join(TMP, f'var-{name}.jpg'); im.save(path, quality=93, subsampling=0)
    pic = slide.shapes.add_picture(path, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
    pic.name = 'Photo'
    if rot: pic.rotation = rot
    return pic

def png(slide, im, name, x, y, w, h):
    path = os.path.join(TMP, f'var-{name}.png'); im.save(path)
    slide.shapes.add_picture(path, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX))).name = name

def type_block(slide, x, y, w, ink=INK, cat_colour=INK, btn='black', cat_size=BIG, head_size=BIG):
    """The same stack on every design. Returns the y it ends at."""
    B.text(slide, x, y, w, cat_size * 1.1, POST['cat'], 'Montserrat', cat_size, cat_colour, 'Category', bold=True, spacing=-cat_size * .75 * 3, line=cat_size)
    y += cat_size * 1.08
    hl = B.wrap(POST['head'], B.font(B.F_HEAD, head_size), w * .95)
    B.text(slide, x, y, w, head_size * len(hl) + 4, '\v'.join(hl), 'Source Sans 3', head_size, ink, 'Headline', spacing=-head_size * .75 * 4, line=head_size)
    y += head_size * len(hl) + SMALL * .6
    dl = B.wrap(POST['deck'], B.font(B.F_HEAD, SMALL), w * .9)
    B.text(slide, x + 2, y, w * .9, SMALL * 1.25 * len(dl) + 4, '\v'.join(dl), 'Source Sans 3', SMALL, ink, 'Deck', line=SMALL * 1.25)
    y += SMALL * 1.25 * len(dl) + SMALL * 1.2
    return button(slide, x, y, ink, btn)

def button(slide, x, y, ink=INK, style='black'):
    bh = SMALL * 2.0
    bw = B.font(B.F_BTN, SMALL * 1.1).getlength('READ POST') + SMALL * 2.2
    fill, label = (INK, '#FFFFFF') if style == 'black' else (CREAM, INK)
    r = B.rect(slide, x, y, bw, bh, fill, 'Button')
    if style == 'outlined':
        r.line.color.rgb = B.RGBColor(255, 255, 255); r.line.width = Emu(int(2 * PX))
    B.text(slide, x, y, bw, bh, 'READ POST', 'EB Garamond', SMALL * 1.1, label, 'Button label', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=SMALL * .75 * 2)
    B.cursor(slide, x + bw - SMALL * .5, y + bh * .55, SMALL * 1.5)
    B.text(slide, x, y + bh + SMALL * .3, 400, SMALL, 'www.soilfoodweb.com', 'Source Sans 3', SMALL * .7, ink, 'Web address', line=SMALL)
    return y + bh + SMALL * 1.3

def paper(slide, name, x, y, w, h):
    path = B.torn_paper('var', name, w, h)
    m = B.PAPER_MARGIN
    slide.shapes.add_picture(path, Emu(int((x - m) * PX)), Emu(int((y - m) * PX)), Emu(int((w + 2 * m) * PX)), Emu(int((h + 2 * m) * PX))).name = 'Paper'

def duotone(dark, light):
    def f(im):
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
        return ImageOps.colorize(g, B.hexrgb(dark), B.hexrgb(light))
    return f

DESIGNS = []
def design(title):
    def deco(fn): DESIGNS.append((title, fn)); return fn
    return deco

@design('1 Paper collage')
def d1(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd1', 500, 0, 524, 768, focus=(.62, .45))
    paper(s, 'd1', 36, 170, 500, 430)
    type_block(s, 76, 210, 430)

@design('2 Full bleed, paper on top')
def d2(s):
    photo(s, 'd2', 0, 0, W, H, focus=(.5, .4))
    paper(s, 'd2', 40, 360, 620, 370)
    type_block(s, 80, 396, 540)

@design('3 Food Web Green split')
def d3(s):
    B.rect(s, 0, 0, W, H, GREEN, 'Green field')
    photo(s, 'd3', 470, 0, 554, 768, focus=(.62, .45))
    type_block(s, 56, 200, 380, ink='#FFFFFF', cat_colour=GLOW)

@design('4 Poster: the word carries it')
def d4(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd4', 0, 0, W, 450, focus=(.5, .35))
    B.text(s, 40, 440, 600, 170, POST['cat'], 'Montserrat', 150, INK, 'Category', bold=True, spacing=-150 * .75 * 4, line=150)
    B.text(s, 44, 610, 560, BIG * 2, POST['head'], 'Source Sans 3', BIG, INK, 'Headline', spacing=-BIG * .75 * 4, line=BIG)
    dl = B.wrap(POST['deck'], B.font(B.F_HEAD, SMALL), 330)
    B.text(s, 650, 500, 330, SMALL * 1.25 * len(dl) + 4, '\v'.join(dl), 'Source Sans 3', SMALL, INK, 'Deck', line=SMALL * 1.25)
    button(s, 650, 630)

@design('5 The print, taped down')
def d5(s):
    B.rect(s, 0, 0, W, H, CREAM, 'Page')
    photo(s, 'd5', 520, 150, 440, 400, focus=(.55, .45), border=16, rot=3)
    tape = Image.new('RGBA', (150, 40), (214, 196, 160, 190)).rotate(-6, expand=True)
    png(s, tape, 'd5-tape', 660, 118, tape.width, tape.height)
    type_block(s, 56, 190, 420)

@design('6 Duotone, moss and glow')
def d6(s):
    B.rect(s, 0, 0, W, H, MOSS, 'Moss field')
    photo(s, 'd6', 0, 0, 600, H, focus=(.45, .45), treat=duotone(MOSS, GLOW))
    c = B.rrect(s, 560, 110, 420, 548, CREAM, 'Card', 12); B.soft_shadow(c)
    type_block(s, 596, 160, 350)

@design('7 Giant word over the picture')
def d7(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd7', 0, 200, W, 568, focus=(.5, .4))
    B.text(s, 24, 20, 1000, 240, POST['cat'], 'Montserrat', 250, INK, 'Category', bold=True, spacing=-250 * .75 * 5, line=250)
    # a torn strip along the foot, below the faces
    paper(s, 'd7', 28, 626, 968, 118)
    B.text(s, 60, 648, 420, BIG + 4, POST['head'], 'Source Sans 3', BIG * .8, INK, 'Headline', spacing=-BIG * .75 * 4, line=BIG * .8)
    dl = B.wrap(POST['deck'], B.font(B.F_HEAD, SMALL * .9), 300)
    B.text(s, 460, 652, 300, SMALL * 1.2 * len(dl) + 4, '\v'.join(dl), 'Source Sans 3', SMALL * .9, INK, 'Deck', line=SMALL * 1.2)
    button(s, 800, 650)

@design('8 Magazine cover')
def d8(s):
    photo(s, 'd8', 0, 0, W, H, focus=(.5, .4))
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for yy in range(H):
        a = int(max(0, (yy - H * .42) / (H * .58)) ** 1.4 * 200)
        d.line([(0, yy), (W, yy)], fill=(20, 19, 18, a))
    for yy in range(160):
        d.line([(0, yy), (W, yy)], fill=(20, 19, 18, int((1 - yy / 160) * 120)))
    png(s, g, 'd8-shade', 0, 0, W, H)
    B.text(s, 44, 30, 700, 110, POST['cat'], 'Montserrat', 96, '#FFFFFF', 'Category', bold=True, spacing=-96 * .75 * 4, line=96)
    B.text(s, 46, 520, 700, BIG * 1.2, POST['head'], 'Source Sans 3', BIG + 10, '#FFFFFF', 'Headline', spacing=-(BIG + 10) * .75 * 4, line=BIG + 10)
    dl = B.wrap(POST['deck'], B.font(B.F_HEAD, SMALL), 560)
    B.text(s, 48, 588, 560, SMALL * 1.25 * len(dl) + 4, '\v'.join(dl), 'Source Sans 3', SMALL, '#FFFFFF', 'Deck', line=SMALL * 1.25)
    button(s, 46, 660, ink='#FFFFFF', style='outlined')

@design('9 Editorial page')
def d9(s):
    B.rect(s, 0, 0, W, H, CREAM, 'Page')
    B.rect(s, 48, 60, 928, 3, INK, 'Rule top')
    B.text(s, 48, 74, 600, 24, 'SOIL FOOD WEB FOUNDATION  ·  22 OCTOBER 2025', 'Source Sans 3', 15, INK, 'Masthead', spacing=15 * .75 * 15)
    B.rect(s, 48, 108, 928, 1, INK, 'Rule')
    photo(s, 'd9', 520, 140, 456, 520, focus=(.6, .45))
    B.text(s, 520, 668, 456, 20, 'Wild Soils UK and TrashIt, Pakistan', 'EB Garamond', 15, INK, 'Caption')
    type_block(s, 48, 150, 430)
    B.rect(s, 48, 708, 928, 1, INK, 'Rule bottom')

@design('10 Colour blocks')
def d10(s):
    B.rect(s, 0, 0, W, H, CREAM, 'Page')
    blocks = [(0, 0, 150, 300, SAGE), (0, 300, 150, 468, TAN), (150, 0, 874, 60, GLOW), (874, 60, 150, 708, MOSS), (150, 640, 724, 128, SAGE)]
    for i, (x, y, w, h, c) in enumerate(blocks): B.rect(s, x, y, w, h, c, f'Block {i+1}')
    photo(s, 'd10', 520, 60, 354, 580, focus=(.62, .45))
    for x, y, w, h in [(150, 0, 5, H), (870, 0, 5, H), (150, 58, 724, 5), (150, 638, 724, 5), (0, 298, 150, 5), (517, 60, 5, 580)]:
        B.rect(s, x, y, w, h, INK, 'Line')
    type_block(s, 186, 110, 310, head_size=44, cat_size=46)

prs = Presentation(); prs.slide_width, prs.slide_height = Emu(W * PX), Emu(H * PX)
for title, fn in DESIGNS:
    sl = prs.slides.add_slide(prs.slide_layouts[6]); fn(sl)
    sl.notes_slide.notes_text_frame.text = title
out = os.path.join(OUT, 'Tablet-headers-soil-health-week-10-versions.pptx')
prs.save(out); print(out)
