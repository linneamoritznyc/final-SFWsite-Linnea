# Trifold brochure, build notes

A running log for the six-panel print trifold. Add to this file rather than replacing it.

**Pass 1, 15 September 2026.** First build. Both spreads rendered, inspected at full size,
corrected for overflow and crop, re-rendered. Nothing outside `Trifold Design/` was touched.

---

## What is here

| File | What it is |
| :-- | :-- |
| `outside-spread.png` | Panels 1, 2, 3 left to right. Cover / Story / Teaching. |
| `inside-spread.png` | Panels 4, 5, 6 left to right. Research / Practice / Community. |
| `build/outside.html`, `build/inside.html` | The two spreads as markup. Edit these. |
| `build/trifold.css` | Print stylesheet. Tokens and `@font-face` rules copied from `css/site.css` sections 1 and 2. |
| `build/make-qr.py` | Generates the three QR codes into `build/qr/`. |
| `build/render.js` | Renders both HTML files to the PNGs and reports any panel overflow. |

Rebuild: `python3 "Trifold Design/build/make-qr.py"` then `node "Trifold Design/build/render.js"`,
both from the repository root.

## The publications link, and two things found under it

Allison and Stephanie, in Communications: send people to our own site rather than
to Google Scholar. Done, and both references now point at the same place. Two
things came out from under it that are bigger than the thread.

**1. `soilfoodweb.com/publications` does not exist.** It was on the Research
panel and it was wrong before Google Scholar came into it. This repository, the
Foundation's own site, serves that content at **`/research`**, whose page title
is "Research and publications" and whose lede is "A growing database of soil food
web science: Dr. Elaine Ingham's publications, research from the wider field...".
There is no `/publications` route anywhere in the site or the sitemap.

**2. The domain may be wrong, and it has NOT been changed.** `sitemap.xml` gives
every page of this site as **`soilfoodweb.org/...`**. The brochure's legal block
prints `soilfoodweb.com`, which is what the organisation's own ratified
boilerplate says and what the 216 links in the site's markup use, but almost all
of those are the School's shop: `/courses`, `/bundles`, `/wp-content`. The
Foundation's site and the School's shop appear to be two different domains, and
the brochure prints one of them in the legal block. **Settle this before the
press date.** Printing the wrong domain on the back of a few thousand brochures
is not recoverable.

**What is printed now.** Both references carry `sfw.one/publications`, a Switchy
short link in the same family as the five codes:

    Our story   Her published record, in full, on our site:
                sfw.one/publications
    Research    Her publications and the wider research, item by item:
                sfw.one/publications

**That link does not exist yet and has to be created.** It is the only choice
that is correct now and stays correct after the site moves, because the
destination can be re-pointed without a reprint, and it means the .com against
.org question does not have to be answered before the brochure goes to press.

Nothing is lost by dropping the Google Scholar address from the panel: the site's
own `about-elaine` page carries her publications list and the Google Scholar
profile beside it, so the trail still ends in the same place, through the
Foundation's site first. Which is what was asked for.

---

## Copy pass on the review comments, 17 September 2026

Everything from Allison Duck and from Linnea's own comments on the review
document is in. Listed so it can be checked off against the thread.

**Allison, house style and accuracy.**

| was | is |
| :-- | :-- |
| The **ground** beneath our farms and forests | The **soil** beneath |
| micro-arthropods | microarthropods, APA style, not hyphenated |
| water when it is intact. | water *when it is intact.* |
| mapped **that web** | mapped **the Soil Food Web** |

"microarthropods" appears twice, in the cover lede and in the testate amoeba
caption on Research; both are changed. "Ground" is gone from the piece
altogether: the case study code said "growers filming their own ground" and now
says their own soil.

Her fifth note, replacing "proving" with "implementing", has no target any more.
The sentence she marked, "proving the practice on real land", was the cover body
before Evan's what / how / why / direct action language replaced it a few hours
earlier. **The review document is a snapshot and the artwork has moved past it
in that one paragraph.** "Real land" is gone from there too, for the reason
below, and it now reads "on working land".

**Linnea, things that read wrong.**

- *"what work?"* Our story opened "She founded this work;" with no antecedent.
  The clause is gone: "The Foundation was created in 2025 to carry that teaching
  forward."
- *"weird grammar"* in the climate box. "less fertilizer manufactured and moved,
  fewer passes over the field" is now a sentence: "because less fertilizer has
  to be made and moved, and the field needs fewer passes."
- *"listed with the programs? shouldn't it be inside the programs?"* Now "Dates
  and places go up on the school site", which says where to look.
- *"I really don't like this"* on the Research heading. "The science is real, and
  we are opening it to the world" was defensive, a claim answering an accusation
  nobody made. Now "The science is open, and anyone can test it."
- *"Real land? Of course the land is real"* on the Practice heading. Right, and
  "real growers" had the same problem. Now "Growers are already doing this, at
  every scale", which the panel then proves from a quarter acre to ten thousand.
- *"I don't like this"* on the Practice lede. The telegraphic "a name, a place, a
  year" is now a sentence: "Every result we publish names the grower who got it
  and the year they did."
- *"Is this true?"* on "the method does not change with the acreage". Not
  provably, as written. Now "The steps are the same at every size", which is what
  the panel can actually support.
