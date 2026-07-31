import fs from "node:fs";
import path from "node:path";
import { loadConfig, loadTheme, loadPack, resolveMaybeFile } from "./load.mjs";
import { renderDocument } from "./render/document.mjs";
import { generateHeroBannerSvg } from "./assets/hero-svg.mjs";

export function build(configPath, { out, brandingDir, force } = {}) {
  const config = loadConfig(configPath);
  const theme = loadTheme(config.theme || "flame");
  const pack = loadPack(config.pack || "ai-agent");

  // Resolve mermaid from files relative to config
  const c = config.content || (config.content = {});
  for (const key of [
    "architecture_mermaid",
    "e2e_mermaid",
    "pipeline_mermaid",
    "agentic_loop_mermaid",
    "agentic_loop_ascii",
  ]) {
    if (c[key]) {
      c[key] = resolveMaybeFile(config.__dir, c[key]);
    }
  }

  const md = renderDocument(config, theme, pack);

  const outPath = path.resolve(out || config.output?.readme || "README.generated.md");
  if (fs.existsSync(outPath) && !force && path.basename(outPath) === "README.md") {
    throw new Error(
      `Refusing to overwrite ${outPath} without --force (use README.generated.md or pass --force)`
    );
  }
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, md, "utf8");

  const brandRoot = path.resolve(
    brandingDir || path.join(config.__dir, config.output?.branding_dir || "branding")
  );
  if (pack.assets?.includes("hero-banner")) {
    fs.mkdirSync(brandRoot, { recursive: true });
    const svg = generateHeroBannerSvg(theme, config.product);
    fs.writeFileSync(path.join(brandRoot, "hero-banner.svg"), svg, "utf8");
  }

  return { outPath, brandRoot, theme: theme.id, pack: pack.id, bytes: md.length };
}
