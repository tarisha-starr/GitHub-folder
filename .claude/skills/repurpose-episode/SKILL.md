---
name: repurpose-episode
description: Turn one long recording, podcast episode, workshop, transcript or article into a full set of drafts across every channel. Use when the user says "repurpose this", "turn this episode into posts", "I recorded a workshop", "what can I use from this call", mentions a new podcast episode or Zoom recording, or wants content drafts pulled out of long-form material.
---

# Content Repurposing Engine

Automation #11. One recording currently produces one episode. It should
produce the episode plus twenty other assets.

This is the highest-leverage automation in this repo, because the raw
material already exists and is currently being used once.

## Step 1: get the transcript

**From Zoom** (most common). Recordings live in the Zoom connector:

- `recordings_list` with a `from`/`to` date range to find the session
- Pull the `TRANSCRIPT` file (`.VTT`) from `recording_files`
- Or use `search_meetings` / `ask` if the user names the meeting

VTT includes timestamps and speaker labels. Keep the timestamps while
working, they let you cite where a quote came from. Strip them from
final output.

**Other sources:** a Drive file, a pasted transcript, a YouTube video, an
article. Same process from Step 2 onward.

## Step 2: mine it before you write anything

Read the whole transcript first. Do not start generating while reading.

Pull out, with rough timestamps:

- **Emotional peaks** — where her voice sharpens, where she says
  something she clearly believes. These become hooks.
- **Client stories and examples** — "I had a woman who..." These are the
  highest-converting content she produces. Never invent these.
- **Reframes** — "it's not X, it's Y". This is her core content shape.
- **Objections and fears** named out loud by participants.
- **Exact phrases used by the women, not by her.** These matter for sales
  copy. Log them verbatim.
- **Practices and exercises** she teaches.

If the transcript is long, work through it in sections rather than
skimming for quotable lines. The best material is usually not in the
first ten minutes.

## Step 3: generate the assets

Match the existing repo formats exactly so output drops straight into the
pipeline. Read the current files first to match structure and field names.

| Asset | Count | Target file | Fields |
|---|---|---|---|
| Image posts | 8-12 | `content/drafts/image_post_drafts.json` | `hook`, `caption`, `question`, `hashtags`, `image` |
| Hooks | 10-15 | `content/hooks.md` | grouped by theme |
| Reels | 4-6 | `content/reels.json` | `hook`, `caption` |
| Journal prompts | 5-8 | `content/drafts/journal_prompt_drafts.json` | `prompt`, `caption` |
| Infographics | 2-3 | `content/drafts/infographic_drafts.json` | `title`, `caption` |
| Newsletter section | 1 | write to Notion | 200-400 words |
| Customer language log | all | see `/customer-voice` | verbatim phrases |

**Write to the `drafts/` files, not the live ones.** Her pipeline
promotes drafts after review. Don't put ungated content into
`content/posts.json`.

## Step 4: brand check, always

Run `/brand-check` on everything before writing it to disk:

```bash
python3 automation/brand_check.py content/drafts/image_post_drafts.json
```

Generated content drifts toward polished prose and coaching cliche. This
step is not optional. Fix violations before committing.

## Rules

- **Never fabricate a client story.** If she didn't say it on the
  recording, it doesn't go in a caption. This is the fastest way to
  destroy trust with an audience that can tell.
- **Quote the women verbatim** when logging customer language. Paraphrase
  destroys the value.
- **One idea per post.** A dense transcript tempts you to pack three
  reframes into one caption. Split them, that's more posts anyway.
- **Don't over-produce.** Twelve strong posts beat thirty thin ones. If
  the recording only has six good ideas in it, produce six.

## Finish

Tell her what came out of it, where it went, and which two or three
pieces are the strongest. She has to choose what to publish, so lead with
the standouts rather than the full inventory.
