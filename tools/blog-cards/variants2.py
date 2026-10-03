"""Ten tablet (1024x768) designs for Soil Health Week 2025, round two.

Built only from devices the brand already uses:
  the approved trifold brochure  gradient colour bands (accent to its deep tone
                                 at 158deg), white spaced-capital eyebrow over a
                                 white Montserrat headline, photos clipped by one
                                 gentle curve, italic Garamond captions
  the website (css/site.css)     white page, cream as a bounded shape, the pale
                                 green specimen case with hairline partitions,
                                 plates with Fig. numbers, real organism cut-outs
                                 floating in white space, seed-shaped buttons,
                                 hairline strata, Soil Brown headings
Linnea's black READ POST box with the cursor stays on every one.
"""
import os, sys, math
OUT = sys.argv[1]
sys.argv = [sys.argv[0], OUT]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B
from PIL import Image, ImageOps, ImageDraw
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

W, H = 1024, 768
PX = B.PX
POST = next(p for p in B.POSTS if p['slug'] == 'soil-health-week-pakistan')
B._CURRENT['slug'] = POST['slug']
SRC = ImageOps.exif_transpose(Image.open(B.photo_for(POST))).convert('RGB')
TMP = B.TMP
REPO = B.REPO

GREEN, MOSS, SOIL, CREAM, CASE, INK, FAINT = '#156826', '#22371F', '#4F3433', '#F4F1EA', '#E6EADC', '#231F1D', '#6A665C'
HEAD, DECK, EYE, CAP = 44, 20, 14, 15      # the four sizes, the same on all ten
CAPTION = 'Soil Health Week 2025, Pakistan.'

def rgb(h): return RGBColor(*B.hexrgb(h))

def band(s, x, y, w, h, c1, c2, name='Band'):
    # the brochure's panel band: the accent into its deeper tone
    sh = s.shapes.add_shape(1, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
    sh.name = name; sh.line.fill.background(); sh.shadow.inherit = False
    f = sh.fill; f.gradient(); f.gradient_angle = 68
    st = f.gradient_stops; st[0].color.rgb = rgb(c1); st[0].position = 0; st[1].color.rgb = rgb(c2); st[1].position = 1
    return sh

def photo(s, name, x, y, w, h, curve=None, radius=0):
    """The whole photograph, faces kept. curve='bottom'|'top'|'left' clips one
    edge with the brochure's single gentle wave."""
    k = max(1, min(2, min(SRC.width / w, SRC.height / h)))
    im = B.cover(SRC, int(w * k), int(h * k), POST['focus'])
    if curve or radius:
        mask = Image.new('L', im.size, 0); d = ImageDraw.Draw(mask)
        if radius:
            d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=int(radius * k), fill=255)
        else:
            amp = (h if curve != 'left' else w) * .09 * k
            pts = []
            if curve in ('bottom', 'top'):
                for i in range(101):
                    t = i / 100; xx = t * im.width
                    off = amp * (.55 - .45 * t + .35 * math.sin(math.pi * t))
                    pts.append((xx, im.height - off if curve == 'bottom' else off))
                poly = ([(0, 0), (im.width, 0)] + pts[::-1]) if curve == 'bottom' else (pts + [(im.width, im.height), (0, im.height)])
            else:
                for i in range(101):
                    t = i / 100; yy = t * im.height
                    pts.append((amp * (.55 - .45 * t + .35 * math.sin(math.pi * t)), yy))
                poly = pts + [(im.width, im.height), (im.width, 0)]
            d.polygon(poly, fill=255)
        im = im.copy(); im.putalpha(mask)
        path = os.path.join(TMP, f'v2-{name}.png'); im.save(path)
    else:
        path = os.path.join(TMP, f'v2-{name}.jpg'); im.save(path, quality=93, subsampling=0)
    s.shapes.add_picture(path, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX))).name = 'Photo'

def eyebrow(s, x, y, text, colour):
    B.text(s, x, y, 500, EYE * 1.5, text.upper(), 'Montserrat', EYE, colour, 'Eyebrow', bold=True, spacing=EYE * .75 * 22, line=EYE * 1.4)

def headline(s, x, y, w, colour=SOIL, text=None, size=HEAD):
    lines = B.wrap(text or POST['head'], B.font(B.F_CAT, size), w * .95)
    B.text(s, x, y, w, size * 1.12 * len(lines) + 4, '\v'.join(lines), 'Montserrat', size, colour, 'Headline', bold=True, spacing=-size * .75 * 1, line=size * 1.12)
    return y + size * 1.12 * len(lines)

