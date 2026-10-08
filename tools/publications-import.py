#!/usr/bin/env python3
"""Load the publications CSV into content/publications.json.

    python3 tools/publications-import.py docs/sfw-publications-final.csv
    python3 tools/site/build.py

The CSV is the single source of truth: 180 rows prepared by Linnea Moritz on
11 September and finalized on 8 October 2026, kept in this repository as
docs/sfw-publications-final.csv (UTF-8 with a BOM). This script writes
content/publications.json: the entries, the filter option lists with counts
(only values that occur), the counts line and the tag guide.
tools/site/gens.py renders /publications/ and every /publication/<slug>/ page
from it.

Nothing in a row is edited. Values are stripped of surrounding whitespace and
that is all. A collection, study type, region or topic that is not in the
controlled lists below stops the import with the row number, so a typo in the
spreadsheet cannot quietly become a new filter option.

Each entry keeps the address it had on staging (content/staging/publications.json),
matched by title, so no published link breaks. Six titles were corrected in
the CSV; RETITLED pairs them with their staging entry by hand. Entries new
in the CSV get a slug made from the title.
"""
import csv, json, os, sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON = os.path.join(ROOT, "content", "publications.json")
STAGING = os.path.join(ROOT, "content", "staging", "publications.json")

# staging id -> the corrected title in the CSV
RETITLED = {
    1019: "Responses of microbial components of the rhizosphere to plant management strategies in a semiarid rangeland",
    1028: "Nitrogen limitation of production and decomposition in prairie, mountain meadow, and pine forest",
    1032: "An analysis of food-web structure and function in a shortgrass prairie, a mountain meadow, and a lodgepole pine forest",
    1038: "Reduction of microbial and faunal groups following application of streptomycin and captan in Georgia no-tillage agroecosystems",
    1093: "Biosafety regulation: Why we need it",
    1070: "Effect of cover crops and tillage system on symphylan (Symphlya: Scutigerella immaculata, Newport) and Pergamasus quisquiliarum Canestrini (Acari: Mesostigmata) populations, and other soil organisms in agricultural soils",
}

# CSV value -> (slug, the label readers see). Order is the page order.
COLLECTIONS = OrderedDict([
    ("Dr. Elaine's publications",   ("elaine",   "Dr. Elaine’s publications")),
    ("Other relevant publications", ("field",    "Soil food web science")),
    ("Internet articles",           ("internet", "Internet articles")),
])

# Shown as a small label on the card. Only USDA is renamed.
TYPE_LABELS = {"USDA": "USDA publication"}

FACETS = [
    ("Organisms", "the groups Soil Food Web students learn to identify under the microscope", [
        ("bacteria", "studies that measure, count or manipulate soil or compost bacteria."),
        ("fungi", "studies of soil fungi, fungal hyphae or fungal biomass, including fungal plant pathogens."),
        ("mycorrhizal fungi", "fungi that live in partnership with plant roots (arbuscular and ectomycorrhizal)."),
        ("protozoa", "flagellates, amoebae and ciliates, the main grazers of bacteria."),
        ("nematodes", "beneficial and root-feeding nematodes."),
        ("soil arthropods", "mites, springtails, symphylans and other small soil animals."),
        ("earthworms", "earthworms, including the worms used to make vermicompost."),
    ]),
    ("Practices and inputs", "what a grower or land manager actually does", [
        ("compost", "making, testing or applying thermal compost."),
        ("compost tea and extracts", "brewed compost tea and water extracts of compost or vermicompost, used as a drench or foliar spray."),
        ("vermicompost", "worm castings and vermicompost as an input."),
        ("cover crops and tillage", "cover crops, no-till, reduced tillage, crop rotation and alley cropping."),
        ("pesticides and fumigants", "the effects of biocides, fungicides, antibiotics and soil fumigants on soil life."),
        ("engineered microbes", "genetically engineered organisms released into soil, and their regulation."),
    ]),
    ("Outcomes", "the results readers care about", [
        ("nutrient cycling", "nitrogen, phosphorus and sulfur cycling, mineralization and nitrogen fixation."),
        ("soil carbon", "carbon storage, carbon sequestration and soil CO2 flux."),
        ("decomposition", "breakdown of litter, logs and other organic matter."),
        ("disease suppression", "biological control of plant diseases, including induced plant resistance."),
        ("pest suppression", "biological control of insect and other plant pests."),
        ("plant growth and yield", "measured plant growth, seedling vigour or crop yield."),
        ("food quality", "nutritional quality of crops, milk and other food."),
        ("remediation", "cleaning up contaminated soil or water, including heavy metals and hazardous waste sites."),
    ]),
    ("Systems", "the kind of land the study was done on", [
        ("farms and crops", "field crops, vegetables, orchards and dairy farms."),
        ("horticulture and nurseries", "container growing, greenhouses, nurseries, turf and ornamentals."),
        ("forests", "conifer, deciduous and riparian forests, and forest restoration."),
        ("grasslands and rangelands", "prairie, meadow and rangeland."),
        ("wetlands and streams", "wetlands and stream-side soils."),
        ("cold and winter soils", "soil life under snow and in the non-growing season."),
    ]),
    ("Approach", "the kind of work", [
        ("soil food web", "studies of the food web as a whole: who eats whom and what that does for plants."),
        ("lab methods and microscopy", "methods for counting, staining and measuring soil organisms."),
        ("soil biodiversity", "the diversity of soil organisms and why it matters."),
        ("policy and soil security", "regulation, policy and soil as a matter of public concern."),
        ("review", "papers that review or summarize a body of research."),
    ]),
]

