# What the live pull surfaced

Read from theloveadventure.com on 3 August 2026 via the public WordPress REST
API. Nothing here has been changed on the live site. Every item is a
discrepancy between what is published and what we have been building to, or a
fault worth fixing.

Ordered by how much damage each one is doing.

---

## 1. The Wanaka retreat is unreachable from the navigation on 18 pages

The header and footer on 18 of the 24 pages link the flagship retreat to
`/together/retreats/wanaka`. That URL returns **404**. The page actually lives
at `/together/wanaka`.

```
/together/wanaka/            200
/together/retreats/wanaka/   404
```

The homepage is the only page with the correct link. Every other page sends
people to a dead end, three or four times each, from both the nav and the
footer, including from `/together` and `/together/therapy`, which are the two
pages most likely to send a warm reader to the retreat.

This is the highest-value fix on the site and it is a find and replace.

## 2. The retreat facts on the live site do not match the confirmed facts

The brief lists 10 couples per retreat, 5 days, 2 therapists. The live site
says something different, and does not agree with itself either.

| Fact | Brief | Live site |
|---|---|---|
| Couples per retreat | 10 | **Six**, on every page that states it |
| Retreat length | 5 days | **Six** on the homepage and `/together/wanaka`, **five** on `/about` and `/together` |
| Therapists | 2 | Never stated anywhere |

"Ten couples" appears nowhere on the live site. "Six couples per retreat"
appears on the homepage, `/about`, `/together`, `/together/wanaka`, `/events`
and `/for-her`.

The day count contradicts itself between pages:

- `/together/wanaka` "Six days in Wanaka", "What six days in Wanaka actually
  look like", "Six days. Six couples maximum."
- homepage "Six days. Six couples. The full braid in the Southern Alps."
- `/about` "The full five-day retreat. Six couples per intake."
- `/together` "The full 5-day retreat. Six couples per intake."

**Needs a decision before any page ships.** `site/index.html` currently states
5 days, 10 couples and 2 therapists, which matches the brief and matches no
page on the live site.

## 3. WordPress ships its demo page and it is in the sitemap

`/sample-page/` is published, returns 200, carries no `noindex`, and sits in
`page-sitemap.xml` alongside the 23 real pages. It contains the WordPress
default text, including the bike messenger who likes piña coladas and the XYZ
Doohickey Company of Gotham City.

`/milestone-1-preview/` is the same story. It is an old build preview, still
published, still indexable, still in the sitemap, and it carries the superseded
"Five days in Wanaka" copy.

Both should be moved to draft or deleted.

## 4. The contact address on the site is not the one in the brief

Every published page uses `hello@theloveadventure.com`, eight times across the
site, including on `/contact` and in the privacy policy as the address for
formal privacy requests.

The brief says the contact address is `tarisha@theloveadventure.com`, and
`site/therapy.html` was built with it.

One of the two is wrong. Whichever wins, the privacy policy has to match it,
because that is the address people use to make a Privacy Act request.

## 5. The free session works differently on the site than in the brief

The brief describes it as "Get the Love You Desire", applied for via a form,
with a reply in 1 to 3 business days, held on Zoom, for the two of them.

On the live site it is called a **discovery call**, it is 20 minutes, and it
books instantly through TidyCal at
`tidycal.com/tarishatourok/get-the-love-you-desire-discovery-session`. The name
survives only inside the booking URL. Nothing on any page calls it "Get the
Love You Desire", and nothing mentions a form, an application, or a wait for a
reply.

`/contact` also promises a response "within five working days", against the 1
to 3 business days in the brief.

So the two models are different products: instant self-booking versus an
application you are accepted into. That is a positioning decision, not a copy
tweak, and it changes what the therapy page should say.

## 6. The live therapy page leads with conflict

`/together/therapy` opens its "This is for couples who:" list with:

> Are stuck in a recurring fight or pattern

then "Feel the spark has gone but love is still there", then desire
discrepancy, then affair recovery. Conflict first, desire third.

This is exactly the positioning the brief wants moved away from. `site/therapy.html`
already reorders these desire first, so the rebuild fixes it. Worth knowing the
live page has not been updated yet.

## 7. Useful things the live site has that the repo build does not

Pulled so they do not get lost or reinvented:

- **Credentials, published and presumably verified.** Master's in Counselling,
  member of the New Zealand Association of Counsellors (NZAC), over a decade of
  clinical practice. Training in Emotionally Focused Therapy for couples levels
  1 and 2, Hakomi somatic psychotherapy, Gottman method, biodynamic breathwork
  facilitation, somatic trauma work, and sex therapy.
- **Therapy pricing.** Sessions are 75 minutes. NZD $295 per session, or a
  six-session block at NZD $1,650, described on the page as saving NZD $120.
  Weekly or fortnightly.
- **Retreat pricing.** NZD $16,000 or USD $9,500 per couple for Wanaka. Three
  intakes per year.
- **Retreat terms.** Deposit secures a place, balance due 60 days before.
  Cancellation over 90 days out is a full refund less a NZ$200 administration
  fee, 60 to 89 days is 50 percent, under 60 days is no refund but a good faith
  credit. Travel insurance covering cancellation is required.
- **Included follow-up.** One private online couples session within 60 days,
  built into the retreat price.

## 8. Smaller things

- `/together/retreats/` returns a 301 rather than a page, so the retreats hub
  in the build plan does not exist yet as a real page.
- The "For Her" nav item points off-site to `sexualempowermentforwomen.com`
  rather than to the `/for-her` section that exists and is published.
- The site is served through **BunnyCDN**, not Cloudflare as the tech stack
  notes say. Anyone purging a Cloudflare cache will be purging nothing.
