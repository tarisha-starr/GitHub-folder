#!/usr/bin/env python3
"""Check a built page against the brand voice rules and the build constraints.

    python3 check_voice.py site/index.html

Exits non-zero if anything fails, so it can gate a handoff. It reads the
visible copy only, so a CSS colour name or a JS variable never trips it, but it
does include <title> and meta descriptions because those are copy too and are
exactly where a stray dash survives review.
"""
import re
import sys

BANNED_WORDS = [
    # "real" as adjective or intensifier. UK spellings that merely start with
    # the same five letters (realise, reality, realm) are different words and
    # must not trip this, or every client testimonial fails.
    (r"\breal(?:ly|-\w+)?\b", "the word 'real' is banned in every form"),
    (r"\bcome as you are\b", "banned phrase"),
    (r"\bqueen energy\b", "coachy cliche"),
    (r"\bboss babe\b", "coachy cliche"),
    (r"\bI see you\b", "performative empathy"),
    (r"\bresearch shows\b", "therapist-speak"),
    (r"\bstudies suggest\b", "therapist-speak"),
    (r"\bfurthermore\b", "stiff transition"),
    (r"\bmoreover\b", "stiff transition"),
]

US_SPELLINGS = [
    "realize", "realized", "realizing", "color", "colors", "colored",
    "favorite", "apologize", "behavior", "organize", "organized",
    "recognize", "center", "centers", "theater", "traveling", "canceled",
]


def visible_text(html):
    """Strip scripts, styles and tags, but keep title and meta description."""
    title = " ".join(re.findall(r"<title>(.*?)</title>", html, re.S))
    metas = " ".join(re.findall(
        r'<meta[^>]+name="description"[^>]+content="([^"]*)"', html, re.I))
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", " ".join([title, metas, body]))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: check_voice.py <page.html>")
    path = sys.argv[1]
    html = open(path, encoding="utf-8").read()
    text = visible_text(html)
    fails, notes = [], []

    for m in re.finditer(r"[—–]", text):
        ctx = text[max(0, m.start() - 45):m.start() + 45].strip()
        fails.append("dash used as punctuation: ...%s..." % ctx)

    for pattern, why in BANNED_WORDS:
        for m in re.finditer(pattern, text, re.I):
            ctx = text[max(0, m.start() - 40):m.start() + 40].strip()
            fails.append("%s (%s): ...%s..." % (m.group(0), why, ctx))

    for word in US_SPELLINGS:
        for m in re.finditer(r"\b%s\b" % word, text, re.I):
            ctx = text[max(0, m.start() - 40):m.start() + 40].strip()
            fails.append("US spelling '%s': ...%s..." % (m.group(0), ctx))

    # build constraints
    # Only resources the browser actually loads count against the one-external
    # -resource rule. An <a href> to another site is an outbound link, not a
    # dependency, and flagging it would punish ordinary citations.
    loaded = set(re.findall(r'<(?:img|script|iframe|source|video|audio)[^>]+src="(https?://[^"]+)"', html))
    loaded |= set(re.findall(r'<link[^>]+href="(https?://[^"]+)"', html))
    loaded |= set(re.findall(r'url\((https?://[^)]+)\)', html))
    stray = [u for u in loaded
             if "fonts.googleapis.com" not in u and "fonts.gstatic.com" not in u]
    if stray:
        fails.append("external resources beyond Google Fonts: %s" % ", ".join(sorted(stray)))

    for tag in ["section", "div", "svg", "a", "ul", "li", "figure", "nav",
                "header", "footer", "main", "aside", "h1", "h2", "h3", "p"]:
        opened = len(re.findall(r"<%s[\s>]" % tag, html))
        closed = len(re.findall(r"</%s>" % tag, html))
        if opened != closed:
            fails.append("unbalanced <%s>: %d open, %d closed" % (tag, opened, closed))

    # things worth a look but not a failure
    if "prefers-reduced-motion" not in html:
        notes.append("no prefers-reduced-motion block")
    if "prefers-color-scheme" not in html and 'data-theme' not in html:
        notes.append("no dark theme handling")
    if re.search(r"animation[^;]*(filter|blur|turbulence)", html):
        notes.append("possible animated filter, check it is not on a hot path")
    for m in re.finditer(r"\b(\d{1,3}(?:,\d{3})*|\d+\.\d)\s*(?:\+|%|★|star)", text):
        notes.append("unverified-looking statistic: %s" % m.group(0))

    print("checked %s" % path)
    for n in notes:
        print("  note   %s" % n)
    if fails:
        for f in fails:
            print("  FAIL   %s" % f)
        print("\n%d failure(s)" % len(fails))
        sys.exit(1)
    print("  voice and build checks clean")


if __name__ == "__main__":
    main()
