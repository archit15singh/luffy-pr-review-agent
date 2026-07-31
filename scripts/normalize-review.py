#!/usr/bin/env python3
"""Normalize Hermes output into a GitHub-safe Luffy review Markdown contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_CHARS = 60_000

# Core contract — keep in sync with agent/review-prompt.md
REQUIRED_SNIPPETS = (
    "**Verdict:**",
    "**Score:**",
    "### Summary",
    "### Blocking",
    "### Security audit",
    "### Tests & risk",
)

# Soft sections we try to ensure exist (repair path only)
SOFT_SECTIONS = (
    "### Walkthrough",
    "### Key findings",
    "### Suggestions",
    "### Code suggestions",
    "### Nits",
    "### What I checked",
)


def strip_outer_fence(text: str) -> str:
    t = text.strip()
    if not (t.startswith("```") and t.endswith("```")):
        return t
    lines = t.splitlines()
    if len(lines) < 2:
        return t
    body = "\n".join(lines[1:-1])
    first = body.lstrip().splitlines()[:1]
    if first and first[0].strip().lower() in {"markdown", "md"}:
        body = "\n".join(body.splitlines()[1:])
    return body.strip()


def ensure_contract(text: str, pr: str) -> str:
    t = text.strip()
    missing = [s for s in REQUIRED_SNIPPETS if s not in t]
    if not missing:
        body = t
        # Append missing soft headings only if completely absent (do not invent content)
        for sec in SOFT_SECTIONS:
            if sec not in body:
                # leave as-is; soft sections are guidance for the model, not hard repair
                pass
    else:
        body = f"""## 🏴‍☠️ Luffy Review — PR #{pr}

**Verdict:** COMMENT
**Confidence:** low
**Score:** 40/100
**Review effort:** 2/5

### Summary
Agent output did not match the review contract (missing: {', '.join(missing)}). Raw content preserved below.

### Walkthrough
- Contract repair only — re-run for a full structured review

### Blocking
- None (contract repair — re-run if this looks incomplete)

### Key findings
None — normalizer fallback.

### Security audit
No

### Suggestions
- None

### Code suggestions
None

### Nits
- None

### Tests & risk
- Relevant tests added/updated: unknown
- Coverage: unknown
- Risk: unknown
- Rollback: n/a

### What I checked
- Normalizer only

### Raw agent output
{t}
"""

    marker = f"<!-- luffy-review pr={pr}"
    if marker not in body:
        body = f"<!-- luffy-review pr={pr} -->\n{body}"

    if "Luffy · Hermes Agent" not in body:
        body = body.rstrip() + "\n\n---\n*Luffy · Hermes Agent · OpenRouter · memory-backed review*\n"

    if len(body) > MAX_CHARS:
        body = (
            body[: MAX_CHARS - 200].rstrip()
            + "\n\n…\n\n_(truncated to fit GitHub comment size limit)_\n"
        )
    return body.rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", "-i", required=True, type=Path)
    p.add_argument("--output", "-o", required=True, type=Path)
    p.add_argument("--pr", required=True)
    p.add_argument("--run-id", default="local")
    args = p.parse_args(argv)

    raw = args.input.read_text(errors="replace")
    cleaned = strip_outer_fence(raw)
    final = ensure_contract(cleaned, str(args.pr))
    final = final.replace(
        f"<!-- luffy-review pr={args.pr} -->",
        f"<!-- luffy-review pr={args.pr} run={args.run_id} -->",
        1,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(final)
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
