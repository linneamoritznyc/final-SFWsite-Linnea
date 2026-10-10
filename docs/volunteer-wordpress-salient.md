# Volunteer page: how to build it in WordPress (Salient + WPBakery)

For Stephanie. The preview of the finished page is
https://finalsite-git-final-images-v2-linneamoritznycs-projects.vercel.app/volunteer/
and the page lives at new.soilfoodweb.com/volunteer/. Every photo and icon is in the Drive
folder "05 Volunteer" (numbered in page order, with the alt text in the image list), and also
in this repo under `exports/stephanie/volunteer/`. The copy is on the preview page: copy it
word for word from there.

Colours used below: Food Web Green `#156826`, Soil Brown `#4F3433`, Organic Cream `#F4F1EA`,
white `#FFFFFF`, card border `#E2DED4`.

The page has six sections, top to bottom. Build each one as its own WPBakery **Row**.

---

## 1. Hero: "Volunteer with us"

- **Row**: white background, 2 columns (1/2 + 1/2), vertically centred.
- **Left column**:
  - Text Block: eyebrow "VOLUNTEER" (small caps, green), H1 "Volunteer with us", the lead paragraph.
  - Two **Buttons**: "Sign up to volunteer" (filled green, link `#join`) and "See the ways to help"
    (outline green, link `#ways`).
- **Right column**: **Single Image**, file 01 (hero). Rounded corners on, size full width.
  Alt text from the image list. No caption.

## 2. "Start in the next ten minutes"

- **Row**: background Organic Cream `#F4F1EA`. Heading (H2) and the one-line intro on top,
  then an inner row with **3 columns** (1/3 each).
- Each column is a white card: give the column a white background, a 1 px `#E2DED4` border,
  12 px rounded corners and no padding at the top, so the photo sits flush at the top edge.
  Set the inner row's column alignment to **top** (Content Position: Top), so each card is only
  as tall as its own content. Equal-height columns leave an empty gap in the shorter cards.
- **Card 1 (Watch the soil food web animation)**: Single Image file 02, cropped 16:9.
  Caption under the photo: "Photo: Patricia J Coppola". Then the small label "ABOUT 5 MINUTES",
  the H3 title, the text, and a text link "Watch the animation →" to `/how-it-works/#the-soil-food-web`.
- **Card 2 (Share a free webinar)**: Single Image file 03, cropped 16:9. No caption. Label,
  title, text, link "Browse free webinars →" to `https://webinar.soilfoodweb.com`.
- **Card 3 (Show us your soil)**: Single Image of our Instagram feed (file in the image list),
  linked to `https://www.instagram.com/soilfoodwebschool/`. A live feed is better: an Instagram
  feed plugin (for example Smash Balloon Instagram Feed) shows the latest posts. The plain
  profile embed below is blocked in some browsers, so only use it as a test:

  ```html
  <iframe src="https://www.instagram.com/soilfoodwebschool/embed/"
          title="Soil Food Web School on Instagram" loading="lazy" scrolling="no"
          style="display:block;width:100%;height:340px;border:0;background:#F4F1EA"></iframe>
  ```

  Then the label, title, text, and the link "Open Instagram →" to
  `https://www.instagram.com/soilfoodwebschool/`.

## 3. "Pick the way you want to help" (21 flip cards with a time filter)

### How the flip cards on new.soilfoodweb.com are built today

Checked in the page source of new.soilfoodweb.com on 10 October 2026:

- **The flip tiles on the home page** ("Observe and assess", "Incubate the biology" ...) are
  Salient's own **Flip Box** element (`nectar-flip-box`), one per column in an inner row with
  4 columns (`vc_col-sm-3`). Settings used: minimum height **400 px**, flip direction
  **horizontal to left**, text aligned **centre / centre**. Front: a photo background with a
  dark overlay and light text. Back: a background colour (`#F4F1EA` or `#59A76C`) with the text.
  There is no filter on those tiles.
- **The filters on the site are not Salient**: they come from the team's own plugins.
  `/workshops/` uses the **sfw-workshops** plugin (version 1.0.22): workshops are their own post
  type, the plugin prints the cards with `data-country` and `data-year`, and its
  `workshops.js` shows and hides cards when you click a country chip
  (`data-sfw-country`) or pick a year. The home page's program carousel is the **sfw-programs**
  plugin (1.1.2). So "chips that filter cards" already exists on the site, built by Alex in a
  plugin.

### Recommended: build the roles like the workshops (Alex)

