// Render the weekly reels for both brands (1080x1920, about 22 seconds).
//
// Each reel: a title card, that week's questions (question and website
// only), then an end card, joined with soft fades, plus a silent audio
// track (TikTok needs one; add music in the app if you like). Scene
// colours follow position, so every cut is a clear change.
//
//   node automation/render_weekly_reels.js                  # both series
//   SERIES=couples node automation/render_weekly_reels.js   # one series
//   SERIES=serw ONLY_ID=3 node automation/render_weekly_reels.js
//
// serw     The Second Awakening      -> videos/awakening/reel-<id>.mp4
// couples  Three questions to ask each other -> videos/couples/reel-<id>.mp4
//
// Needs the Playwright + Chromium already installed, and ffmpeg.

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const W = 1080, H = 1920, FADE = 0.6;
const DUR = { intro: 3.2, question: 5.8, end: 4.5 };
const FONTS = "https://fonts.googleapis.com/css2?family=Marcellus&family=Lora:ital,wght@0,400;1,400" +
  "&family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&display=block";

const comment = (n) => (n === 3 ? "1, 2 or 3" : "1 or 2");

// Sexual Empowerment for Women: burgundy, navy, cream, deep wine, gold.
const SERW = {
  questions: "brave_questions.json",
  reels: "second_awakening_reels.json",
  out: "awakening",
  display: '"Cormorant Garamond",Georgia,serif',
  body: '"Cormorant Garamond",Georgia,serif',
  qWeight: 600, qSize: 104, titleSize: 132, subSize: 60, smallSize: 56,
  footer: "bar",
  site: "SEXUALEMPOWERMENTFORWOMEN.COM",
  frame: { bg: "#1F2A44", glow: "#2C3A5A", ink: "#F4EFE6", accent: "#C2A46D", bar: "#6E1A2E" },
  colours: [
    { bg: "#6E1A2E", glow: "#82263C", ink: "#F4EFE6", accent: "#C2A46D", bar: "#1F2A44" },
    { bg: "#F4EFE6", glow: "#FBF8F2", ink: "#6E1A2E", accent: "#C2A46D", bar: "#1F2A44" },
    { bg: "#4A1220", glow: "#5E1A2C", ink: "#F4EFE6", accent: "#C2A46D", bar: "#1F2A44" },
  ],
  intro: (n) => `<div class="title">The Second Awakening</div>
    <div class="sub">Rewild your sexuality after 40</div>`,
  end: (n) => `<div class="title">The Second Awakening</div>
    <div class="sub">Rewild your sexuality after 40</div>
    <div class="small">${n > 1 ? `Which one got you?<br>Comment ${comment(n)}.` : "Tell me in the comments."}</div>`,
};

// The Love Adventure (couples therapy): Soft Autumn, Marcellus 400, Lora.
// Pine Deep frames the reel; the questions move through Cream, Moss and Camel.
const COUPLES = {
  questions: "couples_questions.json",
  reels: "couples_reels.json",
  out: "couples",
  display: '"Marcellus",Georgia,serif',
  body: '"Lora",Georgia,serif',
  qWeight: 400, qSize: 94, titleSize: 120, subSize: 50, smallSize: 50,
  footer: "line",
  site: "theloveadventure.com",
  frame: { bg: "#1F2C1F", glow: "#2D3E2C", ink: "#F5EFE3", accent: "#C9A579", rule: "#C75D3D" },
  colours: [
    { bg: "#F5EFE3", glow: "#FDFBF5", ink: "#1F2C1F", accent: "#9E4A2A", rule: "#C75D3D" },
    { bg: "#5D6B3F", glow: "#6E7C4E", ink: "#FBF7EE", accent: "#F5EFE3", rule: "#B8945A" },
    { bg: "#C9A579", glow: "#D6B88F", ink: "#1F2C1F", accent: "#1F2C1F", rule: "#9E4A2A" },
  ],
  intro: (n) => `<div class="title">${n > 1 ? "Three questions to ask each other" : "One last question to ask each other"}</div>`,
  end: (n) => `<div class="title">${n > 1 ? `Which one hit home?` : "Ask each other tonight"}</div>
    <div class="sub">${n > 1 ? `Comment ${comment(n)}.<br>Then ask your partner tonight.` : "And listen to the answer."}</div>`,
};

