#!/usr/bin/env bash
# Prepare this worktree for rendering and validation. Installs only into ignored
# project paths and Playwright's user cache; never installs system packages.
# Source .autoresearch-tools/env.sh afterwards, then run hc.sh doctor.
set -euo pipefail

QUARTO_VERSION=1.10.19

# Print a setup status message with the script's prefix.
say() { printf '%s\n' "setup-agent: $*"; }

# Select the official archive and how many leading archive components to remove.
quarto_archive() {
  case "$1 $2" in
    Darwin\ *) printf 'quarto-%s-macos.tar.gz 0\n' "$QUARTO_VERSION" ;;
    Linux\ aarch64|Linux\ arm64) printf 'quarto-%s-linux-arm64.tar.gz 1\n' "$QUARTO_VERSION" ;;
    Linux\ x86_64|Linux\ amd64) printf 'quarto-%s-linux-amd64.tar.gz 1\n' "$QUARTO_VERSION" ;;
    *) say "unsupported platform $1 $2; install Quarto $QUARTO_VERSION and set QUARTO" >&2; return 1 ;;
  esac
}

# Every selection path, including an explicit override, must use the build pin.
# Return success only when the executable reports that exact version.
quarto_ok() { [ -x "$1" ] && [ "$("$1" --version 2>/dev/null)" = "$QUARTO_VERSION" ]; }

# Test the actual revisions required by each client, not the presence of any cache directory.
node_browsers() {
  node -e 'const pw=require("playwright");
Promise.all([pw.chromium.launch(), pw.firefox.launch(), pw.webkit.launch()])
  .then(bs => Promise.all(bs.map(b => b.close()))).catch(() => process.exit(1))'
}
python_browsers() {
  .venv/bin/python -c 'from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    for engine in (p.chromium, p.firefox, p.webkit):
        engine.launch().close()'
}

main() {
  local root tools env_file node_major playwright_version node_version
  local env_quarto quarto asset strip archive_spec pandoc_bin probe probe_result candidate
  root="$(git rev-parse --show-toplevel)"
  cd "$root"
  tools=.autoresearch-tools
  env_file="$tools/env.sh"
  mkdir -p "$tools"

  for tool in git node npm python3; do
    command -v "$tool" >/dev/null || { say "missing $tool; install it and rerun" >&2; return 1; }
  done
  node_major="$(node -p 'process.versions.node.split(".")[0]')"
  [ "$node_major" -ge 18 ] || { say 'Node 18+ is required' >&2; return 1; }

  # Synchronize existing environments too: pytest/playwright imports alone do not
  # establish that pypdf or the required package versions are available.
  [ -x .venv/bin/python ] || python3 -m venv .venv
  .venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements-test.txt
  .venv/bin/python -m pip check
  .venv/bin/python -c 'import pytest, playwright, pypdf'
  playwright_version="$(.venv/bin/python -c 'from importlib.metadata import version; print(version("playwright"))')"
  node_version="$(node -p 'require("playwright/package.json").version' 2>/dev/null || true)"
  if [ "$node_version" != "$playwright_version" ]; then
    npm install --no-save --no-package-lock "playwright@$playwright_version"
  fi
  [ "$(node -p 'require("playwright/package.json").version')" = "$playwright_version" ]
  if ! node_browsers >/dev/null 2>&1; then
    npx --no-install playwright install chromium firefox webkit
  fi
  if ! python_browsers >/dev/null 2>&1; then
    .venv/bin/python -m playwright install chromium firefox webkit
  fi
  node_browsers
  python_browsers
  say "Python and Node Playwright $playwright_version, all three browser launches verified"

  env_quarto="${QUARTO-}"
  quarto="$root/$tools/bin/quarto"
  if [ -n "$env_quarto" ]; then
    quarto_ok "$env_quarto" || { say "QUARTO must point to Quarto $QUARTO_VERSION; correct it or unset QUARTO" >&2; return 1; }
    quarto="$env_quarto"
  elif quarto_ok "$quarto"; then
    :
  elif quarto_ok "$(command -v quarto || true)"; then
    quarto="$(command -v quarto)"
  elif quarto_ok "/opt/quarto/quarto-$QUARTO_VERSION/bin/quarto"; then
    quarto="/opt/quarto/quarto-$QUARTO_VERSION/bin/quarto"
  else
    archive_spec="$(quarto_archive "$(uname -s)" "$(uname -m)")"
    read -r asset strip <<< "$archive_spec"
    say "installing Quarto $QUARTO_VERSION ($asset)"
    curl -fsSL -o "$tools/$asset" "https://github.com/quarto-dev/quarto-cli/releases/download/v$QUARTO_VERSION/$asset"
    # Linux archives have a quarto-<version>/ root; the macOS archive is flat.
    tar -xzf "$tools/$asset" -C "$tools/" --strip-components="$strip"
    rm "$tools/$asset"
    quarto_ok "$quarto" || { say 'extracted Quarto did not match the required version' >&2; return 1; }
  fi

  pandoc_bin=''
  for candidate in "$(dirname "$(readlink -f "$quarto")")"/tools/*/pandoc; do
    if [ -x "$candidate" ]; then pandoc_bin="$candidate"; break; fi
  done
  [ -n "$pandoc_bin" ] || { say 'Quarto bundled pandoc is missing' >&2; return 1; }
  probe="$tools/probe.lua"
  printf 'print(tostring(("\\u{00d7}"):match("^%%a") ~= nil))\n' > "$probe"
  # Probe the default locale even when rerun from a shell that sourced env.sh.
  probe_result="$(env -u LC_ALL "$pandoc_bin" lua "$probe")"
  rm "$probe"
  case "$probe_result" in true|false) ;; *) say 'Lua locale probe failed' >&2; return 1;; esac
  {
    printf '# Source this before rendering, auditing or testing.\n'
    printf 'export QUARTO=%q\n' "$quarto"
    # A fixed locale makes every render deterministic, including subsequent shells.
    printf 'export LC_ALL=C\n'
  } > "$env_file"
  say "locale probe: UTF-8 letter match=$probe_result; env.sh forces byte-based C locale"
  . "$env_file"
  bash scripts/hillclimb/hc.sh doctor
  say "agent environment ready; source $env_file"
}

# Helpers can be sourced by the isolated bootstrap regression tests.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then main "$@"; fi
