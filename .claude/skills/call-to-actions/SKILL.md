---
name: call-to-actions
description: Turn a recorded call, workshop, discovery conversation or meeting into decisions, promises made, objections raised and next steps with owners. Use when the user says "what did I commit to", "extract actions from this call", "what came out of that session", "meeting notes", mentions a Zoom recording needing follow-up, or after any client or collaborator call.
---

# Call Action Item Extractor

Automations #7 and #31 combined. Three recorded calls in the last month,
every one with a transcript, nothing extracted from any of them.

## Step 1: find the call

Zoom connector:
- `recordings_list` with a date range, or `search_meetings` by topic
- Pull the `TRANSCRIPT` (`.VTT`) file from `recording_files`

If she names a person rather than a meeting, search Calendar
(`search_events`) to find when they met, then match by date.

## Step 2: extract into five buckets

Read the full transcript. Produce:

### 1. Decisions made
What was actually settled. Not what was discussed, what was *decided*.
If a topic was raised and left open, it belongs in Open Questions, not
here.

### 2. Promises Tarisha made
The highest-value bucket and the easiest to lose. Anything she said she'd
do: send a resource, make an introduction, follow up, check a date, look
something up. Quote her words, then state the commitment plainly.

> "I'll send you the Wanaka dates this week" → Send Wanaka retreat dates.
> Due: this week.

### 3. Promises made to her
What the other person committed to, and by when.

### 4. Objections and hesitations raised
Especially on discovery or sales calls. Price, timing, partner
resistance, "is this for me", fear of being seen. Log these **verbatim**
and feed them to `/customer-voice`. These are worth more than the action
items over time, because they rewrite sales pages.

### 5. Open questions
Raised, not resolved. Needs a decision.

## Step 3: write it somewhere it'll be seen

Default to Notion. Search for the relevant project page first
(`notion-search`) rather than creating orphan pages:

- Podcast guest call → the **Guest Pipeline** database
- Client or program call → the relevant program hub page
- Business or collaborator call → the matching project page

If nothing fits, create a page and say where you put it.

Format each action as a checkbox with an owner and a due date. Undated
actions don't get done.

For anything due inside 48 hours, also offer to draft the email
(Gmail `create_draft`) or put it on the calendar. Don't send anything
without her seeing it.

## Rules

- **Don't invent due dates.** If no date was agreed, write "no date
  agreed" and flag it. A fabricated deadline is worse than a missing one.
- **Don't inflate a maybe into a commitment.** "I could probably send
  that" is not a promise. Note it as tentative.
- **Attribute correctly.** Zoom speaker labels can be wrong when people
  talk over each other. If you're unsure who said something, say so
  rather than guessing.
- **Personal or sensitive disclosure stays out.** Her calls involve
  women discussing intimacy, trauma and their marriages. Extract the
  business actions. Do not write personal disclosures into a Notion page
  or a summary. If a piece of context is needed to make an action make
  sense, describe it neutrally.

## Finish

Lead with the promises she made, since those are the ones with a clock on
them. Then decisions, then everything else.
