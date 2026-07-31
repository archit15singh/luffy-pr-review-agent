/**
 * Multiple Luffy hero banner variants (pure SVG, code-generated).
 * Flame palette: ink 0B0F19 · flame FF6B2C · crimson C41E3A · gold FFD166
 *
 * Usage:
 *   node -e "import('./src/assets/hero-options.mjs').then(m => m.writeAll('...'))"
 */

const W = 1200;
const H = 320;
const C = {
  ink: "#0B0F19",
  surface: "#111827",
  flame: "#FF6B2C",
  crimson: "#C41E3A",
  gold: "#FFD166",
  white: "#FFFFFF",
  muted: "#9CA3AF",
};

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function svgShell(id, body, title = "Luffy") {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(title)} · ${esc(id)}">
${body}
</svg>
`;
}

/** A — Current-style baseline (control) */
export function optionA_baseline() {
  return svgShell(
    "A-baseline",
    `
  <defs>
    <linearGradient id="gA" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${C.flame}"/>
      <stop offset="100%" stop-color="${C.crimson}"/>
    </linearGradient>
  </defs>
  <rect width="${W}" height="${H}" fill="${C.ink}"/>
  <circle cx="980" cy="60" r="180" fill="url(#gA)" opacity="0.35"/>
  <circle cx="200" cy="280" r="120" fill="${C.gold}" opacity="0.12"/>
  <text x="64" y="140" font-family="ui-sans-serif,system-ui,sans-serif" font-size="64" font-weight="700" fill="${C.white}">Luffy</text>
  <text x="64" y="200" font-family="ui-sans-serif,system-ui,sans-serif" font-size="28" fill="${C.gold}">Comment-triggered PR review agent</text>
  <rect x="64" y="240" width="120" height="8" rx="4" fill="${C.flame}"/>
`
  );
}

/** B — Glass panels + depth orbs (product / OG-card energy) */
export function optionB_glass() {
  return svgShell(
    "B-glass",
    `
  <defs>
    <linearGradient id="bgB" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#070A10"/>
      <stop offset="55%" stop-color="${C.ink}"/>
      <stop offset="100%" stop-color="#1a0a0c"/>
    </linearGradient>
    <linearGradient id="glassB" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.03"/>
    </linearGradient>
    <linearGradient id="orbB" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${C.flame}"/>
      <stop offset="50%" stop-color="${C.crimson}"/>
      <stop offset="100%" stop-color="#5c1020"/>
    </linearGradient>
    <radialGradient id="specB" cx="35%" cy="30%" r="55%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="40%" stop-color="${C.flame}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="${C.crimson}" stop-opacity="0"/>
    </radialGradient>
    <filter id="blurB" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#bgB)"/>
  <circle cx="980" cy="40" r="160" fill="url(#orbB)" opacity="0.55" filter="url(#blurB)"/>
  <circle cx="1040" cy="90" r="90" fill="url(#specB)"/>
  <circle cx="160" cy="280" r="100" fill="${C.gold}" opacity="0.08" filter="url(#blurB)"/>
  <!-- glass card -->
  <rect x="48" y="48" width="620" height="224" rx="24" fill="url(#glassB)" stroke="#ffffff" stroke-opacity="0.12"/>
  <rect x="48" y="48" width="620" height="1" rx="1" fill="#ffffff" opacity="0.25"/>
  <text x="80" y="130" font-family="ui-sans-serif,system-ui,sans-serif" font-size="56" font-weight="800" fill="${C.white}">Luffy</text>
  <text x="80" y="180" font-family="ui-sans-serif,system-ui,sans-serif" font-size="22" fill="${C.gold}">Comment-triggered PR review agent</text>
  <text x="80" y="220" font-family="ui-sans-serif,system-ui,sans-serif" font-size="16" fill="${C.muted}">Hermes · OpenRouter · hub memory · traces</text>
  <rect x="80" y="240" width="96" height="6" rx="3" fill="${C.flame}"/>
  <!-- floating glass chips -->
  <rect x="760" y="90" width="200" height="56" rx="14" fill="url(#glassB)" stroke="#ffffff" stroke-opacity="0.1"/>
  <text x="860" y="125" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="15" fill="${C.white}" opacity="0.9">@luffy review</text>
  <rect x="820" y="170" width="240" height="56" rx="14" fill="url(#glassB)" stroke="${C.flame}" stroke-opacity="0.35"/>
  <text x="940" y="205" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="15" fill="${C.gold}">score · tools · memory</text>
