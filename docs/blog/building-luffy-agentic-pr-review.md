# Building Luffy: a PR review agent you can audit

**Subtitle:** From one GitHub comment to a multi-turn Hermes loop, hub memory, and a full Opus 5 trace on a real Odoo bug.

---

Most AI PR bots do the same thing. They read a diff, emit soft prose, and vanish. No memory of the last review on that repo. No package you can open later and see *which tools the model ran*. No honest score when the code is wrong.

We built **Luffy** for the opposite job: a **comment-triggered review control plane**. You type `@luffy review this pr`. GitHub Actions runs Hermes Agent through OpenRouter. The agent can shell into the workspace, repro failures, and post a structured Markdown review. Then we store a redacted trace and grow hub memory so the next run on that repo is not starting from zero.

This post is how that system is put together, what broke on the way, and what a live run looked like when we pointed Claude Opus 5 at a real Odoo fix.

Proof, not vibe: [Actions run 30574256524](https://github.com/archit15singh/odoo/actions/runs/30574256524) on [archit15singh/odoo#3](https://github.com/archit15singh/odoo/pull/3). Model `anthropic/claude-opus-5`. **REQUEST CHANGES**, score **42/100**. Ten API calls, nine tool-call turns, twenty-six session messages, about four minutes of Hermes wall time, roughly **$0.59**. Full package: [`docs/showcase/e2e-odoo-pr3-opus5-agentic-loop/`](../showcase/e2e-odoo-pr3-opus5-agentic-loop/).

---

## The problem is systems, not “better prompts”

PR review fails for boring reasons.

Humans skip things when the monorepo is huge. Consistency drifts. Institutional knowledge lives in Slack threads that die.

Stateless LLM review fails for different boring reasons. It has no durable notes for *this* codebase. It often cannot prove a claim with a local repro. When the run ends, you get a comment blob and nothing you can replay.

On something Odoo-sized, “clone the world and chat” is also an economics problem. Full checkouts burn minutes before the model even starts.

So the design question is not “which model writes nicer English?” It is:

1. How do we **bound** context (sparse paths, capped diffs)?
2. How do we **structure** the answer so CI and humans can parse it?
3. How do we **keep** what we learned (memory)?
4. How do we **export the loop** (tools, prompts, steps) so we can improve the system?

Luffy is an answer to those four.

---

## What Luffy is (and is not)

**One line:** comment-triggered PR reviews via Hermes + OpenRouter, with a fixed review contract, hub memory, and redacted run traces.

**User path**

```text
@luffy review this pr
  → GitHub Actions
  → Hermes (tools + model)
  → PR comment + ✅/❌
  → artifact trace + hub memory update
```

**v1 is not**

- a global bot that reviews every public repo with no install
- free-model by default (Opus 5 costs real money)
- inline GitHub review threads yet
- a full open dump of Hermes internals beyond what we capture in session + logs

If you need a rubber stamp, use a cheaper model and a shorter prompt. Luffy’s showcase run failed the PR on purpose. That is the point.

---

## Principles we refused to drop

### Explicit trigger

No auto-review on every push. Cost and consent stay with the commenter. We also gate by GitHub `author_association` (default: owner / member / collaborator / contributor) so random drive-by comments do not burn OpenRouter credits.

### PR text is untrusted

Title, body, and diff can contain prompt-injection attempts. The SOUL and review prompt say so out loud. The model is a reviewer, not a servant of the PR description.

### Evidence over vibes

Findings need a path, a symbol, and a concrete trigger when they claim a bug. On the Opus run, the agent did not only *assert* a codec problem. It ran Python against the workspace until `UnicodeDecodeError` showed up.

### Structured contract

Free-form “LGTM” is useless in CI. We force (and repair) a shape: verdict, confidence, score, review effort, walkthrough, blocking, findings table, security audit, suggestions, optional code diffs, tests & risk, what was checked. A normalizer strips outer fences and caps size for GitHub comments.

### Durable state

After each run we:

- distill notes into local MEMORY
- publish a size-capped payload into the hub under `memory/repos/{owner}--{repo}/`
- preload that hub MEMORY on the next review for the same target

Without preload, “memory” is theater.

### Operability

Sparse checkout of changed paths. Hermes install cache. Replace prior Luffy comments instead of stacking noise. Always post a failure stub if the agent dies. Eyes reaction while running; ✅/❌ when done.

---

## Architecture (static)

Roughly four boxes:

```text
Developer ──comment──► Target repo (Actions + sparse PR head)
                              │
                              ▼
                     Luffy agent/ + scripts/
                     (SOUL, prompt, orchestrator)
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Hermes Agent    OpenRouter      Hub repo
         (tools/loop)    (Opus 5…)     memory/ + ingest
              │
              ▼
     PR comment + Actions artifacts (trace)
```

**Where truth lives**

| Thing | Where |
|-------|--------|
| Code under review | sparse PR workspace |
| Diff + assembled prompt | `.luffy-out/` |
| Persona + contract | `agent/SOUL.md`, `agent/review-prompt.md` |
| Growing notes | hub `memory/repos/…/MEMORY.md` |
| Audit package | Actions artifact + optional hub copy |

Hub publish defaults to **direct git push** into the hub. `GITHUB_TOKEN` cannot fire `repository_dispatch` the way people hope; we learned that the hard way (403) and stopped pretending.

---

## Runtime: outer loop vs inner loop

### Outer loop (shell, boring on purpose)

`scripts/run-luffy-review.sh` is the spine:

1. `preload_hub_memory` — pull hub MEMORY for this repo  
2. `assemble-context` — PR JSON, capped diff, prompt fill  
3. `run-hermes-review` — install/run Hermes, capture loop  
4. `normalize-review` — contract repair + HTML marker  
5. `distill-memory` — append structured notes  
6. `save-trace` — redacted package under `.luffy-out/traces/`  
7. `publish-run-to-hub` — grow central memory  

Boring is good. Deterministic stages give you timings, retries, and a place to hang artifacts even when the model fails.

### Inner loop (Hermes + tools)

For the Opus showcase we run roughly:

```bash
hermes -z "$PROMPT" \
  --provider openrouter \
  --model anthropic/claude-opus-5 \
  -t terminal \
  --usage-file hermes-usage.json
```

Then `capture-hermes-loop.py` reads:

- usage JSON (tokens, cost, `session_id`, `api_calls`)
- `state.db` messages (roles, tool_calls, tool results)
- sliced `logs/agent.log`

and writes `agent-loop/agent-loop.md` + `agent-loop.json` into the trace.

That is the part most “PR bots” skip. Without it you only ship the last message.

---

## How we actually built it

Short history, only the turns that mattered.

**Scaffold.** Agent folder (SOUL, prompt, Hermes config), Actions workflow on `issue_comment`, OpenRouter key, one-shot Hermes.

**Traces.** Every run packages prompt, diff, review raw/final, timings. Artifacts keep for 90 days on the trace bundle.

**Hub memory.** Target runs publish into `archit15singh/luffy-pr-review-agent` under `memory/repos/…`. Next review preloads that file.

**ROI fixes.** Monorepo pain forced F1–F6 (sparse + shallow, Hermes cache, preload, reactions). Later F11–F17: association allowlist, comment replace, sparse count bug, stable cache key, honest fail reaction, drop dead install copies.

**Review quality.** We tightened the contract after looking at how serious review products structure findings: score, effort, security line, findings table, optional code suggestion diffs. No third-party branding in the product. We kept the bar we wanted.

**Loop capture.** Opus e2e needed more than stdout. Usage file + session rows + log slice.

**readme-kit.** Themes + packs + YAML → GitHub-safe README and SVG banner. Private-repo shields cannot see Actions status APIs, so badges are static query badges that still link to the right pages.

**Brownfield e2e.** [odoo/odoo#271153](https://github.com/odoo/odoo/issues/271153): `remove_control_characters` encoded a Unicode class and matched it against UTF-8 *bytes*, so U+FFFE/U+FFFF survived into lxml. We fixed it on [archit15singh/odoo#3](https://github.com/archit15singh/odoo/pull/3), then let Luffy review that PR.

---

## Stack (and the tradeoffs)

| Layer | Choice | Why |
|-------|--------|-----|
| Trigger / CI | GitHub Actions | Native `issue_comment`, permissions, artifacts |
| Agent runtime | [Hermes Agent](https://github.com/NousResearch/hermes-agent) | One-shot CLI, tools, session store, logs under `HERMES_HOME` |
| Inference | OpenRouter | Swap models with one id string |
| Showcase model | `anthropic/claude-opus-5` | Quality for hard review; costs ~$0.6/run here |
| Glue | Bash + Python | Assemble, normalize, hub ingest, loop capture |
| Branding | Node `readme-kit` | Compile README from intent; no browser toolchain |

We did not start with a custom agent framework. Hermes already does install, tools, and session accounting. Our job was the **control plane around it**: gate, sparse context, contract, memory, export.

---

## Case study: Opus 5 on the Odoo XML fix

Numbers from the live package:

| Metric | Value |
|--------|-------|
| Run | [30574256524](https://github.com/archit15singh/odoo/actions/runs/30574256524) |
| Session | `20260730_191954_63f003` |
| Model | `anthropic/claude-opus-5` |
| Hermes stage | 251s (total orchestrator ~253s) |
| API calls | 10 |
| Tool-call turns | 9 |
| Messages | 26 |
| Tokens (reported total) | ~195k (heavy cache read) |
| Est. cost | ~$0.59 |
| Verdict | REQUEST CHANGES |
| Score | 42/100 |
| Effort | 4/5 |

What the agent did, condensed from the real steps:

1. Read `pr.diff` and assembled context  
2. Repro latin-1 `café` and open `xml_utils.py`  
3. Grep call sites for `remove_control_characters`  
4. Probe `cleanup_xml_node` and codec edge cases  
5. Compare `surrogatepass` vs what actually works on non-UTF-8 bytes  
6. Write a hard review: the `str` path was fine; the `bytes` path and a test claimed more than the codec delivers  

That is the product working. A soft APPROVE would have been a worse system outcome.

Trace entry points:

- [agent-loop.md](../showcase/e2e-odoo-pr3-opus5-agentic-loop/agent-loop/agent-loop.md) — human walkthrough  
- [agent-loop.json](../showcase/e2e-odoo-pr3-opus5-agentic-loop/agent-loop/agent-loop.json) — messages + tool args  
- [review.md](../showcase/e2e-odoo-pr3-opus5-agentic-loop/review.md) — posted comment  
- [hermes-usage.json](../showcase/e2e-odoo-pr3-opus5-agentic-loop/hermes-usage.json) — cost / tokens  

```bash
gh run download 30574256524 -R archit15singh/odoo -n luffy-trace-pr3-run30574256524
```

High-level mermaid for this run lives in the [repo README](../../README.md#e2e-showcase-live--opus-5-agentic-loop) and in [`e2e-agentic-trace.mmd`](../showcase/e2e-odoo-pr3-opus5-agentic-loop/e2e-agentic-trace.mmd).

---

## If you cannot export the loop, you cannot improve the agent

We treat each run as a small dataset:

| Artifact | Use |
|----------|-----|
| `prompt.md` | what the model was asked |
| `pr.diff` | what code it saw |
| `agent-loop/*` | tools, order, failures |
| `timings.json` | where minutes went |
| `hermes-usage.json` | money and token shape |
| hub MEMORY | what should stick for next time |

Secrets get redacted (`sk-or-…`, Bearer tokens). That is non-negotiable if traces live in a repo or long-lived artifacts.

Long term these packages are the start of an eval set: “did the agent catch the surrogateescape trap?” Regression tests for agents look like golden traces, not only unit tests on pure functions.

---

## Things that hurt (so you do not repeat them)

**Private repos break naive shields.io GitHub badges.** Status APIs return “repo not found”. We switched to static query badges that still deep-link to Actions.

**Sparse path counting.** `COUNT=$(grep -c . f || echo 0)` on an empty file becomes `0\n0` on some greps and forces a full monorepo clone. One character of shell, minutes of waste.

**Cache keys with `run_id` every save** thrash Actions cache. Stable key, save on miss.

**Missing OpenRouter key used to set `pipeline_rc=0`.** Users saw a green reaction on a config failure. Fixed: fail means fail.

**Memory written but never preloaded** is a blog post, not a feature. Preload first.

**Expensive models without tools** still guess. Tools closed the loop on Opus; the score dropped because the code earned it.

---

## What else this points at

Agentic CI is becoming a layer of the SDLC. Not chat in a sidebar. Jobs with permissions, artifacts, and budgets.

Review agents are also **org learning systems** if memory is real. The valuable output is not only the comment. It is the updated MEMORY and the trace you can re-read after the merge.

Open work we have not finished:

- pin Hermes install versions for bit-for-bit CI  
- Docker image with Hermes preinstalled  
- inline review comments  
- reusable `workflow_call` packaging for many target repos  
- tighter tool sandbox policy if you open this to less trusted contributors  

---

## Close

Luffy is a bet that PR review agents should look like **control planes**: explicit trigger, bounded context, structured output, durable memory, and an exportable agentic loop.

The Odoo run is the receipt. The model spent ten calls and about sixty cents, used the shell nine times, and refused to rubber-stamp a broken codec path.

If you want to poke it: install the workflow on a default branch, set `OPENROUTER_API_KEY`, comment `@luffy review this pr`, then download the trace and open `agent-loop/agent-loop.md`.

Hub: [archit15singh/luffy-pr-review-agent](https://github.com/archit15singh/luffy-pr-review-agent)

---

*Written for the Luffy repo. Numbers from trace `pr3-run30574256524-a1`. Prose edited against [NousResearch/autonovel ANTI-SLOP](https://github.com/NousResearch/autonovel/blob/master/ANTI-SLOP.md) patterns (banned filler, list abuse, hedge chains, “not just X but Y”).*