STUDY_TYPES = [
    ("Field study", "done outdoors on real farms, forests or rangeland."),
    ("Greenhouse or pot trial", "plants grown in pots or containers under controlled conditions."),
    ("Lab study", "done in the lab, in petri dishes, microcosms or cultures."),
    ("Review", "summarizes earlier research."),
    ("Method", "describes or tests a way to measure something."),
    ("Report or guide", "technical reports, manuals and handbooks."),
    ("Article or commentary", "magazine columns, newsletters, opinion pieces and internet articles."),
]

REGIONS = ["North America", "South America", "Europe", "Africa", "Asia", "Global"]
REGION_NOTE = ("Region is where the study was done. Global means a review, a multi-country study, "
               "or work that is about no particular place.")

TOPICS = [t for _, _, tags in FACETS for t, _ in tags]


def slug(t):
    out = "".join(ch if ch.isalnum() else "-" for ch in t.lower().replace("’", "").replace("'", ""))
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def norm(t):
    return "".join(ch for ch in t.lower() if ch.isalnum())


def fail(msg):
    sys.exit("publications-import: " + msg)


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    need = ["title", "year", "type", "collection", "topics", "authors", "citation",
            "summary", "useful_for", "external_url", "study_type", "region"]
    missing = [c for c in need if rows and c not in rows[0]]
    if missing:
        fail("CSV is missing column(s): " + ", ".join(missing))
    entries = []
    for line, r in enumerate(rows, 2):   # line 1 is the header
        r = {k: (v or "").strip() for k, v in r.items() if k}
        where = "row %d (%s)" % (line, r["title"][:60])
        if r["collection"] not in COLLECTIONS:
            fail("%s: unknown collection %r" % (where, r["collection"]))
        if r["study_type"] not in [s for s, _ in STUDY_TYPES]:
            fail("%s: unknown study_type %r" % (where, r["study_type"]))
        if r["region"] not in REGIONS:
            fail("%s: unknown region %r" % (where, r["region"]))
        topics = [t.strip() for t in r["topics"].split(",") if t.strip()]
        for t in topics:
            if t not in TOPICS:
                fail("%s: unknown topic %r" % (where, t))
        if not r["year"].isdigit() or len(r["year"]) != 4:
            fail("%s: year %r is not four digits" % (where, r["year"]))
        entries.append(OrderedDict([
            ("title", r["title"]),
            ("year", int(r["year"])),
            ("type", TYPE_LABELS.get(r["type"], r["type"])),
            ("collection", COLLECTIONS[r["collection"]][0]),
            ("authors", r["authors"]),
            ("citation", r["citation"]),
            ("summary", r["summary"]),
            ("useful_for", r["useful_for"]),
            ("url", r["external_url"]),
            ("topics", topics),
            ("study_type", r["study_type"]),
            ("region", r["region"]),
        ]))
    return entries


