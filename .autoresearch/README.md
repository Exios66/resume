# Autoresearch session snapshot

Copies of the gitignored living files (`autoresearch.md`, `autoresearch.ideas.md`, `autoresearch.jsonl`) so the
hill-climb can resume in a fresh clone. To resume: copy them back to the repository root under their original names,
then run `bash autoresearch.sh` and `bash autoresearch.checks.sh`. Quarto renders only `.qmd`, so nothing here is published.

| Path | What it holds |
| --- | --- |
| `session-notes.md`, `ideas-backlog.md`, `session-log.jsonl` | Snapshot of `autoresearch.md`, `autoresearch.ideas.md` and `autoresearch.jsonl` (`hc.sh snapshot` refreshes them) |
| `evidence/run-<N>.md` | Evidence record for each hill-climb run: metrics, checks, screenshot paths, review notes |
| `screenshots/` | Tracked copies of the screenshots the evidence records cite |
| `records/` | Finished one-off verification notes, plans, observation JSON and the capture scripts that produced them. Scripts run from the repository root, for example `.venv/bin/python .autoresearch/records/capture-chart-evidence.py` |
