#!/usr/bin/env bash
# Run Hermes one-shot review with detailed agent-loop capture.
#
# Env:
#   OPENROUTER_API_KEY
#   LUFFY_ROOT, HERMES_HOME, WORKSPACE_ROOT
#   OUT_DIR, PROMPT_PATH (or meta.env)
#   LUFFY_MODEL / OPENROUTER_MODEL  (default: anthropic/claude-opus-5)
#   LUFFY_TOOLSETS  (optional hermes -t value; default: terminal for workspace tools)
#   PR_NUMBER
set -euo pipefail

log() { echo "$*" >&2; }
notice() { echo "::notice::$*" >&2; log "$*"; }
die() { echo "::error::$*" >&2; exit 1; }

: "${OPENROUTER_API_KEY:?OPENROUTER_API_KEY is required}"

LUFFY_ROOT="${LUFFY_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
OUT_DIR="${OUT_DIR:-$LUFFY_ROOT/.luffy-out}"
HERMES_HOME="${HERMES_HOME:-$LUFFY_ROOT/.luffy-hermes-home}"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$LUFFY_ROOT}"
MODEL="${LUFFY_MODEL:-${OPENROUTER_MODEL:-anthropic/claude-opus-5}}"
TOOLSETS="${LUFFY_TOOLSETS:-terminal}"

mkdir -p "$OUT_DIR" "$HERMES_HOME/memories" "$HERMES_HOME/logs"

if [[ -f "$OUT_DIR/meta.env" ]]; then
  # shellcheck disable=SC1091
  source "$OUT_DIR/meta.env"
fi

PROMPT_PATH="${PROMPT_PATH:-$OUT_DIR/prompt.md}"
PR_NUMBER="${PR_NUMBER:-unknown}"
[[ -f "$PROMPT_PATH" ]] || die "Missing prompt: $PROMPT_PATH"

export HERMES_HOME
export OPENROUTER_API_KEY
export PATH="${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"
# Encourage verbose file logging for agent/tool activity
export HERMES_TUI_TOOL_PROGRESS="${HERMES_TUI_TOOL_PROGRESS:-verbose}"
export PYTHONUNBUFFERED=1

# ---------------------------------------------------------------------------
# Ensure Hermes (install path is cached by the workflow when possible)
# ---------------------------------------------------------------------------
ensure_hermes() {
  export PATH="${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"
  if command -v hermes >/dev/null 2>&1; then
    notice "hermes (cached/present): $(command -v hermes)"
    hermes --version 2>/dev/null || true
    return
  fi
  notice "Installing Hermes Agent (cold)..."
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
  export PATH="${HOME}/.local/bin:${HOME}/.hermes/bin:${PATH}"
  # shellcheck disable=SC1091
  [[ -f "${HOME}/.bashrc" ]] && source "${HOME}/.bashrc" || true
  hash -r 2>/dev/null || true
  for candidate in \
    "${HOME}/.local/bin/hermes" \
    "${HOME}/.hermes/bin/hermes" \
    "${HOME}/.hermes/hermes"; do
    if [[ -x "$candidate" ]]; then
      export PATH="$(dirname "$candidate"):${PATH}"
      break
    fi
  done
  command -v hermes >/dev/null 2>&1 || die "hermes not found after install"
  notice "hermes installed: $(command -v hermes)"
}

ensure_hermes

# ---------------------------------------------------------------------------
# Seed HERMES_HOME (preserve growing MEMORY.md)
# ---------------------------------------------------------------------------
cp -f "$LUFFY_ROOT/agent/config.yaml" "$HERMES_HOME/config.yaml"
cp -f "$LUFFY_ROOT/agent/SOUL.md" "$HERMES_HOME/SOUL.md"
umask 077
cat >"$HERMES_HOME/.env" <<EOF
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
EOF

if [[ ! -f "$HERMES_HOME/memories/MEMORY.md" ]]; then
  if [[ -f "$LUFFY_ROOT/agent/MEMORY.seed.md" ]]; then
    cp -f "$LUFFY_ROOT/agent/MEMORY.seed.md" "$HERMES_HOME/memories/MEMORY.md"
  else
    printf '# Luffy review memory\n\n' >"$HERMES_HOME/memories/MEMORY.md"
  fi
fi

PROMPT="$(cat "$PROMPT_PATH")"
RAW_OUT="$OUT_DIR/review-${PR_NUMBER}.raw.md"
STDERR_FILE="$OUT_DIR/hermes-${PR_NUMBER}.stderr"
FINAL_OUT="$OUT_DIR/review-${PR_NUMBER}.md"
USAGE_FILE="$OUT_DIR/hermes-usage.json"
LOOP_DIR="$OUT_DIR/agent-loop"
# Snapshot log position for this run only
LOG_FILE="$HERMES_HOME/logs/agent.log"
LOG_OFFSET=0
if [[ -f "$LOG_FILE" ]]; then
  LOG_OFFSET=$(wc -c <"$LOG_FILE" | tr -d ' ')
