# readme-kit MVP

**Locked spine:** Recipe **δ (Luffy-native)** on **β (Theme + Brand Pack)**  
**Ship path:** α this week (pack + build) → β next → γ later  

| Decision | Choice |
|----------|--------|
| MVP recipe | **δ** = β + AI-agent vertical components |
| Authoring | **YAML** (`readme.config.yaml`) — agent-friendly |
| Visual depth | **V1 tokens + V2 light assets** (SVG mark/hero from tokens) |
| Compiler | **C4** Node CLI, zero browser runtime |
| First pack | **`ai-agent`** (Luffy-shaped) |
| First theme | **`flame`** (Luffy palette) |
| Output | GitHub-safe Markdown (+ optional `/branding` SVGs) |
| Non-goals (MVP) | TSX/React, live Framer canvas, profile widgets, docs-site twin |

---

## User journey (MVP)

```bash
cd my-repo
npx readme-kit init --theme flame --pack ai-agent
# edit readme.config.yaml
npx readme-kit build
# → README.md (+ branding/ if pack requests assets)
```

Inside Luffy monorepo:

```bash
node readme-kit/bin/readme-kit.mjs build examples/luffy/readme.config.yaml -o README.generated.md
```

---

## Config schema (MVP)

```yaml
theme: flame          # themes/*.json
pack: ai-agent        # packs/*/pack.json

product:
  name: Luffy
  tagline: Comment-triggered PR review agent
  one_liner: Hermes + OpenRouter + hub memory + redacted traces

repo:
  owner: archit15singh
  name: luffy-pr-review-agent
  default_branch: main

badges:
  - type: workflow
    workflow: luffy-pr-review.yml
    label: PR Review
  - type: static
    label: trigger
    message: "@luffy review this pr"
    color: FF6B2C
  - type: static
    label: model
    message: anthropic/claude-opus-5
    color: 0B0F19

hero:
  mark: assets/luffy-mark.svg
  show_mark: true

sections:
  - why
  - trigger
  - architecture   # mermaid from file or inline
  - e2e
  - setup
  - local
  - traces
  - memory
  - layout
  - limits
  - footer

content:
  why: |
    Most AI PR bots are stateless chat on a diff...
  trigger:
    - "@luffy review this pr"
    - "@luffy review"
  setup_steps:
    - Copy agent/, scripts/, workflow to default branch
    - Secret OPENROUTER_API_KEY
    - Secret LUFFY_HUB_TOKEN
  architecture_mermaid: docs/diagrams/architecture.mmd  # or inline |
  e2e_mermaid: docs/diagrams/e2e.mmd

output:
  readme: README.md
  branding_dir: branding   # optional generated SVGs
```

---

## Module map

```text
readme-kit/
  bin/readme-kit.mjs
  src/
    cli.mjs           # init | build | brand | preview(stub)
    build.mjs         # load → render → write
    load.mjs          # config + theme + pack
    render/
      document.mjs    # section order
      badges.mjs      # shields.io URLs
      hero.mjs
      mermaid.mjs
      sections.mjs    # why, setup, tables, code fences
      footer.mjs
    assets/
      hero-svg.mjs    # tokenized SVG generator (C5 lite)
  themes/
    flame.json
    terminal.json
  packs/
    ai-agent/
      pack.json       # default section order + copy templates
  examples/
    luffy/
      readme.config.yaml
```

---

## Success criteria (MVP)

1. `readme-kit build` produces valid Markdown GitHub can render  
2. Badges use shields.io with theme colors  
3. Mermaid blocks pass through unchanged  
4. Luffy example builds without hand-editing generated file  
5. `init` scaffolds config + empty content keys  

---

## Explicitly later (not MVP)

- MDX/TSX components (V4/V5)  
- Live preview server (approximate GitHub CSS)  
- CI auto-commit Action (V12)  
- `readme-kit invent` AI (V11)  
- Multiple vertical packs beyond `ai-agent`  
