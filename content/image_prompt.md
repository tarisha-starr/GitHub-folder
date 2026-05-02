# ChatGPT Image Prompt

Paste this into ChatGPT (gpt-image-1 or DALL-E) once per image. Swap the
hook line each time.

```
Create a single photorealistic 4:5 portrait social media image
(1024x1280) for the brand "Sexual Empowerment for Women".

STYLE
- Photorealistic, cinematic, natural skin tones (NOT over-processed)
- Warm soft lighting (golden hour or soft indoor lamp)
- Lived-in, real, intimate — not stock-photo, not posed
- Premium calm aesthetic; soft depth of field; uncluttered background

SUBJECT
- Woman aged 45-60
- Vary across the series: ethnicities (Latina, Black, white, Asian,
  Indigenous, mixed), body sizes (include curvy and plus-size),
  hair (gray, brown, blonde; short, long)
- Natural beauty: minimal makeup, real skin, real hair
- Match her expression and posture to the emotional weight of the hook

SCENE
- Everyday intimate spaces: kitchen window, bedroom edge, couch,
  bathroom mirror, doorway, garden, yoga mat, walking outdoors
- Natural posture: sitting, leaning, standing, walking

TEXT OVERLAY (CRITICAL — render exactly)
- Render the hook text EXACTLY as written. Use straight apostrophes (').
- Font: elegant serif, Lora-style or Cormorant Garamond
- Large, left-aligned, easy to read on mobile
- Color rule:
  * On LIGHT/warm scenes: deep burgundy (#6E1A2E) body, warm gold
    (#C2A46D) on emotionally-weighted words
  * On DARK scenes: cream/white (#F4EFE6) body, warm gold (#C2A46D)
    accent words
- Include small gold ornamental flourishes (filigree dividers)
  between text blocks

HOOK TEXT
"<HOOK GOES HERE>"

BRANDING
- Solid footer bar at bottom: deep navy (#1F2A44), full width
- Footer text: SEXUALEMPOWERMENTFORWOMEN.COM
- Footer font: serif, ALL CAPS, large, cream/white or warm gold
- Center the footer text inside the bar

LOGO
- Circular gold "S" monogram in TOP RIGHT corner (~80px on 1280px height)

DO NOT
- Combine multiple images, include numbers/labels/watermarks
  (other than the brand footer), distort skin tones, use bright
  saturated colors, add any text other than the hook and footer
```

## After generating

1. Upload images to your Dropbox folder (any filename works)
2. Run **Fetch Dropbox images** workflow
3. Update `images/mapping.json` to map each new file to its post id
4. Append the draft entries from `content/draft_hooks.json` into
   `content/posts.json`
