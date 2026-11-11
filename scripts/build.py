"""Build the VibeNinjaOS tool pages from the tool cards.

Each tool lives in its own folder, tools/<slug>/, with one card file, tool.json.
This script reads every card and writes:

  tools/<slug>/index.html   the tool's own page
  tools/index.html          the catalog of all tools
  index.html                the featured and workbench blocks on the home page
  every page                the shared banner, header and footer
  sitemap.xml               every public page

Run from the repository root:

  python scripts/build.py                     rebuild everything
  python scripts/build.py --new my-tool "My Tool"   start a new tool card
  python scripts/build.py --check             exit 1 if any page is out of date

Standard library only. No build step runs on Netlify: the output is committed.
Written 2026-11-10 by V (Claude Opus 5.5) for Shawn.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
SITE_URL = "https://vibeninjaos.app"

STATUS = {
    "live": ("Live", "Try it now. It works today."),
    "by-request": ("By request", "Works today. Done for you by request while it is finished."),
    "workbench": ("On the workbench", "Being designed or built. Not ready yet."),
}
REQUIRED = ["name", "tagline", "slug", "status", "category", "audience", "before", "after",
            "try_url", "try_label", "price_note"]

NAV = [
    ("/", "Home"),
    ("/tools/", "Tools"),
    ("/how-it-works.html", "How it works"),
    ("/list-your-tool.html", "List your tool"),
    ("/contact.html", "Contact"),
]

BANNER = ('<div class="construction-banner" role="status">'
          '<strong>Early preview.</strong> Some tools are live and some are still being built. '
          'Each tool says which.</div>')

FOOTER = ('<footer class="site-footer"><div class="container">'
          '<p>VibeNinjaOS (vibeninjaos.app): working tools, built with AI. '
          '<a href="/tools/">All tools</a> · <a href="/list-your-tool.html">List your tool</a> · '
          '<a href="/contact.html">Contact</a></p></div></footer>')

E = html.escape


def header(current: str) -> str:
    items = []
    for href, label in NAV:
        here = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{href}"{here}>{label}</a></li>')
    return (f"{BANNER}\n  <header class=\"site-header\"><div class=\"container nav-row\">"
            f"<a href=\"/\" class=\"brand\">🥷 VibeNinjaOS</a>"
            f"<nav aria-label=\"Main navigation\"><ul class=\"nav-list\">{''.join(items)}</ul></nav>"
            f"</div></header>")


def load_tools() -> list[dict]:
    tools = []
    for card in sorted(TOOLS.glob("*/tool.json")):
        data = json.loads(card.read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED if not str(data.get(k, "")).strip()]
        if missing:
            sys.exit(f"{card}: missing {', '.join(missing)}")
        if data["slug"] != card.parent.name:
            sys.exit(f"{card}: slug '{data['slug']}' does not match its folder '{card.parent.name}'")
        if data["status"] not in STATUS:
            sys.exit(f"{card}: status must be one of {', '.join(STATUS)}")
        tools.append(data)
    tools.sort(key=lambda t: (t.get("order", 99), t["name"]))
    return tools


def badge(t: dict) -> str:
    label = STATUS[t["status"]][0]
    return f'<span class="status status-{t["status"]}">{label}</span>'


def card_html(t: dict, level: str = "h3") -> str:
    url = f"/tools/{t['slug']}/"
    return (f'<article class="card tool-card">{badge(t)}'
            f'<{level}><a href="{url}">{E(t["name"])}</a></{level}>'
            f'<p>{E(t["tagline"])}</p>'
            f'<p class="tool-meta">{E(t["category"])}</p>'
            f'<a href="{url}" class="btn btn-secondary">Open</a></article>')


def workbench_list(tools: list[dict]) -> str:
    rows = "".join(
        f'<li><a href="/tools/{t["slug"]}/">{E(t["name"])}</a>: {E(t["tagline"])}</li>' for t in tools)
    return f'<ul class="workbench-list">{rows}</ul>'


def page(title: str, description: str, path: str, current: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{E(title)}</title>
  <meta name="description" content="{E(description)}">
  <link rel="canonical" href="{SITE_URL}{path}">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <!-- site:header -->{header(current)}<!-- /site:header -->

  <main class="container">
{body}
  </main>

  <!-- site:footer -->{FOOTER}<!-- /site:footer -->
</body>
</html>
"""