- *"count again? that doesn't sound very scientific"* Now "measure again", and
  "make the amendment that is missing, apply it" is "add what is missing".
- *"I want more text about the community"* and *"I don't like this sentence, it's
  short and weird"* on "Every role in it is open." That sentence is gone and the
  paragraph gained what members actually do: trade results, work through problems
  together, answer each other's questions.
- *"What can you do in the community?"* The code beside it now lists it:
  "Recordings, live discussion and your questions answered. Free, and open to
  anyone."

One comment is a question rather than an edit and is left as it was: *"Should I
talk about the Directory on the brochure?"* The directory box is still on
Practice. It is the only thing on the piece that names a service without a way to
reach it, which is the open item to settle, not whether to mention it.

The Community panel ran out of room once its paragraph grew, so `--foot-h` came
down from 3.00in to 2.80in. Both closing fields shrink together, so the green
still opens on one line across the crease, now at 5.97in, and Community went from
0.037in of slack to 0.237in.

---

## Evan's mission language on the cover, 17 September 2026

New wording from Evan's mission presentation, approved:

> We show the world **what** is possible through our public webinars... We show
> individuals with the desire to learn **how** to partner with life in the
> soil... We continue to advance our collective understanding through rigorous
> scientific research into **why** things work or do not... We roll up our
> sleeves and get dirty through **direct action**, creating partnerships and
> projects to practice what we preach.

It replaces the cover's body rather than being added to it, because the sentence
that was there was already doing the same job in weaker words: "We carry her
work forward: teaching the science, opening the research, proving the practice,
growing the community." The what / how / why / direct action structure is the
same four things said better, and it is now approved, so the swap costs no space
and the cover keeps its 0.165in of slack.

Two things from the presentation are deliberately not printed:

- **"perhaps the world's foremost teacher".** An unattributed superlative, which
  the brief for this piece rules out by name, and which the presentation itself
  hedges with "perhaps". The brochure says what she did instead: forty-five
  years, Oregon State, first President of the Soil Ecology Society, the USDA's
  Soil Biology Primer, and her publications in full.
- **"SFW teachings".** An acronym, which public copy does not use here.

One thing to decide rather than guess at: the four icons under that paragraph
are still labelled EDUCATION / RESEARCH / PRACTICE / COMMUNITY, and the sentence
above them now runs showing / teaching / researching / direct action. They used
to be the same four in the same order. They still complement each other, but
they are no longer a list and its labels, and Community is the one the sentence
no longer names.

---

## The white hairline along the top trim

A white line about 1/300in wide ran the full width of every panel whose banner
is a gradient, along the top edge of the media box, and down the outer edge
beside the photographs.

It is not in the layout. Chromium's own PDF is clean; **Ghostscript's CMYK
conversion introduces it**, and it does so whatever the downsampling and filter
settings are, which is how that was established:

    chromium RGB inside                top edge:     0 px differ
    after gs CMYK inside               top edge:  2212 px differ

pdfwrite turns a CSS gradient into a shading placed a fraction short of the
element it belongs to, and the sliver shows the panel's white paper through. The
fix is to paint every gradient over a solid of its own first colour, so what
shows through is the band's own green. **Do not remove the second value from
those backgrounds.** Measured over both pages, all four edges, before and after:

    before   top 2212 and 1125, right 379, left 34, all white
    after    zero white pixels on any edge of either page

What is left is a tonal difference of a pixel here and there where a photograph
meets the media edge, which a solid backing cannot fix because the colour it
would need is whatever the photograph happens to be at that point. It sits
0.125in outside the trim and is cut off.

Two things were tried first and did not work, recorded so they are not tried
again: pushing every bleeding element `--overshoot` further out with negative
margins (the token stayed, it is more bleed and harms nothing, and `render.js`
now allows for it so the outer panels do not report a permanent two pixels), and
widening the bleeding photographs past the sheet so the panel would clip them,
which made the outer edge marginally worse and was reverted.

`apply-curve.py` grew a clamp at the same time: with the overshoot the
photographs start a little below 0 and end a little above 1 on the sheet, and a
negative base to a fractional power is a complex number in Python.

---

## The curve, the cover band, and a proof you can fold

**The curve was stale.** The photographs are clipped to one curve drawn across
the sheet, and the clip paths are generated into the markup rather than computed
at render time. When the panels were reordered the clip paths travelled with
their sections, so each photograph was still wearing the segment of the curve
that belonged to its old position. At the Community and cover crease the two
edges met in a V. Nothing was wrong with the geometry; `apply-curve.py` simply
had not been run since the panels moved. It has been now, and the lower edge is
one line across both folds again. **Re-run it after any change to panel order,
panel width, band height or photo height.**

**The cover has a band now.** Teaching and Community open with a colour band
ending at 1.105in and the cover opened with white, so the one horizontal edge
every panel on that sheet could share was the only one not drawn. The masthead
takes the banner's box exactly, in Organic Cream rather than green: the same
band, lighter, because it is the cover. That is also where the pale green shape
that had been asked for belongs, and why it is not a decoration sitting in a
corner. The lockup sits a little higher in its band than centring gave it, so it
lands at about the height of the eyebrows either side.

