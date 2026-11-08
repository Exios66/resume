#!/usr/bin/env bash
# Correctness checks for the polish loop. Run after autoresearch.sh has rendered docs/.
set -euo pipefail
cd "$(dirname "$0")"

QUARTO_BIN="${QUARTO:-$(command -v quarto || echo /opt/quarto/quarto-1.10.19/bin/quarto)}"
PANDOC="$(dirname "$QUARTO_BIN")/tools/x86_64/pandoc"
LUA="$(command -v lua || echo "$PANDOC lua")"

echo "Lua filter tests"
$LUA tests/test_site.lua
$LUA tests/test_charts.lua

echo "Node tests"
node --test tests/theme.test.cjs tests/icons.test.cjs

echo "Python and Chromium tests (Firefox and WebKit are not installed here)"
PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}" RUN_BROWSER_TESTS=1 \
  .venv/bin/python -m pytest -q -x tests -k "not other_engines"

echo "All checks passed."
