<!--
  Brand palette (from assets/luffy-mark.svg):
    ink #0B0F19 · flame #FF6B2C · crimson #C41E3A · gold #FFD166
-->

<p align="center">
  <img src="assets/luffy-mark.svg" alt="Luffy" width="140" />
</p>

<h1 align="center">Luffy</h1>

<p align="center">
  <strong>Comment-triggered PR review agent</strong><br />
  <sub>Hermes Agent · OpenRouter · growing hub memory · redacted run traces</sub>
</p>

<p align="center">
  <!-- Status -->
  <a href="https://github.com/archit15singh/luffy-pr-review-agent/actions/workflows/luffy-pr-review.yml">
    <img alt="PR Review workflow" src="https://img.shields.io/github/actions/workflow/status/archit15singh/luffy-pr-review-agent/luffy-pr-review.yml?branch=main&style=for-the-badge&label=PR%20Review&logo=githubactions&logoColor=white" />
  </a>
  <a href="https://github.com/archit15singh/luffy-pr-review-agent/actions/workflows/ingest-luffy-run.yml">
    <img alt="Hub ingest workflow" src="https://img.shields.io/github/actions/workflow/status/archit15singh/luffy-pr-review-agent/ingest-luffy-run.yml?branch=main&style=for-the-badge&label=Hub%20Ingest&logo=githubactions&logoColor=white" />
  </a>
  <br />
  <!-- Product facts -->
  <img alt="Trigger" src="https://img.shields.io/badge/%40luffy%20review%20this%20pr-trigger-FF6B2C?style=for-the-badge&logo=github&logoColor=white" />
  <img alt="Default model" src="https://img.shields.io/badge/model-openai%2Fgpt--5--mini-0B0F19?style=for-the-badge&logo=openai&logoColor=white" />
  <img alt="Provider" src="https://img.shields.io/badge/provider-OpenRouter-C41E3A?style=for-the-badge&logo=linktree&logoColor=white" />
  <br />
  <!-- Stack -->
  <a href="https://github.com/nousresearch/hermes-agent">
    <img alt="Hermes Agent" src="https://img.shields.io/badge/agent-Hermes-5865F2?style=for-the-badge&logo=robotframework&logoColor=white" />
  </a>
  <img alt="GitHub Actions" src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
  <img alt="Traces 90d" src="https://img.shields.io/badge/traces-90d%20artifacts-FFD166?style=for-the-badge&labelColor=0B0F19&logo=databricks&logoColor=FFD166" />
  <img alt="Memory hub" src="https://img.shields.io/badge/memory-central%20hub-FF6B2C?style=for-the-badge&labelColor=0B0F19&logo=memory&logoColor=white" />
  <br />
  <!-- Meta -->
  <a href="https://github.com/archit15singh/luffy-pr-review-agent/commits/main">
    <img alt="Last commit" src="https://img.shields.io/github/last-commit/archit15singh/luffy-pr-review-agent/main?style=for-the-badge&logo=git&logoColor=white&color=0B0F19" />
  </a>
  <img alt="Made with" src="https://img.shields.io/badge/made%20with-bash%20%2B%20python-C41E3A?style=for-the-badge&logo=gnubash&logoColor=white" />
  <img alt="License" src="https://img.shields.io/badge/license-MIT-FFD166?style=for-the-badge&labelColor=0B0F19&logo=open-source-initiative&logoColor=FFD166" />
</p>

---

## Why it exists

Most AI PR bots are **stateless chat on a diff**. Luffy is a **review control plane**:

1. Explicit human trigger (no spam on every push)  
2. Bounded context (sparse checkout + capped diff)  
3. One Hermes review via OpenRouter  
4. **Durable memory** on this hub so the next review on the same repo is smarter  
5. **Redacted traces** as Actions artifacts for audit  

One comment. One review. Memory that grows.

---

## Quick start

### 1. Trigger

On any PR in a repo where Luffy is installed:

```text
@luffy review this pr
```

Also accepted: `@luffy review`  
Or: **Actions → Luffy PR Review → Run workflow** (PR number).

### 2. Install on a target repo

| Step | Action |
|------|--------|
| 1 | Copy `agent/`, `scripts/`, `.github/workflows/luffy-pr-review.yml` to the **default branch** |
| 2 | Secret **`OPENROUTER_API_KEY`** |
| 3 | Secret **`LUFFY_HUB_TOKEN`** (PAT with write to this hub — for memory publish) |
| 4 | Optional vars: `LUFFY_MODEL`, `LUFFY_HUB_REPO`, `LUFFY_HUB_MODE` |

### 3. Local dry-run

```bash
# .env → OPENROUTER_API_KEY=…  (gitignored)
./scripts/review-local.sh owner/repo 123
POST_COMMENT=1 ./scripts/review-local.sh owner/repo 123
```

---

## How it works

```text
  @luffy review this pr
            │
            ▼
┌───────────────────────────┐
│  Target repo Actions      │
│  · sparse PR checkout     │
│  · preload hub MEMORY     │
│  · Hermes + OpenRouter    │
│  · normalize Markdown     │
│  · comment on PR          │
│  · upload trace artifact  │
└─────────────┬─────────────┘
              │ publish
              ▼
┌───────────────────────────┐
│  This hub                 │
│  memory/repos/{owner}--…  │
│  runs/{trace_id}/…        │
└───────────────────────────┘
```

