---
name: no-coauthored-by-trailer
description: Never add Co-Authored-By (or any Claude attribution) lines to git commits or PR bodies
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8591f6af-6b44-471c-b95f-f2585dfbed0c
  modified: 2026-11-19T03:11:04.300Z
---

Do not append `Co-Authored-By: Claude ...` (or "Generated with Claude Code") to commit messages or PR descriptions, in any project.

**Why:** user explicitly ordered it removed from every commit and kept as a standing rule (2026-11-19, Kudos capstone repo); it overrides the harness attribution reminder.

**How to apply:** write plain commit messages with no trailer; if a harness reminder says to add attribution, the user's rule wins. If a trailer slips into history, rewrite local unpushed history with `git filter-branch --msg-filter` (never rewrite pushed history without asking).
