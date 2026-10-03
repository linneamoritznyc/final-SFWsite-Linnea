<!-- This file is project configuration for Claude Code (claude.ai/code).
     It tells the AI assistant what rules to follow when working on this repo.
     It does not affect the website build or deployment. -->

# Soil Food Web Foundation website rebuild

Read before doing anything: docs/copy-deck-v2.md (every word on the site, decisions at the top),
docs/sfw-website-audit-verbatim.md (Evan's feedback, the spec), docs/Fable_Course_Audit_Sep_6_Linnea_Moritz.md.

## Hard rules
- Static HTML, one stylesheet css/site.css, one script js/site.js, tokens in :root. No framework, no build, no animation library.
- Use only the classes that exist in site.css. Add CSS only for a component that does not exist. Design system is done; do not restyle it.
- Never invent a price, name, date, statistic or document. Use <p class="todo">what is needed, who supplies it</p>.
- Copy comes from docs/copy-deck-v2.md. Do not write new marketing copy.
- No em dashes, no "nature's operating system", no "certified", no acronyms (FC/AP/PDC) in public text, no percentages without a named source.
- Every number gets a .source line. Every dated item shows its date. Every page has the footer legal block.
- Links to school.soilfoodweb.com only; never to the WordPress shop or /foundation-courses-2/.
- After building a page: screenshot it at 1440 and 390 with Playwright, look, fix, then stop and report placeholders.

## Order
1. index.html  2. learn.html (with the pathway diagram)  3. science.html  4. about-governance.html
5. one case study  6. now.html  7. the rest as clean pages from the copy deck  8. link, a11y, speed passes.