def addresses(entries):
    """Give each entry its staging slug where it had one, else a new one."""
    with open(STAGING, encoding="utf-8") as f:
        staging = json.load(f)
    by_title = {}
    for x in entries:
        by_title.setdefault(norm(x["title"]), []).append(x)
    for s in staging:
        title = RETITLED.get(s["id"], s["title"])
        hits = [x for x in by_title.get(norm(title), []) if "slug" not in x]
        if len(hits) > 1:   # the same title twice in the CSV: the year decides
            hits = [x for x in hits if str(x["year"]) == str(s["year"])] or hits[:1]
        if not hits:
            fail("staging entry %d (%s) has no row in the CSV; add it to RETITLED"
                 % (s["id"], s["title"][:60]))
        hits[0]["slug"], hits[0]["staging_id"] = s["slug"], s["id"]
    used = {x["slug"] for x in entries if "slug" in x}
    for x in entries:
        if "slug" not in x:
            base = slug(x["title"])
            if len(base) > 90:   # cut at a word, not inside one
                base = base[:91].rsplit("-", 1)[0]
            s, n = base, 2
            if s in used:
                s = "%s-%d" % (base, x["year"])
            while s in used:
                s = "%s-%d-%d" % (base, x["year"], n)
                n += 1
            x["slug"] = s
            used.add(s)


def filters(entries):
    """Option lists built from the data: only values that occur, with counts."""
    col = Counter(x["collection"] for x in entries)
    top = Counter(t for x in entries for t in x["topics"])
    st = Counter(x["study_type"] for x in entries)
    rg = Counter(x["region"] for x in entries)
    opt = lambda value, label, n: OrderedDict([("value", value), ("label", label), ("count", n)])
    return OrderedDict([
        ("collection", [opt(s, label, col[s]) for s, label in COLLECTIONS.values() if col[s]]),
        ("topic", [OrderedDict([("facet", name),
                                ("options", [opt(slug(t), t, top[t]) for t, _ in tags if top[t]])])
                   for name, _, tags in FACETS if any(top[t] for t, _ in tags)]),
        ("study_type", [opt(slug(s), s, st[s]) for s, _ in STUDY_TYPES if st[s]]),
        ("region", [opt(slug(g), g, rg[g]) for g in REGIONS if rg[g]]),
    ])


def tag_guide():
    return OrderedDict([
        ("facets", [OrderedDict([("name", name), ("about", about),
                                 ("tags", [OrderedDict([("tag", t), ("definition", d)]) for t, d in tags])])
                    for name, about, tags in FACETS]),
        ("studyType", OrderedDict([("about", "one per paper"),
                                   ("tags", [OrderedDict([("tag", s), ("definition", d)]) for s, d in STUDY_TYPES])])),
        ("region", OrderedDict([("about", "one per paper"), ("values", REGIONS), ("note", REGION_NOTE)])),
    ])


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 tools/publications-import.py docs/sfw-publications-final.csv")
    entries = read(sys.argv[1])
    addresses(entries)
    total = len(entries)
    linked = sum(1 for x in entries if x["url"])
    out = OrderedDict([
        ("_source", "docs/sfw-publications-final.csv, finalized by Linnea Moritz on 8 October 2026. "
                    "Written by tools/publications-import.py; do not edit by hand."),
        ("counts", "%d publications. %d link to the publisher record, Google Scholar or a repository copy; "
                   "%d %s listed by citation because no copy was found online."
                   % (total, linked, total - linked, "is" if total - linked == 1 else "are")),
        ("total", total),
        ("collections", OrderedDict((s, label) for s, label in COLLECTIONS.values())),
        ("filters", filters(entries)),
        ("tagGuide", tag_guide()),
        ("entries", entries),
    ])
    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(out["counts"])
    print("kept staging addresses: %d, new addresses: %d"
          % (sum(1 for x in entries if "staging_id" in x), sum(1 for x in entries if "staging_id" not in x)))
    for k, opts in out["filters"].items():
        flat = [o for g in opts for o in g["options"]] if k == "topic" else opts
        print(k + ":", ", ".join("%s %d" % (o["label"], o["count"]) for o in flat))


if __name__ == "__main__":
    main()
