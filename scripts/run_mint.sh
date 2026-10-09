#!/usr/bin/env bash
set -euo pipefail

project="${MINT_PROJECT:-.}"
command="${MINT_COMMAND:-check}"
sarif="${MINT_SARIF_OUTPUT:-mint.sarif}"

if [[ "$command" != "check" && "$command" != "plan" ]]; then
  echo "set command to check or plan; refused ${command}" >&2
  exit 1
fi

if [[ ! -f "${project}/mint.toml" ]]; then
  echo "missing ${project}/mint.toml; set project to a Mint project directory" >&2
  exit 1
fi

args=("$command" --project "$project")
if [[ "$command" == "plan" ]]; then
  args+=(--locked)
fi

set +e
if mint check --help 2>&1 | grep -q -- "--sarif-output"; then
  mint "${args[@]}" --sarif-output "$sarif"
  code=$?
else
  stderr="$(mktemp)"
  mint "${args[@]}" 2>"$stderr"
  code=$?
  python3 "${GITHUB_ACTION_PATH}/scripts/sarif_from_mint.py" \
    --exit-code "$code" --stderr "$stderr" --output "$sarif"
  if [[ "$code" != "0" ]]; then
    cat "$stderr" >&2
  fi
  rm -f "$stderr"
fi
set -e
exit "$code"
