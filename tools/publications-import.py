#!/usr/bin/env python3
"""Load the publications CSV into content/research.json.

    python3 tools/publications-import.py path/to/sfw-publications-final.csv

The CSV is the single source of truth (the copy kept in this repository is
docs/sfw-publications-final.csv). This script rewrites only the parts of
content/research.json -> database that come from it: the entries, the filter
option lists, the counts line and the tag guide. The h2, lede, Google Scholar
button, columnNote and workWithUs stay exactly as they are.

Nothing in a row is edited. Values are stripped of surrounding whitespace and
that is all. A collection, study type, region or topic that is not in the
controlled lists below stops the import with the row number, so a typo in the
spreadsheet cannot quietly become a new filter option.

Then run tools/build.py to render research.html.
"""
import csv, json, os, sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON = os.path.join(ROOT, "content", "research.json")

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

# The one note this import makes obsolete. Matched on its opening words so a
# small edit to the wording elsewhere does not keep it alive.
STALE_NOTE = "plain-language one-line summaries"


def slug(t):
    out = "".join(ch if ch.isalnum() else "-" for ch in t.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


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
        sys.exit(__doc__.strip().splitlines()[2].strip())
    entries = read(sys.argv[1])
    linked = sum(1 for x in entries if x["url"])
    total = len(entries)

    with open(JSON, encoding="utf-8") as f:
        c = json.load(f, object_pairs_hook=OrderedDict)
    d = c["database"]
    d["notes"] = [n for n in d.get("notes", []) if not n.startswith(STALE_NOTE)]
    d.pop("sections", None)          # the old numbered sections; entries replace them
    d["counts"] = ("%d publications. %d link to the publisher record, Google Scholar or a repository copy; "
                   "%d %s listed by citation because no copy was found online."
                   % (total, linked, total - linked, "is" if total - linked == 1 else "are"))
    d["filters"] = filters(entries)
    d["tagGuide"] = tag_guide()
    d["entries"] = entries

    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(d["counts"])
    for k, opts in d["filters"].items():
        if k == "topic":
            print("topic:", ", ".join("%s %d" % (o["label"], o["count"]) for g in opts for o in g["options"]))
        else:
            print(k + ":", ", ".join("%s %d" % (o["label"], o["count"]) for o in opts))


if __name__ == "__main__":
    main()
