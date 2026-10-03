# Open-licence asset sources for the SFW living-soil exhibit
## Brief for Claude Code: test every source, fetch one real sample from each

Paste this whole file into Claude Code at the root of the project.

---

## Instruction to Claude Code

Build a folder `scripts/sources/` with one small Python or Node script per source below. For each source:

1. Confirm the endpoint or page is reachable and the access method in this brief still works. If it does not, find the current method from the site's own docs and fix the script; do not guess.
2. Fetch exactly one real sample asset (an image, a page scan, an SVG, a data file) related to soil organisms: bacteria, fungi, protozoa, nematodes, roots, mycelium, soil profiles.
3. Read the licence from the source's own metadata for that asset, not from this brief, and record it verbatim.
4. Write the sample to `assets/raw/{source}/` and append one line to `assets/manifest.json` with: source, asset URL, local path, title, creator, date, licence string, licence URL, and the credit line to display on the site.
5. Print a one-line PASS or FAIL per source, with the reason on FAIL.

Rules: install packages only where listed; prefer plain `requests` or `fetch` over wrappers when a wrapper is stale. Never commit fetched media; add `assets/raw/` to `.gitignore`. Keep every script under 60 lines. Do not skip a source because it looks hard; mark it FAIL with the reason and move on. Finish with a summary table of PASS/FAIL and the licence found for each.

---

## A. Public domain (US federal or CC0). No attribution required, credit anyway.

**NIH BioArt Source**
https://bioart.niaid.nih.gov/
Browse: https://bioart.niaid.nih.gov/discover
Vector illustrations of bacteria, cells, microbes. SVG, AI, EPS, PNG. Test: download one bacteria SVG and confirm it opens.

**CDC Public Health Image Library (PHIL)**
https://phil.cdc.gov/
Search: https://phil.cdc.gov/QuickSearch.aspx
Detail page pattern: https://phil.cdc.gov/Details.aspx?pid={id}
SEMs of bacteria and amoebae. Test: fetch one detail page, extract the high-res image URL and the "Copyright Restrictions: None" field.

**USDA NRCS Soil Biology Primer (Elaine Ingham's chapters)**
https://archive.org/details/CAT31312794
Full text: https://archive.org/stream/CAT31312794/CAT31312794_djvu.txt
Metadata API: https://archive.org/metadata/CAT31312794
Package: `pip install internetarchive`
Test: use the metadata API to list files, download the PDF, and pull the page with the "Typical Numbers of Soil Organisms" table.

**USDA ARS Image Gallery**
https://www.ars.usda.gov/oc/images/image-gallery/
Rhizobium nodules, actinomycetes, roots. Test: find one image page, download the full-size file, record the credit.

**Biodiversity Heritage Library (BHL)**
Site: https://www.biodiversitylibrary.org/
API v3 docs: https://www.biodiversitylibrary.org/docs/api3.html
Get a key: https://www.biodiversitylibrary.org/getapikey.aspx
Page image pattern (no key needed): https://www.biodiversitylibrary.org/pageimage/{pageid}
AWS Open Data bulk: https://registry.opendata.aws/bhl-open-data/
Flickr illustration stream: https://www.flickr.com/photos/biodivlibrary
Target volumes: Cobb, "Contributions to a Science of Nematology"; Leidy, "Fresh-Water Rhizopods of North America" (1879); Ehrenberg, "Die Infusionsthierchen" (1838); Kent, "A Manual of the Infusoria"; Tulasne, "Selecta Fungorum Carpologia".
Test: use `PublicationSearch` to find Leidy 1879, walk to a page ID, download that page image, and record the item's licence field.

**Smithsonian Open Access**
API: https://api.si.edu/openaccess/api/v1.0/search?q={query}&api_key={key}
Key: https://api.data.gov/signup/ (DEMO_KEY works for testing)
Docs: https://edan.si.edu/openaccess/apidocs/
Package: `pip install si-openaccess`
Bulk: https://registry.opendata.aws/smithsonian-open-access/
Test: search "mite" or "nematode", download one CC0 image, record the unit credit.

**PRMI root images (Dryad, CC0)**
https://doi.org/10.5061/dryad.2v6wwpzp4
Project page: https://gatorsense.github.io/PRMI/
Test: download the smallest species subset, confirm one image plus its mask load.

**Wikimedia Commons, NRCS soil profile photos**
https://commons.wikimedia.org/wiki/Category:Soil_Survey_(NRCS)
Test: covered under Commons in section B; pick one file from this category.

**NEON soil microbe and root data (CC0)**
https://data.neonscience.org/
API: https://data.neonscience.org/data-api/
Package: `pip install neonutilities`
Test: list soil microbe community products and download one site-month table.

**Earth Microbiome Project (CC0)**
https://earthmicrobiome.org/
Data: https://github.com/biocore/emp
Test: download one abundance or metadata table from the GitHub release.

---

## B. CC BY and CC BY-SA. Credit author, title, licence.

**NIAID on Flickr (CC BY)**
https://www.flickr.com/photos/niaid/
Flickr API: https://www.flickr.com/services/api/ (key: https://www.flickr.com/services/apps/create/)
Test: list NIAID photos tagged "SEM" or "bacteria", download one original, record `license` id and owner.

**Europe PMC open-access figures (CC BY per article)**
REST API: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=soil%20bacteria%20microscopy%20AND%20LICENSE:%22cc%20by%22&format=json
Docs: https://europepmc.org/RestfulWebService
Full text XML pattern: https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML
Test: find one CC BY article on Streptomyces or Bacillus in soil, extract a figure URL from the XML, download it, record the article citation.

**Wellcome Collection (CC BY 4.0 / PD)**
API: https://api.wellcomecollection.org/catalogue/v2/images?query=bacteria
Docs: https://developers.wellcomecollection.org/
IIIF image endpoints are in each record.
Test: fetch one image record, download at 2000 px via IIIF, record the `license` field.

**Wikimedia Commons (per-file licence, keep CC0 / CC BY / CC BY-SA / PD)**
API: https://commons.wikimedia.org/w/api.php
Category members: https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Testate_amoebae&cmtype=file&cmlimit=50&format=json
File info: https://commons.wikimedia.org/w/api.php?action=query&titles=File:{name}&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=2000&format=json
Categories to test: Testate_amoebae, Ciliophora, Amoebozoa, Nematoda, Hyphae, Mycorrhizae, Collembola, Images_from_the_CDC_Public_Health_Image_Library
Package: `pip install mwclient` (optional; raw requests is fine)
Test: pull one file per category, read `LicenseShortName` and `Artist` from extmetadata, keep only permitted licences.

**iNaturalist Open Dataset (per-photo licence, keep CC0 / CC BY / CC BY-SA)**
Docs: https://github.com/inaturalist/inaturalist-open-data
AWS registry: https://registry.opendata.aws/inaturalist-open-data/
Metadata bucket: s3://inaturalist-open-data/metadata/ (photos.csv.gz, taxa.csv.gz, observations.csv.gz)
Photo URL pattern: https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}/original.{ext}
Live API for a quick test: https://api.inaturalist.org/v1/observations?taxon_name=Collembola&photo_license=cc0,cc-by&quality_grade=research&per_page=5
Package: `pip install pyinaturalist`
Test: use the live API, download one CC0 or CC BY photo, record observer and licence.

