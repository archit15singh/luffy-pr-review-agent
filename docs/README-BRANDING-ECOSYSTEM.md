# README Branding as an Ecosystem

**Status:** ranked + spine locked — see [README-KIT-MVP.md](./README-KIT-MVP.md)  
**Date:** 2026-07-31  
**Lens:** first principles → primitives → axes → permutations → concrete variants → **MVP**

---

## 1. First principles

A GitHub README is not a document system. It is a **constrained frontend** that only renders a fixed set of primitives:

| Primitive | Role |
|-----------|------|
| Text | Hierarchy, narrative, copy |
| Images | SVG / PNG / GIF / animated SVG |
| HTML | Layout hacks GitHub still allows |
| Badges | shields.io / badgen / custom SVG endpoints |
| Generated assets | Banners, icons, social cards |
| Dynamic endpoints | Actions, stats APIs, shields dynamic |
| Markdown structure | Sections, tables, code, Mermaid |

**Branding** = *consistently generating and composing those primitives* so the repo feels intentional (Linear / Vercel / OpenAI), not stitched together from random widgets.

That implies three jobs, not one:

1. **Author** — what humans write (intent, content, structure)  
2. **Compile** — transform intent → primitives  
3. **Distribute** — assets + `README.md` land in git for GitHub to render  

Today everyone does (1) and skips a real (2): they hand-author Markdown and paste shields/SVGs by muscle memory.

---

## 2. The six categories (orthogonal axes)

Treat these as **independent axes**, not competing products. Real systems are combinations.

| # | Category | One-line | Author writes | System generates |
|---|----------|----------|---------------|------------------|
| **C1** | Theme packs | Tailwind for README | theme + YAML content | Full visual language |
| **C2** | Component library | Shadcn for README | `<Hero />` tree | Composed Markdown/HTML |
| **C3** | Design systems | Shared tokens | brand tokens | Colors, type, spacing, icons |
| **C4** | Build systems | Next-like compile | `README.tsx` / source | Deterministic `README.md` |
| **C5** | Asset generators | `readme generate *` | commands / specs | SVG/PNG packs |
| **C6** | Branding packs | `npx readme brand X` | one archetype | Folder of assets + skeleton |

### Dependencies (not free combinations)

```text
C6 (brand pack)  ──uses──►  C5 (assets) + C3 (tokens)
C1 (theme)       ──uses──►  C3
C2 (components)  ──uses──►  C3 + often C5
C4 (build)       ──hosts──► C1 ∪ C2 ∪ C5 ∪ C6
```

**C4 is the platform.** Everything else is a package on the platform.

---

## 3. Existing tools map (gaps)

| Gap | Partial tools | Missing |
|-----|---------------|---------|
| Badges only | shields, badgen | Composition rules |
| Stats widgets | github-readme-stats | Brand integration |
| One-off SVG | typing-svg, Mermaid | Design system |
| Docs themes | Docusaurus, Mintlify | README-as-entry product |
| Templates | Awesome README | Build step + reuse |

**Whitespace:** *Framer / shadcn for GitHub READMEs* — author intent, compile to GitHub-safe Markdown + assets.

---

## 4. Combinatorial space

With 6 binary “include?” axes → **2⁶ = 64** theoretical products.  
Most are useless. Collapse by **platform choice**:

| Platform mode | Meaning |
|---------------|---------|
| **P0** | No compiler (paste templates/assets only) |
| **P1** | Compiler exists (C4) |
| **P2** | Compiler + live preview (local or web) |

Then layer **content authoring**:

| Authoring mode | Meaning |
|----------------|---------|
| **A0** | Pure Markdown templates |
| **A1** | YAML / theme pack (C1) |
| **A2** | Component tree (C2) |
| **A3** | Full TSX/JSX (C2+C4 heavy) |

And **visual depth**:

| Visual mode | Meaning |
|-------------|---------|
| **V0** | Typography + badges only |
| **V1** | Tokenized theme (C3) |
| **V2** | Generated SVG asset pack (C5/C6) |