**HOME-PROOF-cut-and-fold.pdf.** Three fold tests have now failed at the kitchen
table, and the last two failures were as likely to be the fold landing in the
wrong place as the allowance being wrong: the press file carries no crop or fold
marks, because a shop reads the TrimBox, so folding one by hand means guessing
where 3.75in falls on a sheet you cut with scissors. `make-home-proof.py` builds
a separate Letter proof: the trimmed artwork at 94.2%, inside a margin a desktop
printer can reach, with corner crop marks, a cut outline and labelled fold ticks.
Print it at 100%, not fit-to-page, or the marks stop meaning anything. It never
goes to a printer; the press file is unchanged.

---

## Front and back made to line up, 16 September 2026

The cover and Community are the front and the back of the folded piece and sit
side by side on the same sheet, so every horizontal edge on one is read against
the other. Three of them did not match. All three now do, and none of it is done
by eye: the numbers below are measured out of the render on every build.

**The photograph.** The cover's was 1.58in against 1.20in everywhere else, so
its bottom edge sat 0.38in lower than its neighbour's. `--hero-h` is now
`var(--photo-h)`. All three photographs on the sheet end at 2.305in.

**The white.** It follows from the photograph above and the field below, so it
is one band once those two agree.

**The green foot.** Community had none: it ended in white where the cover ended
in the figures field. Its legal block and donation code now sit in a
`.field field--flush field--foot`, and both panels' fields are fixed to
`--foot-h` rather than sized by their own content, so the top edge of the green
is one line across the crease. Both open at 5.75in. Content is bottom-aligned
inside, which is what keeps the two blocks looking set rather than dropped in.
White type inside a bounded field had never been needed before, so the
`.panel--field` reverse-out rules now have `.field` counterparts.

Making the two fields equal cost 0.64in, because Community's foot wanted 3.37in
and the cover could only reach 3.28in. Three things paid for it:

- The cover's body lost the four-item list, which named teaching, research,
  practice and community in a sentence sitting directly on top of four icons
  labelled EDUCATION, RESEARCH, PRACTICE and COMMUNITY. It said the same thing
  twice and the icons say it better.
- The legal block's address lost its first line, "Soil Food Web Foundation",
  which the sentence directly beneath it opens with.
- **The tagline came off Community.** It is still on the cover, 3.75in away on
  the same printed side, and on the folded piece the front carries it. Printing
  it twice on one side of one sheet was the redundancy worth spending. It can go
  back the moment something else gives up 0.42in.

**The lockup is larger.** The mark is 240 x 208, so width sets its height: at
0.62in it stood 0.537in inside a 0.70in box. It is 0.80in now, filling the box
at 0.693in, and the wordmark went 10.2pt to 11.6pt with it.

Ink coverage unchanged at 308%: the green Community's foot gained is the same
green that came off its body.

---

## Third fold test: the tuck allowance, settled at 1/4in

Folded carefully from a cut sheet, the tuck flap still would not sit inside and
had to be trimmed with scissors. That is the second time an allowance from the
published letter-trifold specs has failed on real paper, so the allowance is now
set from the test rather than from the spec sheets.

    was   3.6875  / 3.6875  / 3.625     tuck 1/16in short   bound
    then  3.71875 / 3.71875 / 3.5625    tuck 5/32in short   still bound
    now   3.75    / 3.75    / 3.5       tuck 1/4in short

The asymmetry is deliberate and it only goes one way. A flap that stops a little
shy of the crease is invisible once the piece is closed; a flap that is a little
long is the thing that has now failed twice and had to be cut. 1/4in is at the
generous end of the range and that is the point.

The round numbers are a bonus rather than the reason, but they are worth having:
two panels at 3 3/4in and a flap at 3 1/2in is something a print shop can set
without a calculator and something a person can find on a ruler, which the
thirty-seconds were not. All three are whole pixels at 300 DPI as well, 1125 /
1125 / 1050, so the panel edges no longer land on a fraction.

The flap lost another 1/16in of measure. Practice absorbed it without
overflowing; Teaching's opening line had to lose four words to keep "it." off a
line of its own, and now reads "From first curiosity to professional practice."

---

## Re-imposed after the second fold test, 16 September 2026

The panels moved. Asked for: the donate ask on the back of the folded piece,
Our story first of its three, and the Cover beside Community so white could
carry across that crease.

    outside   Teaching (tuck)  Community  Cover
    inside    Our story        Research   Practice (tuck)

Folded, the Cover is the front, Community the back, Practice the hidden tuck.
Reading order is unchanged: Cover, then Our story beside Teaching, then Research
beside Practice, then Community. The fold positions did not move, because the
tuck is still first on the outside sheet and last on the inside; only which
panel is which changed, so the print spec's width table still holds.

Three things came with it:

**The white carry, and then no carry at all.** The first attempt ran the
cover's paper left into Community's right padding column as a rounded tongue,
which read as a sticker rather than a continuation, so the panel went the whole
way instead: Community is no longer a colour field. Below its banner and its
photograph it is the same paper as the cover, and the crease between them has no
seam. Its type and icons, which were white out of green, are now the ordinary
dark ink every white panel uses; nothing needed overriding, the `.panel--field`
rules simply stopped applying. The tongue and its two positioning tokens are
gone from the stylesheet along with the check render.js carried for them.

Removing the tongue took `.panel { z-index: 1 }` with it, which was a mistake
worth recording: that one line is what makes a panel a stacking context, and a
field panel paints its colour in a `::before` at z-index -1. Without the context
the purple and blue panels lost their colour entirely and their white type was
left on white paper. The line is back with a comment on it.

