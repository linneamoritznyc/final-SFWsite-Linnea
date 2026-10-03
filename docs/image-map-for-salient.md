# Image map: static site to Salient Nonprofit theme

Use this table to upload each image to the WordPress Media Library (or theme assets folder where noted). The **Google Drive name** column shows the original filename from the Foundation's Drive; the **repo path** column shows where it lives in this repo. The **Salient placement** column tells you which page section the image appears in.

Images referenced as `img/w/` are WebP conversions with responsive `-800` variants. Upload the full-size version; WordPress + Salient's responsive image handling will generate the sizes it needs.

---

## Global (every page)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| sfwlogo-240.png | `img/sfwlogo-240.png` | Header logo, overlay menu, footer | Temporary wordmark; final logo goes at `img/logo.svg` (Decision 16) |
| icons.svg | `img/icons.svg` | Inline SVG sprite (all icons) | Paste into Salient theme `functions.php` via `wp_body_open` hook |

---

## Homepage (`index.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| sfw-amoeba-still-square.jpg | `img/w/sfw-amoeba-still-square.jpg` | Hero microscopy circles (video poster) | **Theme asset**, not Media Library |
| sfw-amoeba-loop-square.mp4/.webm | `video/sfw-amoeba-loop-square.*` | Hero microscopy circle 1 | **Theme asset** |
| sfw-amoeba-loop-hero.mp4/.webm | `video/sfw-amoeba-loop-hero.*` | Hero microscopy circle 2 | **Theme asset** |
| sfw-amoeba-lab-640.mp4/.webm | `video/sfw-amoeba-lab-640.*` | Hero microscopy circle 3 | **Theme asset** |
| hand-soil-roots-fungi.jpg | `img/w/hand-soil-roots-fungi.jpg` | Intro section photo | |
| hand-wet-dirt-worm.jpg | `img/w/hand-wet-dirt-worm.jpg` | Intro section photo | |
| hand-of-compost.jpg | `img/w/hand-of-compost.jpg` | Intro section photo | |
| handling-loose-soil.jpg | `img/w/handling-loose-soil.jpg` | Intro section photo | |
| hand-scooping-planter-bed-soil.jpg | `img/w/hand-scooping-planter-bed-soil.jpg` | Intro section photo | |
| 2-dirty-hands.jpg | `img/w/2-dirty-hands.jpg` | Ledger / photo strip | |
| 2-hands-planting-shrub.jpg | `img/w/2-hands-planting-shrub.jpg` | Ledger / photo strip | |
| ctpfw-student-moving-compost-1.jpg | `img/w/ctpfw-student-moving-compost-1.jpg` | Case study card | |
| ctpfw-student-squeezing-compost-1.jpg | `img/w/ctpfw-student-squeezing-compost-1.jpg` | Case study card | |
| el-nino-2017-tractor-in-mud-w-crew.jpg | `img/w/el-nino-2017-tractor-in-mud-w-crew.jpg` | Case study card | |
| erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg | `img/w/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg` | Case study card | |
| erc-panchamana-treeplanting-3-fb-img-1666271008784.jpg | `img/w/erc-panchamana-treeplanting-3-fb-img-1666271008784.jpg` | Case study card | |
| erc-rancho-cacachilas-agro.jpg | `img/w/erc-rancho-cacachilas-agro.jpg` | Case study card | |
| erc-rancho-cacachilas-agro8.jpg | `img/w/erc-rancho-cacachilas-agro8.jpg` | Case study card | |
| carla-nicks-son-nick-eri-wild-soils-event-11-2024.jpg | `img/w/carla-nicks-son-nick-eri-wild-soils-event-11-2024.jpg` | Testimonial / quote section | |
| hvdb-inplanten-002.jpg | `img/w/hvdb-inplanten-002.jpg` | Testimonial / quote section | |
| harringtons-organic-land-care-york-farms-1-768x1024.jpg | `img/w/harringtons-organic-land-care-york-farms-1-768x1024.jpg` | Before/after or case study | |
| soil-sample-close-up-test-tube.jpg | `img/w/soil-sample-close-up-test-tube.jpg` | Science link section | |
| test-tubes-with-sample.jpg | `img/w/test-tubes-with-sample.jpg` | Science link section | |
| erc-rancho-cacachilas-agro2.jpg | `img/w/erc-rancho-cacachilas-agro2-800.jpg` | Photo strip (800px only) | Full-size version may be missing |

---

## Learn (`learn.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| elaine-flower-shirt-microscope.jpg | `img/w/elaine-flower-shirt-microscope.jpg` | Hero or intro image | |
| sampling-equipment.jpg | `img/w/sampling-equipment.jpg` | Course section | |
| erc-panchamana-garden.jpg | `img/w/erc-panchamana-garden.jpg` | Course section | |
| 2-dirty-hands.jpg | `img/w/2-dirty-hands.jpg` | Course section | Also used on homepage |
| ctpfw-student-squeezing-compost-1.jpg | `img/w/ctpfw-student-squeezing-compost-1.jpg` | Course section | Also used on homepage |
| soil-sample-close-up-test-tube.jpg | `img/w/soil-sample-close-up-test-tube.jpg` | Course section | Also used on homepage |
| erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg | `img/w/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg` | Course section | Also used on homepage |

