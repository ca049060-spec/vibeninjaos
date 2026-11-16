# VibeNinjaOS

Website for vibeninjaos.app: the home for the tools Shawn builds with AI, and later a shelf for tools built by other people.

## How the site is laid out

- `/` home: one promise, price the job before you leave the driveway. The tool shelf below lists every tool with its status. How the tools get built lives on `/how-it-works.html`.
- `/tools/` the catalog. Every tool has its own space at `/tools/<slug>/`.
- `/tools/<slug>/tool.json` the tool's card (its PROJECT_HANDOFF): name, status, problem, solution, who it is for, price note, where to try it.
- `/tools/<slug>/index.html` the tool's page, generated from the card.
- `/tools/<slug>/app/` the tool itself, when it is a static web app (QuickQuote is). A tool that needs a server gets its own Netlify site on a subdomain, `<slug>.vibeninjaos.app`, and its card's `try_url` points there.
- `/how-it-works.html`, `/contact.html`, `/list-your-tool.html` (the start of the marketplace: a Netlify form), `/thanks.html`.

Tool status is one of three, shown on every card: `live` (chip: Live), `by-request` (chip: By request), `workbench` (chip: Being built). Prices appear only as notes on the card, marked planned until something is for sale.

## Adding or changing a tool

```
python scripts/build.py --new my-tool "My Tool"   # starts tools/my-tool/tool.json
# fill in the card
python scripts/build.py                           # writes the tool page, catalog, home blocks, nav, sitemap
python scripts/build.py --check                   # exit 1 if any page is out of date
```

The shared head links, header and footer live in `scripts/build.py` and are written into every page between the `<!-- site:head -->`, `<!-- site:header -->` and `<!-- site:footer -->` markers. Edit them there, not in the pages. The home page tool shelf is generated there too, between the `<!-- site:shelf -->` markers, and it includes every tool. Standard library Python only; Netlify runs no build step, the output is committed.

## Status

- Started 2026-11-05 from Shawn's prototype in Google Drive (`VIBENINJA_ENTERPRISE_OS_ROOT`).
- Netlify publishes `main` to vibeninjaos.app (connected 2026-11-10). The live page is still the first prototype until a pull request is merged.
- Tools hub built 2026-11-10 on branch `v/hub-v2`, on top of the five-page draft in `v/site-v1`.
- No email addresses on the site; contact goes through Netlify forms.

## Working on this repo

Work on a branch and open a pull request. Nothing goes to `main` directly, because `main` is the live site.
