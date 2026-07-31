import fs from "node:fs";
import path from "node:path";
import { build } from "./build.mjs";
import { KIT_ROOT } from "./load.mjs";

function usage() {
  console.log(`readme-kit — compile README branding from intent

Usage:
  readme-kit build <config.yaml|json> [-o out.md] [--force]
  readme-kit init [--theme flame] [--pack ai-agent] [--dir .] [--format yaml|json]
  readme-kit brand <pack> [--theme flame] [--dir ./branding]
  readme-kit themes
  readme-kit packs

Examples:
  readme-kit build examples/luffy/readme.config.yaml -o README.generated.md
  readme-kit init --theme flame --pack ai-agent
`);
}

export async function main(argv = process.argv.slice(2)) {
  const cmd = argv[0];
  if (!cmd || cmd === "-h" || cmd === "--help") {
    usage();
    return 0;
  }

  if (cmd === "themes") {
    const dir = path.join(KIT_ROOT, "themes");
    for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".json"))) {
      console.log(f.replace(/\.json$/, ""));
    }
    return 0;
  }

  if (cmd === "packs") {
    const dir = path.join(KIT_ROOT, "packs");
    for (const f of fs.readdirSync(dir)) {
      if (fs.existsSync(path.join(dir, f, "pack.json"))) console.log(f);
    }
    return 0;
  }

  if (cmd === "build") {
    const configPath = argv[1];
    if (!configPath) {
      console.error("build requires <config.yaml|json>");
      return 1;
    }
    let out;
    let force = false;
    for (let i = 2; i < argv.length; i++) {
      if (argv[i] === "-o" || argv[i] === "--out") out = argv[++i];
      else if (argv[i] === "--force") force = true;
    }
    const result = build(configPath, { out, force });
    console.log(`wrote ${result.outPath} (${result.bytes} bytes) theme=${result.theme} pack=${result.pack}`);
    console.log(`branding → ${result.brandRoot}`);
    return 0;
  }

  if (cmd === "init") {
    let theme = "flame";
    let pack = "ai-agent";
    let dir = process.cwd();
    let format = "yaml";
    for (let i = 1; i < argv.length; i++) {
      if (argv[i] === "--theme") theme = argv[++i];
      else if (argv[i] === "--pack") pack = argv[++i];
      else if (argv[i] === "--dir") dir = path.resolve(argv[++i]);
      else if (argv[i] === "--format") format = String(argv[++i] || "yaml").toLowerCase();
    }
    if (format !== "yaml" && format !== "json") {
      console.error("--format must be yaml or json");
      return 1;
    }
    const dest = path.join(dir, format === "yaml" ? "readme.config.yaml" : "readme.config.json");
    if (fs.existsSync(dest)) {
      console.error(`already exists: ${dest}`);
      return 1;
    }
    const scaffold = {
      theme,
      pack,
      product: {
        name: "My Agent",
        tagline: "One-line product promise",
        one_liner: "What it does in a sentence.",
      },
      repo: {
        owner: "your-org",
        name: "your-repo",
        default_branch: "main",
      },
      badges: [
        {
          type: "workflow",
          workflow: "ci.yml",
          label: "CI",
        },
        {
          type: "static",
          label: "status",
          message: "mvp",
          color: "FF6B2C",
        },
      ],
      hero: { show_mark: false },
      sections: [
        "hero",
        "badges",
        "why",
        "trigger",
        "setup",
        "local",
        "limits",
        "footer",
      ],
      content: {
        why: "Explain the problem and why this agent exists.",
        trigger: ["@agent do the thing"],
        setup_steps: [
          "Install the workflow on your default branch",
          "Add required secrets",
        ],
        local_commands: "# local run instructions",
        limits: ["v1 is intentionally small"],
        footer: "Built with readme-kit",
      },
      output: {
        readme: "README.generated.md",
        branding_dir: "branding",
      },
    };
    if (format === "yaml") {
      const { stringify } = await import("yaml");
      fs.writeFileSync(dest, stringify(scaffold, { lineWidth: 100 }));
    } else {
      fs.writeFileSync(dest, JSON.stringify(scaffold, null, 2) + "\n");
    }
    console.log(`wrote ${dest}`);
    console.log(`next: edit config, then: readme-kit build ${path.basename(dest)}`);
    return 0;
  }

  if (cmd === "brand") {
    const pack = argv[1] || "ai-agent";
    let theme = "flame";
    let dir = path.join(process.cwd(), "branding");
    for (let i = 2; i < argv.length; i++) {
      if (argv[i] === "--theme") theme = argv[++i];
      else if (argv[i] === "--dir") dir = path.resolve(argv[++i]);
    }
    // Reuse build's asset path via a tiny synthetic config
    const tmp = path.join(dir, ".brand-config.json");
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(
      tmp,
      JSON.stringify(
        {
          theme,
          pack,
          product: { name: "Brand", tagline: pack },
          sections: ["footer"],
          content: { footer: "brand only" },
          output: { readme: path.join(dir, ".discard.md"), branding_dir: dir },
        },
        null,
        2
      )
    );
    build(tmp, { out: path.join(dir, ".discard.md"), brandingDir: dir, force: true });
    fs.unlinkSync(tmp);
    fs.unlinkSync(path.join(dir, ".discard.md"));
    console.log(`brand pack assets → ${dir}`);
    return 0;
  }

  console.error(`unknown command: ${cmd}`);
  usage();
  return 1;
}
