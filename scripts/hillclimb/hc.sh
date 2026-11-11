#!/usr/bin/env bash
# Polish hill-climb helper. Run from anywhere inside the repository. Full procedure:
# .claude/skills/portfolio-hillclimb/SKILL.md
#
#   hc.sh doctor                              check every tool the loop needs, and say how to get what is missing
#   hc.sh status                              where the session stands and what to do next
#   hc.sh baseline                            render + audit the unchanged tree (then: hc.sh checks; hc.sh log keep "baseline")
#   hc.sh experiment "<what>" <paths...>      render + audit, then commit <paths> and docs/ as "experiment: <what>"
#   hc.sh shot <page> <width> <light|dark> <name> [--at css] [--text words] [--height px] [--full]
#                                             screenshot; name it run-<N>-... so evidence picks it up
#   hc.sh checks                              correctness gate; on success stamps the commit in checks.ok
#   hc.sh evidence ["<visual review notes>"]  write .hillclimb-evidence/run-<N>.md for the current experiment
#   hc.sh log <status> "<what>" ['<asi>']     append the run to autoresearch.jsonl (keep is refused without evidence)
#   hc.sh discard                             revert the last experiment commit (log it first)
#   hc.sh findings [file]                     list every scored finding on the current docs/ (no render)
#   hc.sh segment "<name>"                    start a new segment after changing the audit
#   hc.sh snapshot                            copy session files and evidence records into .autoresearch/ to commit
#   hc.sh restore                             copy .autoresearch/ back to the living files (fresh clone)
#
# Environment: QUARTO (path to quarto), PLAYWRIGHT_BROWSERS_PATH (preinstalled browsers).
# Commit messages are plain: no session links, co-author trailers or tool footers (the script refuses them).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
HERE="scripts/hillclimb"
SNAP=.autoresearch
EVID=.hillclimb-evidence
SHOTS=.hillclimb-shots
QUARTO_BIN="${QUARTO:-$(command -v quarto || echo /opt/quarto/quarto-1.10.19/bin/quarto)}"
# Use the same explicit override or Playwright default cache as setup-agent.sh.

ledger() { python3 "$HERE/ledger.py" "$@"; }

metrics() {
  grep '^METRIC ' run.log | tr '\n' ' '; echo
  python3 -c 'import json;d=json.load(open("audit.details.json"))["details"];print("non-zero:",{k:v for k,v in d.items() if v} or "none")'
}

# Quarto rewrites every <lastmod> on each render. Keep docs/sitemap.xml unless its pages changed.
settle_sitemap() {
  if [ "$(git show HEAD:docs/sitemap.xml 2>/dev/null | grep -o '<loc>[^<]*' | sort)" = \
       "$(grep -o '<loc>[^<]*' docs/sitemap.xml | sort)" ]; then
    git checkout -- docs/sitemap.xml
  fi
}

# Every benchmark also lists its findings, so each experiment can be compared with the best kept state.
bench() {
  AUDIT_LIST="$ROOT/findings.tsv" bash autoresearch.sh > run.log 2>&1 || {
    tail -40 run.log; echo "BENCHMARK FAILED (see run.log)"; exit 1; }
}

head_short() { git rev-parse --short=7 HEAD; }

# Session links and tool footers must never reach commits, PRs or issues.
no_links() {
  if printf '%s' "$*" | grep -qiE 'claude\.ai/code|session_[0-9a-z]{6,}|Claude-Session:|Co-Authored-By: *Claude|Generated with \[?Claude'; then
    echo "REFUSED: text contains a session link, co-author trailer or tool footer. Remove it."; exit 1
  fi
}