const SERIES = { serw: SERW, couples: COUPLES };

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const typeset = (s) => s.replace(/(^|[\s(])"/g, "$1“").replace(/"/g, "”").replace(/'/g, "’");

function page(s, t, inner) {
  const footer = s.footer === "bar"
    ? `<div class="bar">${esc(s.site)}</div>`
    : `<div class="site"><span class="rule"></span>${esc(s.site)}</div>`;
  return `<!doctype html><html><head><meta charset="utf-8">
<link href="${FONTS}" rel="stylesheet">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:${W}px;height:${H}px}
  body{background:${t.bg};background-image:radial-gradient(120% 70% at 85% 8%, ${t.glow} 0%, ${t.bg} 60%);
    color:${t.ink};font-family:${s.body};position:relative;overflow:hidden}
  /* Text lives in the middle: Instagram covers the top and bottom of a reel. */
  .wrap{position:absolute;left:120px;right:120px;top:330px;bottom:560px;
    display:flex;flex-direction:column;justify-content:center}
  .q{font-family:${s.display};font-weight:${s.qWeight};line-height:1.16;font-size:${s.qSize}px;text-wrap:balance}
  .title{font-family:${s.display};font-weight:${s.qWeight};font-size:${s.titleSize}px;line-height:1.06;text-wrap:balance}
  .sub{font-style:italic;font-size:${s.subSize}px;color:${t.accent};margin-top:36px;line-height:1.3}
  .small{font-size:${s.smallSize}px;line-height:1.3;margin-top:80px}
  .bar{position:absolute;left:0;right:0;bottom:400px;height:120px;background:${t.bar};color:${t.accent};
    display:flex;align-items:center;justify-content:center;font-family:"Cormorant Garamond",Georgia,serif;
    font-weight:600;font-size:40px;letter-spacing:.12em}
  .site{position:absolute;left:120px;right:120px;bottom:440px;display:flex;align-items:center;gap:28px;
    font-family:"Lora",Georgia,serif;font-size:42px;color:${t.accent};letter-spacing:.04em}
  .site .rule{width:80px;height:3px;background:${t.rule || t.accent}}
</style></head><body>${inner}${footer}</body></html>`;
}

function scenes(s, questions, reel) {
  const qs = reel.question_ids.map((id) => questions.find((q) => q.id === id));
  const n = qs.length;
  const out = [{ dur: DUR.intro, html: page(s, s.frame, `<div class="wrap">${s.intro(n)}</div>`) }];
  qs.forEach((q, i) => {
    out.push({ dur: DUR.question, fit: true, html: page(s, s.colours[i % s.colours.length],
      `<div class="wrap"><div class="q" id="q">${esc(typeset(q.question))}</div></div>`) });
  });
  out.push({ dur: DUR.end, html: page(s, s.frame, `<div class="wrap">${s.end(n)}</div>`) });
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
  const names = process.env.SERIES ? [process.env.SERIES] : Object.keys(SERIES);
  const only = process.env.ONLY_ID ? Number(process.env.ONLY_ID) : null;
  const browser = await chromium.launch();
  const pg = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  for (const name of names) {
    const s = SERIES[name];
    if (!s) throw new Error(`unknown SERIES ${name}`);
    const questions = JSON.parse(fs.readFileSync(path.join(ROOT, "content", s.questions), "utf8"));
    const reels = JSON.parse(fs.readFileSync(path.join(ROOT, "content", s.reels), "utf8"));
    const outDir = path.join(ROOT, "videos", s.out);
    fs.mkdirSync(outDir, { recursive: true });
    for (const reel of reels) {
      if (only && reel.id !== only) continue;
      const tmp = fs.mkdtempSync(path.join(os.tmpdir(), `${name}-reel-${reel.id}-`));
      const list = scenes(s, questions, reel), files = [];
      for (let i = 0; i < list.length; i++) {
        await pg.setContent(list[i].html, { waitUntil: "networkidle" });
        await pg.evaluate(() => document.fonts.ready);
        if (list[i].fit) {
          await pg.evaluate((start) => {
            const wrap = document.querySelector(".wrap"), q = document.getElementById("q");
            let size = start;
            while (wrap.scrollHeight > wrap.clientHeight && size > 56) { size -= 2; q.style.fontSize = size + "px"; }
          }, s.qSize);
        }
        const f = path.join(tmp, `scene-${i}.png`);
        await pg.screenshot({ path: f });
        files.push(f);
      }
      const outFile = path.join(outDir, `reel-${reel.id}.mp4`);
      const secs = stitch(files, list.map((x) => x.dur), outFile);
      fs.rmSync(tmp, { recursive: true, force: true });
      console.log(`rendered ${path.relative(ROOT, outFile)} (${secs.toFixed(1)}s)`);
    }
  }
  await browser.close();
})();
