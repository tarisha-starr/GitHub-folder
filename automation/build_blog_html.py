"""Turn content/blog/preview.html into paste ready WordPress bodies.

    python3 automation/build_blog_html.py

Reads the two articles out of the reading page and writes one self contained
HTML file per post into content/blog/wordpress/. Each file goes straight into a
WordPress Custom HTML block: it carries its own scoped stylesheet, so the
diagrams survive without the theme knowing anything about them.

What changes on the way through:
  - the slug line and the <h2> title are dropped, because WordPress holds the
    title and the post meta itself
  - <h3> section headings become <h2>, since the post title is the h1
  - every rule is scoped under .serw-post and uses the locked brand colours,
    light only, because the blog is a light theme
"""

from __future__ import annotations

import os
import re

SRC = "content/blog/preview.html"
OUTDIR = "content/blog/wordpress"

POSTS = {
    "deida": "best-friends-still-dont-want-each-other.html",
    "basson": "basson-response-model-responsive-desire.html",
}

# Locked SERW palette: Cream, Near-Black, Rust, Copper, Navy.
STYLE = """<style>
.serw-post{--ink:#15110D;--soft:#5C544A;--faint:#8A8071;--rule:#E2D8C4;
  --cream:#F5EFE3;--copper:#C75D3D;--rust:#9E4A2A;--navy:#1F2A44;
  color:var(--ink);font-family:"Lora",Georgia,serif;line-height:1.75}
.serw-post h2{font-family:"Marcellus","Times New Roman",serif;font-weight:400;
  font-size:1.5rem;line-height:1.3;margin:2.75rem 0 1rem;color:var(--ink)}
.serw-post p{margin:0 0 1.25rem}
.serw-post .lede{font-size:1.15rem;line-height:1.65}
.serw-post strong{font-weight:600}
.serw-post a{color:var(--rust)}
.serw-post .pull{font-family:"Marcellus","Times New Roman",serif;
  font-size:1.5rem;line-height:1.3;color:var(--rust);
  border-left:2px solid var(--copper);padding:0.15rem 0 0.15rem 1.5rem;
  margin:2.25rem 0}
.serw-post ol.steps{counter-reset:step;list-style:none;margin:1.5rem 0 0;
  padding:0;display:grid;gap:1.25rem}
.serw-post ol.steps li{counter-increment:step;padding-left:2.25rem;
  position:relative}
.serw-post ol.steps li::before{content:counter(step);position:absolute;left:0;
  top:0.1rem;font-family:"Marcellus",serif;font-size:0.95rem;color:var(--rust)}
.serw-post figure{margin:2.75rem 0;background:var(--cream);
  border:1px solid var(--rule);padding:1.5rem 1.25rem 1.35rem}
.serw-post .eyebrow{font-size:0.76rem;letter-spacing:0.18em;
  text-transform:uppercase;font-weight:500;color:var(--rust);margin:0 0 0.5rem}
.serw-post .fig-title{font-family:"Marcellus",serif;font-size:1.2rem;
  line-height:1.3;margin:0 0 1.25rem}
.serw-post figcaption{font-size:0.92rem;line-height:1.6;color:var(--soft);
  margin-top:1.25rem;border-top:1px solid var(--rule);padding-top:0.9rem}
.serw-post .stages{display:grid;gap:1px;background:var(--rule);
  border-top:1px solid var(--rule)}
.serw-post .stage{background:var(--cream);display:grid;
  grid-template-columns:1.6rem 1fr auto;gap:0.3rem 1rem;padding:1.1rem 0.1rem}
.serw-post .stage-num{font-family:"Marcellus",serif;font-size:1.15rem;
  color:var(--rust);line-height:1.4}
.serw-post .stage-name{font-family:"Marcellus",serif;font-size:1.05rem;
  line-height:1.35}
.serw-post .stage-note{grid-column:2;font-size:0.95rem;line-height:1.55;
  color:var(--soft)}
.serw-post .marks{grid-row:1 / span 2;grid-column:3;display:flex;gap:1.1rem;
  align-self:center}
.serw-post .mark{display:grid;justify-items:center;gap:0.4rem;font-size:0.75rem;
  letter-spacing:0.1em;text-transform:uppercase;color:var(--faint)}
.serw-post .dot{width:0.7rem;height:0.7rem;border-radius:50%;
  border:1px solid var(--copper)}
.serw-post .dot.on{background:var(--copper)}
.serw-post .compare{display:grid;grid-template-columns:1fr 1fr;gap:1px;
  background:var(--rule);border-top:1px solid var(--rule)}
.serw-post .compare>div{background:var(--cream);padding:1.2rem 0.9rem 1.3rem 0}
.serw-post .compare>div+div{padding-left:1.1rem;padding-right:0}
.serw-post .compare h5{font-family:"Marcellus",serif;font-weight:400;
  font-size:1.05rem;margin:0 0 0.85rem}
.serw-post .compare .no{color:var(--faint)}
.serw-post .compare .yes{color:var(--rust)}
.serw-post .compare ul{list-style:none;margin:0;padding:0;display:grid;
  gap:0.6rem}
.serw-post .compare li{font-size:0.95rem;line-height:1.5;color:var(--soft)}
.serw-post .line-chips{display:flex;flex-wrap:wrap;align-items:center;
  gap:0.5rem 0.65rem;margin:0 0 2rem}
.serw-post .chip{font-size:0.85rem;padding:0.35rem 0.8rem;
  border:1px solid var(--rule);background:#FBF7EE;color:var(--soft)}
.serw-post .arrow{color:var(--faint);font-size:0.9rem}
.serw-post .circle-wrap{display:grid;grid-template-columns:13rem 1fr;
  gap:1.5rem 1.75rem;align-items:center}
.serw-post .ring{width:100%;height:auto;max-width:13rem;display:block}
.serw-post .ring .track{fill:none;stroke:var(--rule);stroke-width:2}
.serw-post .ring .tip{fill:var(--faint)}
.serw-post .ring .node{fill:#FBF7EE;stroke:var(--rule);stroke-width:1.5}
.serw-post .ring .node-key{fill:var(--copper);stroke:var(--copper)}
.serw-post .ring .num{fill:var(--soft);font-family:"Lora",Georgia,serif;
  font-size:14px;font-weight:500}
.serw-post .ring .num-key{fill:var(--cream)}
.serw-post .cycle{list-style:none;margin:0;padding:0;display:grid;gap:0.55rem;
  counter-reset:ring}
.serw-post .cycle li{counter-increment:ring;display:grid;
  grid-template-columns:1.35rem 1fr;gap:0.6rem;font-size:0.95rem;
  line-height:1.5}
.serw-post .cycle li::before{content:counter(ring);
  font-family:"Marcellus",serif;color:var(--faint)}
.serw-post .cycle li.key,.serw-post .cycle li.key::before{color:var(--rust)}
.serw-post .refs{background:var(--cream);border-left:2px solid var(--rust);
  padding:1.5rem 1.5rem 1.6rem;margin:2.75rem 0 0}
.serw-post .refs h4{font-size:0.76rem;letter-spacing:0.16em;
  text-transform:uppercase;color:var(--rust);font-weight:500;margin:0 0 1rem}
.serw-post .refs h4+h4{margin-top:1.5rem}
.serw-post .refs ul{list-style:none;margin:0;padding:0;display:grid;gap:0.9rem}
.serw-post .refs li{font-size:0.96rem;line-height:1.6;color:var(--soft)}
.serw-post .refs .work{color:var(--ink);font-style:italic}
.serw-post .signoff{font-family:"Marcellus",serif;font-size:1.1rem;
  color:var(--soft);margin-top:2.25rem}
.serw-post .sr{position:absolute;width:1px;height:1px;overflow:hidden;
  clip-path:inset(50%)}
@media (max-width:34rem){
  .serw-post .stage{grid-template-columns:1.6rem 1fr}
  .serw-post .marks{grid-row:auto;grid-column:2;justify-content:start;
    margin-top:0.6rem}
  .serw-post .compare{grid-template-columns:1fr}
  .serw-post .compare>div,.serw-post .compare>div+div{padding-left:0;
    padding-right:0}
  .serw-post .circle-wrap{grid-template-columns:1fr;justify-items:center}
  .serw-post .circle-wrap ol{justify-self:start}
}
</style>
"""


def extract(html: str, post_id: str) -> str:
    m = re.search(
        r'<article id="%s"[^>]*>(.*?)</article>' % post_id, html, re.S)
    if not m:
        raise SystemExit("no article with id " + post_id)
    body = m.group(1)
    body = re.sub(r'\s*<p class="slug">.*?</p>\n', "", body, flags=re.S)
    body = re.sub(r"\s*<h2>.*?</h2>\n", "", body, count=1, flags=re.S)
    body = body.replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    # the inline margin-top on stacked reference headings is handled in the
    # stylesheet instead, so strip it
    body = body.replace(' style="margin-top: 1.5rem;"', "")
    return body.strip()


def main() -> None:
    html = open(SRC, encoding="utf-8").read()
    os.makedirs(OUTDIR, exist_ok=True)
    for post_id, filename in POSTS.items():
        body = extract(html, post_id)
        out = '%s<div class="serw-post">\n%s\n</div>\n' % (STYLE, body)
        path = os.path.join(OUTDIR, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
        print("wrote %s (%d bytes)" % (path, len(out)))


if __name__ == "__main__":
    main()
