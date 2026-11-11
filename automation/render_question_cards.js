// Render the question cards for both brands (1080x1350, Instagram portrait).
// Each card carries only the question and the website.
//
//   node automation/render_question_cards.js                 # both brands
//   BRAND=couples node automation/render_question_cards.js   # one brand
//   BRAND=serw ONLY_ID=7 node automation/render_question_cards.js
//
// serw    -> content/brave_questions.json   -> images/questions/serw/
// couples -> content/couples_questions.json -> images/questions/couples/
//
// Uses the Playwright + Chromium already installed in the environment.

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const FONTS = "https://fonts.googleapis.com/css2?family=Marcellus&family=Lora:ital,wght@0,400;0,500;1,400" +
  "&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=block";

// Sexual Empowerment for Women: burgundy, navy, gold, cream, blush.
// Footer bar with the site in gold capitals, as on the existing image posts.
const SERW = {
  data: "brave_questions.json",
  out: "serw",
  site: "SEXUALEMPOWERMENTFORWOMEN.COM",
  font: '"Cormorant Garamond",Georgia,serif',
  weight: 600,
  size: 96,
  footer: "bar",
  themes: {
    desire:   { bg: "#6E1A2E", glow: "#82263C", ink: "#F4EFE6", accent: "#C2A46D", bar: "#1F2A44" },
    marriage: { bg: "#1F2A44", glow: "#2C3A5A", ink: "#F4EFE6", accent: "#C2A46D", bar: "#6E1A2E" },
    body:     { bg: "#F4EFE6", glow: "#FBF8F2", ink: "#6E1A2E", accent: "#C2A46D", bar: "#1F2A44" },
    single:   { bg: "#F4D9D6", glow: "#F9E9E6", ink: "#6E1A2E", accent: "#C2A46D", bar: "#1F2A44" },
    self:     { bg: "#4A1220", glow: "#5E1A2C", ink: "#F4EFE6", accent: "#C2A46D", bar: "#1F2A44" },
  },
};

// The Love Adventure (couples therapy): Soft Autumn palette, Marcellus 400.
const COUPLES = {
  data: "couples_questions.json",
  out: "couples",
  site: "theloveadventure.com",
  font: '"Marcellus",Georgia,serif',
  weight: 400,
  size: 86,
  footer: "line",
  themes: {
    connection: { bg: "#1F2C1F", glow: "#2D3E2C", ink: "#F5EFE3", accent: "#C9A579", rule: "#C75D3D" },
    conflict:   { bg: "#2D3E2C", glow: "#5D6B3F", ink: "#FBF7EE", accent: "#C9A579", rule: "#C75D3D" },
    sex:        { bg: "#2A2520", glow: "#3A332C", ink: "#F5EFE3", accent: "#B8945A", rule: "#C75D3D" },
    life:       { bg: "#F5EFE3", glow: "#FDFBF5", ink: "#1F2C1F", accent: "#9E4A2A", rule: "#C75D3D" },
    repair:     { bg: "#5D6B3F", glow: "#6E7C4E", ink: "#FBF7EE", accent: "#F5EFE3", rule: "#B8945A" },
  },
};

const BRANDS = { serw: SERW, couples: COUPLES };

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const typeset = (s) => s.replace(/(^|[\s(])"/g, "$1“").replace(/"/g, "”").replace(/'/g, "’");

function html(brand, card) {
  const t = brand.themes[card.theme];
  const footer = brand.footer === "bar"
    ? `<div class="bar">${esc(brand.site)}</div>`
    : `<div class="site"><span class="rule"></span>${esc(brand.site)}</div>`;
  const bottom = brand.footer === "bar" ? 260 : 230;
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="${FONTS}" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:1080px;height:1350px}
  body{background:${t.bg};background-image:radial-gradient(120% 80% at 85% 10%, ${t.glow} 0%, ${t.bg} 60%);
    color:${t.ink};position:relative;overflow:hidden}
  .wrap{position:absolute;left:120px;right:120px;top:130px;bottom:${bottom}px;display:flex;align-items:center}
  .q{font-family:${brand.font};font-weight:${brand.weight};line-height:1.16;font-size:${brand.size}px;text-wrap:balance}
  .bar{position:absolute;left:0;right:0;bottom:0;height:150px;background:${t.bar};color:${t.accent};
    display:flex;align-items:center;justify-content:center;font-family:"Cormorant Garamond",Georgia,serif;
    font-weight:600;font-size:40px;letter-spacing:.12em}
  .site{position:absolute;left:120px;right:120px;bottom:120px;display:flex;align-items:center;gap:28px;
    font-family:"Lora",Georgia,serif;font-size:38px;color:${t.accent};letter-spacing:.04em}
  .site .rule{width:72px;height:3px;background:${t.rule || t.accent}}
</style></head><body>
<div class="wrap"><div class="q" id="q">${esc(typeset(card.question))}</div></div>
${footer}
</body></html>`;
}

(async () => {
  const names = process.env.BRAND ? [process.env.BRAND] : Object.keys(BRANDS);
  const only = process.env.ONLY_ID ? Number(process.env.ONLY_ID) : null;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const name of names) {
    const brand = BRANDS[name];
    if (!brand) throw new Error(`unknown BRAND ${name}`);
    const data = JSON.parse(fs.readFileSync(path.join(ROOT, "content", brand.data), "utf8"));
    const outDir = path.join(ROOT, "images", "questions", brand.out);
    fs.mkdirSync(outDir, { recursive: true });
    for (const card of data) {
      if (only && card.id !== only) continue;
      await page.setContent(html(brand, card), { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      await page.evaluate((start) => {
        const wrap = document.querySelector(".wrap"), q = document.getElementById("q");
        let size = start;
        while (q.scrollHeight > wrap.clientHeight && size > 48) { size -= 2; q.style.fontSize = size + "px"; }
      }, brand.size);
      const file = path.join(outDir, `question-${card.id}.jpg`);
      await page.screenshot({ path: file, type: "jpeg", quality: 92 });
      console.log("rendered", path.relative(ROOT, file));
    }
  }
  await browser.close();
})();