A **variant** = `(P, A, V)` × optional packaging story.

---

## 5. Concrete product variants

Each variant is a **named product shape** you can rank later.  
Scoring axes (for later): *time-to-pretty*, *expressiveness*, *GitHub-fidelity*, *maintenance*, *ecosystem lock-in*, *AI-agent fit*.

---

### V1 — “Shields + Skeleton”  
**Axes:** P0 · A0 · V0 · pieces of C6  

**What it is:** Curated badge rows + section skeleton Markdown. No compiler.

```bash
npx readme-kit init --skeleton ai-agent
# drops README.md + badge snippets only
```

| Pros | Cons |
|------|------|
| Zero build | Inconsistent over time |
| Instant | No real brand system |

**Closest to today + tiny lift.**

---

### V2 — “Brand Pack Drop” ⭐  
**Axes:** P0 · A0 · V2 · **C6 + C5**  

**What it is:** One archetype command dumps `/branding/*` SVGs + a README that only *references* them.

```bash
npx readme brand ai-agent
# branding/hero.svg logo.svg architecture.svg social-card.png ...
# README.md with image links + install sections
```

| Pros | Cons |
|------|------|
| Instant “Vercel feel” | Hand-edit drift |
| No build required | Hard to re-theme later |

**Highest ROI for open-source agent repos (e.g. Luffy) in a weekend.**

---

### V3 — “Theme Pack YAML”  
**Axes:** P1 · A1 · V1 · **C1 + C3 + C4**  

**What it is:** Tailwind-for-README.

```yaml
# readme.config.yaml
theme: ai-dark
hero:
  title: Luffy
  subtitle: Comment-triggered PR reviews
features:
  - Multi-repo hub memory
  - Redacted traces
```

```bash
readme-kit build   # → README.md
```

| Pros | Cons |
|------|------|
| Non-devs can author | Less layout control |
| Consistent sections | Themes need maintenance |

---

### V4 — “Component Library (MDX-ish)” ⭐⭐  
**Axes:** P1 · A2 · V1 · **C2 + C3 + C4**  

**What it is:** Shadcn for README.

```mdx
<Hero product="Luffy" gradient="flame" />
<FeatureGrid items={features} />
<Architecture mermaid={diagram} />
<Install secrets={["OPENROUTER_API_KEY"]} />
<Metrics />
<Footer />
```

Compile → GitHub-safe Markdown + HTML + badges.

| Pros | Cons |
|------|------|
| Composition & reuse | Learning curve |
| Ecosystem of components | Need strict GitHub HTML allowlist |

---

### V5 — “README.tsx Frontend”  
**Axes:** P1 · A3 · V1–V2 · **C2 + C4 + C5**  

**What it is:** React/JSX source of truth.

```tsx
export default function Readme() {
  return (
    <>
      <Hero product="Luffy" buttons={["GitHub", "Docs"]} />
      <FeatureGrid />
      <Architecture />
      {stars > 1000 && <Sponsors />}
      <LatestRelease />
    </>
  )
}
```

```bash
readme-kit build && git add README.md branding/
```

| Pros | Cons |
|------|------|
| Conditionals, data fetch, full power | Heaviest |
| Themes as packages | Overkill for small libs |

**“Framer for GitHub README” trajectory.**

---

### V6 — “Asset Studio CLI”  
**Axes:** P0–P1 · A0 · V2 · **C5 dominant**  

**What it is:** Only generates graphics; you still write Markdown.

```bash
readme generate hero --title "Luffy" --palette flame
readme generate architecture --from mermaid.mmd
readme generate badges --stack hermes,openrouter,actions
readme generate social-card
```

| Pros | Cons |
|------|------|
| Solves the hard visual part | Still glue Markdown by hand |
| Composable with anything | Two workflows |

---

### V7 — “Theme + Brand Pack Hybrid” ⭐⭐⭐  
**Axes:** P1 · A1 · V2 · **C1 + C3 + C5 + C6**  

**What it is:** YAML content + named theme + auto-generated asset pack that matches the theme.

