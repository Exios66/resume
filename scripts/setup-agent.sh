#!/usr/bin/env bash
# One-time setup for an agent or a fresh clone so the hill-climb can run at once.
# Idempotent: every step re-checks and skips what is already installed. Afterwards
# source the printed env file before running tools from scripts/hillclimb/hc.sh:
#
#   bash scripts/setup-agent.sh
#   . "$PWD/.autoresearch-tools/env.sh"
#   bash scripts/hillclimb/hc.sh doctor   # must end with: All tools present.
#
# What it installs, all inside the repo or ignored paths (never system-wide):
# - Python venv .venv with tests' requirements
# - Node's playwright package (no-save, in .autoresearch-tools) used by the audit
# - a Chromium for playwright
# - Quarto 1.10.19 into .autoresearch-tools/ if no Quarto 1.10.x is on PATH
#
# Environment notes:
# - The rendered docs/ were built with Quarto 1.10.19 set here; other versions change
#   generator metas and Libs bundle hashes and churn docs/.
# - This script probes the locale. On machines whose LANG forces pandoc's embedded
#   Lua away from byte-based pattern matching (this was the case with LANG=C.UTF-8,
#   where "×" matched ^%a and chart labels came out "4 ×"), the env file gains
#   LC_ALL=C so the pattern semantics match the committed site and the tests.
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "Run from inside the repository (git required)"; exit 1; }
cd "$ROOT"

TOOLS=.autoresearch-tools
ENV_FILE="$TOOLS/env.sh"
QUARTO_VERSION=1.10.19

say() { printf '%s\n' "setup-agent: $*"; }

need() {
  # need <check-commands> <fixed> <how-to-install-text>
  if eval "$1" >/dev/null 2>&1; then say "ok   $2"; else say "MISS $2 -> $3"; return 1; fi
}

# ---------------------------------------------------------------- base tools
fails=0
need "command -v git" "git" "required; install git first" || fails=$((fails+1))
need "command -v node" "node 18+" "install Node 18+ (nodejs.org, or brew install node)" || fails=$((fails+1))
need "command -v npm" "npm" "ships with Node 18+" || fails=$((fails+1))
need "command -v python3" "python3" "install Python 3.11+ from python.org" || fails=$((fails+1))
[ "$fails" = 0 ] || { say "fix the base tools above, then re-run"; exit 1; }
NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
if [ "$NODE_MAJOR" -lt 18 ]; then say "node $NODE_MAJOR is too old; install Node 18+ (nodejs.org)"; exit 1; fi

# ----------------------------------------------------------------------- venv
if [ ! -x .venv/bin/pytest ] || ! .venv/bin/python -c 'import playwright' >/dev/null 2>&1; then
  say "creating .venv and installing tests' requirements"
  python3 -m venv .venv
  .venv/bin/pip install --quiet --disable-pip-version-check -r requirements-test.txt
else
  say "ok   .venv with pytest and playwright"
fi

# ------------------------------------------------------- node browser package
if ! node -e "require('playwright')" >/dev/null 2>&1; then
  say "installing node playwright (no-save)"
  npm install --no-save playwright >/dev/null \
    || { say "npm install failed; run 'npm install --no-save playwright' and see the error"; exit 1; }
else
  say "ok   node playwright"
fi

CHROME_STEM="chromium_headless_shell"
BROWSER_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/Library/Caches/ms-playwright}"
case "$(uname -s)" in Linux*) BROWSER_DIR="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}";; esac
if ! find "$BROWSER_DIR" -maxdepth 1 -name "${CHROME_STEM}-*" 2>/dev/null | grep -q .; then
  say "installing chromium for playwright"
  npx playwright install chromium
else
  say "ok   chromium for playwright"
fi

