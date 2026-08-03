#!/usr/bin/env python3
"""Make a preview copy of a page with its Google Fonts inlined as data URIs.

    python3 embed_fonts.py site/index.html preview.html

Why this exists: the artifact host enforces a CSP that blocks font CDNs, so a
page whose only external resource is a Google Fonts link renders in Times in
the preview. The user then reviews a design nobody built. This leaves the
deliverable untouched and produces a separate preview file that carries its
own fonts.

It reads the Google Fonts <link> already in the page, downloads the latin
subsets, and registers them under "<Family> Fallback" aliases. Those aliases
need to already be present in the font stacks, which is the convention the
website-build skill uses:

    --f-display:"Marcellus",'Marcellus Fallback',Georgia,serif;

That way the CDN font wins when it loads, and the inlined copy takes over when
it is blocked, with no duplicate-family ambiguity.
"""
import base64
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=60).read()


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: embed_fonts.py <page.html> <preview.html>")
    src, dest = sys.argv[1], sys.argv[2]
    html = open(src, encoding="utf-8").read()

    links = re.findall(r'<link[^>]+href="(https://fonts\.googleapis\.com/css2[^"]+)"', html)
    if not links:
        sys.exit("no Google Fonts css2 link found in " + src)

    faces = []
    for link in links:
        css = fetch(link.replace("&amp;", "&")).decode("utf-8")
        blocks = re.findall(r"/\*\s*([a-z0-9-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S)
        if not blocks:  # no subset comments, take every face
            blocks = [("latin", b) for b in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)]
        for subset, body in blocks:
            if subset != "latin":
                continue
            fam = re.search(r"font-family:\s*'([^']+)'", body)
            sty = re.search(r"font-style:\s*(\w+)", body)
            wgt = re.search(r"font-weight:\s*([\d ]+)", body)
            url = re.search(r"url\((https://[^)]+)\)", body)
            if not (fam and url):
                continue
            data = fetch(url.group(1))
            faces.append(
                "@font-face{font-family:'%s Fallback';font-style:%s;font-weight:%s;"
                "font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}"
                % (fam.group(1),
                   sty.group(1) if sty else "normal",
                   (wgt.group(1).strip() if wgt else "400"),
                   base64.b64encode(data).decode())
            )
            print("embedded %s %s %s, %.1f KB"
                  % (fam.group(1), sty.group(1) if sty else "normal",
                     wgt.group(1).strip() if wgt else "400", len(data) / 1024))

    if not faces:
        sys.exit("no latin subsets found; check the font URL")

    if "<style>" not in html:
        sys.exit("no <style> block to inject into")
    out = html.replace("<style>", "<style>\n" + "".join(faces) + "\n", 1)
    open(dest, "w", encoding="utf-8").write(out)
    print("\nwrote %s, %.1f KB (source was %.1f KB)"
          % (dest, len(out) / 1024, len(html) / 1024))
    print("publish this file as the artifact; commit the source unchanged")


if __name__ == "__main__":
    main()
