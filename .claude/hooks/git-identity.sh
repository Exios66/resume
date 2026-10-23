#!/bin/sh
# Commits made in Claude Code sessions are authored by the repository owner.
# Claude is credited with a Co-Authored-By trailer when it helps with a change.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
git config user.name "Jack J. Burleson"
git config user.email "exios4@protonmail.com"
