#!/usr/bin/env bash
# Check whether a GitHub author_association is allowed to trigger Luffy.
#
# Usage:
#   association-allowed.sh <ASSOCIATION> [ALLOWLIST]
# ALLOWLIST: comma-separated (default OWNER,MEMBER,COLLABORATOR,CONTRIBUTOR)
# Empty allowlist = allow all.
#
# Exit: 0 allowed, 1 denied
set -euo pipefail

assoc="$(printf '%s' "${1:-NONE}" | tr '[:lower:]' '[:upper:]' | tr -d ' ')"
# Explicit 2nd arg (even empty) overrides default; empty = allow all.
if [[ $# -ge 2 ]]; then
  allowed="$(printf '%s' "$2" | tr '[:lower:]' '[:upper:]' | tr -d ' ')"
else
  allowed="OWNER,MEMBER,COLLABORATOR,CONTRIBUTOR"
fi

if [[ -z "$allowed" ]]; then
  exit 0
fi

IFS=',' read -ra parts <<<"$allowed"
for a in "${parts[@]}"; do
  [[ -n "$a" && "$a" == "$assoc" ]] && exit 0
done
exit 1
