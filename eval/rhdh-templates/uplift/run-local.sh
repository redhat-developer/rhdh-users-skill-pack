#!/usr/bin/env bash
set -euo pipefail
readonly AEH_VERSION="v1.39.2"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
readonly MODEL="gpt-5.6-luna"
usage() { cat <<'EOF'
Usage: ./eval/rhdh-templates/uplift/run-local.sh [--runs COUNT]

Runs skill and baseline arms the same number of times (default: three),
retains local AEH results, and generates an observed-only comparison.
Set AEH_CHECKOUT to reuse an AEH checkout.
EOF
}
runs=3
if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then usage; exit 0; fi
if [[ ${1:-} == "--runs" && ${2:-} =~ ^[1-9][0-9]*$ ]]; then runs=$2; shift 2; fi
if [[ $# -ne 0 ]]; then usage >&2; exit 2; fi
if [[ -n ${AEH_CHECKOUT:-} ]]; then aeh_checkout=${AEH_CHECKOUT}; else aeh_checkout="/tmp/rhdh-agent-eval-harness-${AEH_VERSION}"; fi
if [[ ! -f "${aeh_checkout}/skills/eval-run/scripts/execute.py" ]]; then
  if [[ -e ${aeh_checkout} ]]; then echo "AEH_CHECKOUT is not usable: ${aeh_checkout}" >&2; exit 1; fi
  git clone --depth 1 --branch "${AEH_VERSION}" https://github.com/opendatahub-io/agent-eval-harness.git "${aeh_checkout}"
fi
cd "${REPO_ROOT}"
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/rhdh-aeh-uv-cache}"
export AGENT_EVAL_RUNS_DIR="${REPO_ROOT}/eval/runs/rhdh-templates-uplift"
for arm in skill baseline; do
  config="${SCRIPT_DIR}/${arm}.eval.yaml"
  for index in $(seq 1 "${runs}"); do
    run_id="uplift-${arm}-${index}"
    uv run --project "${aeh_checkout}" python "${SCRIPT_DIR}/run.py" --aeh-dir "${aeh_checkout}" --config "${config}" --model "${MODEL}" --run-id "${run_id}"
  done
done
comparison_dir="/tmp/rhdh-templates-uplift-comparison"
comparison_input="$(mktemp -d /tmp/rhdh-templates-uplift-runs.XXXXXX)"
for index in $(seq 1 "${runs}"); do
  cp -a "${AGENT_EVAL_RUNS_DIR}/rhdh-templates/uplift-skill-${index}" "${comparison_input}/"
  cp -a "${AGENT_EVAL_RUNS_DIR}/rhdh-templates-uplift-baseline/uplift-baseline-${index}" "${comparison_input}/"
done
uv run --project "${aeh_checkout}" python "${aeh_checkout}/skills/eval-compare/scripts/compare.py" generate "${comparison_input}" --output "${comparison_dir}" --title "rhdh-templates uplift" --overview "Observed comparison only; no generalization beyond this reviewed case set."
echo "Comparison: ${comparison_dir}"
