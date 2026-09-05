# images/site/

Photography for theloveadventure.com. `site/index.html` references these four
files by name, so dropping them in here is the only step left.

Every one of them has a colour gradient behind it in the CSS, so if a file is
missing the page still composes correctly. That is deliberate, and it means the
page can go to review before the photography lands.

## The four files the homepage wants

| Filename | The shot | Where it goes |
| --- | --- | --- |
| `hero-piha.jpg` | Wide. Tarisha in the green dress, Mark behind her, standing on the wet rock shelf. Sea mist over Lion Rock, surf breaking left. They are small in a big frame. | Full bleed hero |
| `walking-out.jpg` | Portrait. The two of them walking hand in hand out of the sea cave, backlit, wet sand, long shadows toward camera. | The trail plate, "Therapy meets the trail" |
| `tarisha-mark.jpg` | Portrait. Close. His hand on her face, her laughing up at him, dark rock behind. | Founder portrait, 4:5 crop |
| `closing-beach.jpg` | Wide. The two of them sitting on the black sand, her leaning into him, bare feet, cliff behind. | The closing invitation plate |

Plus one for sharing:

| `og-card.jpg` | 1200x630 crop of the hero. | Open Graph and Twitter card |

## Why those four

`hero-piha.jpg` is the strongest frame in the set and it is doing exactly what
the hero needs: two people small in a large landscape, with the light and the
mist carrying the mood. The composition already has the type space built into
it, on the left, over the water.

`walking-out.jpg` is the one that earns the "the trail does the talking" idea.
Backlit, side by side, moving. It's a picture of the thing the retreats sell.

The playful frame (her foot on his chest, Lion Rock behind) is lovely and it is
not for the homepage. It belongs on `/about`, where personality is the point.

## Export settings

- Long edge 2000px, quality 82, sRGB
- AVIF or WebP preferred, with a `.jpg` at the same name as the fallback
- `hero-piha.jpg` under 220KB, since it is the LCP element
- Do not crop tight. The plates use `object-fit:cover` and the drift moves the
  image up to 60px, so leave headroom at the top and bottom

## The house grade

The CSS applies `saturate(.92) contrast(1.04) brightness(.97)` plus two pine
gradients over every plate. That pulls the teal dress and the red dress toward
the Soft Autumn palette without touching the files, so mixed frames read as one
shoot. Do not pre grade the exports; let the site do it.

## Getting them here

This environment has no Dropbox credentials, so the fetch cannot run from a
Claude session. Two ways in:

1. **Drop them in this folder** and commit. Simplest.
2. **Wire the Dropbox folder up once.** Add the shared link for the 2026 photos
   folder as the repository secret `DROPBOX_SITE_PHOTOS_URL`, then run the
   "Fetch Dropbox images" workflow. The existing Dropbox credentials
   (`DROPBOX_REFRESH_TOKEN`, `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`) are
   already set, so the folder link is the only missing piece.

Either way, rename to the four filenames above. The page does not guess.