Add the 21 roles the same way the workshops are done: a "Volunteer role" post type (title,
short text, Time line, time group, icon) and a shortcode that prints the chips and the grid of
flip cards, with the filter script copied from `workshops.js` (chips set a value, cards whose
`data-time` does not match get `is-hidden`). This keeps the grid without gaps when cards are
hidden, lets Stephanie edit roles like workshops, and the flip styling can copy Salient's Flip
Box look (or the CSS of the preview, `.flip` in this repo's css/site.css).

### Quicker option: Salient Flip Box elements only (Stephanie)

If the plugin is not ready in time, build the cards with the same Flip Box element as the
home page and add the filter as a Raw HTML snippet (below).

- **Cards**: an inner row with **3 columns** per row, 7 rows (21 cards), each column holding one
  **Flip Box**. Settings, matching the home page tiles:
  - Flip direction: **horizontal to left**. Minimum height: **240 px** (the home tiles use
    400 px with photos; these cards only hold an icon and a title). Text align: centre / centre.
  - **Front**: background white, text dark. Content: the icon (file "icon N", 48 x 48 px, alt
    text empty because it is decorative), then the card title as an H3 in Soil Brown.
  - **Back**: background **Food Web Green `#156826`**, text light (white). Content: the card's
    text, then "**Time:** …" on its own line.
  - Extra class name: the card's time group, e.g. `time-event`, used by the filter.

| # | Card | Time | Filter class(es) |
|---|---|---|---|
| 1 | Host a compost day | One weekend, a few times a year | time-event |
| 2 | Share your microscope | 2 to 4 hours a month | time-monthly |
| 3 | Translate the science | Flexible, remote | time-flexible |
| 4 | Run a local meetup | About 5 hours a month | time-monthly |
| 5 | Document the work | Per event | time-event |
| 6 | Lend professional skills | Project based | time-flexible |
| 7 | Collect field data | Seasonal, a few hours a visit | time-event |
| 8 | Welcome new students | 1 to 2 hours a week | time-weekly |
| 9 | Staff an event table | Per event | time-event |
| 10 | Write and research | Flexible, remote | time-flexible |
| 11 | Host a fundraiser | One-off | time-event |
| 12 | Share your own idea | Up to you | time-flexible |
| 13 | Put your farm on the map | 15 minutes | time-quick |
| 14 | Run a jar test | One afternoon | time-event |
| 15 | Interview a grower | A few hours per story | time-event |
| 16 | Lend land or a space | When you can | time-flexible |
| 17 | Move supplies | Now and then | time-flexible |
| 18 | Start a worm bin | 10 minutes a week | time-quick time-weekly |
| 19 | Spread the word | 10 minutes a week | time-quick time-weekly |
| 20 | Host a watch party | One evening | time-event |
| 21 | Answer questions online | An hour a week | time-weekly |

The card text for each is on the preview page (back of each card).

### The time filter (quick option only)

A **Raw HTML** element above the cards: it draws the chips and hides the columns whose flip box
does not have the chosen class.

```html
<div class="vol-chips" role="group" aria-label="Filter by time">
  <button type="button" data-time="" aria-pressed="true">All</button>
  <button type="button" data-time="time-quick" aria-pressed="false">Under an hour</button>
  <button type="button" data-time="time-weekly" aria-pressed="false">Weekly</button>
  <button type="button" data-time="time-monthly" aria-pressed="false">Monthly</button>
  <button type="button" data-time="time-event" aria-pressed="false">Per event or one-off</button>
  <button type="button" data-time="time-flexible" aria-pressed="false">Flexible</button>
</div>
<script>
document.addEventListener("DOMContentLoaded", function () {
  var chips = document.querySelectorAll(".vol-chips button");
  var cols = document.querySelectorAll("#ways .wpb_column");
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      var t = c.getAttribute("data-time");
      chips.forEach(function (o) { o.setAttribute("aria-pressed", String(o === c)); });
      cols.forEach(function (col) {
        var box = col.querySelector("[class*='time-']");
        if (!box) return;
        col.style.display = (!t || box.className.indexOf(t) > -1) ? "" : "none";
      });
    });
  });
});
</script>
```

CSS for Salient → Custom CSS:

```css
.vol-chips { display: flex; flex-wrap: wrap; gap: .5rem; margin: 0 0 1.25rem; }
.vol-chips button { font-family: Montserrat, sans-serif; font-weight: 600; font-size: 13px;
  padding: .55em 1.1em; border-radius: 999px; border: 1px solid #156826; background: #fff;
  color: #156826; cursor: pointer; }
.vol-chips button[aria-pressed="true"] { background: #156826; color: #fff; }
```

With Salient columns, hidden cards leave gaps in their rows (each row keeps its 3 slots).
Put all 21 flip boxes in **one** inner row so the columns wrap, or use the plugin route above,
which has no gaps.

## 5. "Questions people ask first"

- **Row**: white background, row ID `questions`, 2 columns (1/2 + 1/2), vertically centred.
- **Left column**: H2, then a Salient **Toggles** element (style: minimal, all closed) with the
  five questions as toggle titles and the answers inside.
- **Right column**: Single Image file 26, rounded corners, no caption.

## 6. "Join the volunteer network"

- **Row**: Organic Cream background, row ID `join` (the hero button jumps here), 2 columns
  (2/3 + 1/3).
- **Left column**: H2, the intro line, and the volunteer form. Use the site's form plugin (the
  same one as the workshop interest forms) with these fields: Name (required), Email (required),
  Where are you?, Time you can give (dropdown), What would you like to do? (dropdown with the
  21 card titles and "Other"), Languages you speak, a message box, and a Send button.
  Confirmation text: "Sent. A volunteer coordinator will reply within a week." Who receives the
  form, Evan and Stephanie decide.
- **Right column**: Single Image file 27 at the top, rounded corners, no caption. Under it:
  H2 "How it works" with the four numbered steps, then "Other ways to help" with three links
  (Give money instead → /donations/, Invite us to speak → /invite-us-to-speak/,
  Find a professional → /find-a-professional/).

---

## Checks before publishing

- Every image has its alt text from the image list. Icons: alt text empty.
- Only one H1 on the page (the hero).
- Flip cards turn over on hover on a laptop and on tap on a phone. Check both.
- The Instagram block shows the profile and posts (it can take a few seconds to load).
- The time filter: each chip shows only its cards; "All" shows all 21.
- No em dashes in the copy.