Total ink coverage came down from 311% to 305% with the green gone.

**The masthead got a height.** Nothing had set one, so the cover's photograph
started 0.16in above the photographs on the two panels beside it. On a sheet
where all three are visible at once that reads as a mistake. It is now
`--band-h` less the panel's top padding, which puts the three photograph tops on
one line. The 0.16in it cost the cover came back out of the hero photograph,
1.72in to 1.58in.

**Practice became the tuck** and lost 5/32in of measure, which cost it 15px. The
trio photographs came down from 0.98in to 0.82in, in proportion with the
narrower panel, and the lede lost one "and".

---

## Pass after the first home-printer test, 16 September 2026

Four things came back from folding a printed copy by hand, and all four are fixed
in the artwork rather than worked around.

**The tuck panel bound on the fold.** It was 3.625in against 3.6875in, a 1/16in
allowance, which is the tight end of what a roll fold wants and not enough once
the paper's own thickness is taken up. The green community flap would not sit
inside without bowing. The three panels are now 3.71875 / 3.71875 / 3.5625,
still 11in: the tuck clears the far crease by 5/32in, and the two others stay
equal so the cover meets the folded edge instead of stopping short of it and
showing a strip of the panel behind. Narrowing the tuck cost panel 6 three
pixels of height, recovered by breaking the address onto its own lines and
shortening the donate line to the copy deck's own words.

**The crease between panels 4 and 5 was invisible.** Both were white, so there
was nothing to fold by eye. Panel 5 now carries Organic Cream, `--panel`,
`#F4F1EA`, the brand's only light neutral. `css/site.css` keeps that token for
shapes and never for the page; a printed panel has to declare its own edge, so
this piece uses it as a ground. About 4% off the paper: enough to find the fold,
not enough to read as a coloured panel beside the two that are.

**One photograph printed as a near black rectangle** on a home printer while
every other photograph on the same sheet came out right. The file itself is
sound. Both Ghostscript and poppler render that image correctly, every embedded
JPEG is baseline, 4 component, Adobe APP14 with transform 0, and none of them is
truncated, so there is nothing in the PDF that says black. What that image was,
and nothing else was, is oversized: the test tubes photograph went in at
3083 x 2235, about 811 ppi over its 3.8in frame and nearly seven megapixels,
more than twice any other image in the piece. A decoder that has run out of room
for one image is what a single black photograph looks like. `make-pdfx.py` now
caps colour images at 400 ppi, bicubic, threshold 1.2. That is well above what a
175 line screen resolves, so nothing visible is given up; the outlier is gone,
the largest image on either sheet is now under two megapixels, and the X-4 file
dropped from 4.9 MB to 2.9 MB. Worth re-testing on the same printer before the
run, because this is a diagnosis by elimination and not a reproduction.

**Two facts corrected, on Sammie's review.** 40 years became 45, and 100
countries became 132. Each appears four times across the piece and all eight
were changed together: the two figures on the cover, "for forty-five years" in
the cover body, "across forty-five years" on panel 2, "more than 132 countries"
on panel 2, and the panel 4 lede. Source: Sammie, 16 September 2026. **The
website still says 40 years and more than 100 countries**, in `index.html`,
`content/home.json`, `content/community.json`, `content/news.json`,
`community.html`, `news.html`, `contact.html`, `about-elaine.html` and
`_dev/`. That is a separate pass and has not been made.

**The host-a-workshop icon did not read as a hand.** The old drawing put a
ribbed grip above a blade, which at 0.3in looked like a spring on a screwdriver.
It is now a trowel angled into a soil mound with a closed hand on the handle,
checked at printed size rather than enlarged.

---

## Geometry, as delivered

Both PNGs are **3375 x 2625 px**: the 3300 x 2550 trim asked for, plus **0.125in (37.5px) of bleed
on all four sides**. Bleed is included, not skipped.

- Panels 1, 2, 4, 6: 3.75in wide (1125px at 300 DPI)
- Panels 3 and 5, the tuck-in flap: 3.5in wide (1050px)
- All panels 8.5in tall; the spread trims to 11in x 8.5in

All three are whole pixels at 300 DPI, which the sixteenths and thirty-seconds they replaced were
not, and they add to exactly 3300px. Safe margin is 0.28in in from trim on
every side; nothing but photography crosses it.

Layout is written in inches and points and rendered at `deviceScaleFactor` 3.125 (CSS defines 1in as
96px, and 300/96 = 3.125), so the type is specified at real print sizes rather than scaled up from
screen pixels. Body text is 8.4pt, headlines 15.5 to 20pt.

## Imposition: the outside sheet is mirrored

**Fixed.** This section used to say the imposition was as briefed and might be wrong; it was wrong,
and it is corrected.

A letter roll fold has one narrow tuck panel, 3.5in against 3.75in for the other two. That panel
is a single physical flap, so it sits on the right of one side of the sheet and on the **left** of
the other. The brief asked for panels 1, 2, 3 across the outside and 4, 5, 6 across the inside, which
put the narrow panel third on both sides. Printed that way every panel would have been 1/16in out of
register with its own back.

`build/outside.html` now runs in the opposite order to `build/inside.html`:

