# E2E showcase — Luffy · Hermes · Claude Opus 5

**Issue:** [odoo/odoo#271153](https://github.com/odoo/odoo/issues/271153)  
**PR:** [archit15singh/odoo#3](https://github.com/archit15singh/odoo/pull/3)  
**Actions run:** [30574256524](https://github.com/archit15singh/odoo/actions/runs/30574256524)  
**Trace id:** `pr3-run30574256524-a1`  
**Model:** `anthropic/claude-opus-5` via OpenRouter · Hermes one-shot with tools  

## Headline numbers

| Metric | Value |
|--------|-------|
| Verdict | REQUEST CHANGES |
| Score | 42/100 |
| Review effort | 4/5 |
| Hermes wall time | 253s (hermes stage 251s) |
| API calls | 10 |
| Tokens (in / out / total) | 20 / 14601 / 195197 |
| Cache read / write | 156634 / 23942 |
| Reasoning tokens | 1585 |
| Est. cost USD | 0.5930795 |
| Session messages | 26 |
| Tool-call turns | 9 |
| Session id | `20260730_191954_63f003` |

## What is in this package

| Path | Description |
|------|-------------|
| `review.md` | Final PR comment (structured Luffy contract) |
| `review.raw.md` | Hermes stdout before normalize |
| `prompt.md` | Full assembled agent prompt |
| `context.md` | Untrusted PR context |
| `pr.diff` | Unified diff Hermes saw |
| `pr.json` / `files.txt` | PR metadata + file list |
| `timings.json` | Orchestrator stage durations |
| `meta.json` / `trace.json` | Trace identity + inventory hashes |
| `hermes-usage.json` | Tokens, cost, api_calls, session_id |
| `hermes-run.log` | Hermes file-log slice for this run |
| `agent-loop/agent-loop.md` | **Human walkthrough of every step** |
| `agent-loop/agent-loop.json` | Full messages + tool calls (redacted) |
| `agent-loop/usage.json` | Same usage snapshot |
| `agent-loop/agent.log` | Redacted Hermes agent.log excerpt |
| `memory-after.md` | Hub memory after distill |

## Agentic loop (summary)

Hermes ran a multi-turn tool loop (`api_calls=10`, `tool_call_turns=9`):

1. User prompt (assembled Luffy review contract + PR meta + workspace paths)
2. Repeated `terminal` tool calls to `cat` the diff, context, source files, and execute small Python repros
3. Final assistant message = structured Markdown review (REQUEST CHANGES on surrogatepass vs surrogateescape)

See the full step-by-step narrative in [`agent-loop/agent-loop.md`](agent-loop/agent-loop.md).

## Download live artifact

```bash
gh run download 30574256524 -R archit15singh/odoo -n luffy-trace-pr3-run30574256524
```
