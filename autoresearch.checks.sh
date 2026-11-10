#!/usr/bin/env bash
# Correctness checks for the polish loop. Run after autoresearch.sh has rendered docs/.
set -euo pipefail
cd "$(dirname "$0")"

QUARTO_BIN="${QUARTO:-$(command -v quarto || echo /opt/quarto/quarto-1.10.19/bin/quarto)}"
# Resolve a symlinked quarto (e.g. /usr/local/bin/quarto) to its install, where the bundled pandoc lives.
QUARTO_DIR="$(dirname "$(readlink -f "$QUARTO_BIN")")"
PANDOC="$(ls "$QUARTO_DIR"/tools/*/pandoc 2>/dev/null | head -1)"
LUA="$(command -v lua || echo "$PANDOC lua")"

echo "Lua filter tests"
$LUA tests/test_site.lua
$LUA tests/test_charts.lua

echo "Node tests"
node --test tests/theme.test.cjs tests/icons.test.cjs

echo "Python and browser tests (Chromium, Firefox and WebKit)"
# Use preinstalled browsers when this machine has them; otherwise Playwright's default cache.
if [ -z "${PLAYWRIGHT_BROWSERS_PATH:-}" ] && [ -d /opt/pw-browsers ]; then export PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; fi
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q -x tests

echo "All checks passed."