| sheet | left to right | folds from its own left trim |
| :-- | :-- | :-- |
| inside | 2 Our story (wide), 4 Research (wide), 5 Practice (**tuck**) | 3.75in, 7.5in |
| outside | 3 Teaching (**tuck**), 6 Community (wide), 1 Cover (wide) | 3.5in, 7.25in |

Each fold mirrors the other: 11 minus 3.5 is 7.5, and 11 minus 7.25 is 3.75. Measured from the
rendered pages, not calculated by hand.

Backing, which decides where the cover lands: inside panel 5 (Practice, the tuck flap) folds in
first, then panel 2 (Our story) folds over it, so the face that ends up on top is the **back of panel
2**, which is the cover. The back of the folded piece is then the back of panel 4 (Research), which
is Community, and that is where the donation code sits. Note for anyone reading an older version of
this file: the cover used to back Research and the tuck used to be Community. Both moved.

The reading order is unchanged. Opening the piece gives Cover, then Our story beside Teaching, then
Research beside Practice, then Community on the back: the same six in the same sequence as before.

`.panel--first` and `.panel--last` used to hardcode `--w-wide` and `--w-tuck` respectively, which
silently assumed the tuck panel is always last on a sheet. Each panel now carries its own trim width
in `--pw` and the bleed modifiers add to whatever that is, so either panel can take either edge.

---

## The gold and purple decision

`css/site.css` scopes two colours more tightly than the earlier print brief for this brochure did.
Neither was carried over silently.

**Harvest Gold `--gold` #C9A227 is not used anywhere in this brochure.** The token's comment in
`site.css` reads "Donate button only", and there is no donate button on any panel. The earlier brief
assigned gold to one of the three QR codes; that assignment is dropped rather than quietly honoured.

**Legacy Purple `--legacy` #6B4C7A is used for one thing only: the QR rule and code on panel 2**,
which is the Dr. Elaine story panel. The token's comment reads "Dr. Elaine content ONLY", and panel 2
is that content, so this is inside its documented scope rather than decorative spending elsewhere. It
appears nowhere else in the piece.

The three QR treatments are therefore:

| Panel | QR | Colour | Token |
| :-- | :-- | :-- | :-- |
| 2, Story | Watch a free webinar | #6B4C7A | `--legacy` |
| 3, Teaching | Apply for a scholarship | #3780B8 | `--edu` |
| 6, Community | Join the free community | #156826 | `--green` |

Linnea reassigned these on 15 September: the scholarship code belongs on the
education panel and the community code on the community panel. The webinar code
took the slot that left on the story panel, since the one-code-per-panel rule
holds and it is the lightest first step of the three.

**The colour follows the panel, not the code.** Each code is generated in its
panel's accent, so moving a code means regenerating it. Moving the markup alone
leaves all three mismatched, which is what happened on the first pass of this
change.

**Settled, 15 September.** Linnea signed off on the purple and gave design authority for the piece.
Legacy Purple stays on panel 2: that panel is Dr. Elaine's content, which is the token's documented
scope, and the QR rule is the only place it appears. Education Blue stays on panel 3 for the same
reason. Two accents against a green system read as accents rather than noise, and each one carries a
meaning rather than decorating.

## One rhythm across the panels

The band and the photograph are fixed heights, `--band-h` and `--photo-h`, not
sized to their contents. Before this they were neither: photographs ran from
1.05in to 2.05in and bands grew with the heading, so every panel's edges landed
somewhere different and the three columns read as unrelated pieces of paper.
Now a heading that needs fewer lines sits lower in its band rather than pulling
the photograph up with it.

The cover is the deliberate exception: it carries the wordmark where the others
carry a band.

Photographs are not cut with a shape of their own. **One curve is drawn across
the whole sheet and each picture is clipped by the segment of it that falls in
that panel**, so the three lower edges join into a single line across both
folds. Flat, the eye reads one horizon; folded, each panel still stands up.

The maths has to work in sheet coordinates, not per image. The cover's
photograph starts higher than the other five, because that panel carries the
wordmark where the others carry a band, so the same percentage is a different
height on the page. `build/apply-curve.py` measures the real positions with
`build/measure-figs.js` and generates the polygons from those, which is why the
clip lives inline on each image rather than in the stylesheet.

Rebuild the curve after changing `--band-h` or `--photo-h`:

    python3 "Trifold Design/build/apply-curve.py"
    node "Trifold Design/build/render.js"

The crest is set to the shallowest photograph's lower edge and the trough
leaves about two fifths of the frame, so the pictures are full at the middle of
the spread without thinning to slivers at the outer edges.

The band and the photograph both carry `flex: 0 0 auto`. Without it the panel,
being a flex column, shrinks them on whichever panel holds the most copy: the
practice panel's band came out a fifth of an inch short, which broke the rhythm
on exactly one panel and pulled its photograph out of the curve.

**Both dimensions are load-bearing.** The six panels sit between 687 and 763
points against 762 available, and `used` in the render report counts children
only, not margins, so a panel can report under and still overflow. Trust the
`overflow` figure. Raising `--photo-h` by a quarter inch is enough to push the
practice panel over.

## The colour system

The piece runs on one idea at three sizes, all Food Web Green into moss:

| | What it is | Where |
| :-- | :-- | :-- |
| `.banner` | The eyebrow and heading at the top of a pillar panel, reversed out | Panels 2, 3, 4, 5, 6 |
| `.field` | A bounded block inside a white panel | The cover's closing block |
| `.panel--field` | A whole panel given to the colour | Panel 6 |

