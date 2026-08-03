#!/usr/bin/env python3
"""Screenshot and QA a self-contained HTML page using the Chromium already
installed in this environment.

    python3 shoot.py site/index.html              # screenshots + overflow check
    python3 shoot.py site/index.html --qa         # also click links, menu, focus
    python3 shoot.py site/index.html --full       # full-page shots, not viewport

Writes PNGs next to the page in ./shots/. Do not run "playwright install";
the browser is at /opt/pw-browsers and is passed explicitly below, because
the pip package's expected build number often differs from the installed one.
"""
import argparse
import glob
import os
import sys

VIEWPORTS = [("mobile", 390, 844), ("tablet", 820, 1180), ("desktop", 1440, 900)]


def find_chromium():
    env = os.environ.get("CHROMIUM_PATH")
    if env and os.path.exists(env):
        return env
    for pattern in (
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
    ):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--qa", action="store_true", help="exercise links, menu, focus")
    ap.add_argument("--full", action="store_true", help="full-page screenshots")
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()

    path = os.path.abspath(args.page)
    if not os.path.exists(path):
        sys.exit("no such page: " + path)
    outdir = args.outdir or os.path.join(os.path.dirname(path), "shots")
    os.makedirs(outdir, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright missing. run: pip install playwright")

    exe = find_chromium()
    if not exe:
        sys.exit("no chromium under /opt/pw-browsers; set CHROMIUM_PATH")

    problems = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe)
        for name, w, h in VIEWPORTS:
            page = browser.new_page(viewport={"width": w, "height": h})
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto("file://" + path)
            # let webfonts settle and one-shot intro animations finish
            page.wait_for_timeout(2200)

            shot = os.path.join(outdir, "%s.png" % name)
            page.screenshot(path=shot, full_page=args.full)
            print("wrote %s" % shot)

            sw = page.evaluate("document.documentElement.scrollWidth")
            cw = page.evaluate("document.documentElement.clientWidth")
            if sw > cw + 1:
                problems.append("%s: horizontal scroll, %spx wide in %spx viewport"
                                % (name, sw, cw))

            # text too small to read comfortably on a phone
            if name == "mobile":
                tiny = page.evaluate("""() => {
                  let n = 0;
                  document.querySelectorAll('p,li,a,span,div').forEach(el => {
                    if (!el.textContent.trim()) return;
                    const fs = parseFloat(getComputedStyle(el).fontSize);
                    if (fs && fs < 12) n++;
                  });
                  return n;
                }""")
                if tiny:
                    problems.append("mobile: %d elements with text under 12px" % tiny)

                # Only standalone controls need a 32px target. A link inside a
                # sentence is ~20px tall by definition and flagging it just
                # trains people to ignore the report.
                taps = page.evaluate("""() => {
                  let n = 0;
                  document.querySelectorAll('a,button,label,input').forEach(el => {
                    const r = el.getBoundingClientRect();
                    if (r.width === 0 && r.height === 0) return;
                    const d = getComputedStyle(el).display;
                    if (d === 'inline') return;              // inline text link
                    if (el.closest('p,li,figcaption,cite')) return;
                    if (r.height < 32 || r.width < 32) n++;
                  });
                  return n;
                }""")
                if taps:
                    problems.append("mobile: %d tap targets under 32px" % taps)

            for e in errors:
                problems.append("%s: JS error: %s" % (name, e))
            page.close()

        if args.qa:
            problems.extend(run_qa(browser, path))
        browser.close()

    print("\n--- report ---")
    if problems:
        for p_ in problems:
            print("  ISSUE  " + p_)
        sys.exit(1)
    print("  clean")


def run_qa(browser, path):
    """Click every in-page link, open the mobile menu, check focus visibility."""
    found = []
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto("file://" + path)
    page.wait_for_timeout(1200)

    # every in-page anchor should resolve to an element that exists
    targets = page.evaluate("""() => Array.from(document.querySelectorAll('a[href^="#"]'))
        .map(a => a.getAttribute('href')).filter(h => h && h.length > 1)""")
    for t in sorted(set(targets)):
        exists = page.evaluate("sel => !!document.querySelector(sel)", t)
        if not exists:
            found.append("dead in-page link: %s" % t)

    # placeholder hrefs are fine in a draft but should be reported
    placeholders = page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href="#"]')).length""")
    if placeholders:
        found.append("%d placeholder links still pointing at '#'" % placeholders)

    # mobile menu must actually open
    toggle = page.query_selector(".nav-toggle") or page.query_selector("[data-menu-toggle]")
    if toggle:
        before = page.evaluate(
            """() => { const n = document.querySelector('.nav');
                       return n ? getComputedStyle(n).display : null; }""")
        page.evaluate("""() => { const c = document.querySelector('.nav-toggle');
                                 if (c) { c.checked = true;
                                 c.dispatchEvent(new Event('change')); } }""")
        page.wait_for_timeout(250)
        after = page.evaluate(
            """() => { const n = document.querySelector('.nav');
                       return n ? getComputedStyle(n).display : null; }""")
        if before == after and before == "none":
            found.append("mobile menu does not open when toggled")

    # keyboard focus must be visible somewhere
    page.keyboard.press("Tab")
    page.wait_for_timeout(120)
    outline = page.evaluate("""() => {
        const el = document.activeElement;
        if (!el || el === document.body) return null;
        const s = getComputedStyle(el);
        return s.outlineStyle + '|' + s.outlineWidth + '|' + s.boxShadow;
    }""")
    if outline and outline.startswith("none|") and "rgb" not in outline:
        found.append("first focusable element has no visible focus state")

    # the page must survive with JavaScript switched off
    page.close()
    nojs = browser.new_context(java_script_enabled=False,
                               viewport={"width": 390, "height": 844})
    p2 = nojs.new_page()
    p2.goto("file://" + path)
    p2.wait_for_timeout(600)
    hidden = p2.evaluate("""() => {
        let n = 0;
        document.querySelectorAll('.reveal, [data-reveal]').forEach(el => {
            if (parseFloat(getComputedStyle(el).opacity) < 0.5) n++;
        });
        return n;
    }""")
    if hidden:
        found.append("%d sections stay invisible with JS disabled" % hidden)
    p2.close()
    nojs.close()
    return found


if __name__ == "__main__":
    main()
