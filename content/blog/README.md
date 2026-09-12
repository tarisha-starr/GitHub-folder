# Blog drafts

Long form posts for the Sexual Empowerment for Women blog. One markdown file per
post, with YAML front matter for the title, slug, meta description, category and
tags so it can be set up in Yoast without rewriting anything, plus a paste ready
HTML body for the WordPress editor.

Checked against `content/style_guide.md` and the voice rules in the
`website-build` skill: no dashes as punctuation, UK and NZ spelling,
contractions, no banned phrases.

## What's in here

| File | What it is |
| --- | --- |
| `david-deida-on-relationships.md` | Post: Why You Can Be Best Friends And Still Not Want Each Other |
| `basson-response-model.md` | Post: Why You Never Want Sex Until You're Already Having It |
| `infographics.md` | Prompts for four portrait social graphics, two per post |
| `preview.html` | Both posts as one designed reading page, with the diagrams drawn |
| `wordpress/*.html` | Paste ready bodies, one per post, for the WordPress editor |

These two are a natural pair. The Deida post ends on brakes and accelerators,
which is exactly where the Basson post starts, so each one links to the other at
the end. Those links use the slugs in the front matter, so they'll only resolve
once both are live.

## The diagrams

Four of them, two per post, already drawn in `preview.html`:

1. Deida's three stages, with freedom and charge marked present or absent on each
2. Polarity, what it is and what it isn't
3. Basson's circle against the straight line it replaced
4. Willingness against duty sex

`infographics.md` turns each one into a prompt for the portrait version that goes
on Instagram and Pinterest, in the same pipeline as
`content/chatgpt_infographic_prompts.md`, on the same locked brand: Cream
background, Near-Black headlines, Rust labels, Copper accents, Navy footer.

## Getting a post onto the blog

Each file in `wordpress/` is one WordPress Custom HTML block. Copy the whole
file, paste it into a new post, and put the title from the front matter in the
title field. The block carries its own scoped stylesheet, so the four diagrams
render without the theme knowing anything about them, and nothing leaks out to
the rest of the page.

Then fill in from the front matter: slug, meta description for Yoast, category,
tags. Add a featured image, and drop infographic 1 or 3 in as the in post image
if you want one above the fold.

Rebuild the two files after any edit to `preview.html`:

```bash
python3 automation/build_blog_html.py
```

Edit `preview.html`, not the generated files, or your changes get overwritten.

## Things for Tarisha to decide before publishing

**Click every outbound link once.** The books, the journal citations and the DOI
are solid. The YouTube links and the two blog articles in the reading lists were
found by search and look right, but nobody has watched or read them end to end,
and a dead link in a reading list is the thing readers notice first.

**Client stories are composite placeholders.** The couple with the colour coded
shared calendar in the Deida post is a made up illustration, not a client. Swap
it for one of your own, or cut it. Nothing in either post should read as a case
study you haven't approved.

**One book title is missing on purpose.** In the Basson post, Emily Nagoski's
2015 book is referred to without its name, because the title is on the banned
phrase list in the voice checker. If you're happy to use it in a reading list,
add it back in the two places she's mentioned.

**The DSM reference in the Basson post** says the diagnoses were merged in 2013
and that absent spontaneous desire isn't itself a problem. That's accurate, and
it's deliberately kept non clinical in tone. If you'd rather not cite a
diagnostic manual at all on a blog for women, that whole section can go without
breaking the piece.

**Deida is genuinely contested.** The post says so out loud, in its own section,
which is the only honest way to reference him for an audience of women over 40.
Worth a read before publishing in case you want that section stronger or softer.
