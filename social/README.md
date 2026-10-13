# Instagram carousels, Soil Food Web School

Two posts, five slides each, 1080 x 1350.

| Post | Date | Editable file | PNGs |
|---|---|---|---|
| We turned 1! (open house, October 16) | Wednesday 14 October 2026 | post-1-2026-10-14-anniversary.html | post-1-2026-10-14-anniversary/ |
| What does Regenerative actually mean? | Thursday 15 October 2026 | post-2-2026-10-15-regenerative.html | post-2-2026-10-15-regenerative/ |

Each PNG folder also holds contact-sheet.png, the five slides in a row.

## To edit

1. Change the words in the post's .html file. Shared styling is in slides.css.
2. Fill `[TIME + TIME ZONE]` in post 1 (slides 1 and 5), then delete `class="fill"` from those spans to remove the gold dashed outline.
3. From the repo root: `node social/tools/render.cjs`. It rewrites the PNGs and contact sheets.

To change a photo crop, edit the anchors in tools/crop.py and run `python3 social/tools/crop.py`.

## Photos

| Slide | File | Source | Note |
|---|---|---|---|
| Post 1, slide 2 | photos/microscope.jpg | img/costa-rica-2025-microscopy-students-mentors.jpg (Costa Rica, March 2025) | Source is 1536 px wide; the 4:5 crop is 922 px wide, so it is enlarged 1.17x. |
| Post 1, slide 3 | photos/compost-pile.jpg | img/pile-turning-wes-8-scaled.jpg | Photographer not recorded. |
| Post 1, slide 5 | photos/group.jpg | img/wild-ken-hill/IMG_1500.jpg (Wild Ken Hill, June 2026) | |
| Post 2, slide 1 | photos/living-soil.jpg | img/ctpfw-student-squeezing-compost-1.jpg | Crop is 900 px wide, enlarged 1.20x. |
| Post 2, slide 5 | photos/field.jpg | img/uploads/loida-teaching-3.jpg | Loida Vasquez teaching at a workshop, not a farmer. Crop is 853 px wide, enlarged 1.27x. |

Not used: Ecosystem Restoration Camps photos (removed from the site 5 October), Harrington's York Farms photos (768 px wide, permission pending), Canva stock and screenshots.