fi
echo "$LOG_OFFSET" >"$OUT_DIR/hermes-log-offset.txt"

notice "Hermes review · model=$MODEL toolsets=$TOOLSETS workspace=$WORKSPACE_ROOT hermes_home=$HERMES_HOME"

set +e
(
  cd "$WORKSPACE_ROOT"
  # --usage-file: tokens/cost/session_id for the agentic loop package
  # -t toolsets: allow terminal/file tools so the loop can inspect the workspace
  hermes -z "$PROMPT" \
    --provider openrouter \
    --model "$MODEL" \
    -t "$TOOLSETS" \
    --usage-file "$USAGE_FILE" \
    >"$RAW_OUT" 2>"$STDERR_FILE"
)
RC=$?
if [[ $RC -ne 0 || ! -s "$RAW_OUT" ]]; then
  notice "hermes -z failed or empty (rc=$RC); trying hermes chat -q"
  (
    cd "$WORKSPACE_ROOT"
    hermes chat -q "$PROMPT" \
      --provider openrouter \
      --model "$MODEL" \
      >"$RAW_OUT" 2>>"$STDERR_FILE"
  )
  RC=$?
fi
set -e

if [[ $RC -ne 0 ]]; then
  notice "hermes exit=$RC"
  [[ -s "$STDERR_FILE" ]] && tail -c 8000 "$STDERR_FILE" >&2 || true
fi

# Slice of agent.log written during this invocation
if [[ -f "$LOG_FILE" ]]; then
  python3 - <<'PY' "$LOG_FILE" "$OUT_DIR/hermes-run.log" "$LOG_OFFSET"
import sys
from pathlib import Path
src, dest, off = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3] or 0)
data = src.read_bytes()
chunk = data[off:] if off < len(data) else data[-200_000:]
dest.write_bytes(chunk)
print(f"hermes-run.log bytes={len(chunk)}", file=sys.stderr)
PY
fi

# Detailed agentic-loop package (messages, tool calls, usage, logs)
export HERMES_HOME OUT_DIR LUFFY_MODEL="$MODEL" OPENROUTER_MODEL="$MODEL"
export HERMES_USAGE_FILE="$USAGE_FILE"
export AGENT_LOOP_DIR="$LOOP_DIR"
export LUFFY_PROVIDER=openrouter
chmod +x "$LUFFY_ROOT/scripts/capture-hermes-loop.py" 2>/dev/null || true
python3 "$LUFFY_ROOT/scripts/capture-hermes-loop.py" || notice "capture-hermes-loop soft-failed"

if [[ ! -s "$RAW_OUT" ]]; then
  cat >"$RAW_OUT" <<EOF
## 🏴‍☠️ Luffy Review — PR #${PR_NUMBER}

**Verdict:** COMMENT
**Confidence:** low
**Score:** 20/100
**Review effort:** 1/5

### Summary
Luffy failed to produce a review (hermes exit ${RC}). Check workflow logs, Hermes install, and OpenRouter credits/key.

### Walkthrough
- Agent runner failure only

### Blocking
- Review agent run failed — re-trigger with \`@luffy review this pr\` after fixing CI/OpenRouter.

### Key findings
None — runner failure.

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
- Agent runner only (no successful model response)

---
*Luffy · Hermes Agent · OpenRouter · memory-backed review*
EOF
fi

# Normalize into final review.md
python3 "$LUFFY_ROOT/scripts/normalize-review.py" \
  --input "$RAW_OUT" \
  --output "$FINAL_OUT" \
  --pr "$PR_NUMBER" \
  --run-id "${GITHUB_RUN_ID:-local}"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "review_file=$FINAL_OUT"
    echo "raw_file=$RAW_OUT"
    echo "hermes_rc=$RC"
    echo "agent_loop_dir=$LOOP_DIR"
    echo "usage_file=$USAGE_FILE"
  } >>"$GITHUB_OUTPUT"
fi

echo "REVIEW_FILE=$FINAL_OUT"
echo "AGENT_LOOP_DIR=$LOOP_DIR"
notice "Review written: $FINAL_OUT ($(wc -c <"$FINAL_OUT" | tr -d ' ') bytes)"
if [[ -f "$LOOP_DIR/agent-loop.json" ]]; then
  notice "Agent loop captured: $LOOP_DIR"
fi
