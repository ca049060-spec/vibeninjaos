# VibeNinjaOS

Website for vibeninjaos.app: the home for the tools Shawn builds with AI, and later a shelf for tools built by other people.

## How the site is laid out

- `/` home, `/how-it-works.html`, `/pricing.html`, `/contact.html`, and `/thanks.html` are hand-authored marketing pages. They are published as written, with `styles.css`. `scripts/build.py` does not read or write them.
- `/tools/` the catalog. Every tool has its own space at `/tools/<slug>/`.
- `/tools/<slug>/tool.json` the tool's card (its PROJECT_HANDOFF): name, status, problem, solution, who it is for, price note, where to try it.
- `/tools/<slug>/index.html` the tool's page, generated from the card.
- `/tools/<slug>/app/` the tool itself, when it is a static web app (QuickQuote is). A tool that needs a server gets its own Netlify site on a subdomain, `<slug>.vibeninjaos.app`, and its card's `try_url` points there.
- `/list-your-tool.html` is the start of the marketplace: a Netlify form. It keeps the tool-page header and `styles-legacy.css`.

Tool status is one of three words, shown on every card: `live` (works today), `by-request` (works, done for you while it is finished), `workbench` (not ready). Prices appear only as notes on the card, marked planned until something is for sale.

## Adding or changing a tool

```
python scripts/build.py --new my-tool "My Tool"   # starts tools/my-tool/tool.json
# fill in the card
python scripts/build.py                           # writes the tool page, catalog, list-your-tool chrome, sitemap
python scripts/build.py --check                   # exit 1 if any generated page is out of date
```

The shared head links, header and footer for the tool pages and `list-your-tool.html` live in `scripts/build.py` and are written between the `<!-- site:head -->`, `<!-- site:header -->` and `<!-- site:footer -->` markers. Edit them there, not in those pages. Those pages link to `styles-legacy.css`. The marketing pages listed above are not part of that pass. Standard library Python only; Netlify runs no build step, the output is committed.

## Status

- Started 2026-11-05 from Shawn's prototype in Google Drive (`VIBENINJA_ENTERPRISE_OS_ROOT`).
- Netlify publishes `main` to vibeninjaos.app (connected 2026-11-10). The live page is still the first prototype until a pull request is merged.
- Tools hub built 2026-11-10 on branch `v/hub-v2`, on top of the five-page draft in `v/site-v1`.
- No email addresses on the site; contact goes through Netlify forms.

## Working on this repo

Work on a branch and open a pull request. Nothing goes to `main` directly, because `main` is the live site.
