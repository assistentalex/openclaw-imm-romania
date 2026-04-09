#!/bin/bash

# GitHub Releases Email Wrapper
# Thin wrapper that delegates release-check logic to the MSP GitHub checker.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMM_CLI="$PROJECT_DIR/scripts/imm-romania.py"
RECIPIENT="${MSP_GITHUB_RECIPIENT:-alex.bogdan@firmade.it}"
STATE_PATH="${MSP_GITHUB_STATE_PATH:-$PROJECT_DIR/data/msp-github-releases-state.json}"

DEFAULT_REPOS=(
  "ollama/ollama"
  "open-webui/open-webui"
  "vllm-project/vllm"
  "Mintplex-Labs/anything-llm"
  "Martian-Engineering/lossless-claw"
  "openclaw/openclaw"
)

REPO_ARGS=()
for repo in "${DEFAULT_REPOS[@]}"; do
  REPO_ARGS+=(--repo "$repo")
done

DIGEST_JSON=$(python3 "$IMM_CLI" msp github-check digest --check --state "$STATE_PATH" "${REPO_ARGS[@]}")
SUBJECT=$(printf '%s' "$DIGEST_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["subject"])')
BODY=$(printf '%s' "$DIGEST_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["body"])')

python3 "$IMM_CLI" mail send --to "$RECIPIENT" --subject "$SUBJECT" --body "$BODY"
