# Salient rebuild brief

The brief for rebuilding this site in the Salient Nonprofit theme, as received on 13 September 2026. Kept here word for word so the WordPress build works from the same list as the static reference. The reference build now lives on branch `claude/new-session-12x7z2`, which carries everything on `claude/session-gni7rl` plus the audit changes listed below. Section-by-section element mappings are in `salient-migration-guide.md`; the photograph list is in `image-map-for-salient.md`.

Two items under "Images still needed" below were already in the repository when the brief arrived: the microbe cutout PNGs (`img/uploads/1.png` to `7.png`, on Science and Volunteer) and the Wild Ken Hill highlight reel (`video/wild-ken-hill/wkh-2026-reel.mp4`, on the story page since 13 September 2026). The five community photographs, the staff headshots, the hero photograph's caption and the Vimeo ids are still open.

---

# Fable Prompt: SFW Website Rebuild for Salient WordPress Theme

You are helping rebuild the Soil Food Web Foundation website. The static HTML reference build is at github.com/linneamoritznyc/SFW-newwebsite (branch `claude/session-gni7rl`). The target theme is **Salient Nonprofit** by ThemeNectar (https://themenectar.com/salient/nonprofit/).

## What has been done (static HTML reference)
- Full site structure: index.html, learn.html, science.html, about.html, about-team.html, about-elaine.html, about-governance.html, community.html, volunteer.html, donate.html, practice.html, research.html, news.html, calendar.html, directory.html, contact.html, learn-webinars.html, learn-scholarships.html, login.html, privacy.html, terms.html, accessibility.html
- Design system in css/site.css with custom properties (tokens in :root)
- All copy sourced from docs/copy-deck-v2.md
- Microbe cutout gallery with float animation on science + volunteer pages
- 8-column pathway grid on learn page showing roles (Designer, Farmer, Consultant, etc.) with course boxes below
- Stats section with 3 numbers: 100+ countries, 10,000+ enrolled, 40-year legacy
- Amoeba loop videos (hero, square, lab variants in /video/)

## Key changes from Evan's audit (already applied to HTML, carry into WordPress)

### Copy/text changes
1. **Utility bar** (top dark strip): now says "The Soil Food Web Foundation 501(c)(3)" (NOT "Join a global community...")
2. **Hero h1**: "Join a global community of Soil Regenerators" is the BIG heading. "Healing soil. Feeding humanity. Restoring the living world." is the subtext below it.
3. **learn.html heading**: "Partner with nature's intelligence" (NOT "Work with the life in your soil")
4. **All buttons**: "Explore our programs" replaces "See every program and price" everywhere
5. **NEVER use**: "nature's operating system", any em dashes, acronyms (FC/AP/PDC) in public text, "certified" 
6. **Subscribe button text**: just "Subscribe" (not "Subscribe to the newsletter")

### Visual/layout priorities Evan stressed
1. **The hero image should NOT be full-width** -- it uses `shot--wide` class (constrained width), not `shot--full`
2. **More and better photographs** -- Evan wants the site to feel image-heavy like the Salient nonprofit demo. Use big image cards (like the Salient card style) with less white space. Especially:
   - People at microscopes (lab images, students learning)
   - Group photos from events/workshops  
   - Hands-on compost/soil work
   - The microscopy cutouts (Nicole Masters images) with the floating animation
3. **Microscopy is the core differentiator** -- the ability to SEE soil life under a microscope is what makes SFW unique. Don't bury this. Lead with microscopy images and the "see and understand" message.
4. **Salient card-style image blocks** -- where we have text-heavy sections, convert to large image cards with overlaid or adjacent text, similar to Salient's demo sections
5. **Stats section needs all 3 numbers** visible (100+ countries, 10,000+ enrolled, 40-year legacy)

### Learn page pathway diagram
The pathway section on learn.html is an **8-column horizontal grid** where each column has:
- An oval role label on top (Designer, Farmer, Consultant, Lab Tech, Composter, Gardener, Ecosystem Restorationist, Scientist)
- 1-2 rectangular course boxes below the oval
- All 8 columns visible simultaneously (horizontally scrollable on mobile)
- This is NOT a click-to-reveal accordion -- everything shows at once

### Course structure (from Evan's Miro board)
- **Foundation Courses** = prerequisite for everything else (theory)
- **Advanced Programs** (4 tracks): Observe and Assess (microscopy), Biocomplete Compost, Biological Liquid Amendments (Multiply and Apply), Field Trials (Manage and Monitor)
- **Accelerator Workshop** = compressed version (in-person, includes 2-day seminar replacing FC prerequisite)
- **Intro to Foundation Courses** = 10% of FC content, $500, for people who want the big picture only
- **Complete Practicum** = full bundle of all 4 advanced programs (~3.5 years)
- Prerequisite is important to communicate clearly
- Bundle and save discount exists for Complete Practicum

### Pages/sections to improve
1. **Practice page**: The "three ways in" / "come in the door" section Evan flagged as AI-sounding. Reframe.
2. **Science page**: Evan said the reference build's science page is better than his. Keep the Vimeo embeds for the 6 mechanisms. Lead with microscopy.
3. **Volunteer page**: Keep the tiered volunteer levels but cut the fake testimonials. Add microbe gallery.
4. **Community page**: 5 images in the news section are BROKEN (files don't exist). Need real images from Evan.

### Images still needed (ask Evan)
- Hero image: Evan prefers a group photo (people making compost together, arms around each other at an event) over the current Elaine microscope shot
- 5 broken community page images
- Microbe cutout PNGs (1-7.png) for the Nicole Masters gallery -- these need to be uploaded to the repo
- Staff headshots for about-team page
- Wild Ken Hill highlight reel video
- Confirm Vimeo embed IDs are final

### Technical notes for Salient migration
- Static site uses no framework -- one CSS file, one JS file
- Keep HTML semantic and clean for WordPress portability
- Links go to school.soilfoodweb.com only (never old WordPress shop)
- Every number needs a .source line
- Every dated item shows its date
- Footer must have the legal block (EIN, registered office, Form 990 reference)
- Respect the `<p class="todo">` placeholder system -- these mark content that still needs to come from the Foundation

### Tone
- Warm, direct, community-focused
- NOT technical/enumerated/AI-sounding
- "Learn with us", "Explore our programs", "Join the community" -- invitational language
- Avoid language that "screams AI" per Evan: overly specific enumerations like "see every program and price", technical specs phrasing, "come in the door that is yours"