`
  );
}

/** C — Isometric “control plane” (3D-ish blocks) */
export function optionC_isometric() {
  // simple isometric diamond helpers
  const iso = (x, y, w, h, top, left, right) => {
    const t = `${x},${y - h} ${x + w},${y - h / 2} ${x},${y} ${x - w},${y - h / 2}`;
    const l = `${x - w},${y - h / 2} ${x},${y} ${x},${y + h} ${x - w},${y + h / 2}`;
    const r = `${x + w},${y - h / 2} ${x},${y} ${x},${y + h} ${x + w},${y + h / 2}`;
    return `
    <polygon points="${t}" fill="${top}"/>
    <polygon points="${l}" fill="${left}"/>
    <polygon points="${r}" fill="${right}"/>`;
  };
  return svgShell(
    "C-isometric",
    `
  <defs>
    <linearGradient id="bgC" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#06080f"/>
      <stop offset="100%" stop-color="${C.ink}"/>
    </linearGradient>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#bgC)"/>
  <!-- perspective grid -->
  <g opacity="0.12" stroke="${C.flame}" stroke-width="1" fill="none">
    ${Array.from({ length: 12 }, (_, i) => {
      const y = 80 + i * 22;
      return `<path d="M0,${y} Q600,${y + 40} 1200,${y}"/>`;
    }).join("")}
  </g>
  ${iso(920, 150, 70, 40, C.flame, "#b3471f", C.crimson)}
  ${iso(1000, 190, 55, 32, C.gold, "#b8963a", "#8a6a20")}
  ${iso(840, 210, 48, 28, "#3b82f6", "#1e3a5f", "#172554")}
  ${iso(1080, 130, 40, 24, C.crimson, "#7a1528", "#4a0e18")}
  <text x="64" y="120" font-family="ui-sans-serif,system-ui,sans-serif" font-size="58" font-weight="800" fill="${C.white}">Luffy</text>
  <text x="64" y="170" font-family="ui-sans-serif,system-ui,sans-serif" font-size="24" fill="${C.gold}">PR review control plane</text>
  <text x="64" y="210" font-family="ui-sans-serif,system-ui,sans-serif" font-size="16" fill="${C.muted}">trigger · sparse context · hermes loop · hub memory</text>
  <g font-family="ui-sans-serif,system-ui,sans-serif" font-size="13" fill="${C.white}">
    <rect x="64" y="240" width="110" height="32" rx="8" fill="${C.flame}" opacity="0.9"/>
    <text x="119" y="261" text-anchor="middle">Actions</text>
    <rect x="186" y="240" width="110" height="32" rx="8" fill="${C.surface}" stroke="${C.flame}" stroke-opacity="0.5"/>
    <text x="241" y="261" text-anchor="middle" fill="${C.gold}">Hermes</text>
    <rect x="308" y="240" width="110" height="32" rx="8" fill="${C.surface}" stroke="${C.crimson}" stroke-opacity="0.5"/>
    <text x="363" y="261" text-anchor="middle" fill="${C.muted}">OpenRouter</text>
  </g>