def deck(s, x, y, w, colour=INK):
    lines = B.wrap(POST['deck'], B.font(B.F_HEAD, DECK), w * .95)
    B.text(s, x, y, w, DECK * 1.35 * len(lines) + 4, '\v'.join(lines), 'Source Sans 3', DECK, colour, 'Deck', line=DECK * 1.35)
    return y + DECK * 1.35 * len(lines)

def caption(s, x, y, w, colour=FAINT, text=CAPTION):
    tb = B.text(s, x, y, w, CAP * 1.4, text, 'EB Garamond', CAP, colour, 'Caption', line=CAP * 1.3)
    for r in tb.text_frame.paragraphs[0].runs: r.font.italic = True

def read_post(s, x, y, seed=False, url_colour=INK):
    bh, lab = 44, 22
    bw = B.font(B.F_BTN, lab).getlength('READ POST') + 46
    if seed:
        # the site's seed-shaped button: two opposite corners rounded, leaning like a leaf
        sh = s.shapes.add_shape(152, Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(bw * PX)), Emu(int(bh * PX)))
        B.rgb(sh, INK); sh.name = 'Button'; sh.shadow.inherit = False; sh.adjustments[0] = .5; sh.adjustments[1] = 0
    else:
        B.rect(s, x, y, bw, bh, INK, 'Button')
    B.text(s, x, y, bw, bh, 'READ POST', 'EB Garamond', lab, '#FFFFFF', 'Button label', align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=lab * .75 * 2)
    B.cursor(s, x + bw - 10, y + bh * .55, 28)
    B.text(s, x, y + bh + 7, 400, 18, 'www.soilfoodweb.com', 'Source Sans 3', 14, url_colour, 'Web address', line=18)

def logo(s, x, y, size):
    s.shapes.add_picture(os.path.join(REPO, 'img', 'sfwlogo-240.png'), Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(size * PX)), Emu(int(size * PX))).name = 'Logo'

def hair(s, x, y, w, h=1, colour=SOIL, name='Hairline'):
    r = B.rect(s, x, y, w, h, colour, name); return r

DESIGNS = []
def design(title):
    def deco(fn): DESIGNS.append((title, fn)); return fn
    return deco

