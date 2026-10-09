Hi Claude! You're continuing image work on the Soil Food Web Foundation website with me (Linnea). In this chat we finalise the images on the **Community** page. Stephanie (who builds the real site in WordPress) has ideas for photos to add, and I'll send them to you as Google Drive links or screenshots as we go.

## Repo and branches
Repo: `linneamoritznyc/final-SFWsite-Linnea` (one repo, two branches, two Vercel sites):

1. **main** is the site I review on: https://finalsite-tau.vercel.app/ (Community page: https://finalsite-tau.vercel.app/community/). I've approved pushing image changes to main. Push straight to main after each finished change, then check the live page shows it.
2. **final-images-v2** is an exact copy of new.soilfoodweb.com (same addresses, sections, copy and image slot sizes). It exists only to hand Stephanie the final image for every slot. Preview: https://finalsite-git-final-images-v2-linneamoritznycs-projects.vercel.app/community/
   Every image change on main goes into the same slot on final-images-v2 too, where that slot exists there. Never push final-images-v2 to main.

Clone the repo, put a git worktree for each branch side by side, and read `CLAUDE.md` on each branch before you start.

## How images go in
- Put source photos (my Drive links, HEIC is fine; convert to JPG) in `img/new-2026-10/`. Place them in the page fragment `src/pages/community.html` with `{{photo file="..." alt="..." class="card__img" card sizes="..."}}`, copying the line the slot already uses.
- The build makes WebP and JPG at 1600 and 800 px, under 300 KB, with EXIF removed and no upscaling.
- Then run `python3 tools/site/build.py` and `python3 tools/site/check.py`. Main must print 0 problems. On final-images-v2, 8 problems on /testimonial/ pages were already there; leave them.
- **When an image changes, give it a new file name.** Vercel caches /img/ for a week, so a changed image under the same name won't show in the browser.
- To crop, crop the source file in Python, centred on the subject. If I mark a crop on a screenshot, match it exactly.
- Screenshot the section at 1440 and 390 px wide with Playwright (`NODE_PATH=/opt/node-tools/node_modules`, executablePath `/opt/pw-browsers/chromium`, serve the folder with `python3 -m http.server`). Look at it before telling me it's done.
- Alt text: plain description of only what's visible. Microscope photos get a short caption. Diagrams and R5A shoot photos get none.

## Image rules (never break these)
- **Never use:**
  - USDA NRCS photos
  - stock photos (garden-vegetable-beds is the only exception, and it's already used elsewhere, so don't reuse it)
  - Rancho Cacachilas photos
  - EN-ERC-Fig diagrams
  - the Gerald liquid amendments photo, anywhere (costa-rica-2025-gerald-liquid-amendments / 2025-year-in-review-gerald)
- "CTPFW Students Smiling 1" (card-students-holding-buckets) goes on the Community page only.
- **Don't reuse a photo that's already on another page.** Check `src/pages/` and `tools/site/gens.py` on both branches before you pick one. The Wild Ken Hill blog post is hidden from post lists for now (`"hidden": true` in content/repo-posts.json on main). Keep it in the repo.
- Copy on final-images-v2 stays word for word what's on new.soilfoodweb.com. Don't change text unless I ask.
- Use the classes that already exist in `css/site.css`, and don't restyle.

## Handoff for Stephanie (on final-images-v2, after each round)
- Measure every slot: `node tools/handoff/slots.js http://localhost:<port> <pages.json> tools/handoff/slots-1440.json`. pages.json lists every page path; build it from the sitemap or the `path:` front matter in src/pages plus the item pages.
- Then run `python3 tools/handoff/export.py tools/handoff/slots-1440.json`. That writes `exports/stephanie/<page>/` JPGs cut to each slot and `exports/stephanie/image-handoff.csv`.
- export.py wipes `exports/stephanie/`, so keep messages in `exports/messages/`.
- When I say the Community page is final, write a message for my other Claude chat (the one that builds Stephanie's Drive folder) in the same format as `exports/messages/message-home-final.txt`:
  - a numbered list in page order, grouped by section, with a "Jump to" text-fragment link to each section on new.soilfoodweb.com
  - slot, "Save as" name, raw GitHub file link, alt text, caption, size and the original's Drive link
  - the subfolder named "0X Community (FINAL)"

## How to talk to me
I'm an artist, not a developer. Keep replies short and plain: what changed, the live link, and anything that failed. Don't describe what you're about to do, and don't ask permission for routine steps. Decide and keep going. When I say a picture doesn't work, find an alternative that fits the section's message and isn't used elsewhere.

## Where things stand
- **Home:** final. The message for the Drive folder is done.
- **About Us:**
  - Teaching & learning = Learning Outside, Santa Fe 2026 (learning-outside-santa-fe-2026.jpg)
  - Pursuing knowledge = the funnel test photo (pursuing-knowledge-sieve-funnel-test.jpg)
  - Incubating applied practice = the compost windrow photo (R5A_3980.jpg)
- **Programs Overview:** approved.
- **Community:** this chat. Start by screenshotting https://finalsite-tau.vercel.app/community/ and the final-images-v2 Community page, list every image slot in order (section, slot, current photo) so I can see what's there, then wait for Stephanie's photos.
