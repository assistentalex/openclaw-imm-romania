#!/bin/bash

# GitHub Releases Email Wrapper
# Thin wrapper that delegates release-check logic to the MSP GitHub checker.
# Config-first behavior:
# - use MSP_GITHUB_REPOS env override when present
# - otherwise use repo config file when present
# - otherwise exit cleanly without sending mail

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMM_CLI="$PROJECT_DIR/scripts/imm-romania.py"
CONFIG_PATH="${MSP_GITHUB_CONFIG_PATH:-$PROJECT_DIR/data/msp-github-repos.json}"
STATE_PATH="${MSP_GITHUB_STATE_PATH:-$PROJECT_DIR/data/msp-github-releases-state.json}"

REPO_ARGS=()
CONFIG_ARGS=(--state "$STATE_PATH")

if [[ -n "${MSP_GITHUB_REPOS:-}" ]]; then
  IFS=',' read -r -a REPOS <<< "$MSP_GITHUB_REPOS"
  for repo in "${REPOS[@]}"; do
    repo="$(printf '%s' "$repo" | xargs)"
    [[ -n "$repo" ]] && REPO_ARGS+=(--repo "$repo")
  done
elif [[ -f "$CONFIG_PATH" ]]; then
  CONFIG_ARGS+=(--config "$CONFIG_PATH")
else
  echo "No GitHub checker config found; exiting cleanly."
  exit 0
fi

RECIPIENT="${MSP_GITHUB_RECIPIENT:-}"
if [[ -z "$RECIPIENT" && -f "$CONFIG_PATH" ]]; then
  RECIPIENT=$(python3 - <<'PY' "$CONFIG_PATH"
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    raw = json.loads(path.read_text(encoding='utf-8'))
    print(raw.get('recipient', ''))
except Exception:
    print('')
PY
)
fi

if [[ -z "$RECIPIENT" ]]; then
  echo "No GitHub checker recipient configured; exiting cleanly."
  exit 0
fi

DIGEST_JSON=$(python3 "$IMM_CLI" msp github-check digest --check "${CONFIG_ARGS[@]}" "${REPO_ARGS[@]}")
SUBJECT=$(printf '%s' "$DIGEST_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["subject"])')
BODY=$(printf '%s' "$DIGEST_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["body"])')
# Render HTML from digest via in-repo renderer
HTML=$(printf '%s' "$DIGEST_JSON" | python3 "$PROJECT_DIR/modules/msp/render_digest.py")
ENABLED=$(printf '%s' "$DIGEST_JSON" | python3 -c 'import json,sys; data=json.load(sys.stdin); print("yes" if data.get("results") or data.get("has_updates") or "No GitHub repositories are configured" not in data.get("body", "") else "no")')

if [[ "$ENABLED" != "yes" ]]; then
  echo "GitHub checker not enabled; exiting cleanly."
  exit 0
fi

# Prefer HTML if renderer produced content
if [[ -n "$HTML" && "$HTML" != "<p>Invalid digest</p>" ]]; then
  python3 "$IMM_CLI" mail send --to "$RECIPIENT" --subject "$SUBJECT" --html "$HTML"
else
  python3 "$IMM_CLI" mail send --to "$RECIPIENT" --subject "$SUBJECT" --body "$BODY"
fi