**GBIF media (per-record licence)**
API: https://api.gbif.org/v1/occurrence/search?mediaType=StillImage&license=CC0_1_0&q=nematoda&limit=5
Docs: https://techdocs.gbif.org/en/openapi/
Package: `pip install pygbif`
Test: fetch one CC0 image URL and its publisher.

**Zenodo 13321089, phase-contrast bacteria time-lapse (CC BY)**
https://zenodo.org/records/13321089
Test: download the smallest file, extract one frame, record licence.

**Broad BBBC010, C. elegans brightfield (CC BY 3.0)**
https://bbbc.broadinstitute.org/BBBC010
Test: download one image set zip, confirm one PNG loads.

**ISRIC WoSIS soil profiles (CC BY 4.0)**
https://www.isric.org/explore/wosis
WFS/REST access: https://www.isric.org/explore/wosis/accessing-wosis-derived-datasets
Test: query profiles near Corvallis, Oregon (44.57, -123.26) and return horizon depths for one profile.

**ISRIC SoilGrids (CC BY 4.0)**
REST point query: https://rest.isric.org/soilgrids/v2.0/properties/query?lon=-123.26&lat=44.57&property=soc&depth=0-5cm&value=mean
Docs: https://www.isric.org/explore/soilgrids/faq-soilgrids
Test: run the point query above and print the result.

**Fricker lab FungalNetworkAnalysis (CC BY)**
https://zenodo.org/records/14931863
Test: download, locate the sample mycelium image, save it.

---

## C. MIT. Credit only.

**WHOI-Plankton (IFCB)**
Paper: https://arxiv.org/abs/1510.00745
Data: https://github.com/hsosik/WHOI-Plankton
Test: download one class folder, confirm images load, record the licence file.

---

## D. Citation requested.

**Cornell spatial-fungi, 270 real mycelial networks**
https://www.cs.cornell.edu/~arb/data/spatial-fungi/
Direct zip: https://www.cs.cornell.edu/~arb/data/spatial-fungi/fungal_networks.zip
Cite: Lee, Fricker, Porter, "Mesoscale analyses of fungal networks as an approach for quantifying phenotypic traits", J. Complex Networks 2017.
Test: download, load one Phanerochaete velutina network, print node and edge counts and coordinate ranges. This is the hero animation; after PASS, export it as JSON `{nodes:[{id,x,y}], edges:[{source,target,weight}]}` to `assets/data/fungal_network.json`.

**RSML root system files**
https://rootsystemml.github.io/
Examples: https://github.com/RootSystemML/RootSystemML.github.io/tree/master/images/examples
Raw file pattern: https://raw.githubusercontent.com/RootSystemML/RootSystemML.github.io/master/images/examples/{name}.rsml
Cite: Lobet et al. 2015, Plant Physiology.
Already tested and working; `anagallis.rsml` is in the mockup. Include in the manifest for completeness.

---

## After the tests

Write `SOURCES.md` from the manifest: one line per PASS source with the credit line exactly as it should appear on the site. Then stop and report; do not start processing images until the manifest is reviewed.