case "${1:-}" in
  doctor)
    ok=1
    check() { if eval "$2" >/dev/null 2>&1; then echo "ok    $1"; else echo "MISSING $1 -> $3"; ok=0; fi; }
    check "git" "command -v git" "install git"
    pinned_quarto() { [ "$("$QUARTO_BIN" --version)" = "1.10.19" ]; }
    check "quarto 1.10.19 ($QUARTO_BIN)" "pinned_quarto" "run bash scripts/setup-agent.sh or set QUARTO to Quarto 1.10.19"
    check "pandoc lua (bundled with Quarto)" "ls '$(dirname "$(readlink -f "$QUARTO_BIN" 2>/dev/null || echo "$QUARTO_BIN")")'/tools/*/pandoc || command -v lua" "comes with Quarto; or install lua 5.4"
    check "node 18+" "node -e 'process.exit(+process.versions.node.split(\".\")[0] >= 18 ? 0 : 1)'" "install Node.js 18 or newer"
    check "npm (axe-core install)" "command -v npm" "comes with Node.js"
    check "python3" "command -v python3" "install Python 3.10+"
    check ".venv with pytest + playwright + pypdf" ".venv/bin/python -c 'import pytest, playwright, pypdf'" "python3 -m venv .venv && .venv/bin/pip install -r requirements-test.txt (see .github/BUILDING.md)"
    check "node playwright" "node -e 'require(\"playwright\")'" "npm install --no-save playwright (match the Python playwright version)"
    for engine in chromium firefox webkit; do
      check "node $engine" "node -e 'require(\"playwright\").$engine.launch().then(b=>b.close())'" "npx playwright install $engine, or set PLAYWRIGHT_BROWSERS_PATH to preinstalled browsers"
    done
    matching_playwright() {
      local node_version python_version
      node_version="$(node -p 'require("playwright/package.json").version')" || return 1
      python_version="$(.venv/bin/python -c 'from importlib.metadata import version; print(version("playwright"))')" || return 1
      [ "$node_version" = "$python_version" ]
    }
    check "matching Python/Node Playwright versions" "matching_playwright" "run bash scripts/setup-agent.sh"
    for engine in chromium firefox webkit; do
      check "Python $engine" ".venv/bin/python -c 'from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.$engine.launch(); b.close(); p.stop()'" ".venv/bin/python -m playwright install $engine"
    done
    check "built site in docs/" "[ -f docs/index.html ]" "run: hc.sh baseline"
    [ $ok = 1 ] && echo "All tools present." || { echo "Fix the MISSING items before running the loop."; exit 1; } ;;
  status) ledger status ;;
  baseline) bench; settle_sitemap; metrics ;;
  experiment)
    [ $# -ge 3 ] || { echo 'usage: hc.sh experiment "<what>" <source paths...>'; exit 2; }
    what=$2; shift 2
    [ -n "$(git status --porcelain -- "$@")" ] || { echo "no changes in: $*"; exit 2; }
    bench; settle_sitemap
    no_links "$what"
    git add -- "$@" docs
    git commit -q -m "experiment: $what"
    echo "run $(ledger next) committed as $(git log --oneline -1)"
    metrics
    echo "Next: screenshots named run-$(ledger next)-<page>-<width>-<theme>, then hc.sh checks, then hc.sh evidence" ;;
  shot) shift; node "$HERE/shot.cjs" "$@" ;;
  checks)
    rm -f checks.ok
    if bash autoresearch.checks.sh > checks.log 2>&1; then
      tail -2 checks.log; head_short > checks.ok
    else
      grep -E "FAILED|Error|assert" checks.log | head -20; tail -3 checks.log; echo "CHECKS FAILED (see checks.log)"; settle_sitemap; exit 1
    fi
    settle_sitemap ;;
  evidence)
    run=$(ledger next); mkdir -p "$EVID"; out="$EVID/run-$run.md"
    review=${2:-}
    base=$(git log -1 --format=%h HEAD~1)
    shots=$(ls "$SHOTS"/run-"$run"-*.png 2>/dev/null || true)
    {
      echo "# Evidence for run $run"
      echo
      echo "- Commit: \`$(git log --oneline -1)\` (parent \`$base\`)"
      echo "- Branch: \`$(git rev-parse --abbrev-ref HEAD)\`"
      echo "- Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo
      echo "## Source change (docs/ excluded)"
      echo '```'
      git diff --stat HEAD~1 HEAD -- . ':(exclude)docs' | tail -20
      echo '```'
      echo
      echo "## Measurement"
      echo "- Command: \`scripts/hillclimb/hc.sh experiment\` (runs \`AUDIT_LIST=findings.tsv bash autoresearch.sh\`)"
      echo "- Best kept before this run: $(ledger best)"
      echo "- This run:"
      echo '```'
      metrics
      echo '```'
      echo
      echo "## Findings delta against the best kept state"
      if [ -f findings.best.tsv ] && [ -f findings.tsv ]; then
        echo "Removed ($(comm -23 <(sort findings.best.tsv) <(sort findings.tsv) | wc -l)):"
        echo '```'; comm -23 <(sort findings.best.tsv) <(sort findings.tsv) | head -40; echo '```'
        echo "Added ($(comm -13 <(sort findings.best.tsv) <(sort findings.tsv) | wc -l)):"
        echo '```'; comm -13 <(sort findings.best.tsv) <(sort findings.tsv) | head -40; echo '```'
      else
        echo "No findings.best.tsv yet (first kept run of this clone); full list in findings.tsv."
      fi
      echo
      echo "## Correctness checks"
      if [ -f checks.ok ] && [ "$(cat checks.ok)" = "$(head_short)" ]; then
        echo "- Command: \`bash autoresearch.checks.sh\` on \`$(head_short)\`"
        echo '```'; grep -E "passed|failed|deselected" checks.log | tail -3; echo '```'
      else
        echo "- NOT RUN on this commit."
      fi
      echo
      echo "## Visual evidence"
      if [ -n "$shots" ]; then for s in $shots; do echo "- \`$s\`"; done; else echo "- none"; fi
      echo
      echo "Reviewer notes: ${review:-none given}"
      echo
      echo "## Not checked"
      echo "- Firefox and WebKit unless installed; real phones and tablets; screen readers (VoiceOver, NVDA, TalkBack);"
      echo "  external links and live GitHub Pages deployment."
    } > "$out"
    echo "$out" ;;
  log)
    status=${2:-}; what=${3:-}
    [ -n "$status" ] && [ -n "$what" ] || { echo 'usage: hc.sh log <keep|discard|crash|checks_failed> "<what>" [asi]'; exit 2; }
    no_links "$what" "${4:-}"
    # The first run of a segment is its baseline; every later keep needs the full evidence contract.
    if [ "$status" = keep ] && [ "$(ledger status | sed -n 's/^SEGMENT_RUNS=//p')" != 0 ]; then
      run=$(ledger next)
      [ -f checks.ok ] && [ "$(cat checks.ok)" = "$(head_short)" ] || {
        echo "REFUSED: checks have not passed on $(head_short). Run hc.sh checks."; exit 1; }
      [ -f "$EVID/run-$run.md" ] || { echo "REFUSED: no evidence record. Run hc.sh evidence \"<review notes>\"."; exit 1; }
      if git diff --name-only HEAD~1 HEAD | grep -qE '\.(css|qmd|lua|js|html)$' && \
         ! ls "$SHOTS"/run-"$run"-*.png >/dev/null 2>&1; then
        echo "REFUSED: a visible change needs screenshots named $SHOTS/run-$run-*.png (hc.sh shot ...), reviewed."; exit 1
      fi
      grep -q "Reviewer notes: none given" "$EVID/run-$run.md" && {
        echo "REFUSED: evidence lacks your visual review notes. Re-run hc.sh evidence \"<what you saw>\"."; exit 1; }
    fi
    if [ "$status" = keep ] && [ -f findings.tsv ]; then cp findings.tsv findings.best.tsv; fi
    shift; ledger log "$@" ;;
  discard)
    git checkout -- docs 2>/dev/null || true
    git revert --no-edit HEAD >/dev/null
    git log --oneline -1 ;;
  findings)
    out=${2:-findings.tsv}; [[ "$out" = /* ]] || out="$ROOT/$out"
    AXE="$ROOT/.autoresearch-tools/node_modules/axe-core/axe.min.js"
    [ -f "$AXE" ] || npm install --silent --prefix .autoresearch-tools axe-core@4.10.2 >/dev/null
    AXE_PATH="$AXE" AUDIT_LIST="$out" node autoresearch.audit.cjs 2>audit.details.json | grep '^METRIC polish' ||
      { echo "AUDIT FAILED (see audit.details.json)"; exit 1; }
    cut -f4 "$out" | sort | uniq -c | sort -rn
    echo "every finding (width, theme, page, kind, where): $out" ;;
  segment) ledger segment "$2" ;;
  snapshot)
    mkdir -p "$SNAP/evidence"
    for pair in autoresearch.md:session-notes.md autoresearch.ideas.md:ideas-backlog.md autoresearch.jsonl:session-log.jsonl; do
      [ -f "${pair%%:*}" ] && cp "${pair%%:*}" "$SNAP/${pair##*:}"
    done
    cp "$EVID"/*.md "$SNAP/evidence/" 2>/dev/null || true
    ls -R "$SNAP" ;;
  restore)
    for pair in autoresearch.md:session-notes.md autoresearch.ideas.md:ideas-backlog.md autoresearch.jsonl:session-log.jsonl; do
      if [ -f "$SNAP/${pair##*:}" ] && [ ! -f "${pair%%:*}" ]; then cp "$SNAP/${pair##*:}" "${pair%%:*}"; echo "restored ${pair%%:*}"; fi
    done ;;
  *) sed -n '2,21p' "$0"; exit 2 ;;
esac
