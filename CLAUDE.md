# CLAUDE.md: buildowners.com

Instructions for Claude working in this repository. Note: GitHub Pages publishes every file here, so this file is public at buildowners.com/CLAUDE.md. Keep anything private out of it.

## How to talk to Matt

- Be as succinct as possible in every reply and message. Lead with the answer or the result. No preamble, no recap, no narration of steps.
- Plain English. Never use em dashes or en dashes.
- End every reply with `Confidence: X%`.
- Recommend one option when there are several. Ask only when the decision is truly his.

## What this site is

BUILD (Business United In Leadership Development): monthly peer rooms for Northeast Ohio business owners, run by Josh Muller and Matt LaFleur of Maple Creek Advisors. Static HTML, no build framework.

## Publishing

- The default branch `claude/new-session-okqft0` is the live site. Every push publishes to buildowners.com within about a minute (GitHub Pages, workflow "pages build and deployment"). There is no staging.
- Do not push until Matt approves, unless he has said to publish. Commit locally and show him the change first.
- CDN caching can delay what you see for up to 10 minutes. Verify live pages with a cache-busting query string.

## Files

| File | Role |
| --- | --- |
| `index.html` | Homepage, edited by hand. Its nav and footer are the source for every room page. |
| `assets/site.css` | Shared stylesheet. |
| `tools/build_pages.py` | Generates the room pages (`akron-breakfast/`, `independence-breakfast/`, `akron-lunch/`) and `sitemap.xml`. |
| `CNAME`, `.nojekyll`, `robots.txt`, `404.html` | Hosting and crawl settings. Leave alone unless asked. |

## Room pages

- Never edit the room pages' `index.html` by hand. Edit `ROOMS` in `tools/build_pages.py`, then run `python3 tools/build_pages.py`.
- Each room has `rsvps` (label, URL, last day shown) and `skip` (cancelled dates). Every room runs 90 minutes. End times are calculated from the start time.
- Rerunning the generator also refreshes the event dates and the sitemap. If a task is narrow, do not commit unrelated date changes with it.
- After a change to a room's day, time, venue, or RSVP link, update the matching homepage location card in `index.html` too.

## Content rules

- Never invent prices, dates, venues, capacities, outcomes, or testimonials. If a fact is missing, ask or leave it out.
- Framework name: "BUILD 52". Book name: "BUILD 52 OS".
- Contact emails: josh@maplecreekadvisors.com and matt@maplecreekadvisors.com.
- Use only the approved headshots in `assets/`. No other personal photos.

## Phones, tablets, and desktops

- Every page must work well on phones, tablets, and desktop browsers.
- Before asking Matt to publish a layout or page change, check it at three widths with Playwright: phone (390 px), tablet (820 px), and desktop (1280 px or wider). Confirm there is no sideways scrolling, text and buttons are readable and easy to tap, and nothing overlaps or gets cut off.
- Show Matt a screenshot when the change is visual.

## Keep Maple Creek Advisors in sync

maplecreekadvisors.com (repo `mattlafleur-cle/mca`) lists BUILD rooms in `site.config.mjs` under `build.gatherings`. When rooms, cities, or the Retreat to Advance wording change here, update that repo too and follow its own CLAUDE.md.

## Commits

Clear, specific messages (for example, "Akron Lunch: RSVP button for Jan 19, 2027").
