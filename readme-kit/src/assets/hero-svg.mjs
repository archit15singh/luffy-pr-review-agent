/** Generate a simple branded SVG banner from theme tokens (C5 lite). */
export function generateHeroBannerSvg(theme, product = {}) {
  const c = theme.colors;
  const title = product.name || "Project";
  const sub = product.tagline || "";
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-label="${escapeXml(title)}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#${c.flame}"/>
      <stop offset="100%" stop-color="#${c.crimson}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="320" fill="#${c.ink}"/>
  <circle cx="980" cy="60" r="180" fill="url(#g)" opacity="0.35"/>
  <circle cx="200" cy="280" r="120" fill="#${c.gold}" opacity="0.12"/>
  <text x="64" y="140" font-family="${theme.fonts?.display || "sans-serif"}" font-size="64" font-weight="700" fill="#ffffff">${escapeXml(title)}</text>
  <text x="64" y="200" font-family="${theme.fonts?.display || "sans-serif"}" font-size="28" fill="#${c.gold}">${escapeXml(sub)}</text>
  <rect x="64" y="240" width="120" height="8" rx="4" fill="#${c.flame}"/>
</svg>
`;
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
