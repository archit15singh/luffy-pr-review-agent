#!/usr/bin/env bash
# Pull central hub MEMORY.md for this repo into HERMES_HOME before review.
#
# Env:
#   REPO / GITHUB_REPOSITORY
#   HERMES_HOME
#   LUFFY_HUB_REPO (default archit15singh/luffy-pr-review-agent)
#   LUFFY_HUB_TOKEN / GH_TOKEN / GITHUB_TOKEN (optional; public read works too)
set -euo pipefail

log() { echo "$*" >&2; }
notice() { echo "::notice::$*" >&2; log "$*"; }

REPO="${REPO:-${GITHUB_REPOSITORY:-}}"
HERMES_HOME="${HERMES_HOME:-}"
HUB_REPO="${LUFFY_HUB_REPO:-archit15singh/luffy-pr-review-agent}"
TOKEN="${LUFFY_HUB_TOKEN:-${GH_TOKEN:-${GITHUB_TOKEN:-}}}"

if [[ -z "$REPO" || -z "$HERMES_HOME" ]]; then
  log "REPO/HERMES_HOME missing; skip hub memory preload"
  exit 0
fi

# owner/name -> owner--name
SLUG="$(printf '%s' "$REPO" | sed 's|/|--|g')"
MEM_PATH="memory/repos/${SLUG}/MEMORY.md"
mkdir -p "$HERMES_HOME/memories"

API="https://api.github.com/repos/${HUB_REPO}/contents/${MEM_PATH}"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
HDR=(-H "Accept: application/vnd.github.raw+json")
if [[ -n "$TOKEN" ]]; then
  HDR+=(-H "Authorization: Bearer ${TOKEN}")
fi

set +e
HTTP=$(curl -sS -L -o "$TMP" -w "%{http_code}" "${HDR[@]}" "$API")
set -e

if [[ "$HTTP" == "200" && -s "$TMP" ]]; then
  LOCAL="$HERMES_HOME/memories/MEMORY.md"
  ROOT="${LUFFY_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
  python3 "$ROOT/scripts/memory_snapshot.py" "$TMP" "$LOCAL" "${MAX_MEMORY_BYTES:-100000}"
  notice "Preloaded hub memory: ${HUB_REPO}/${MEM_PATH} ($(wc -c <"$LOCAL" | tr -d ' ') bytes)"
  echo "HUB_MEMORY=preloaded"
else
  log "No hub memory yet for ${SLUG} (HTTP ${HTTP}); using seed/local only"
  echo "HUB_MEMORY=missing"
fi
rm -f "$TMP"