---

## Learn Scholarships (`learn-scholarships.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| ctpfw-student-squeezing-compost-1.jpg | `img/w/ctpfw-student-squeezing-compost-1.jpg` | Hero or intro | Shared |
| hvdb-inplanten-002.jpg | `img/w/hvdb-inplanten-002.jpg` | Scholarship section | |

---

## Learn Webinars (`learn-webinars.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| Sampling equipment.jpg | `img/Sampling equipment.jpg` | Webinar thumbnail | Original filename with space |
| sampling-equipment.jpg | `img/w/sampling-equipment.jpg` | Webinar section | WebP version |
| test-tubes-with-sample.jpg | `img/w/test-tubes-with-sample.jpg` | Webinar thumbnail | |

---

## Science (`science.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| fungal-spores-in-suspension.jpg | `img/w/fungal-spores-in-suspension.jpg` | Hero or intro | |

---

## About (`about.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| dr-elaine-ingham-with-microscope.jpg | `img/w/dr-elaine-ingham-with-microscope.jpg` | Founder section | |
| copy-of-9.jpg | `img/w/copy-of-9.jpg` | About section photo | |
| carla-nicks-son-nick-eri-wild-soils-event-11-2024.jpg | `img/w/carla-nicks-son-nick-eri-wild-soils-event-11-2024.jpg` | Team / community | Shared |
| ctpfw-student-squeezing-compost-1.jpg | `img/w/ctpfw-student-squeezing-compost-1.jpg` | About section | Shared |
| handling-loose-soil.jpg | `img/w/handling-loose-soil.jpg` | About section | Shared |
| erc-panchmana-treeplanting-fb-img-1666270907385.jpg | `img/w/erc-panchmana-treeplanting-fb-img-1666270907385.jpg` | About section | |
| soil-sample-close-up-test-tube.jpg | `img/w/soil-sample-close-up-test-tube.jpg` | About section | Shared |

---

## About Elaine (`about-elaine.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| Dr Elaine Ingham with Microscope.jpg | `img/w/dr-elaine-ingham-with-microscope.jpg` | Portrait | |
| Elaine Flower Shirt Microscope.png | `img/w/elaine-flower-shirt-microscope.jpg` | Portrait | |
| Elaine Smile talking.png | `img/w/elaine-smile-talking.jpg` | Portrait | |
| Elaine and nematode extraction.png | `img/w/elaine-and-nematode-extraction.jpg` | Portrait | |
| Elaine with Sample bag.png | `img/w/elaine-with-sample-bag.jpg` | Portrait | |
| copy-of-9.jpg | `img/w/copy-of-9.jpg` | Bio section | |
| copy-of-17.jpg | `img/w/copy-of-17.jpg` | Bio section | |

---

## About Team (`about-team.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| erc-panchmana-treeplanting-fb-img-1666270907385.jpg | `img/w/erc-panchmana-treeplanting-fb-img-1666270907385.jpg` | Team hero | |
| cutout-placeholder.svg | `img/cutout-placeholder.svg` | Team member portrait placeholder | Awaiting real headshots (Decision 10) |

---

## Practice (`practice.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| erc-rancho-cacachilas-aerial-shot.jpg | `img/w/erc-rancho-cacachilas-aerial-shot.jpg` | Case study hero | |
| hand-scooping-planter-bed-soil.jpg | `img/w/hand-scooping-planter-bed-soil.jpg` | Case study card | Shared |
| red-soil-hand.jpg | `img/w/red-soil-hand.jpg` | Case study card | |
| ctpfw-student-moving-compost-1.jpg | `img/w/ctpfw-student-moving-compost-1.jpg` | Case study card | Shared |
| farmer-case-studies.jpg | `img/video/farmer-case-studies.jpg` | Video theatre poster | |
| 790985081.jpg | `img/video/790985081.jpg` | Video thumbnail (Vimeo ID) | |
| 812185778.jpg | `img/video/812185778.jpg` | Video thumbnail (Vimeo ID) | |
| 812188293.jpg | `img/video/812188293.jpg` | Video thumbnail (Vimeo ID) | |

---

## Community (`community.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| erc-rancho-cacachilas-aerial-2.jpg | `img/w/erc-rancho-cacachilas-aerial-2.jpg` | Community hero | |
| costa-rica-liquid-amendments.jpg | `img/costa-rica-liquid-amendments.jpg` | Event card | **MISSING from repo** |
| costa-rica-microscopes.jpg | `img/costa-rica-microscopes.jpg` | Event card | **MISSING from repo** |
| living-legacy-webinar.jpg | `img/living-legacy-webinar.jpg` | Webinar card | **MISSING from repo** |
| soil-health-week-karachi-university.jpg | `img/soil-health-week-karachi-university.jpg` | Event card | **MISSING from repo** |
| soil-health-week-pakistan.jpg | `img/soil-health-week-pakistan.jpg` | Event card | **MISSING from repo** |
| Wild Ken Hill photos (IMG_1492-1502) | `img/wild-ken-hill/IMG_1492.jpg` thru `IMG_1502.jpg` | Wild Ken Hill event gallery | |