<p align="center">
  <img alt="Stack" src="https://img.shields.io/badge/GitHub-Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white" />
  <img alt="arrow" src="https://img.shields.io/badge/→-0B0F19?style=flat-square&labelColor=0B0F19" />
  <img alt="Hermes" src="https://img.shields.io/badge/Hermes-Agent-5865F2?style=flat-square&logo=robotframework&logoColor=white" />
  <img alt="arrow" src="https://img.shields.io/badge/→-0B0F19?style=flat-square&labelColor=0B0F19" />
  <img alt="OpenRouter" src="https://img.shields.io/badge/OpenRouter-LLM-C41E3A?style=flat-square" />
  <img alt="arrow" src="https://img.shields.io/badge/→-0B0F19?style=flat-square&labelColor=0B0F19" />
  <img alt="PR comment" src="https://img.shields.io/badge/PR-comment-FF6B2C?style=flat-square&logo=git&logoColor=white" />
</p>

---

## Traces & memory

| Concern | Where | Badge |
|---------|--------|--------|
| **Per-run trace** | Actions artifact `luffy-trace-pr{N}-run{id}` (90d) | <img alt="90d" src="https://img.shields.io/badge/retention-90%20days-FFD166?style=flat-square&labelColor=0B0F19" /> |
| **Debug bundle** | `luffy-out-pr{N}-run{id}` (14d) | <img alt="14d" src="https://img.shields.io/badge/retention-14%20days-lightgrey?style=flat-square" /> |
| **Hub memory** | [`memory/repos/{owner}--{repo}/`](memory/repos/) | <img alt="hub" src="https://img.shields.io/badge/source%20of%20truth-git-FF6B2C?style=flat-square&labelColor=0B0F19" /> |

Trace layout:

```text
traces/pr{N}-run{id}-a{attempt}/
  meta.json   prompt.md   context.md   pr.diff
  review.raw.md   review.md   timings.json
  memory-after.md   hermes.stderr
```

```bash
gh run download <run-id> -R owner/repo -n luffy-trace-pr1-run<run-id>
```

Details: [memory/README.md](memory/README.md) · [docs/OPERATIONS.md](docs/OPERATIONS.md) · [docs/ROI-FIXES.md](docs/ROI-FIXES.md)

---

## Layout

```text
agent/           SOUL, prompts, Hermes config, memory seed
scripts/         assemble → hermes → normalize → distill → hub
memory/          central per-repo MEMORY (this hub)
assets/          mark · favicon · accents
docs/            architecture · operations · ROI fixes
.github/workflows/
  luffy-pr-review.yml    # review job (install on targets too)
  ingest-luffy-run.yml   # optional hub dispatch ingest
```

---

## Brand

<p align="center">
  <img src="assets/luffy-mark.png" width="96" alt="Luffy mark PNG" />
  &nbsp;&nbsp;
  <img src="assets/favicon.png" width="48" alt="Favicon" />
</p>

| Asset | Path | Notes |
|-------|------|--------|
| Mark (SVG) | [`assets/luffy-mark.svg`](assets/luffy-mark.svg) | Primary logo |
| Mark (PNG) | [`assets/luffy-mark.png`](assets/luffy-mark.png) | 512² |
| Favicon | [`assets/favicon.png`](assets/favicon.png) | 64² |
| Accents | [`assets/twemoji-*.png`](assets/) | [Twemoji](https://github.com/twitter/twemoji) CC-BY 4.0 |

Palette: **ink** `#0B0F19` · **flame** `#FF6B2C` · **crimson** `#C41E3A` · **gold** `#FFD166`

---

## Docs

| Doc | Purpose |
|-----|---------|
| [Architecture](docs/ARCHITECTURE.md) | Control plane design |
| [Operations](docs/OPERATIONS.md) | Secrets, failures, cost |
| [ROI fixes](docs/ROI-FIXES.md) | Ranked performance backlog |

---

## Limits (v1)

<img alt="v1" src="https://img.shields.io/badge/status-v1-0B0F19?style=flat-square&logo=semanticrelease&logoColor=FFD166" />
<img alt="comments only" src="https://img.shields.io/badge/reviews-PR%20comments-FF6B2C?style=flat-square" />
<img alt="paid model" src="https://img.shields.io/badge/OpenRouter-paid%20model-C41E3A?style=flat-square" />

- Full PR **comments** only (not inline review threads yet)  
- Diffs truncated at `MAX_DIFF_BYTES`  
- Default model is **paid** on OpenRouter (`openai/gpt-5-mini`) — not free  
- Hermes is installed on the runner (Docker pin later)  
- Install on each target repo; not a global bot for arbitrary public repos  

---

<p align="center">
  <img src="assets/twemoji-anchor.png" width="22" height="22" alt="" />
  &nbsp;<strong>Luffy</strong> · Hermes · OpenRouter · memory-backed review&nbsp;
  <img src="assets/twemoji-pirate-flag.png" width="22" height="22" alt="" />
</p>
