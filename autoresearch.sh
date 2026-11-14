#!/usr/bin/env bash
# Benchmark for the portfolio polish loop: render the site, then audit the built pages.
# Prints METRIC lines; the primary metric is polish_defects (lower is better).
set -euo pipefail
cd "$(dirname "$0")"

QUARTO_BIN="${QUARTO:-$(command -v quarto || echo /opt/quarto/quarto-1.10.19/bin/quarto)}"
[ -x "$QUARTO_BIN" ] || { echo "ERROR: quarto not found (set QUARTO=/path/to/quarto)"; exit 1; }

# axe-core lives outside the site so it is never published.
TOOLS=.autoresearch-tools
if [ ! -f "$TOOLS/node_modules/axe-core/axe.min.js" ]; then
  npm install --silent --prefix "$TOOLS" axe-core@4.10.2 >/dev/null
fi

start=$(date +%s)
"$QUARTO_BIN" render --quiet >/dev/null 2>render.err || { cat render.err; exit 1; }
render_s=$(( $(date +%s) - start ))
rm -f render.err

AXE_PATH="$TOOLS/node_modules/axe-core/axe.min.js" node autoresearch.audit.cjs 2>audit.details.json
echo "METRIC render_s=$render_s"
# Experience KPIs read the same rendered docs/, so one benchmark prints both metric
# sets and the ledger can score experience_gaps against a polish_defects gate.
python3 scripts/hillclimb/kpi.py