`
  );
}

/** D — Neural mesh / agent graph (depth via layers) */
export function optionD_mesh() {
  const nodes = [
    [700, 80],
    [820, 60],
    [960, 100],
    [1080, 70],
    [740, 160],
    [880, 180],
    [1020, 150],
    [1120, 200],
    [780, 250],
    [940, 260],
    [1060, 240],
  ];
  const edges = [
    [0, 1],
    [1, 2],
    [2, 3],
    [0, 4],
    [1, 4],
    [1, 5],
    [2, 5],
    [2, 6],
    [3, 6],
    [4, 5],
    [5, 6],
    [4, 8],
    [5, 8],
    [5, 9],
    [6, 9],
    [6, 10],
    [3, 7],
    [6, 7],
    [9, 10],
  ];
  const edgeEls = edges
    .map(([a, b], i) => {
      const [x1, y1] = nodes[a];
      const [x2, y2] = nodes[b];
      const op = 0.15 + (i % 3) * 0.08;
      const col = i % 2 === 0 ? C.flame : C.gold;
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${col}" stroke-opacity="${op}" stroke-width="1.5"/>`;
    })
    .join("\n");
  const nodeEls = nodes
    .map(([x, y], i) => {
      const r = 4 + (i % 3);
      const fill = i % 3 === 0 ? C.flame : i % 3 === 1 ? C.gold : C.crimson;
      return `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" opacity="0.85"/><circle cx="${x}" cy="${y}" r="${r + 6}" fill="${fill}" opacity="0.12"/>`;
    })
    .join("\n");
  return svgShell(
    "D-mesh",
    `
  <defs>
    <radialGradient id="glowD" cx="75%" cy="40%" r="50%">
      <stop offset="0%" stop-color="${C.flame}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="${C.ink}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="${W}" height="${H}" fill="${C.ink}"/>
  <rect width="${W}" height="${H}" fill="url(#glowD)"/>
  <g>${edgeEls}</g>
  <g>${nodeEls}</g>
  <text x="64" y="130" font-family="ui-sans-serif,system-ui,sans-serif" font-size="60" font-weight="800" fill="${C.white}">Luffy</text>
  <text x="64" y="185" font-family="ui-sans-serif,system-ui,sans-serif" font-size="24" fill="${C.gold}">Agentic PR review · multi-turn loop</text>
  <text x="64" y="230" font-family="ui-sans-serif,system-ui,sans-serif" font-size="16" fill="${C.muted}">tools · memory · traces · not a rubber stamp</text>
  <rect x="64" y="258" width="140" height="8" rx="4" fill="${C.flame}"/>
`
  );
}

/** E — Volumetric orbs (fake 3D spheres with specular) */
export function optionE_volumetric() {
  const sphere = (cx, cy, r, id) => `
  <defs>
    <radialGradient id="sph${id}" cx="32%" cy="28%" r="70%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.7"/>
      <stop offset="18%" stop-color="${C.flame}"/>
      <stop offset="55%" stop-color="${C.crimson}"/>
      <stop offset="100%" stop-color="#1a0508"/>
    </radialGradient>
    <radialGradient id="sh${id}" cx="50%" cy="100%" r="50%">
      <stop offset="0%" stop-color="#000000" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <ellipse cx="${cx}" cy="${cy + r * 0.85}" rx="${r * 0.85}" ry="${r * 0.18}" fill="url(#sh${id})"/>
  <circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#sph${id})"/>
  <circle cx="${cx - r * 0.28}" cy="${cy - r * 0.32}" r="${r * 0.12}" fill="#ffffff" opacity="0.35"/>
`;
  return svgShell(
    "E-volumetric",
    `
  <rect width="${W}" height="${H}" fill="#05070c"/>
  <rect width="${W}" height="${H}" fill="${C.ink}" opacity="0.9"/>
  ${sphere(980, 150, 110, "1")}
  ${sphere(820, 210, 48, "2")}
  ${sphere(1100, 90, 36, "3")}
  <text x="64" y="125" font-family="ui-sans-serif,system-ui,sans-serif" font-size="62" font-weight="800" fill="${C.white}">Luffy</text>
  <text x="64" y="180" font-family="ui-sans-serif,system-ui,sans-serif" font-size="26" fill="${C.gold}">Comment-triggered PR review agent</text>
  <text x="64" y="225" font-family="ui-sans-serif,system-ui,sans-serif" font-size="16" fill="${C.muted}">Hermes Agent · OpenRouter · hub memory · redacted traces</text>
  <g font-family="ui-monospace,monospace" font-size="13" fill="${C.flame}">
    <text x="64" y="270">@luffy review this pr</text>
  </g>
`
  );
}

