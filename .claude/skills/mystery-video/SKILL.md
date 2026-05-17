---
name: mystery-video
description: End-to-end workflow for building a faceless AI YouTube mystery video — concept ideation, case development, retention scripting, and cinematic storyboarding. Use when the user wants to write, plan, or produce a mystery short / long-form mystery video, or build a repeatable mystery channel format.
---

# Mystery Video Workflow

A 4-step pipeline for turning a mystery angle into a script-ready, scene-ready faceless video.

## When to use

Invoke this skill when the user asks to:
- Pick a mystery video concept or idea
- Develop a mystery case
- Write a 60–90s mystery voiceover script for Shorts / Reels / TikTok
- Storyboard a mystery script into cinematic scenes for AI video tools (Sora, Runway, Veo, Kling, etc.)
- Build a repeatable mystery channel format

## How to run

Always confirm the target audience before STEP 1. Then run steps sequentially, gating between each step on the user picking which concept / case / script to move forward with. Do not skip ahead — each step's output is the next step's input.

If the user gives you raw material mid-pipeline (e.g. they already have a case), start at the matching step.

---

## STEP 1 — Pick a mystery angle people already want to click

Do NOT start with visuals. Start with the angle.

Strongest angles: missing objects, strange disappearances, hidden clues, secret rooms, unsolved puzzles, creepy discoveries, fake suspects, shocking final reveals.

Ask the user for `[AUDIENCE]` if not already known, then run this prompt:

> You are a YouTube mystery channel strategist.
>
> I want to build a faceless AI mystery video that can turn into a repeatable channel format.
>
> My target audience is: [AUDIENCE]
>
> Give me 10 mystery video concepts people would actually click.
>
> For each concept, include:
> 1. The video title
> 2. The main mystery
> 3. Why people would keep watching
> 4. The first clue
> 5. The twist
> 6. The final reveal
> 7. The visual style
> 8. How easy it is to produce with AI
>
> Rank the ideas from strongest to weakest based on curiosity and repeatability.

**Gate:** user picks one concept (by rank or title) before moving on.

---

## STEP 2 — Develop the chosen concept into a full case

(Prompt template not yet provided by the user. Until it is, use this interim gate:
expand the picked concept into a case file containing: setting, main character, timeline,
list of clues in reveal order, suspects / red herrings, the twist mechanism, and the final
reveal. Keep it tight — this is the source-of-truth doc that feeds STEP 3.)

**Gate:** user approves the case before moving on.

---

## STEP 3 — Write the script for retention

The script is where the money is. Mystery content works because people stay for the answer. Short lines, fast pacing, a new clue every few seconds.

Run this prompt with the case from STEP 2 pasted in:

> You are a YouTube Shorts scriptwriter who specializes in mystery videos with high retention.
>
> Write a 60 to 90 second voiceover script from this mystery case:
>
> [PASTE CASE]
>
> Rules:
> - Open with the strongest curiosity line.
> - Use short sentences.
> - Reveal clues slowly.
> - Do not explain too much.
> - Do not reveal the twist until near the end.
> - Make the final reveal satisfying.
> - Make the last line strong enough that people will comment.
>
> After the script, give me 5 title options and 5 hook options.

**Gate:** user picks a title + hook and approves the script before moving on.

---

## STEP 4 — Turn the script into scenes

Every scene does one job: reveal a clue, create tension, show danger, or move the viewer closer to the answer.

Run this prompt with the approved script:

> You are a cinematic storyboard artist and YouTube retention editor.
>
> Break this mystery script into 8 to 12 visual scenes:
>
> [PASTE SCRIPT]
>
> For each scene, give me:
> 1. Scene title
> 2. What happens
> 3. Camera angle
> 4. Main character action
> 5. Emotion
> 6. Clue revealed
> 7. Visual details
> 8. Transition to the next scene
>
> Keep the scenes cinematic, dark, clear, and easy to generate with AI video tools.
> Use the same main character and same visual world across the full video.

**Output:** a scene-by-scene storyboard the user can paste straight into an AI video tool.

---

## STEP 5 — (placeholder)

(Prompt template not yet provided by the user. Likely covers voiceover / image / video
generation. Skip cleanly to STEP 6 until the user supplies this step.)

---

## STEP 6 — Fix the weak parts before generating anything

A mystery video dies when the viewer figures it out too early or gets bored before the reveal. Audit and tighten BEFORE you spend tokens / credits generating audio and video.

Run this prompt with the approved script + scenes:

> You are a ruthless YouTube retention editor.
>
> Review my mystery script and scene plan:
>
> [PASTE SCRIPT AND SCENES]
>
> Find every weak moment where viewers might leave.
>
> For each weak moment, tell me:
> 1. Why it is weak
> 2. What curiosity is missing
> 3. How to make it stronger
> 4. The improved version
>
> Then give me:
> 1. The final improved script
> 2. The best scene order
> 3. The strongest hook
> 4. The best title
> 5. The best thumbnail idea
> 6. The exact moment to reveal the twist
>
> Do not make the video longer.
> Make it tighter and more addictive.

**Output:** the locked-in final script, scene order, hook, title, thumbnail concept, and twist timestamp — the production-ready package.

---

## Output conventions

- Number every concept, scene, and option so the user can reference them ("go with #3").
- Keep script lines short — one beat per line, no paragraphs.
- For storyboards, render each scene as a labeled block, not prose.
- Never invent the user's audience, niche, or case details — ask.