**A background costs no height.** That is why panel 6 can turn green on a sheet where four of the six
panels have under twelve points spare, and why the banner was affordable at all: its top padding was
already empty white, so only its bottom padding is new. Bounded fields do cost their padding, which is
what pushed the cover over on the first pass.

`.carry` continues panel 6's colour left across the crease, so the field starts before the fold rather
than at it. It is absolutely placed on the sheet, sized to panel 5's right padding exactly, so no copy
ever sits on it.

The photo fade belongs to `.panel--field` only. On a white panel the same fade lands behind the
caption and turns grey italic type into grey type on a grey-green band. The caption carries a
`z-index` so it clears the fade either way.

Cards are pale green with a Food Web Green left edge. `.card--cream` keeps Organic Cream with a tan
edge for anything that should read as a note rather than a panel. No panel has a cream background:
cream is still a shape, never the page.

Organic Cream `--panel` #F4F1EA is used only as bounded rectangles: the figures block on panel 1, the
"On claims" box on panel 4, the directory box on panel 5, the legal block on panel 6. No panel has a
cream background. The pale green `--panel-green` carries the climate callout on panel 2 the same way.

## Type

Montserrat 700 for headlines, eyebrows and the wordmark; Montserrat 600 for subheads; Source Sans 3
for body; **EB Garamond for every piece of small considered text**, as `site.css` asks: the ledes, all
photo captions, all source lines, both pull quotes, and every placeholder note. Font files are the
repository's own subsetted `.woff2` files in `fonts/`; nothing is fetched from a CDN.

## Photographs used, and why

| Panel | File | Why |
| :-- | :-- | :-- |
| 1, Cover | `img/hand-soil-roots-fungi.jpg` | The only file in the library that actually shows what the cover line claims: an aggregate with roots and white fungal strands visible in a hand. 2000 x 2000, plenty at 300 DPI. Chosen over `2-hands-clasped-holding-plant-roots.jpg`, where the soil is a dark mass with no structure legible. |
| 2, Story | `img/Dr Elaine Ingham with Microscope.jpg` | The portrait the copy deck names for this content. 3516 x 4677, the best resolution in the repository. Cropped to keep the microscope in frame, because the caption refers to it. Not paired with a workshop photo: panel 2 already carries the callout and the QR, and a second image pushed the QR off the panel. |
| 3, Teaching | `img/uploads/Loida Teaching 3.JPG` | A mentor teaching outdoors on working land, which is what the panel is about. 1600 x 1066, enough for the 3.75in width used. `ctpfw-student-*-compost` are closer crops of hands and read as compost, not as teaching. |
| 4, Research | `img/Test tubes with sample_.jpg` | Samples with a microscope behind them: lab and field in one frame. 3083 x 2235. Paired with `img/uploads/testate-amoeba-40x.jpg` as a small inset, because that is literally the microscope count the panel says every recommendation starts with. `Elaine and nematode extraction.png` is only 940 x 788, too small to print at any useful size. |
| 5, Practice | `img/erc-rancho-cacachilas-agro.jpg` | Cultivated rows on real land under real sky. 1500 x 1000. Used for the panel's atmosphere only, and the caption says so. **This is not the South Africa tomato farm** named in the copy; see below. |
| 6, Community | `img/uploads/MAR Group Photo 2.jpg` | About thirty people around a finished compost pile, which is what a community panel needs. 1600 x 1200. |

**The logo is provisional.** `img/sfwlogo-240.png` is a 240 x 208 stand-in; `OPEN-ITEMS.md`
Decision 16 records that the real vector mark has never reached the repository. It is set at 0.46in
wide on panel 1, which is about as large as 240px can go at 300 DPI without softening. The type-set
wordmark beside it carries the name, exactly as the live site does. **Replace with the real artwork
before print.** Everything else in the piece is at or above 300 DPI at the size used.

---

## Open items carried forward, not resolved

Every one of these prints as a visible italic note on the panel it belongs to. The site's own `.todo`
class was deliberately not reused: it is `display:none` until `?notes=1` is set, and in a flattened
print PNG that would render as nothing at all. These are set in the `.awaiting` tone instead, always
visible, a straight sentence about what is needed and who supplies it.

1. **Dr. Ingham's publication count (panel 2).** Three different figures are live in this repository
   at once. `about-elaine.html` says 89 publications, 53 of them journal articles. `docs/copy-deck-v2.md`
   section 14 says 82 verified links, and separately lists 77 journal papers, 6 book chapters, 10
   reports and 43 other. `OPEN-ITEMS.md` already flags the contradiction as waiting on Linnea and Evan.
   The brief told me to print "77 peer-reviewed journal papers"; the live page is newer than the copy
   deck and disagrees with both, so **no number is printed**. The panel says so instead. Linnea and Evan.
2. **Dr. Ingham's birth year (panel 2).** Printed as "1952 to 2026" with the standing note that the
   year is unconfirmed against the obituary, same as `about-elaine.html`.
3. **The South Africa tomato case (panel 5).** The brief's draft gave "Grade 1 produce from 18% to
   50% in a single season". `docs/copy-deck-v2.md` line 449 records this as a placeholder needing the
   grower's name, the year and the source. It is an unattributed percentage under the house rule, so
   **the figures are not printed**. The panel names the case and says what is missing. There is also no
   photograph of that farm in this repository; panel 5 uses a different farm and its caption says so. Evan.
