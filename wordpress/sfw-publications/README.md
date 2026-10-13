# SFW Publications (WordPress plugin)

The publications list for soilfoodweb.com: 180 entries, each with a Summary and a
Useful for line, plus a search box, collection buttons and Topic, Study type, Region
and Sort dropdowns. No API key, no outside service, no other plugin needed.

## Install

1. In WordPress: Plugins → Add New → Upload Plugin → choose `sfw-publications.zip` → Install → Activate.
2. Edit the Publications page and add a Shortcode block containing:

       [sfw_publications]

   Put it where the old list was. Remove the old list (and its search box and Topic
   dropdown) from the page.
3. Update the page and view it.

## Update the list

The list is read from `data/sfw-publications-final.csv` inside the plugin. To change
an entry, edit the spreadsheet, export it as CSV with the same columns, and replace
that file (by uploading a new plugin zip, or over SFTP). The page refreshes on its own
when the file changes.

Columns used: title, status (only "publish" rows show), year, type, collection,
topics (comma-separated), authors, citation, summary, useful_for, external_url,
study_type, region. The others (id, content, source_url, slug) are ignored.

## How the search works

Every entry is printed on the page. A small script (`assets/sfw-publications.js`,
plain JavaScript) hides and shows them as the reader types or picks a filter: an entry
shows only if it passes every filter and contains every word typed. Search reads the
title, authors, citation, summary, useful-for line, topics and year. The filters are
kept in the address (`?topic=compost-tea-and-extracts&region=europe&q=tea`), so a
filtered view can be shared as a link. Without JavaScript the full list shows.

## Files

- `sfw-publications.php`: the shortcode, reads the CSV and prints the list (cached until the CSV changes).
- `assets/sfw-publications.css`: the styles, all scoped to `.sfwp` so the theme is not affected.
- `assets/sfw-publications.js`: the search and filters.
- `data/sfw-publications-final.csv`: the list (finalized 8 October 2026).
