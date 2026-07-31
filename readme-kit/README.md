# readme-kit

Compile **intent** (theme + pack + config) into GitHub-safe README Markdown and light branding assets.

**Spine:** Recipe δ (Luffy-native) on β (theme + brand pack). See [docs/README-KIT-MVP.md](../docs/README-KIT-MVP.md).

## Setup

```bash
cd readme-kit && npm install   # pulls `yaml` (v2) for .yaml/.yml configs
```

JSON configs work with zero install; YAML needs the dependency above.

## Commands

```bash
# from monorepo root (or cd readme-kit)
node readme-kit/bin/readme-kit.mjs themes
node readme-kit/bin/readme-kit.mjs packs

# YAML preferred (agent-friendly); JSON also supported
# Preview (safe):
node readme-kit/bin/readme-kit.mjs build readme-kit/examples/luffy/readme.config.yaml -o README.generated.md
# Live GitHub README (needs --force):
cd readme-kit && npm run build:luffy:write

node readme-kit/bin/readme-kit.mjs init --theme flame --pack ai-agent
# → readme.config.yaml

node readme-kit/bin/readme-kit.mjs brand ai-agent --theme flame --dir ./branding
```

**Note:** GitHub only renders root `README.md`. Kit defaults used to write `README.generated.md` so the live page never changed until you promote with `--force` / `build:luffy:write`.

## Layout

```text
themes/     flame, terminal (tokens / badge colors)
packs/      ai-agent (section order)
src/        build + render + asset generators
examples/   luffy config (yaml + json) + mermaid diagrams
```

Node ≥ 18. Dependency: [`yaml`](https://www.npmjs.com/package/yaml) for YAML parsing.

## Hero banner options

```bash
npm run brand:options   # → ../assets/brand-options/hero-*.svg + gallery
```
