# Blog cards

One editable PowerPoint per size, one slide per post, made to be dragged into
the Canva "Blogs Updated" folder:

| File | Size |
| --- | --- |
| feature-social | 1400 x 1400 |
| desktop-header | 1920 x 720 |
| tablet-header | 1024 x 768 |
| mobile-header | 750 x 1000 |

The chosen design (`STYLE=brand`): the website's white page with the post's
photograph whole, and a cream panel with the site's 12px radius and soft
shadow. The type is Linnea's, off her PDC card: the category as a big bold
Montserrat word, the headline in Source Sans 3, the black READ POST box in EB
Garamond with the cursor, and www.soilfoodweb.com. Posts about Dr. Elaine
take the category in Legacy Purple. Every piece is its own layer.

The other styles in build.py (rect, lens, window, print) were tried and
turned down; they are kept only for reference.

```
pip install python-pptx pillow
STYLE=brand python3 tools/blog-cards/build.py <output folder>   # all four
STYLE=brand python3 tools/blog-cards/build.py <output folder> tablet-header-1024x768
./tools/blog-cards/preview.sh <deck.pptx> <sheet.png>        # needs LibreOffice Impress
```

Posts, colours, headline splits and photos are the `POSTS` list at the top
of `build.py`. Fonts in `fonts/` are the site's own (OFL), converted to TTF
for measuring.

## Open items

- Photos: upload each post's original to `photos/` under its slug (see
  `photos/README.md`) and rerun. Until then each card uses a stand-in from `img/`.
- Headlines are the live titles split at their own colon or dash; the deck
  line is the other half. The PDC card keeps Linnea's wording. Category words
  follow the blog's categories, except PDC (Education, Linnea's) and the
  obituary (In Memoriam). Check before publishing.
- Only the ciliates post has a known author, so no card carries a byline.