# --------------------------------------------------------------------- quarto
quarto_ok() { "$1" --version 2>/dev/null | grep -q "^1\.10\."; }
ENV_QUARTO="${QUARTO-}"
QUARTO="$ROOT/$TOOLS/bin/quarto"
if [ -n "$ENV_QUARTO" ] && [ -x "$ENV_QUARTO" ]; then
  QUARTO="$ENV_QUARTO"
  say "ok   QUARTO from environment ($QUARTO)"
elif quarto_ok "$QUARTO"; then
  say "ok   $QUARTO"
elif quarto_ok "$(command -v quarto 2>/dev/null || true)"; then
  QUARTO="$(command -v quarto)"
  say "ok   quarto on PATH ($QUARTO)"
elif [ -x /opt/quarto/quarto-"$QUARTO_VERSION"/bin/quarto ]; then
  QUARTO=/opt/quarto/quarto-"$QUARTO_VERSION"/bin/quarto
  say "ok   $QUARTO"
else
  say "installing Quarto $QUARTO_VERSION into $TOOLS/"
  case "$(uname -sm)" in
    Darwin*)  ASSET="quarto-$QUARTO_VERSION-macos.tar.gz";;
    Linux*arm64) ASSET="quarto-$QUARTO_VERSION-linux-arm64.tar.gz";;
    Linux*)   ASSET="quarto-$QUARTO_VERSION-linux-amd64.tar.gz";;
    *) say "unsupported platform $(uname -sm); install Quarto 1.10.x from quarto.org and re-run"; exit 1;;
  esac
  mkdir -p "$TOOLS"
  URL="https://github.com/quarto-dev/quarto-cli/releases/download/v$QUARTO_VERSION/$ASSET"
  curl -fsSL -o "$TOOLS/$ASSET" "$URL" \
    || { say "download failed: $URL ; install Quarto 1.10.x and re-run"; exit 1; }
  tar -xzf "$TOOLS/$ASSET" -C "$TOOLS/"
  rm "$TOOLS/$ASSET"
  quarto_ok "$QUARTO" || { say "the installed Quarto is not 1.10.x; install Quarto 1.10.x and re-run"; exit 1; }
  say "ok   $QUARTO"
fi

# ---------------------------------------------------------------- locale probe
# Byte-based Lua patterns are assumed by the filters, the audit and the committed
# docs. If pandoc's Lua treats "×" as ^%a, LC_ALL=C is required for every render.
PANDOC_BIN="$(ls "$(dirname "$(readlink -f "$QUARTO")")"/tools/*/pandoc 2>/dev/null | head -1)"
PROBE="$TOOLS/probe.lua"
printf 'print(tostring(("\\u{00d7}"):match("^%%a") ~= nil))\n' > "$PROBE"
if [ -n "$PANDOC_BIN" ] && [ "$("$PANDOC_BIN" lua "$PROBE" 2>/dev/null | tail -1)" = "true" ]; then
  NEEDS_C=1
else
  NEEDS_C=""
fi
rm -f "$PROBE"

# ------------------------------------------------------------------ env file
mkdir -p "$TOOLS"
{
  echo "# Source this before the hill-climb: . \"$ROOT/$TOOLS/env.sh\""
  echo "export QUARTO=\"$QUARTO\""
  [ "$NEEDS_C" = 1 ] && echo "# Byte-based Lua patterns require a C locale here (see setup-agent.sh)"
  [ "$NEEDS_C" = 1 ] && echo "export LC_ALL=C"
} > "$ENV_FILE"
if [ "$NEEDS_C" = 1 ]; then
  say "locale probe: this environment changes Lua pattern semantics; env file sets LC_ALL=C"
else
  say "locale probe: byte-based Lua patterns already fine"
fi

say "env file written: . .autoresearch-tools/env.sh"

# --------------------------------------------------------------------- doctor
if . "$ENV_FILE" && bash scripts/hillclimb/hc.sh doctor | tail -4; then
  say "agent environment ready."
else
  say "doctor still reports problems; fix them and re-run setup-agent.sh"
  exit 1
fi