4. **The partner list (panel 5).** Only Isha Outreach is named, because it is the only partner named
   anywhere in the built site (`index.html` partner strip, `calendar.html`). The draft's RySS / APCNF
   line is dropped: `docs/copy-deck-v2.md` line 430 records that collaboration as proposed and unsigned,
   and its "close to two million farmers" is an unattributed figure. Kiss the Ground is dropped too:
   `docs/2026-08-interview-evan-buckman.md` describes them as close contacts, not a partner. No partner
   logos exist in the repository. Evan.
5. **Ecoregion hubs (panel 5).** Described as in planning, because `docs/copy-deck-v2.md` carries
   the hub pilots as a placeholder. No hub is named. Evan.
6. **The practitioner directory address (panel 5).** The draft gave `soilfoodweb.com/practitioners`.
   That address appears nowhere in this repository; the copy deck puts the page at `/community/directory`,
   and `OPEN-ITEMS.md` separately records that the production hostname itself is still a guess. No URL
   is printed. Linnea and Evan.
7. **The research roadmap (panel 4).** Published replications, open data releases and a microscopy
   methodology paper appear in no Foundation document in this repository. Named on the panel as
   unconfirmed rather than printed as a commitment. Evan.
8. **Every photo caption.** Place, people and date are unconfirmed for all six photographs, which is
   the standing `OPEN-ITEMS.md` entry covering fourteen pages of the site. Each caption says so.
9. **Consent for the group photograph on panel 6.** `OPEN-ITEMS.md` records that nobody has confirmed
   everyone in `MAR Group Photo 2.jpg` agreed to be published. That is a live question on the website;
   **in print it is worse, because a printed run cannot be taken down.** The caption flags it. Someone
   should clear this specifically before the job is placed.
10. **Prices (panel 3).** Deliberately not printed, and the panel says why. Foundation Courses at
    $4,999 and the Complete Practicum at $3,999 are verified in the copy deck, but the refund rule
    (Decision 2) and payment plans (Decision 3) are open, and a printed price outlives the price. The
    panel points at `school.soilfoodweb.com` instead. Evan.
11. **The grower path (Decision 1)** is not mentioned. Panel 3 had no room for it once the three
    program blocks and the QR were in. It belongs on a later pass if the decision lands.

## Copy I cut from the brief's draft, and why

- **"A teaspoon of healthy soil holds more microorganisms than there are people on Earth."** Cut from
  panel 1. It is a real and widely repeated figure, but it appears nowhere in this repository and has no
  named source, and the house rule is no statistic without one. The cover now uses the homepage lede's
  own wording instead.
- **"Soil is the largest terrestrial carbon sink on Earth."** Cut from the panel 2 climate callout. It
  is a superlative claim with no source in the repository. Replaced verbatim with mechanism six from
  `science.html`, which says the same thing in checkable terms and is already fact-checked.
- **"around eighty peer-reviewed papers"** and its correction to "77 peer-reviewed journal papers".
  Neither is printed; see open item 1.
- **"When she started, the idea that microbes mattered to plant health was considered fringe."** Cut.
  Replaced with the verified lede from `about-elaine.html`.
- **"a community-led organization"** softened to "through the Foundation and the school inside it",
  which is the copy deck's own formulation. No governance document in the repository uses "community-led".
- **"lower input costs, healthier plants, and soil that holds carbon and water the way it's supposed
  to"** on the cover, rewritten to the homepage's own claim language, which is sourced.
- **"The ground beneath our farms is alive"** corrected to **"The ground beneath our farms and forests
  is alive"**, which is the H1 on `index.html` and in the copy deck.
- **"a two-week, in-person intensive ... run several times a year"** softened to "held periodically",
  the copy deck's own word. The durations on record disagree: the copy deck says two weeks, the Wild Ken
  Hill workshop in `community.html` ran ten days, and the India workshop runs twelve. Worth settling, but
  no duration is printed, so nothing is wrong on the panel.
- **Panel 5's film list** was added, not in the brief's draft. Eleven named practitioners with named
  places are published on `practice.html`, and a panel about real growers reads better with real growers
  in it than with three flagged placeholders and nothing else.

## House rules checked

No em dashes anywhere (grepped, zero). No "certified" (grepped, zero). No acronyms in public text:
Foundation Courses, Advanced Programs, Complete Practicum, Soil Microscopy, all spelled out. No
percentages printed at all. No acreage claims. Sentence case headings. American spelling. Every figure
that is printed carries a source line: the three cover figures, the "more than 100 countries" on panel
4, and the eleven films on panel 5. Every dated item shows its date. The ratified legal block is on
panel 6, verbatim from `docs/copy-deck-v2.md` section 1.3. Every course link points at
`school.soilfoodweb.com`; nothing points at the WordPress shop or `/foundation-courses-2/`.

## QR codes

Five, on panels 2, 3, 5 and 6. Panel 6 carries two, the free community under the photograph and the
donate ask at its foot; they sit about six inches apart at opposite ends of the panel, which is far
enough that a phone cannot frame both at once. Panels 1 and 4 carry none.

