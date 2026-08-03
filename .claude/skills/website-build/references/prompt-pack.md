# The ten founder prompts, and what changed

This skill was built from a pack of ten website prompts. Most of the ideas are
sound and are folded into `SKILL.md`. Four of them break against this
particular setup, so they are adapted rather than followed. Recorded here so
nobody re-adopts the original wording later and quietly builds the wrong thing.

## Kept, close to the original

1. **Three layout variants first.** Layout is a visual decision and nobody can
   choose from prose. One change: vary structure only. The palette is fixed by
   the brand guidelines, so three colourways would be three wrong answers.
2. **Always invoke the design skill.** Correct, and it is the single biggest
   quality lever. The advice to avoid Inter and purple-to-blue gradients is
   already moot here, since Marcellus and Lora are mandated.
3. **Section-by-section.** Keeps feedback specific and stops one pass from
   silently breaking another section.
4. **Screenshot self-correction loop.** Two or three passes before showing a
   first version. `scripts/shoot.py` does this against the Chromium already
   installed. Skip motion-heavy sections, judge those in code.
5. **Browser QA.** Adapted to headless, since the container has no display, so
   "use a headed browser so I can watch" is not possible. `--qa` covers what
   watching would have caught: dead links, the mobile menu, focus states, and
   whether the page survives with JavaScript off.
6. **Mobile pass.** Folded into every screenshot run rather than left as a
   separate late step, because it is the step everyone forgets. The script
   fails on horizontal scroll, sub-12px text and small tap targets.

## Adapted

7. **Clone a reference site's code.** Fine for layout and feel. Do not carry
   over their copy, photography, logo or icon set: that is someone else's
   work and it would also break the brand. Note that this environment's proxy
   blocks most domains, so the source usually has to be pasted in by hand
   rather than fetched.
8. **Brand assets build.** The original tags a logo file and a guidelines
   image. Here the source of truth is Notion, and the logo files in
   `images/brand/` are from the *previous* brand. Following the original
   prompt produces a plum and gold site instead of a Pine Forest one. Always
   read the Notion brand docs first.
9. **Pull a polished component.** Useful, with a constraint the original does
   not mention: pasted components usually assume React, Tailwind or a CDN
   script, and every page here has to be one self-contained file. Port the
   idea into plain HTML and inline CSS rather than pasting the dependency.

## Replaced

10. **Ship it via GitHub and Vercel.** This is the one to drop. The site is
    WordPress on DreamHost behind Cloudflare, and the documented plan depends
    on it: blog migration from two old domains, Fluent Forms, the membership,
    Stripe, the quiz, Yoast, and Tarisha editing her own pages. A Vercel deploy
    creates a second site at a different URL and never touches
    theloveadventure.com.

    The pipeline that actually ships work here: build one self-contained file,
    preview it as an artifact with fonts inlined, commit it and open a draft
    PR, then paste it into the matching Kadence page. Editing the live site
    directly needs the domain added to this environment's network allowlist
    plus a WordPress application password.

## Added, because the pack has no equivalent

- **Voice compliance as a gate.** The brand bans dashes as punctuation, the
  word "real", and a list of coachy phrases. These survive human review and
  they are trivial to catch mechanically. `scripts/check_voice.py`.
- **Preview fonts.** The artifact host blocks font CDNs, so previews silently
  fall back to Times unless fonts are inlined. `scripts/embed_fonts.py`.
- **Never invent proof.** Ratings, client counts and testimonials are claims
  about a therapy practice. The pack is silent on this; it matters more here
  than the design does.
