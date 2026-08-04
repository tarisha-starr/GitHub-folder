"""Pull the published copy off theloveadventure.com into content/live/.

Read only. Uses the public WordPress REST API, so it needs no credentials and
cannot change anything on the live site.

For each published page it writes:
  content/live/<path>.md        the visible copy, headings and links kept
  content/live/raw/<path>.html  the rendered HTML exactly as WordPress serves it
  content/live/index.md         a table of every page
  content/live/_shared-chrome.md  the header and footer, kept once

Most pages were pasted into Kadence as whole-page HTML blocks, so each one
carries its own <header class="nav"> and <footer class="footer">. Those are
stripped out of the per-page files and stored once, otherwise the same nav and
footer buries the copy on all twenty four pages.

Usage:
    python3 automation/pull_live_pages.py
"""

import html
import json
import os
import re
import subprocess
import sys

BASE = "https://theloveadventure.com/wp-json/wp/v2"
SITE = "https://theloveadventure.com"
OUT = "content/live"
RAW = os.path.join(OUT, "raw")

BLOCK = ("p", "div", "section", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5",
         "h6", "blockquote", "figcaption", "td", "article", "header", "footer")


def get(url):
    r = subprocess.run(["curl", "-sS", "-m", "40", url],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"curl failed for {url}: {r.stderr[:200]}")
    return json.loads(r.stdout)


def path_name(link):
    """Name files by full URL path, so /together/therapy and /for-her/therapy
    do not collide on the shared 'therapy' slug."""
    path = re.sub(r"^https?://[^/]+/", "", link).strip("/")
    return re.sub(r"[^a-z0-9]+", "-", path.lower()).strip("-") or "home"


def cut_element(markup, tag, attr):
    """Remove one <tag ...attr...>...</tag> element, matching nesting.

    Returns (remainder, removed) with removed as '' when nothing matched.
    """
    m = re.search(rf"<{tag}[^>]*{attr}[^>]*>", markup, re.I)
    if not m:
        return markup, ""
    depth, pos = 1, m.end()
    token = re.compile(rf"</?{tag}\b", re.I)
    while depth:
        t = token.search(markup, pos)
        if not t:
            return markup, ""
        depth += -1 if markup[t.start():t.start() + 2 + len(tag)].startswith(
            f"</{tag}") else 1
        pos = t.end()
    end = markup.find(">", pos)
    end = len(markup) if end == -1 else end + 1
    return markup[:m.start()] + markup[end:], markup[m.start():end]


def to_text(markup):
    """Visible copy only. Keeps heading levels and link targets."""
    s = re.sub(r"(?is)<(style|script|svg|noscript)[^>]*>.*?</\1>", " ", markup)
    s = re.sub(r"(?is)<!--.*?-->", " ", s)

    for n in range(1, 7):
        s = re.sub(rf"(?is)<h{n}[^>]*>(.*?)</h{n}>", rf"\n\n{'#' * n} \1\n\n", s)
    s = re.sub(r"(?is)<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>",
               lambda m: f"[{m.group(2).strip()}]({m.group(1)})", s)
    s = re.sub(r"(?is)<li[^>]*>", "\n- ", s)
    s = re.sub(rf"(?is)</?({'|'.join(BLOCK)})[^>]*/?>", "\n", s)
    s = re.sub(r"(?is)<[^>]+>", "", s)

    s = html.unescape(s).replace(" ", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"\n- (?=\n)", "\n", s)
    return s.strip()


def main():
    pages = get(f"{BASE}/pages?per_page=100&_fields=id,slug,link,title,content,"
                "parent,menu_order,modified,status")
    pages.sort(key=lambda p: p["link"])
    os.makedirs(RAW, exist_ok=True)

    index, chrome = [], {}
    for p in pages:
        name = path_name(p["link"])
        title = html.unescape(re.sub(r"<[^>]+>", "", p["title"]["rendered"])).strip()
        rendered = p["content"]["rendered"]

        with open(os.path.join(RAW, f"{name}.html"), "w") as f:
            f.write(rendered)

        body, head_el = cut_element(rendered, "header", 'class="nav"')
        body, foot_el = cut_element(body, "footer", 'class="footer"')
        if head_el and "header" not in chrome:
            chrome["header"] = to_text(head_el)
        if foot_el and "footer" not in chrome:
            chrome["footer"] = to_text(foot_el)

        copy = to_text(body)
        has_chrome = bool(head_el or foot_el)

        with open(os.path.join(OUT, f"{name}.md"), "w") as f:
            f.write(f"# {title}\n\n")
            f.write(f"- Page ID: {p['id']}\n")
            f.write(f"- URL: {p['link']}\n")
            f.write(f"- Slug: {p['slug']}\n")
            f.write(f"- Parent ID: {p['parent']}\n")
            f.write(f"- Status: {p['status']}\n")
            f.write(f"- Last modified on the live site: {p['modified']}\n")
            f.write(f"- Raw HTML: raw/{name}.html\n")
            if has_chrome:
                f.write("- Shared header and footer stripped, see "
                        "[_shared-chrome.md](_shared-chrome.md)\n")
            f.write("\n---\n\n" + copy + "\n")

        index.append((p["id"], p["link"], title, name, len(copy), has_chrome))
        print(f"{p['id']:>4}  {len(copy):>6} chars  {name}")

    with open(os.path.join(OUT, "_shared-chrome.md"), "w") as f:
        f.write("# Shared header and footer\n\nRepeated on most pages, so it is "
                "stripped from the individual page files and kept here once.\n")
        for k in ("header", "footer"):
            f.write(f"\n## {k.title()}\n\n{chrome.get(k, '(not found)')}\n")

    with open(os.path.join(OUT, "index.md"), "w") as f:
        f.write("# Live site copy, pulled from WordPress\n\n"
                "Every published page on theloveadventure.com, read from the "
                "public REST API on the date of the last pull. This is what is "
                "actually on the site, so an edit starts from the published "
                "words rather than from a reconstruction.\n\n"
                "Read only. Nothing here is wired back to WordPress, and "
                "editing these files changes nothing on the live site. "
                "Re-run with `python3 automation/pull_live_pages.py`.\n\n"
                "| ID | Page | File | Copy |\n|---:|---|---|---:|\n")
        for pid, link, title, name, n, _ in index:
            path = link.replace(SITE, "") or "/"
            f.write(f"| {pid} | {title}<br>`{path}` | [{name}.md]({name}.md) "
                    f"| {n:,} |\n")
        f.write(f"\n{len(index)} published pages.\n")

    print(f"\nwrote {len(index)} pages to {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
