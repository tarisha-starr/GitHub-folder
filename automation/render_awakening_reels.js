// Render the weekly "The Second Awakening" reels (SERW brand).
//
// Each reel in content/second_awakening_reels.json becomes
// videos/awakening/reel-<id>.mp4 (1080x1920, about 22 seconds):
//   title card, then each question of that week (question and website
//   only), then an end card, joined with soft fades, plus a silent audio
//   track (TikTok needs one; add music in the app if you like).
//
//   node automation/render_awakening_reels.js
//   ONLY_ID=3 node automation/render_awakening_reels.js
//
// Needs the Playwright + Chromium already installed, and ffmpeg.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const QUESTIONS = JSON.parse(fs.readFileSync(path.join(ROOT, "content", "brave_questions.json"), "utf8"));
const REELS = JSON.parse(fs.readFileSync(path.join(ROOT, "content", "second_awakening_reels.json"), "utf8"));
const OUT = path.join(ROOT, "videos", "awakening");

const W = 1080, H = 1920, FADE = 0.6;
const DUR = { intro: 3.2, question: 5.8, end: 4.5 };
const SITE = "SEXUALEMPOWERMENTFORWOMEN.COM";
const FONTS = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=block";

// Same colourways as the SERW question cards.
const THEMES = {
  desire:   { bg: "#6E1A2E", glow: "#82263C", ink: "#F4EFE6", accent: "#C2A46D", bar: "#1F2A44" },
  marriage: { bg: "#1F2A44", glow: "#2C3A5A", ink: "#F4EFE6", accent: "#C2A46D", bar: "#6E1A2E" },
  body:     { bg: "#F4EFE6", glow: "#FBF8F2", ink: "#6E1A2E", accent: "#C2A46D", bar: "#1F2A44" },
  single:   { bg: "#F4D9D6", glow: "#F9E9E6", ink: "#6E1A2E", accent: "#C2A46D", bar: "#1F2A44" },
  self:     { bg: "#4A1220", glow: "#5E1A2C", ink: "#F4EFE6", accent: "#C2A46D", bar: "#1F2A44" },
};
const BRAND = THEMES.desire;

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const typeset = (s) => s.replace(/(^|[\s(])"/g, "$1“").replace(/"/g, "”").replace(/'/g, "’");

function page(t, inner) {
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="${FONTS}" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:${W}px;height:${H}px}
  body{background:${t.bg};background-image:radial-gradient(120% 70% at 85% 8%, ${t.glow} 0%, ${t.bg} 60%);
    color:${t.ink};font-family:"Cormorant Garamond",Georgia,serif;position:relative;overflow:hidden}
  /* Text lives in the middle: Instagram covers the top and bottom of a reel. */
  .wrap{position:absolute;left:120px;right:120px;top:330px;bottom:560px;
    display:flex;flex-direction:column;justify-content:center}
  .q{font-weight:600;line-height:1.16;font-size:104px;text-wrap:balance}
  .title{font-weight:600;font-size:132px;line-height:1.02}
  .sub{font-style:italic;font-weight:500;font-size:60px;color:${t.accent};margin-top:36px;line-height:1.2}
  .small{font-weight:500;font-size:56px;line-height:1.3;margin-top:80px}
  .bar{position:absolute;left:0;right:0;bottom:400px;height:120px;background:${t.bar};color:${t.accent};
    display:flex;align-items:center;justify-content:center;font-weight:600;font-size:40px;letter-spacing:.12em}
</style></head><body>${inner}<div class="bar">${SITE}</div></body></html>`;
}

function scenes(reel) {
  const qs = reel.question_ids.map((id) => QUESTIONS.find((q) => q.id === id));
  const n = qs.length;
  const out = [];
  out.push({ dur: DUR.intro, html: page(BRAND, `<div class="wrap">
    <div class="title">The Second Awakening</div>
    <div class="sub">Rewild your sexuality after 40</div></div>`) });
  qs.forEach((q) => {
    out.push({ dur: DUR.question, fit: true, html: page(THEMES[q.theme],
      `<div class="wrap"><div class="q" id="q">${esc(typeset(q.question))}</div></div>`) });
  });
  const ask = n > 1 ? `Which one got you?<br>Comment ${n === 3 ? "1, 2 or 3" : "1 or 2"}.` : "Tell me in the comments.";
  out.push({ dur: DUR.end, html: page(BRAND, `<div class="wrap">
    <div class="title">The Second Awakening</div>
    <div class="sub">Rewild your sexuality after 40</div>
    <div class="small">${ask}</div></div>`) });
  return out;
}

function stitch(files, durs, outFile) {
  const args = ["-y", "-loglevel", "error"];
  files.forEach((f, i) => args.push("-loop", "1", "-framerate", "30", "-t", String(durs[i]), "-i", f));
  const total = durs.reduce((a, b) => a + b, 0) - FADE * (durs.length - 1);
  args.push("-f", "lavfi", "-t", total.toFixed(2), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100");
  let chain = "", prev = "[0:v]", offset = 0;
  for (let i = 1; i < files.length; i++) {
    offset += durs[i - 1] - FADE;
    const label = i === files.length - 1 ? "[vx]" : `[v${i}]`;
    chain += `${prev}[${i}:v]xfade=transition=fade:duration=${FADE}:offset=${offset.toFixed(2)}${label};`;
    prev = label;
  }
  chain += `[vx]format=yuv420p[v]`;
  args.push("-filter_complex", chain, "-map", "[v]", "-map", `${files.length}:a`,
    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", "30",
    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", outFile);
  execFileSync("ffmpeg", args, { stdio: "inherit" });
  return total;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const only = process.env.ONLY_ID ? Number(process.env.ONLY_ID) : null;
  const browser = await chromium.launch();
  const pg = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  for (const reel of REELS) {
    if (only && reel.id !== only) continue;
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), `reel-${reel.id}-`));
    const list = scenes(reel), files = [];
    for (let i = 0; i < list.length; i++) {
      await pg.setContent(list[i].html, { waitUntil: "networkidle" });
      await pg.evaluate(() => document.fonts.ready);
      if (list[i].fit) {
        await pg.evaluate(() => {
          const wrap = document.querySelector(".wrap"), q = document.getElementById("q");
          let size = 104;
          while (wrap.scrollHeight > wrap.clientHeight && size > 56) { size -= 2; q.style.fontSize = size + "px"; }
        });
      }
      const f = path.join(tmp, `scene-${i}.png`);
      await pg.screenshot({ path: f });
      files.push(f);
    }
    const outFile = path.join(OUT, `reel-${reel.id}.mp4`);
    const secs = stitch(files, list.map((s) => s.dur), outFile);
    fs.rmSync(tmp, { recursive: true, force: true });
    console.log(`rendered ${path.relative(ROOT, outFile)} (${secs.toFixed(1)}s)`);
  }
  await browser.close();
})();