@design('1 Brochure panel: band, curve, caption')
def d1(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    band(s, 0, 0, W, 190, GREEN, MOSS)
    eyebrow(s, 56, 52, POST['cat'], '#FFFFFFDB'[:7])
    headline(s, 56, 80, 700, '#FFFFFF')
    photo(s, 'd1', 0, 190, W, 370, curve='bottom')
    caption(s, 56, 570, 600)
    deck(s, 56, 612, 560)
    read_post(s, 760, 612)

@design('2 Brochure panel, turned on its side')
def d2(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    band(s, 0, 0, 430, H, GREEN, MOSS)
    eyebrow(s, 48, 150, POST['cat'], '#FFFFFF')
    y = headline(s, 48, 180, 340, '#FFFFFF')
    deck(s, 48, y + 20, 330, '#FFFFFF')
    photo(s, 'd2', 400, 0, 624, H, curve='left')
    read_post(s, 48, 560)
    caption(s, 48, 690, 330, '#FFFFFF')

@design('3 Brochure cover: masthead, curve, big headline')
def d3(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    B.rect(s, 0, 0, W, 110, CASE, 'Masthead')
    logo(s, 40, 13, 84)
    B.text(s, 140, 26, 400, 60, 'Soil Food Web\vFoundation', 'Montserrat', 22, SOIL, 'Wordmark', bold=True, line=25)
    eyebrow(s, 700, 48, POST['cat'], GREEN)
    photo(s, 'd3', 0, 110, W, 400, curve='bottom')
    y = headline(s, 48, 520, 620, size=54)
    deck(s, 48, y + 10, 600)
    read_post(s, 760, 560)

@design('4 Specimen case: plate on pale green, hairline drawer')
def d4(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    B.rect(s, 32, 32, W - 64, H - 64, CASE, 'Case')
    hair(s, 560, 32, 1, H - 64, name='Partition')
    hair(s, 32, 600, 528, 1, name='Partition')
    photo(s, 'd4', 592, 64, 400, 560)
    caption(s, 592, 634, 400, INK, 'Fig. 01  Soil Health Week 2025, Pakistan.')
    eyebrow(s, 72, 88, POST['cat'], GREEN)
    y = headline(s, 72, 118, 450)
    deck(s, 72, y + 18, 440)
    read_post(s, 72, 634)

@design('5 A specimen in the margin: real ciliate cut-out')
def d5(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd5', 470, 56, 510, 600, radius=8)
    caption(s, 470, 668, 510)
    cut = Image.open(os.path.join(REPO, 'img', 'uploads', '3.png')).convert('RGBA')
    cw_ = 190; chh = int(cut.height * cw_ / cut.width)
    s.shapes.add_picture(os.path.join(REPO, 'img', 'uploads', '3.png'), Emu(int(64 * PX)), Emu(int(58 * PX)), Emu(int(cw_ * PX)), Emu(int(chh * PX))).name = 'Specimen'
    caption(s, 64, 64 + chh, 300, FAINT, 'A ciliate, from the Foundation’s microscopy.')
    eyebrow(s, 64, 300, POST['cat'], GREEN)
    y = headline(s, 64, 330, 370)
    deck(s, 64, y + 16, 360)
    read_post(s, 64, 600)

@design('6 The wave: photo above, white below')
def d6(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd6', 0, 0, W, 470, curve='bottom')
    eyebrow(s, 56, 486, POST['cat'], GREEN)
    headline(s, 56, 514, 560)
    deck(s, 56, 580, 520)
    read_post(s, 760, 520)
    caption(s, 760, 640, 240)

@design('7 Strata: three bands and hairlines')
def d7(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd7', 0, 0, W, 400)
    hair(s, 0, 400, W, 2, SOIL, 'Rule')
    eyebrow(s, 56, 428, POST['cat'], GREEN)
    headline(s, 56, 456, 600)
    deck(s, 56, 520, 560)
    read_post(s, 760, 460)
    band(s, 0, 640, W, 128, GREEN, MOSS, 'Foot')
    B.text(s, 56, 668, 600, 80, 'Healing soil.\vFeeding humanity.\vRestoring the living world.', 'Montserrat', 18, '#FFFFFF', 'Tagline', bold=True, line=23)
    # the roundel goes muddy on green, so dark grounds take the wordmark in white (site.css does the same)
    B.text(s, 700, 672, 280, 60, 'Soil Food Web\vFoundation', 'Montserrat', 20, '#FFFFFF', 'Wordmark', bold=True, line=24, align=PP_ALIGN.RIGHT)

@design('8 Homepage hero: text beside photo, seed button')
def d8(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    photo(s, 'd8', 430, 64, 546, 600, radius=8)
    caption(s, 430, 676, 546)
    eyebrow(s, 56, 170, POST['cat'], GREEN)
    y = headline(s, 56, 200, 340, size=48)
    tb = B.text(s, 56, y + 16, 340, 90, '\v'.join(B.wrap(POST['deck'], B.font('EBGaramond-Italic.ttf', 22), 330)), 'EB Garamond', 22, SOIL, 'Lede', line=28)
    for r in tb.text_frame.paragraphs[0].runs: r.font.italic = True
    read_post(s, 56, 520, seed=True)

@design('9 Cream card behind, photo overhanging')
def d9(s):
    B.rect(s, 0, 0, W, H, '#FFFFFF', 'Page')
    B.rect(s, 380, 120, 600, 560, CREAM, 'Cream shape')
    photo(s, 'd9', 440, 64, 500, 520, radius=8)
    caption(s, 440, 600, 500)
    eyebrow(s, 56, 150, POST['cat'], GREEN)
    y = headline(s, 56, 180, 320)
    deck(s, 56, y + 16, 300)
    read_post(s, 56, 560)

@design('10 Brochure foot: photo curving into green')
def d10(s):
    band(s, 0, 0, W, H, GREEN, MOSS, 'Green')
    photo(s, 'd10', 0, 0, W, 450, curve='bottom')
    eyebrow(s, 56, 486, POST['cat'], '#FFFFFF')
    y = headline(s, 56, 514, 600, '#FFFFFF')
    deck(s, 56, y + 12, 560, '#FFFFFF')
    read_post(s, 780, 520, url_colour='#FFFFFF')
    caption(s, 780, 636, 220, '#FFFFFF')

if __name__ == "__main__":
  prs = Presentation(); prs.slide_width, prs.slide_height = Emu(W * PX), Emu(H * PX)
  for title, fn in DESIGNS:
      sl = prs.slides.add_slide(prs.slide_layouts[6]); fn(sl)
      sl.notes_slide.notes_text_frame.text = title
  out = os.path.join(OUT, 'Tablet-headers-soil-health-week-round-2.pptx')
  prs.save(out); print(out)