/** F — Perspective cyber grid (svg-banners / neon energy) */
export function optionF_cyber() {
  const lines = [];
  for (let i = 0; i < 16; i++) {
    const t = i / 15;
    const y = 100 + t * t * 220;
    lines.push(`<line x1="0" y1="${y}" x2="1200" y2="${y}" stroke="${C.flame}" stroke-opacity="${0.05 + t * 0.12}" stroke-width="1"/>`);
  }
  for (let i = -8; i <= 8; i++) {
    const x = 600 + i * 80;
    lines.push(`<line x1="600" y1="80" x2="${x}" y2="320" stroke="${C.crimson}" stroke-opacity="0.12" stroke-width="1"/>`);
  }
  return svgShell(
    "F-cyber",
    `
  <defs>
    <linearGradient id="fadeF" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${C.ink}"/>
      <stop offset="100%" stop-color="#1a0808"/>
    </linearGradient>
    <linearGradient id="neonF" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="${C.flame}"/>
      <stop offset="100%" stop-color="${C.gold}"/>
    </linearGradient>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#fadeF)"/>
  <g>${lines.join("\n")}</g>
  <rect x="0" y="0" width="${W}" height="${H}" fill="url(#fadeF)" opacity="0.35"/>
  <text x="600" y="130" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="68" font-weight="900" fill="${C.white}">LUFFY</text>
  <text x="600" y="175" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="20" fill="${C.gold}">PR REVIEW CONTROL PLANE</text>
  <rect x="480" y="200" width="240" height="3" fill="url(#neonF)"/>
  <text x="600" y="245" text-anchor="middle" font-family="ui-monospace,monospace" font-size="14" fill="${C.muted}">hermes · opus · traces · memory</text>
`
  );
}

/** G — Mark-forward + extruded wordmark look */
export function optionG_mark() {
  // straw-hat-ish abstract ring + L mark (no IP assets — abstract)
  return svgShell(
    "G-mark",
    `
  <defs>
    <linearGradient id="ringG" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="${C.gold}"/>
      <stop offset="50%" stop-color="${C.flame}"/>
      <stop offset="100%" stop-color="${C.crimson}"/>
    </linearGradient>
    <linearGradient id="faceG" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1f2937"/>
      <stop offset="100%" stop-color="#0B0F19"/>
    </linearGradient>
    <filter id="softG"><feGaussianBlur stdDeviation="12"/></filter>
  </defs>
  <rect width="${W}" height="${H}" fill="${C.ink}"/>
  <circle cx="200" cy="160" r="130" fill="${C.flame}" opacity="0.15" filter="url(#softG)"/>
  <!-- abstract mark -->
  <circle cx="200" cy="160" r="88" fill="url(#faceG)" stroke="url(#ringG)" stroke-width="10"/>
  <path d="M160 130 Q200 100 240 130" fill="none" stroke="${C.gold}" stroke-width="8" stroke-linecap="round"/>
  <circle cx="175" cy="155" r="6" fill="${C.white}"/>
  <circle cx="225" cy="155" r="6" fill="${C.white}"/>
  <path d="M170 190 Q200 215 230 190" fill="none" stroke="${C.flame}" stroke-width="6" stroke-linecap="round"/>
  <!-- “extruded” title: shadow layers -->
  <text x="340" y="148" font-family="ui-sans-serif,system-ui,sans-serif" font-size="72" font-weight="900" fill="${C.crimson}" opacity="0.35">Luffy</text>
  <text x="336" y="144" font-family="ui-sans-serif,system-ui,sans-serif" font-size="72" font-weight="900" fill="${C.flame}" opacity="0.5">Luffy</text>
  <text x="332" y="140" font-family="ui-sans-serif,system-ui,sans-serif" font-size="72" font-weight="900" fill="${C.white}">Luffy</text>
  <text x="332" y="200" font-family="ui-sans-serif,system-ui,sans-serif" font-size="24" fill="${C.gold}">Comment-triggered PR review agent</text>
  <text x="332" y="240" font-family="ui-sans-serif,system-ui,sans-serif" font-size="16" fill="${C.muted}">Hermes · OpenRouter · hub memory · redacted traces</text>
`
  );
}