Every code holds a **Switchy short link** (`sfw.one/brochure-*`), not the destination. That is the
important decision on this page. A printed code cannot be edited, and the destinations under this
brochure have already moved once: three addresses pointed at rebuilt-site paths that 404 on the live
WordPress site. With a short link in the code, a moved destination or a renamed path is a redirect
edit rather than a reprint. The campaign UTM parameters ride on the redirect, so the reporting is
unchanged and none of it costs modules here.

The short payload also buys the error correction back. Generated at **H (30% recoverable)**, four
modules of quiet zone, pure black on white, printed at **1.15in (29.2mm) square**. All five are
version 5, 45 modules, **0.649mm a module**. The long URLs with UTM tails could only manage M at
0.48 to 0.60mm, and the community code was under the practical print minimum. There is real margin
now, but a proof scanned off the press rather than off a laser print is still worth asking for.

Each code carries its own panel's colour on a white ground, and they are the real brand tokens:
Legacy Purple `#6B4C7A` on the Dr. Elaine panel, Education Blue `#3780B8` on teaching, Food Web Green
`#156826` on practice, Moss `#22371F` on community, Gold `#C9A227` on the donate ask.

`build/make-qr.py` gates the colours, but with a scan test rather than a contrast rule. It renders
each code at its printed size, degrades it to simulate ink spread and a phone camera, and decodes it;
the build stops if it does not come back. An earlier pass used a WCAG contrast threshold of 4.5:1 and
rejected both Education Blue (4.25:1) and the brand gold (2.42:1). That was wrong: WCAG 4.5:1 is a
readability figure for small text, and a QR code at error correction H with 0.649mm modules is a far
more forgiving thing. Measured properly, blur tolerance runs from 2.8px on the community code down to
1.2px on the gold, and all five read. The deep ends of the gradients, `#1F4E73` and `#8A6E15`, survive
about twice the blur and are the fallback if a press proof ever disappoints; gold is the one to look
at first.

`build/make-qr.py` writes the placed SVGs and the standalone PNGs in `exports/qr/` from one table.
`build/check-qr.py` decodes every placed code back out of the 300 DPI render and fails if any does
not read. Run both after any change to a link, a colour, or the size of `.qr img`.

## Also worth a person's eye

- Panel 2's photograph is cropped fairly tight on Dr. Ingham to keep the microscope in frame. A wider
  crop would be kinder to the portrait but loses the instrument the caption names. Worth a look.
- Panel 5's photograph is a 3 to 1 horizon band rather than a full block, because the panel carries
  three placeholder notes and they had to fit. When the tomato case and the partner list land, those
  notes come out and the photograph can grow.
- There is no donate call to action anywhere in the piece. Panel 6 says "donate" as one of four open
  roles, but there is no amount, no code and no link, because `donate.html` still has the impact lines
  for its preset amounts waiting on program costs. Worth deciding whether a print piece should carry one.
- Panel 1 is the only panel carrying the wordmark. On a folded piece the cover is the outward face, so
  that is correct, but confirm it against how the piece will actually be stacked and displayed.

---

## A code to buy the Foundation Courses, 22 September 2026

Linnea: add a QR code to buy the Foundation Courses; "join the community" is
there twice. It was, in effect: the webinar code on Our story already lands
people in the free community, and the Community panel had a second code to the
same place. So the community code is gone and the Foundation Courses code
takes its place in the set of five.

| panel | was | is |
| :-- | :-- | :-- |
| Teaching | Apply for a scholarship, `sfw.one/brochure-scholarship`, Education Blue | **Enroll in the Foundation Courses**, `sfw.one/brochure-courses`, Education Blue |
| Community | Join the free community, `sfw.one/brochure-community`, Moss | Apply for a scholarship, `sfw.one/brochure-scholarship`, now Moss |

The purchase code sits on Teaching because that is where the Foundation Courses
are described; the scholarship moved to Community, under "there is a way in
for anyone", and took that panel's colour like every other code. Copy on the
new code is lifted from the panel above it. No price is printed; the panel
already says every price is listed at school.soilfoodweb.com.

**`sfw.one/brochure-courses` does not exist yet and has to be created in
Switchy**, pointing at
`https://school.soilfoodweb.com/bundles/soilfoodweb-foundation-courses`
(the purchase page `learn.html` links to), with the campaign UTM parameters
on the redirect like the others. `sfw.one/brochure-community` is no longer
printed and can be left alone or retired.

All five codes decode out of the PNG proofs, the X-4 file and the X-1a file.

---

## The Community panel sends people to the website, 23 September 2026

Linnea: the code and paragraph on the Community panel (the middle of the
outside spread) are replaced with a website call to action.

    Curious about the Soil Food Web approach?
    Visit our website to explore our courses, workshops, and free resources.
    Learn how soil biology supports healthy plants and discover ways to get
    involved.
    [code]  Learn more / www.soilfoodweb.com

- The code carries `https://www.soilfoodweb.com` directly, as asked, not a
  sfw.one short link. It is moss `#22371F`, version 4, 41 modules, and survives
  2.4px of blur. All five codes decode from every output.
- **The scholarship code is gone from the brochure.** It was the code in that
  spot. If it should come back, it needs a new home.
- The domain question above (.com against .org) still stands. This code prints
  the .com, which is the one Linnea named.
- `qr/scholarship.svg` and the scholarship PNGs are removed; `website` replaces
  them everywhere. Print PDFs, proof and delivery folders rebuilt.
