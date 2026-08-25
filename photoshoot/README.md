# Piha shoot, 26 August

Shot list for the post-haircut photos: 40 solo frames (S1 to S40) and 40 with
Mark (D1 to D40), shot at Piha.

Two sessions, because the first window was only two hours.

**Session one, the morning.** Blocks 1 to 8, S1 to S40 and D1 to D40.

- `piha-shot-list.html` — the working call sheet. Tap a shot to tick it off,
  filter by solo or together, state saved in the browser. Published at
  https://claude.ai/code/artifact/7912e724-1746-4d25-b25c-a8ec70c7bffe
- `Piha-shot-list.pdf` — print and field version, 14 pages, one block per page
  with tick boxes.

**Session two, the long afternoon.** Blocks 9 to 14, thirty new frames from low
water to full dark, S41 to S55 and D41 to D55, plus a runsheet that folds in
every frame session one left outstanding.

- `piha-afternoon-shot-list.html` — published at
  https://claude.ai/code/artifact/a3571c31-2983-4236-bf19-45b99b720a8a
- `Piha-afternoon-shot-list.pdf` — 11 pages.

## The direction

Pine Deep is the brand anchor and cream is meant to act as relief, not the
other way round. Piha supplies that anchor in the landscape for free: iron
sand, wet rock, water under cloud. So the shoot does not build the mood, it
puts the warm thing in a dark frame. Cream, camel, rust and terracotta against
black sand, with terracotta staying an accent rather than a wash.

Follows the photography direction in Notion under **Assets & Ops → Website
Build → 1. Brand Guidelines**: outdoors, evening light, no posed studio, no
white backgrounds, and no stock-style couples photography.

## Frames mapped to pages

The call sheet ends with an index tying every frame to a slot: the
theloveadventure.com homepage and Together pages, the sexual confidence mini
course, the workshop, the Desire Blueprint quiz opt in, podcast art and
thumbnails.

## What the first trip could not cover

The 26 August window was 10am to 12pm, so everything built on low sun is still
outstanding: S33 at its best, S35 to S39, S40, D31, D35 to D40. That includes
D37 and S39, which are the two strongest frames on the list. They need about
forty five minutes at Piha from 5.10pm on a clear evening.

## Regenerating the PDF

```bash
pip install playwright pypdfium2 pillow
python3 photoshoot/topdf.py            # session one
python3 photoshoot/topdf-afternoon.py  # session two
```

Both scripts drive the Chromium already installed in the environment and print
the HTML through its own print stylesheet, so the PDF and the web version never
drift apart. Google Fonts has to be reachable or the display face falls back to
Times; the scripts check and print `fonts loaded: True` before writing.