/** H — Split cinematic (left type, right abstract 3D stack) */
export function optionH_cinematic() {
  return svgShell(
    "H-cinematic",
    `
  <defs>
    <linearGradient id="splitH" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="${C.ink}"/>
      <stop offset="55%" stop-color="${C.ink}"/>
      <stop offset="100%" stop-color="#1c0a0e"/>
    </linearGradient>
    <linearGradient id="slabH" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${C.flame}"/>
      <stop offset="100%" stop-color="${C.crimson}"/>
    </linearGradient>
    <linearGradient id="slabH2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${C.gold}"/>
      <stop offset="100%" stop-color="#8a6a20"/>
    </linearGradient>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#splitH)"/>
  <!-- stacked 3D slabs (right) -->
  <g transform="translate(780,40)">
    <g transform="skewY(-12)">
      <rect x="40" y="40" width="280" height="48" rx="8" fill="url(#slabH)" opacity="0.95"/>
      <rect x="55" y="100" width="280" height="48" rx="8" fill="${C.surface}" stroke="${C.flame}" stroke-opacity="0.4"/>
      <rect x="70" y="160" width="280" height="48" rx="8" fill="url(#slabH2)" opacity="0.9"/>
      <rect x="85" y="220" width="280" height="48" rx="8" fill="${C.surface}" stroke="${C.gold}" stroke-opacity="0.35"/>
    </g>
  </g>
  <text x="64" y="115" font-family="ui-sans-serif,system-ui,sans-serif" font-size="20" font-weight="600" fill="${C.flame}" letter-spacing="4">AGENTIC CI</text>
  <text x="64" y="175" font-family="ui-sans-serif,system-ui,sans-serif" font-size="58" font-weight="800" fill="${C.white}">Luffy</text>
  <text x="64" y="225" font-family="ui-sans-serif,system-ui,sans-serif" font-size="22" fill="${C.gold}">Review control plane with memory + traces</text>
  <text x="64" y="270" font-family="ui-monospace,monospace" font-size="14" fill="${C.muted}">preload → assemble → hermes → normalize → hub</text>
`
  );
}

export const OPTIONS = [
  { id: "A-baseline", name: "Baseline (current style)", fn: optionA_baseline },
  { id: "B-glass", name: "Glass panels + orbs", fn: optionB_glass },
  { id: "C-isometric", name: "Isometric control plane", fn: optionC_isometric },
  { id: "D-mesh", name: "Neural mesh / agent graph", fn: optionD_mesh },
  { id: "E-volumetric", name: "Volumetric orbs (fake 3D)", fn: optionE_volumetric },
  { id: "F-cyber", name: "Cyber perspective grid", fn: optionF_cyber },
  { id: "G-mark", name: "Mark + extruded type", fn: optionG_mark },
  { id: "H-cinematic", name: "Cinematic split + slabs", fn: optionH_cinematic },
];

export function writeAll(outDir) {
  const fs = awaitImportFs();
  const path = awaitImportPath();
  // sync version for node script
}

function awaitImportFs() {
  return null;
}
function awaitImportPath() {
  return null;
}
