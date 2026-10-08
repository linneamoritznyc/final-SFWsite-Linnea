# Publications page: WordPress handoff

For Alex. 8 October 2026. The prototype is /publications/ in this preview, plus one page per
entry under /publication/<slug>/. Build new.soilfoodweb.com/publications/ to look and behave like it.

Source of truth: `docs/sfw-publications-final.csv` (180 rows, UTF-8 with BOM, read with `utf-8-sig`).
`tools/publications-import.py` loads it into `content/publications.json`; `tools/site/gens.py`
(`publications`, `publication_pages`) renders the pages. CSS: the "Publications" block at the end
of `css/site.css`. Behaviour: section 5b of `js/site.js`.

Addresses: the 134 entries already on staging keep their slugs (matched by title); the 46 new
ones get a slug made from the title. The CSV's `slug` column is empty, so take the slugs from
`content/publications.json`. Each entry page shows the title, Summary, Useful for, the details as
a list (year, type, study type, region, authors, citation, collection), the tag chips and a link
button.

## Card: CSV column → where it shows

| CSV column | On the card |
|---|---|
| year | Top line, first item |
| type | Top line, second item. `USDA` shows as "USDA publication" |
| study_type | Top line, third item |
| region | Top line, fourth item |
| title | Heading. Linked to `external_url` when there is one, with the external-link icon kept on the last word |
| authors | Line under the title, then " · " |
| citation | Same line, after the authors |
| external_url empty | Small line under the citation: "No online copy found. Listed by citation." (16 rows) |
| summary | **Summary:** label in bold, sentence in normal weight |
| useful_for | **Useful for:** label in bold, sentence in normal weight |
| topics | Tag chips (comma-separated in the CSV). Clicking one sets the Topic filter to that tag |
| collection | Not on the card. Used for the group headings and the Collection filter |
| id, status, content, source_url, slug | Not shown |

Collection display names: `Dr. Elaine's publications` → "Dr. Elaine's publications",
`Other relevant publications` → "Soil food web science", `Internet articles` → "Internet articles".

## Filters

| Control | CSV column | URL parameter | Values |
|---|---|---|---|
| Search ("Search by title, author, topic or year") | title, authors, citation, summary, useful_for, topics, year | `q` | free text; every word must match, accents ignored |
| Collection | collection | `collection` | `elaine`, `field`, `internet` |
| Topic (grouped by facet with `<optgroup>`) | topics | `topic` | the tag slugged: `compost-tea-and-extracts` |
| Study type | study_type | `study` | slugged: `field-study` |
| Region | region | `region` | slugged: `north-america` |
| Sort | year | `sort` | empty = Oldest first (default), `newest` = Newest first |

- Each dropdown defaults to "Any" and lists only values that occur, with their counts.
- All filters combine with AND. Filtering runs in the browser, no reload.
- State lives in the query string, e.g. `?topic=compost-tea-and-extracts&region=europe&q=tea`, so a view can be shared and the back button works.
- Results line "Showing 23 of 180 publications" sits in an `aria-live="polite"` region.
- "Clear filters" appears only when a search or a dropdown other than Sort is set.
- Nothing matches: "No publications match these filters." plus Clear filters.
- Oldest first: cards grouped under the three collection headings, in that order. Newest first: one flat list.
- Without JavaScript: the full list shows and the filter bar stays hidden.
- No entry numbers.

## Tag guide

Shown under the filter bar as a collapsed `<details>` "How the tags work". Stored as `database.tagGuide`
in `content/research.json`. A paper gets every tag that describes its main subject, usually 2 to 5.

**Organisms** (the groups Soil Food Web students learn to identify under the microscope)
- bacteria: studies that measure, count or manipulate soil or compost bacteria.
- fungi: studies of soil fungi, fungal hyphae or fungal biomass, including fungal plant pathogens.
- mycorrhizal fungi: fungi that live in partnership with plant roots (arbuscular and ectomycorrhizal).
- protozoa: flagellates, amoebae and ciliates, the main grazers of bacteria.
- nematodes: beneficial and root-feeding nematodes.
- soil arthropods: mites, springtails, symphylans and other small soil animals.
- earthworms: earthworms, including the worms used to make vermicompost.

**Practices and inputs** (what a grower or land manager actually does)
- compost: making, testing or applying thermal compost.
- compost tea and extracts: brewed compost tea and water extracts of compost or vermicompost, used as a drench or foliar spray.
- vermicompost: worm castings and vermicompost as an input.
- cover crops and tillage: cover crops, no-till, reduced tillage, crop rotation and alley cropping.
- pesticides and fumigants: the effects of biocides, fungicides, antibiotics and soil fumigants on soil life.
- engineered microbes: genetically engineered organisms released into soil, and their regulation.

**Outcomes** (the results readers care about)
- nutrient cycling: nitrogen, phosphorus and sulfur cycling, mineralization and nitrogen fixation.
- soil carbon: carbon storage, carbon sequestration and soil CO2 flux.
- decomposition: breakdown of litter, logs and other organic matter.
- disease suppression: biological control of plant diseases, including induced plant resistance.
- pest suppression: biological control of insect and other plant pests.
- plant growth and yield: measured plant growth, seedling vigour or crop yield.
- food quality: nutritional quality of crops, milk and other food.
- remediation: cleaning up contaminated soil or water, including heavy metals and hazardous waste sites.

**Systems** (the kind of land the study was done on)
- farms and crops: field crops, vegetables, orchards and dairy farms.
- horticulture and nurseries: container growing, greenhouses, nurseries, turf and ornamentals.
- forests: conifer, deciduous and riparian forests, and forest restoration.
- grasslands and rangelands: prairie, meadow and rangeland.
- wetlands and streams: wetlands and stream-side soils.
- cold and winter soils: soil life under snow and in the non-growing season.

**Approach** (the kind of work)
- soil food web: studies of the food web as a whole: who eats whom and what that does for plants.
- lab methods and microscopy: methods for counting, staining and measuring soil organisms.
- soil biodiversity: the diversity of soil organisms and why it matters.
- policy and soil security: regulation, policy and soil as a matter of public concern.
- review: papers that review or summarize a body of research.

**Study type** (one per paper)
- Field study: done outdoors on real farms, forests or rangeland.
- Greenhouse or pot trial: plants grown in pots or containers under controlled conditions.
- Lab study: done in the lab, in petri dishes, microcosms or cultures.
- Review: summarizes earlier research.
- Method: describes or tests a way to measure something.
- Report or guide: technical reports, manuals and handbooks.
- Article or commentary: magazine columns, newsletters, opinion pieces and internet articles.

**Region** (one per paper): North America, South America, Europe, Africa, Asia, Global.
Region is where the study was done. Global means a review, a multi-country study, or work that is about no particular place.

## Screenshots

- Desktop, 1440: `docs/screenshots/publications-1440-default.png`
- Mobile, 390: `docs/screenshots/publications-390-default.png`

Filtered views at both widths are beside them (`-compost-tea`, `-europe-tea`).
