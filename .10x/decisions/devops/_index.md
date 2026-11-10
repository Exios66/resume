# DevOps index
[DISCOVERED]
- Deploy = merge to main with rendered `docs/`. Rollback = revert the merge.
- Checks: `bash autoresearch.checks.sh` (Lua, Node, pytest with Chromium). Firefox and WebKit not installed.
- Setup: `bash scripts/setup-agent.sh`, then `. .autoresearch-tools/env.sh`, then `scripts/hillclimb/hc.sh doctor`.
