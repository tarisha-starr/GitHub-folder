# Quick builds, standalone sites

These are for small sites that stand on their own: a personal homepage, a site
for another business, a rebuild of a layout you admire. They are **not** for
theloveadventure.com. That site is WordPress and its pages get pasted into
Kadence, so the rules in `SKILL.md` apply there instead.

The difference matters most at the deploy step. For a standalone one-pager
there is no WordPress to respect, so a static host is genuinely the right
answer and the "no Vercel" rule in `SKILL.md` does not apply.

## 1. One-page personal site, about 15 minutes

> Build me a one-page personal website for [NAME]. Include a hero with my name
> and a one-line bio, an about section, and links to [LINKS]. Make it look
> designed rather than generic, pick a bold modern style, then deploy it and
> give me the live URL.

Load `artifact-design` or `/mnt/skills/public/frontend-design` first. For a
personal site the brand is the person, so ask for or infer one concrete thing
about them and let the design come from that, rather than reaching for a
default. Publish an artifact preview before deploying, since it is faster to
iterate on and needs no account.

## 2. Site for a local business, about 20 minutes

> Build a modern website for a [TYPE] called [NAME]. Include hero, services,
> testimonials, and a contact section. Make it convert with clear calls to
> action. Deploy it live and give me the URL.

Two cautions worth raising before building:

- If the business is a **client of Tarisha's**, or any organisation that
  exists, do not invent testimonials, ratings, prices or credentials. Mark
  every placeholder plainly so it cannot reach production by accident. This is
  the same rule as the main site and it matters more here, because a stranger's
  business carries the consequences.
- If the business is imagined, say so somewhere on the page or in the handoff,
  so a practice piece is never mistaken for a live trading site.

`references/conversion.md` covers which conversion elements earn their place.
A local business page usually wants the Tier 2 set: hero, clear calls to
action, guarantee, FAQ. It rarely wants a countdown.

## 3. Rebuild a layout you admire, about 15 minutes

> Here is a screenshot of a website I love: [SCREENSHOT]. Rebuild this layout
> and feel as my own site for [PURPOSE]. Match the quality, not the content.
> Deploy it live.

Screenshots get you a good way there. Pasted HTML and CSS get you the rest,
so ask for the source if the result needs to be close. This environment's
proxy blocks most domains, so fetching the reference site directly usually
fails and the user has to paste it in.

What to carry over: layout, spacing rhythm, type scale, density, the way the
hero is composed. What not to carry over: their copy, photography, logo, icon
set, or illustrations. Those belong to someone else, and swapping in the
user's own branding is the point of the exercise anyway.

## Deploying

Check the host is reachable before promising a URL:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://vercel.com
```

A `403` from the proxy on `CONNECT` means the host is not on this
environment's allowlist, and the deploy cannot happen from here. Say so rather
than working around it. The fallback that always works is an artifact preview
link, plus the HTML file committed to the repo so the user can deploy it
themselves in a couple of minutes.

When a deploy is possible, walk the user through any sign-in one click at a
time and in plain language. Confirm it is live by loading the URL and reporting
the status code, rather than assuming the deploy succeeded.
