#!/usr/bin/env bash
# Polish hill-climb helper. Run from anywhere inside the repository.
#
#   hc.sh status                              where the session stands and what to do next
#   hc.sh baseline                            render + audit the unchanged tree (log it with: hc.sh log keep "baseline")
#   hc.sh experiment "<what>" <paths...>      render + audit, then commit <paths> and docs/ as "experiment: <what>"
#   hc.sh checks                              correctness checks (Lua, Node, pytest + Chromium); must pass to keep
#   hc.sh log <status> "<what>" ['<asi>']     append the run in run.log to autoresearch.jsonl
#   hc.sh discard                             revert the last experiment commit (log it as discard first)
#   hc.sh findings [file]                     list every scored finding on the current docs/ (no render)
#   hc.sh shot <page> <width> <light|dark> <name> [--at selector] [--text words] [--height px] [--full]
#   hc.sh segment "<name>"                    start a new segment after changing the audit
#   hc.sh snapshot                            copy the living session files into .autoresearch/ to commit
#   hc.sh restore                             copy .autoresearch/ back to the living files (fresh clone)
#
# Optional environment: QUARTO, PLAYWRIGHT_BROWSERS_PATH, HILLCLIMB_COMMIT_BODY (extra commit message
# paragraph, e.g. attribution trailers).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
HERE="scripts/hillclimb"
SNAP=.autoresearch

metrics() {
  grep '^METRIC ' run.log | tr '\n' ' '; echo
  python3 - <<'PY'
import json
details = json.load(open("audit.details.json"))["details"]
print("non-zero:", {k: v for k, v in details.items() if v} or "none")
PY
}

# Quarto rewrites every <lastmod> on each render. Keep docs/sitemap.xml unless its pages changed.
settle_sitemap() {
  if [ "$(git show HEAD:docs/sitemap.xml 2>/dev/null | grep -o '<loc>[^<]*' | sort)" = \
       "$(grep -o '<loc>[^<]*' docs/sitemap.xml | sort)" ]; then
    git checkout -- docs/sitemap.xml
  fi
}

bench() { bash autoresearch.sh > run.log 2>&1 || { tail -40 run.log; echo "BENCHMARK FAILED (see run.log)"; exit 1; }; }

case "${1:-}" in
  status) python3 "$HERE/ledger.py" status ;;
  baseline) bench; settle_sitemap; metrics ;;
  experiment)
    [ $# -ge 3 ] || { echo 'usage: hc.sh experiment "<what>" <source paths...>'; exit 2; }
    what=$2; shift 2
    bench; settle_sitemap
    git add -- "$@" docs
    if [ -n "${HILLCLIMB_COMMIT_BODY:-}" ]; then
      git commit -q -m "experiment: $what" -m "$HILLCLIMB_COMMIT_BODY"
    else
      git commit -q -m "experiment: $what"
    fi
    git log --oneline -1
    metrics ;;
  checks)
    bash autoresearch.checks.sh > checks.log 2>&1 && { tail -2 checks.log; } || {
      grep -E "FAILED|Error|assert" checks.log | head -20; tail -3 checks.log; echo "CHECKS FAILED (see checks.log)"; exit 1; }
    settle_sitemap ;;
  log) shift; python3 "$HERE/ledger.py" log "$@" ;;
  discard)
    git checkout -- docs 2>/dev/null || true
    git revert --no-edit HEAD >/dev/null
    git log --oneline -1 ;;
  findings)
    out=${2:-findings.tsv}
    AXE="$ROOT/.autoresearch-tools/node_modules/axe-core/axe.min.js"
    [ -f "$AXE" ] || npm install --silent --prefix .autoresearch-tools axe-core@4.10.2 >/dev/null
    AXE_PATH="$AXE" AUDIT_LIST="$out" node autoresearch.audit.cjs 2>/dev/null | grep '^METRIC polish'
    cut -f4 "$out" | sort | uniq -c | sort -rn
    echo "every finding (width, theme, page, kind, where): $out" ;;
  shot) shift; node "$HERE/shot.cjs" "$@" ;;
  segment) python3 "$HERE/ledger.py" segment "$2" ;;
  snapshot)
    mkdir -p "$SNAP"
    for pair in autoresearch.md:session-notes.md autoresearch.ideas.md:ideas-backlog.md autoresearch.jsonl:session-log.jsonl; do
      [ -f "${pair%%:*}" ] && cp "${pair%%:*}" "$SNAP/${pair##*:}"
    done
    ls "$SNAP" ;;
  restore)
    for pair in autoresearch.md:session-notes.md autoresearch.ideas.md:ideas-backlog.md autoresearch.jsonl:session-log.jsonl; do
      if [ -f "$SNAP/${pair##*:}" ] && [ ! -f "${pair%%:*}" ]; then cp "$SNAP/${pair##*:}" "${pair%%:*}"; echo "restored ${pair%%:*}"; fi
    done ;;
  *) sed -n '2,19p' "$0"; exit 2 ;;
esac