def tool_page(t: dict) -> str:
    rows = [("Who it's for", t["audience"]), ("Price", t["price_note"])]
    if t.get("privacy_note"):
        rows.append(("Your data", t["privacy_note"]))
    if t.get("built_with"):
        rows.append(("How it's built", t["built_with"]))
    facts = "".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in rows)
    origin = f'<p class="note">{E(t["origin"])}</p>' if t.get("origin") else ""
    primary = "btn-primary" if t["status"] != "workbench" else "btn-secondary"
    body = f"""    <section class="page-intro tool-intro">
      <p class="eyebrow"><a href="/tools/">Tools</a> / {E(t["category"])}</p>
      {badge(t)}
      <h1>{E(t["name"])}</h1>
      <p class="lead">{E(t["tagline"])}</p>
      <p class="status-help">{STATUS[t["status"]][1]}</p>
      <div class="cta-group"><a href="{E(t["try_url"])}" class="btn {primary}">{E(t["try_label"])}</a></div>
    </section>

    <section class="card-section">
      <div class="grid-2">
        <div class="card card-before"><h2>Before</h2><p>{E(t["before"])}</p></div>
        <div class="card card-after"><h2>After</h2><p>{E(t["after"])}</p></div>
      </div>
    </section>

    <section class="card-section">
      <dl class="tool-facts">{facts}</dl>
      {origin}
    </section>

    <section class="cta-banner">
      <h2>Need a tool like this for your business?</h2>
      <a href="/contact.html" class="btn btn-primary">Ask about it</a>
    </section>"""
    return page(f"{t['name']} | VibeNinjaOS", t["tagline"], f"/tools/{t['slug']}/", "/tools/", body)


def catalog(tools: list[dict]) -> str:
    ready = [t for t in tools if t["status"] != "workbench"]
    bench = [t for t in tools if t["status"] == "workbench"]
    body = f"""    <section class="page-intro">
      <h1>Tools</h1>
      <p class="lead">Small tools that do one job well. Each one says plainly whether it works today.</p>
    </section>

    <section class="card-section">
      <h2>Ready now</h2>
      <div class="tool-grid">{''.join(card_html(t) for t in ready)}</div>
    </section>

    <section class="card-section">
      <h2>On the workbench</h2>
      <p class="muted">Being designed or built. Open one to see the problem it solves, or ask to hear when it is ready.</p>
      {workbench_list(bench)}
    </section>

    <section class="cta-banner">
      <h2>Built a tool with AI?</h2>
      <p>We are starting a shelf for tools made by other builders.</p>
      <a href="/list-your-tool.html" class="btn btn-primary">List your tool</a>
    </section>"""
    return page("Tools | VibeNinjaOS", "Working tools for small businesses, built with AI. Try the live ones free.",
                "/tools/", "/tools/", body)


ROOT_PAGES = {
    "index.html": "/",
    "how-it-works.html": "/how-it-works.html",
    "list-your-tool.html": "/list-your-tool.html",
    "contact.html": "/contact.html",
    "thanks.html": "/contact.html",
}


def replace_block(text: str, name: str, new: str) -> str:
    pattern = re.compile(rf"<!-- site:{name} -->.*?<!-- /site:{name} -->", re.S)
    if not pattern.search(text):
        sys.exit(f"missing <!-- site:{name} --> markers")
    return pattern.sub(lambda _: f"<!-- site:{name} -->{new}<!-- /site:{name} -->", text)


def build() -> dict[Path, str]:
    tools = load_tools()
    out: dict[Path, str] = {}
    for t in tools:
        out[TOOLS / t["slug"] / "index.html"] = tool_page(t)
    out[TOOLS / "index.html"] = catalog(tools)

    for name, current in ROOT_PAGES.items():
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        text = replace_block(text, "header", header(current))
        text = replace_block(text, "footer", FOOTER)
        if name == "index.html":
            ready = [t for t in tools if t["status"] != "workbench"]
            bench = [t for t in tools if t["status"] == "workbench"]
            text = replace_block(text, "featured", f'<div class="tool-grid">{"".join(card_html(t) for t in ready)}</div>')
            text = replace_block(text, "workbench", workbench_list(bench))
        out[path] = text

    urls = ["/", "/tools/", "/how-it-works.html", "/list-your-tool.html", "/contact.html"]
    urls += [f"/tools/{t['slug']}/" for t in tools]
    out[ROOT / "sitemap.xml"] = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                 + "".join(f"  <url><loc>{SITE_URL}{u}</loc></url>\n" for u in urls)
                                 + "</urlset>\n")
    return out


def new_tool(slug: str, name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit("slug must be lowercase words joined by dashes, e.g. my-tool")
    folder = TOOLS / slug
    if (folder / "tool.json").exists():
        sys.exit(f"{folder / 'tool.json'} already exists")
    folder.mkdir(parents=True, exist_ok=True)
    card = {"name": name, "tagline": "", "slug": slug, "order": 50, "status": "workbench",
            "category": "", "audience": "", "before": "", "after": "",
            "try_url": "/contact.html", "try_label": "Tell me when it's ready",
            "price_note": "Price set at launch.", "privacy_note": "", "origin": "",
            "built_with": "", "repo": "", "updated": ""}
    (folder / "tool.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    print(f"Started {folder / 'tool.json'}. Fill in the empty fields, then run: python scripts/build.py")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", nargs=2, metavar=("SLUG", "NAME"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.new:
        new_tool(*args.new)
        return
    out = build()
    stale = [p for p, text in out.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if args.check:
        for p in stale:
            print(f"out of date: {p.relative_to(ROOT)}")
        sys.exit(1 if stale else 0)
    for p in stale:
        p.write_text(text if (text := out[p]) else "", encoding="utf-8", newline="\n")
        print(f"wrote {p.relative_to(ROOT)}")
    print(f"{len(out)} pages checked, {len(stale)} written")


if __name__ == "__main__":
    main()
