---
name: feedback-latest-stable-versions
description: Always use the latest stable version of every stack component and upgrade the rest alongside it
metadata:
  type: feedback
---

Use the latest stable release of every part of the stack (language runtimes, frameworks, npm and composer packages, Docker base images) and upgrade npm/node and the rest together, not piecemeal.

**Why:** the owner caught Laravel 12 being used when Laravel 13 was current and asked for "every stack latest stable, npm node all upgrade" (2026-11-19). Training-data version assumptions are stale; the official starter kit itself lagged a major behind.

**How to apply:** look versions up (packagist.org `p2/<pkg>.json`, `registry.npmjs.org/<pkg>/latest`, Docker Hub tags API) instead of trusting memory or a starter kit's pins; use `npm-check-updates` and `composer require ...:^latest -W`. When a latest version is blocked by a peer dependency, hold only that one back, say why in CLAUDE.md/project memory, and revisit later (TypeScript 7 vs typescript-eslint, ESLint 10 vs eslint-plugin-react). See [[kudos-capstone]].