---

## Volunteer (`volunteer.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| sfw-amoeba-still-wide.jpg | `img/w/sfw-amoeba-still-wide.jpg` | Background video poster | **Theme asset** |
| sfw-amoeba-lab-640.mp4/.webm | `video/sfw-amoeba-lab-640.*` | Background video loop | **Theme asset**, shared with homepage |
| 2-dirty-hands.jpg | `img/w/2-dirty-hands.jpg` | Volunteer section | Shared |
| gloved-hands-red-bucket-mulch.jpg | `img/w/gloved-hands-red-bucket-mulch.jpg` | Volunteer section | |
| hand-of-compost.jpg | `img/w/hand-of-compost.jpg` | Volunteer section | Shared |
| fungal-spores-in-suspension.jpg | `img/w/fungal-spores-in-suspension.jpg` | Volunteer section | Shared |
| ctpfw-student-moving-compost-1.jpg | `img/w/ctpfw-student-moving-compost-1.jpg` | Before/after comparison | Shared |
| erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg | `img/w/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg` | Before/after comparison | Shared |
| cutout-placeholder.svg | `img/cutout-placeholder.svg` | Team/volunteer portrait placeholder | |

---

## Calendar (`calendar.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| ctpfw-student-moving-compost-1.jpg | `img/w/ctpfw-student-moving-compost-1.jpg` | Calendar hero | Shared |

---

## Research (`research.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| soil-sample-shovel-and-bag.jpg | `img/w/soil-sample-shovel-and-bag.jpg` | Research hero | |
| test-tubes-with-sample.jpg | `img/w/test-tubes-with-sample.jpg` | Research section | Shared |

---

## Donate (`donate.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| 2-hands-planting-shrub.jpg | `img/w/2-hands-planting-shrub.jpg` | Donate hero | Shared |
| erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg | `img/w/erc-panchamana-treeplanting-2-fb-img-1666270988322.jpg` | Donate section | Shared |

---

## News (`news.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| Multiple images used as article thumbnails | Various `img/w/*-800.jpg` | News card grid | All shared from other pages |

---

## News: Wild Ken Hill (`news/wild-ken-hill-2026.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| IMG_1492.jpg | `img/wild-ken-hill/IMG_1492.jpg` | Article photo | |
| IMG_1493.jpg | `img/wild-ken-hill/IMG_1493.jpg` | Article photo | |
| IMG_1494.jpg | `img/wild-ken-hill/IMG_1494.jpg` | Article photo | |
| IMG_1497.jpg | `img/wild-ken-hill/IMG_1497.jpg` | Article photo | |
| IMG_1499.jpg | `img/wild-ken-hill/IMG_1499.jpg` | Article photo | |
| IMG_1502.jpg | `img/wild-ken-hill/IMG_1502.jpg` | Article photo | |
| IMG_1465.mp4 | `video/wild-ken-hill/IMG_1465.mp4` | Article clip | |
| IMG_1467.mp4 | `video/wild-ken-hill/IMG_1467.mp4` | Article clip | |
| IMG_1471.mp4 | `video/wild-ken-hill/IMG_1471.mp4` | Article clip | |

---

## Login (`login.html`)

| Google Drive name | Repo path | Salient placement | Notes |
| :-- | :-- | :-- | :-- |
| hand-soil-roots-fungi.jpg | `img/w/hand-soil-roots-fungi.jpg` | Login background | |

---

## Missing images (need to source from Google Drive)

These are referenced in the HTML but not present in the repo:

| Filename | Used on | Action needed |
| :-- | :-- | :-- |
| costa-rica-liquid-amendments.jpg | community.html | Get from Google Drive |
| costa-rica-microscopes.jpg | community.html | Get from Google Drive |
| living-legacy-webinar.jpg | community.html | Get from Google Drive |
| soil-health-week-karachi-university.jpg | community.html | Get from Google Drive |
| soil-health-week-pakistan.jpg | community.html | Get from Google Drive |
| sfwlogo-240.jpg (WebP) | about-governance, about-team, contact, directory, privacy, terms, accessibility, news articles, projects | Generate WebP version from sfwlogo-240.png |

---

## Videos summary (theme assets, not Media Library)

| File | Format | Used on |
| :-- | :-- | :-- |
| sfw-amoeba-loop-square | .mp4, .webm | index.html (circle 1) |
| sfw-amoeba-loop-hero | .mp4, .webm | index.html (circle 2) |
| sfw-amoeba-lab-640 | .mp4, .webm | index.html (circle 3), volunteer.html |
| sfw-amoeba-lab-512 | .mp4, .webm | Available but not currently referenced |
| sfw-amoeba-instagram-4x5 | .mp4, .webm | Social media only, not on site |
| wild-ken-hill clips | .mp4 | news/wild-ken-hill-2026.html |
