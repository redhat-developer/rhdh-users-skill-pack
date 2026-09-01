#!/usr/bin/env bash
set -euo pipefail

readonly AEH_VERSION="v1.39.2"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

usage() {
  cat <<'EOF'
Usage: ./eval/rhdh-templates/run-local.sh behavior-local [agent-eval options]

Suites:
  behavior-local   Validate an already-valid template without modifying it

The runner uses Agent Eval Harness v1.39.2 and gpt-5.6-luna by default. Set
AEH_CHECKOUT to an existing checkout to avoid the first-run clone into /tmp.
Set AEH_CODEX_HOME to use a specific writable Codex configuration directory
for evaluated agents.
EOF
}

if [[ ${1:-} == "--help" || ${1:-} == "-h" ]]; then
  usage
  exit 0
fi

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 2
fi

suite=$1
shift

case "${suite}" in
  behavior-local)
    ;;
  *)
    echo "Unknown suite: ${suite}" >&2
    usage >&2
    exit 2
    ;;
esac

cd "${REPO_ROOT}"

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/rhdh-aeh-uv-cache}"

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
  echo "Cloning Agent Eval Harness ${AEH_VERSION} into ${aeh_checkout}" >&2
  git clone --depth 1 --branch "${AEH_VERSION}" \
    https://github.com/opendatahub-io/agent-eval-harness.git "${aeh_checkout}"
fi

runtime_codex_home=""
cleanup_codex_home() {
  if [[ ${runtime_codex_home} == /tmp/rhdh-aeh-codex-home.* ]]; then
    rm -rf -- "${runtime_codex_home}"
  fi
}

if [[ -n ${AEH_CODEX_HOME:-} ]]; then
  if [[ ! -d ${AEH_CODEX_HOME} ]]; then
    echo "AEH_CODEX_HOME is not a directory: ${AEH_CODEX_HOME}" >&2
    exit 1
  fi
  export CODEX_HOME="${AEH_CODEX_HOME}"
else
  source_codex_home=${CODEX_HOME:-}
  if [[ -z ${source_codex_home} && -n ${HOME:-} ]]; then
    source_codex_home="${HOME}/.codex"
  fi
  runtime_codex_home=$(mktemp -d /tmp/rhdh-aeh-codex-home.XXXXXX)
  chmod 700 "${runtime_codex_home}"
  for filename in auth.json config.toml installation_id; do
    if [[ -n ${source_codex_home} && -f ${source_codex_home}/${filename} ]]; then
      cp -p -- "${source_codex_home}/${filename}" "${runtime_codex_home}/${filename}"
    fi
  done
  export CODEX_HOME="${runtime_codex_home}"
  trap cleanup_codex_home EXIT
fi

uv run --project "${aeh_checkout}" python "${SCRIPT_DIR}/run_suite.py" \
  --aeh-dir "${aeh_checkout}" "$@"