```bash
npx create-readme my-agent --theme openai --pack ai-agent
readme-kit build
```

Outputs:

```text
branding/   # C5/C6 assets in theme tokens
README.md   # C1 sections filled from YAML
readme.lock  # pin theme + pack versions
```

| Pros | Cons |
|------|------|
| Best “pretty + consistent” ratio | Needs good default packs |
| Re-themeable | Still not freeform layout |

**Strong default product MVP.**

---

### V8 — “Components + Asset Generators” ⭐⭐⭐⭐  
**Axes:** P1 · A2 · V2 · **C2 + C4 + C5 + C3**  

**What it is:** Component tree *drives* both Markdown structure and SVG generation.

```tsx
<Architecture src="docs/flow.mmd" brand="flame" />
// compiles mermaid → branding/architecture.svg + embeds in README
```

| Pros | Cons |
|------|------|
| One authoring surface | Implementation depth |
| Diagrams match brand | Needs render pipeline |

**Closest to a real design system.**

---

### V9 — “GitHub Profile Mode”  
**Axes:** P1 · A1–A2 · V1 · C1/C2 + dynamic badges  

**What it is:** Optimized for profile READMEs (stats, typing, trophies) with a theme so widgets don’t clash.

| Pros | Cons |
|------|------|
| Huge existing demand | Different from product repos |
| Widget ecosystem | Dependent on third-party APIs |

---

### V10 — “Docs-site twin”  
**Axes:** P1 · A3 · V1 · C4 + export  

**What it is:** Same component source builds **Mintlify/Nextra site** *and* a GitHub README “trailer.”

| Pros | Cons |
|------|------|
| One brand, two surfaces | Complex |
| Pro teams care | Heavy for OSS solo |

---

### V11 — “AI-authored kit”  
**Axes:** any P/A/V + LLM  

**What it is:** `readme-kit invent --from repo` analyzes code, proposes theme + features + Mermaid, generates pack.

| Pros | Cons |
|------|------|
| Fits Luffy/agent world | Quality variance |
| Fast onboarding | Needs human lockfile |

**Natural extension of Luffy’s “agent produces structured artifacts”.**

---

### V12 — “Zero-install GitHub Action brand”  
**Axes:** P1 in CI · A1 · V2  

**What it is:** On push, Action builds README from `readme.config.yaml` + regenerates assets; commits or uploads artifact.

| Pros | Cons |
|------|------|
| No local toolchain | Needs write token |
| Always consistent on main | CI noise |

---

## 6. Permutation matrix (useful cells only)

|  | **V0 badges** | **V1 tokens** | **V2 asset packs** |
|--|---------------|---------------|---------------------|
| **A0 Markdown** | V1 Skeleton | — | **V2 Brand Pack Drop** |
| **A1 YAML theme** | thin | **V3 Theme Pack** | **V7 Theme+Pack** |
| **A2 Components** | thin | **V4 Component lib** | **V8 Components+Assets** |
| **A3 TSX** | rare | V5 lite | **V5 full** |

---

## 7. Ranking rubric (for later mix-and-match)

Score 1–5 each; weight as you care:

| Criterion | Question |
|-----------|----------|
| **T** Time-to-pretty | Minutes from empty repo to “looks intentional”? |
| **E** Expressiveness | Can power users escape the box? |
| **G** GitHub fidelity | Renders correctly on github.com (HTML allowlist, no JS)? |
| **M** Maintainability | Re-theme / update without rewriting copy? |
| **S** Scope fit | Right for *product* READMEs vs profiles vs docs? |
| **A** Agent-native | Can an AI agent author the source format reliably? |
| **O** Open ecosystem | Themes/components as installable packages? |

**Suggested weights for OSS agent tools (Luffy-class):**  
`T×3 + G×3 + A×2 + M×2 + E×1 + S×1 + O×1`

---

## 8. Provisional ranking (discussion, not final)

