#!/usr/bin/env bash
set -euo pipefail

readonly AEH_VERSION="v1.39.2"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
readonly CONFIG="${SCRIPT_DIR}/eval.yaml"
readonly MODEL="gpt-5.6-luna"

usage() {
  cat <<'EOF'
Usage: ./eval/rhdh-templates/routing/run-local.sh [--runs COUNT]

Runs the reviewed routing matrix through Agent Eval Harness with the pinned
reference model. The default three runs report activation precision, recall,
variance, and named false positives and false negatives.

Set AEH_CHECKOUT to an existing Agent Eval Harness checkout to avoid cloning it
into /tmp on the first run. Run artifacts are local under eval/runs/.
EOF
}

runs=3
if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  usage
  exit 0
fi
if [[ ${1:-} == "--runs" && ${2:-} =~ ^[1-9][0-9]*$ ]]; then
  runs=$2
  shift 2
fi
if [[ $# -ne 0 ]]; then
  usage >&2
  exit 2
fi

if [[ -n ${AEH_CHECKOUT:-} ]]; then
  aeh_checkout=${AEH_CHECKOUT}
else
  aeh_checkout="/tmp/rhdh-agent-eval-harness-${AEH_VERSION}"
fi
if [[ ! -f "${aeh_checkout}/skills/eval-run/scripts/execute.py" ]]; then
  if [[ -e ${aeh_checkout} ]]; then
    echo "AEH_CHECKOUT is not a usable AEH checkout: ${aeh_checkout}" >&2
    exit 1
  fi
  git clone --depth 1 --branch "${AEH_VERSION}" https://github.com/opendatahub-io/agent-eval-harness.git "${aeh_checkout}"
fi

cd "${REPO_ROOT}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/rhdh-aeh-uv-cache}"
summaries=()
prefix="routing-$(date -u +%Y%m%dT%H%M%SZ)"
for index in $(seq 1 "${runs}"); do
  run_id="${prefix}-${index}"
  uv run --project "${aeh_checkout}" python "${SCRIPT_DIR}/run.py" \
    --aeh-dir "${aeh_checkout}" --config "${CONFIG}" --model "${MODEL}" --run-id "${run_id}"
  summaries+=("eval/runs/rhdh-templates-routing/${run_id}/summary.yaml")
done
python "${SCRIPT_DIR}/summarize.py" --summaries "${summaries[@]}" --cases-dir "${SCRIPT_DIR}/cases"
