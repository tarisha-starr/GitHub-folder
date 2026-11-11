// Render the brave-question cards in content/brave_questions.json to
// images/questions/question-<id>.jpg (1080x1350, Instagram portrait).
//
//   node automation/render_question_cards.js          # all cards
//   ONLY_ID=7 node automation/render_question_cards.js
//
// Uses the Playwright + Chromium already installed in the environment.
// Brand: Soft Autumn palette, Marcellus display (400 only), Lora body.

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const DATA = JSON.parse(
  fs.readFileSync(path.join(ROOT, "content", "brave_questions.json"), "utf8")
);
const OUT = path.join(ROOT, "images", "questions");

// One colourway per theme, so the grid has rhythm. Terracotta stays an accent.
const THEMES = {
  desire:   { bg: "#1F2C1F", glow: "#2D3E2C", ink: "#F5EFE3", label: "#C9A579", rule: "#C75D3D" },
  marriage: { bg: "#2D3E2C", glow: "#5D6B3F", ink: "#FBF7EE", label: "#C9A579", rule: "#C75D3D" },
  body:     { bg: "#F5EFE3", glow: "#FDFBF5", ink: "#1F2C1F", label: "#9E4A2A", rule: "#C75D3D" },
  single:   { bg: "#5D6B3F", glow: "#6E7C4E", ink: "#FBF7EE", label: "#F5EFE3", rule: "#B8945A" },
  self:     { bg: "#2A2520", glow: "#3A332C", ink: "#F5EFE3", label: "#B8945A", rule: "#C75D3D" },
};

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Curly quotes and apostrophes read better in a display serif.
function typeset(s) {
  return s
    .replace(/(^|[\s(])"/g, "$1“")
    .replace(/"/g, "”")
    .replace(/'/g, "’");
}

function html(card) {
  const t = THEMES[card.theme];
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Marcellus&family=Lora:ital,wght@0,400;1,400&display=block" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:1080px;height:1350px}
  body{background:${t.bg};
    background-image:radial-gradient(120% 80% at 85% 10%, ${t.glow} 0%, ${t.bg} 60%);
    color:${t.ink};font-family:"Lora",Georgia,serif;position:relative;overflow:hidden}
  .frame{position:absolute;inset:44px;border:1px solid ${t.label};opacity:.35}
  .wrap{position:absolute;left:120px;right:120px;top:150px;bottom:210px;
    display:flex;flex-direction:column;justify-content:center}
  .label{font-style:italic;font-size:34px;color:${t.label};letter-spacing:.02em}
  .rule{width:84px;height:3px;background:${t.rule};margin:30px 0 54px}
  .q{font-family:"Marcellus",Georgia,serif;font-weight:400;line-height:1.2;
    letter-spacing:-.005em;font-size:84px}
  .foot{position:absolute;left:120px;right:120px;bottom:110px;display:flex;
    justify-content:space-between;align-items:baseline;font-size:26px;color:${t.label}}
  .name{font-family:"Marcellus",Georgia,serif;letter-spacing:.22em;text-transform:uppercase;font-size:24px}
  .save{font-style:italic}
</style></head><body>
<div class="frame"></div>
<div class="wrap">
  <div class="label">${esc(card.theme_label)}</div>
  <div class="rule"></div>
  <div class="q" id="q">${esc(typeset(card.question))}</div>
</div>
<div class="foot"><span class="name">Tarisha Tourok</span><span class="save">Save this for later</span></div>
</body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const only = process.env.ONLY_ID ? Number(process.env.ONLY_ID) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const card of DATA) {
    if (only && card.id !== only) continue;
    await page.setContent(html(card), { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    // Shrink the question until the whole block fits inside the safe area.
    await page.evaluate(() => {
      const wrap = document.querySelector(".wrap");
      const q = document.getElementById("q");
      let size = 84;
      while (wrap.scrollHeight > wrap.clientHeight && size > 44) {
        size -= 2;
        q.style.fontSize = size + "px";
      }
    });
    const file = path.join(OUT, `question-${card.id}.jpg`);
    await page.screenshot({ path: file, type: "jpeg", quality: 92 });
    console.log("rendered", path.relative(ROOT, file));
  }
  await browser.close();
})();