| Rank | Variant | Why |
|------|---------|-----|
| 1 | **V7 Theme + Brand Pack** | Best pretty/consistent ratio; YAML is agent-friendly |
| 2 | **V8 Components + Assets** | Long-term design system; higher build cost |
| 3 | **V2 Brand Pack Drop** | Fastest ship; no compiler; upgrade path to V7 |
| 4 | **V4 Component library** | Great if you already accept a build step |
| 5 | **V5 README.tsx** | Power users / design-heavy orgs |
| 6 | **V11 AI-authored** | Killer feature *on top of* V7/V8, not alone |
| 7 | **V6 Asset CLI only** | Good module, incomplete product |
| 8 | **V12 CI brand** | Ops layer on V7 |
| 9 | **V3 YAML only** | Weaker without assets |
| 10 | **V1 Skeleton** | Table stakes, not differentiated |
| 11 | **V9 Profile** | Different market |
| 12 | **V10 Docs twin** | Later enterprise |

---

## 9. Mix-and-match “final product” recipes (for voting)

### Recipe α — **Ship this month**
- Core: **V2** brand packs  
- Add: **V6** commands for regenerate  
- Add: shields recipes (not full C1)  
→ Folder of assets + README skeleton. No compiler.

### Recipe β — **Default product (recommended spine)**
- Core: **V7** (YAML + theme + pack)  
- Add: **V12** optional CI build  
- Add: **V11** `readme-kit invent` later  
→ Compiler + packs + themes; components optional.

### Recipe γ — **Platform endgame**
- Core: **V8** components drive Markdown *and* SVG  
- Themes as packages (`@readme-kit/theme-linear`)  
- Asset pipeline + preview  
- Optional **V5** TSX for power users  
→ “shadcn + Framer for README.”

### Recipe δ — **Luffy-native**
- Start from **β**  
- First-class components: `<Architecture mermaid>`, `<TriggerBadge>`, `<HubMemory>`, `<TraceDownload>`  
- `npx create-readme --template ai-pr-agent` ships Luffy-shaped README + brand pack  
→ Vertical specialization beats horizontal generic tool *at first*.

---

## 10. Proposed open-source layout (platform-shaped)

Only build this if ranking picks β or γ:

```text
readme-kit/
  packages/
    core/           # compile pipeline (C4)
    tokens/         # design tokens (C3)
    components/     # Hero, FeatureGrid, ... (C2)
    themes/         # openai, linear, terminal, ... (C1)
    assets/         # generators (C5)
    packs/          # ai-agent, library, cli, ... (C6)
    cli/            # create / build / preview / generate
  examples/
    luffy/
    generic-lib/
```

User journey:

```bash
npx create-readme my-ai-agent --theme terminal --pack ai-agent
cd my-ai-agent
# edit readme.config.yaml or README.mdx
pnpm readme build      # → README.md + branding/
pnpm readme preview    # local HTML approx of GitHub
```

---

## 11. Decision log

| Decision | Options | Choice | Date |
|----------|---------|--------|------|
| MVP recipe | α / β / γ / δ | **δ** (β + Luffy vertical) | 2026-07-31 |
| Authoring format | YAML / MDX / TSX | **YAML** | 2026-07-31 |
| Asset strategy | hand SVG / generated / hybrid | **hybrid** (keep mark; generate hero/badge chrome) | 2026-07-31 |
| First vertical | generic / AI agents / profiles | **AI agents (`ai-agent` pack)** | 2026-07-31 |
| Relation to Luffy | separate OSS / monorepo / ignore | **monorepo path `readme-kit/`** | 2026-07-31 |
| Ship order | — | α mechanics → β compiler → γ components later | 2026-07-31 |
---

## 12. One-sentence thesis

> **README branding becomes an ecosystem when authoring is intent (theme, components, pack) and shipping is a compile step to GitHub’s fixed primitives—not when people paste better Markdown by hand.**

---

## Next step (for you)

Rank **Recipes α–δ** (and any variant V1–V12) by the rubric in §7.  
Then we lock a spine and mix features into **one** MVP spec (CLI surface, file formats, first pack: `ai-agent` / Luffy).
