#!/usr/bin/env node
/**
 * Generate Luffy hero banner options into assets/brand-options/
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { OPTIONS } from "../src/assets/hero-options.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "../..");
const OUT = path.join(REPO, "assets", "brand-options");

fs.mkdirSync(OUT, { recursive: true });

const rows = [];
for (const opt of OPTIONS) {
  const file = `hero-${opt.id}.svg`;
  const svg = opt.fn();
  fs.writeFileSync(path.join(OUT, file), svg, "utf8");
  rows.push({ ...opt, file });
  console.log("wrote", file, svg.length, "bytes");
}

const gallery = `# Brand banner options (review)

Code-generated pure SVG heroes for the Luffy README. Open each file (or view this page on GitHub) and pick a winner.

**Flame palette:** ink \`#0B0F19\` · flame \`#FF6B2C\` · crimson \`#C41E3A\` · gold \`#FFD166\`

Regenerate:

\`\`\`bash
node readme-kit/scripts/generate-hero-options.mjs
\`\`\`

## Recommendation

**Primary pick: B-glass** — reads like a modern product card, uses glass depth + specular orb, still regenerable from tokens, works well at README width.

**Runner-up: E-volumetric** — strongest “3D ball” look without a real 3D runtime.

**Runner-up: H-cinematic** — bold marketing split; good if you want “agentic CI” energy.

A is the control (current style). C/D/F/G are distinct directions if you want isometric, mesh, cyber, or mark-led.

---

${rows
  .map(
    (r) => `## ${r.id} — ${r.name}

![${r.id}](${r.file})

Path: [\`assets/brand-options/${r.file}\`](${r.file})
`
  )
  .join("\n")}

## After you choose

Tell the agent e.g. **“use B”**. We’ll set:

- \`assets/luffy-hero-banner.svg\` ← chosen file  
- readme-kit hero generator default / theme hook  
- rebuild README
`;

fs.writeFileSync(path.join(OUT, "README.md"), gallery, "utf8");
fs.writeFileSync(path.join(OUT, "index.json"), JSON.stringify(rows.map(({ id, name, file }) => ({ id, name, file })), null, 2) + "\n");

// local HTML for offline flip-through
const html = `<!doctype html>
<html lang="en">
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Luffy brand options</title>
<style>
  body{margin:0;background:#0B0F19;color:#e5e7eb;font-family:system-ui,sans-serif;padding:24px}
  h1{color:#FFD166}
  .card{margin:0 0 40px;padding:16px;border:1px solid #1f2937;border-radius:12px;background:#111827}
  .card h2{margin:0 0 12px;font-size:18px;color:#FF6B2C}
  img{width:100%;max-width:1200px;height:auto;border-radius:8px;display:block}
  code{color:#FFD166}
</style>
<h1>Luffy hero options</h1>
<p>Pick one. Recommendation: <code>B-glass</code>, then <code>E-volumetric</code>, then <code>H-cinematic</code>.</p>
${rows
  .map(
    (r) => `<div class="card"><h2>${r.id} — ${r.name}</h2><img src="${r.file}" alt="${r.id}"/></div>`
  )
  .join("\n")}
</html>
`;
fs.writeFileSync(path.join(OUT, "preview.html"), html, "utf8");
console.log("gallery →", OUT);
