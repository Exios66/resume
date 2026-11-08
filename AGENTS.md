# Agent verification contract

- Treat `docs/` as generated output; render source changes with Quarto instead of editing it by hand. See `.github/BUILDING.md` for setup and commands.
- For changes, identify the affected behavior and run the relevant tests. For site UI, navigation, reports, or figures, run the real-browser suite and exercise the affected pages and controls in a browser, including relevant mobile and desktop layouts. The suite checks every built page but does not prove that every interaction or external site works.
- For visual or interactive changes, save and share actual screenshots or a recording of the changed behavior, including relevant viewport and state. Keep evidence outside the published site unless explicitly requested. Check it for sensitive data before sharing.
- Report the exact commands, results, evidence paths, and what was not checked. Screenshots supplement assertions; they do not prove functionality. If a required tool, permission, or check is unavailable, report the blocker and do not claim that validation passed.
- Never invent results, screenshots, recordings, or coverage. Do not test external links by submitting forms, sending messages, or otherwise changing external state without permission.

# Polish hill-climb

To polish, sweep or audit the site's quality, follow `.claude/skills/portfolio-hillclimb/SKILL.md` (any agent can; Claude Code also loads it as a skill and offers the `portfolio-hillclimber` subagent in `.claude/agents/`). It is a measured loop: one small change, `scripts/hillclimb/hc.sh experiment`, screenshots, `hc.sh checks`, then keep or revert, logged in `autoresearch.jsonl`. The audit (`autoresearch.audit.cjs`) and checks are fixed within a segment; never change them to rescue a result.

# Commits, pull requests and issues

Never put session links (for example `claude.ai/code/session_…`), `Claude-Session:` or `Co-Authored-By:` trailers, or "Generated with" tool footers in commit messages, pull request or issue bodies, or comments. They expose private session URLs. Write plain messages.
