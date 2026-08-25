# Piha shoot

Shot list for the post-haircut photos. Two hours, split into two clean halves:

- **Hour one, just Tarisha.** 40 shots, S1 to S40, four stations.
- **Hour two, Tarisha and Mark.** 40 shots, D1 to D40, four stations.

Ten shots per station, all within a few minutes of the main Piha carpark, so
forty frames in sixty minutes is achievable without running.

## Files

- `piha-two-hours.html` — the working call sheet. Tap a shot to tick it off,
  filter to one hour at a time, state saved in the browser. Published at
  https://claude.ai/code/artifact/7912e724-1746-4d25-b25c-a8ec70c7bffe
- `Piha-two-hours.pdf` — print and field version, 11 pages, with tick boxes.

## The direction

Pine Deep is the brand anchor and cream is meant to act as relief, not the
other way round. Piha supplies that anchor in the landscape for free: iron
sand, wet rock, water under cloud. So the shoot does not build the mood, it
puts the warm thing in a dark frame.

Follows the photography direction in Notion under **Assets & Ops → Website
Build → 1. Brand Guidelines**: outdoors, no posed studio, no white
backgrounds, and no stock-style couples photography. The couple frames that
carry the site are the quiet ones, because the closeness lives in the
shoulders rather than the smile.

## Wardrobe, and why each outfit sits where it does

| Outfit | Station | Why |
|---|---|---|
| Flowing dress | Hour 1, dunes and waterline | Movement is the one thing it does better than the others, and Piha supplies wind for free |
| Cocktail dress | Hour 1, black rock | Sharpest contrast on the list, and it yields the press and podcast frames in one go |
| Jeans | Hour 1 and 2, open sand and car boot | Carries everything warm and human |
| Skirt and top | Hour 2, Lion Rock | These frames have to sit next to a retreat price and be believed |

## Frames mapped to pages

The sheet ends with an index tying every frame to a slot: the
theloveadventure.com homepage and Together pages, the sexual confidence mini
course, the workshop, the Desire Blueprint quiz opt in, podcast art, press
and thumbnails.

## Regenerating the PDF

```bash
pip install playwright pypdfium2 pillow
python3 photoshoot/topdf-two-hours.py
```

The script drives the Chromium already installed in the environment and prints
the HTML through its own print stylesheet, so the PDF and the web version never
drift apart. Google Fonts has to be reachable or the display face falls back to
Times; the script checks and prints `fonts loaded: True` before writing.
