// Render the weekly "The Second Awakening" reels.
//
// Each reel in content/second_awakening_reels.json becomes
// videos/awakening/reel-<id>.mp4 (1080x1920, about 22 seconds):
//   intro card, then each question of that week, then an end card,
// joined with soft fades, plus a silent audio track (TikTok needs one;
// add music in the app if you like).
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

const THEMES = {
  desire:   { bg: "#1F2C1F", glow: "#2D3E2C", ink: "#F5EFE3", label: "#C9A579", rule: "#C75D3D" },
  marriage: { bg: "#2D3E2C", glow: "#5D6B3F", ink: "#FBF7EE", label: "#C9A579", rule: "#C75D3D" },
  body:     { bg: "#F5EFE3", glow: "#FDFBF5", ink: "#1F2C1F", label: "#9E4A2A", rule: "#C75D3D" },
  single:   { bg: "#5D6B3F", glow: "#6E7C4E", ink: "#FBF7EE", label: "#F5EFE3", rule: "#B8945A" },
  self:     { bg: "#2A2520", glow: "#3A332C", ink: "#F5EFE3", label: "#B8945A", rule: "#C75D3D" },
};
const BRAND = THEMES.desire;

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const typeset = (s) => s.replace(/(^|[\s(])"/g, "$1“").replace(/"/g, "”").replace(/'/g, "’");

function page(t, inner) {
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Marcellus&family=Lora:ital,wght@0,400;1,400&display=block" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:${W}px;height:${H}px}
  body{background:${t.bg};background-image:radial-gradient(120% 70% at 85% 8%, ${t.glow} 0%, ${t.bg} 60%);
    color:${t.ink};font-family:"Lora",Georgia,serif;position:relative;overflow:hidden}
  .frame{position:absolute;inset:48px;border:1px solid ${t.label};opacity:.35}
  /* Text lives in the middle: Instagram covers the top and bottom of a reel. */
  .wrap{position:absolute;left:120px;right:120px;top:330px;bottom:520px;
    display:flex;flex-direction:column;justify-content:center}
  .label{font-style:italic;font-size:40px;color:${t.label}}
  .rule{width:96px;height:3px;background:${t.rule};margin:34px 0 60px}
  .q{font-family:"Marcellus",Georgia,serif;font-weight:400;line-height:1.2;font-size:92px;text-wrap:balance}
  .title{font-family:"Marcellus",Georgia,serif;font-size:118px;line-height:1.08}
  .sub{font-style:italic;font-size:50px;color:${t.label};margin-top:40px;line-height:1.3}
  .small{font-size:44px;line-height:1.4;margin-top:70px}
  .name{position:absolute;left:0;right:0;bottom:420px;text-align:center;font-family:"Marcellus",Georgia,serif;
    letter-spacing:.22em;text-transform:uppercase;font-size:30px;color:${t.label}}
</style></head><body><div class="frame"></div>${inner}</body></html>`;
}

function scenes(reel) {
  const qs = reel.question_ids.map((id) => QUESTIONS.find((q) => q.id === id));
  const n = qs.length;
  const out = [];
  out.push({ dur: DUR.intro, html: page(BRAND, `<div class="wrap">
    <div class="label">The Second Awakening</div><div class="rule"></div>
    <div class="title">${n > 1 ? "Three questions you might not want to answer" : "One last question"}</div>
    <div class="sub">Rewild your sexuality after 40</div></div>`) });
  qs.forEach((q, i) => {
    const t = THEMES[q.theme];
    const tag = n > 1 ? `${i + 1} of ${n}. ${q.theme_label}` : q.theme_label;
    out.push({ dur: DUR.question, fit: true, html: page(t, `<div class="wrap">
      <div class="label">${esc(tag)}</div><div class="rule"></div>
      <div class="q" id="q">${esc(typeset(q.question))}</div></div>`) });
  });
  const ask = n > 1 ? `Which one got you?<br>Comment ${n === 3 ? "1, 2 or 3" : "1 or 2"}.` : "Tell me in the comments.";
  out.push({ dur: DUR.end, html: page(BRAND, `<div class="wrap">
    <div class="title">The Second Awakening</div>
    <div class="sub">Rewild your sexuality after 40</div><div class="rule"></div>
    <div class="small">${ask}<br><em>Save this for a quiet moment.</em></div></div>
    <div class="name">Tarisha Tourok</div>`) });
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
          let size = 92;
          while (wrap.scrollHeight > wrap.clientHeight && size > 50) { size -= 2; q.style.fontSize = size + "px"; }
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
