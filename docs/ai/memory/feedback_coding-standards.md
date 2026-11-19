---
name: feedback-coding-standards
description: Owner's mandatory code standards for backend and frontend (DTOs, enums, strict types, PSR-12, early return, DRY, SOLID)
metadata:
  type: feedback
---

Write code with DTOs, backed enums, strict types, PSR-12, early returns, DRY, SOLID, strict data types and easy-to-maintain structure, in both backend and frontend.

**Why:** stated by the owner on 2026-11-19 as a standing requirement for the capstone; enforced by Pint (`pint.json`), Larastan level 8, `tsc --noEmit` and the `critic` subagent.

**How to apply:** PHP `declare(strict_types=1)`, `final` classes, readonly DTOs in `app/Data`, enums in `app/Enums` for any fixed value, thin controllers + single-purpose Actions, Policies, interfaces for external services, guard clauses. TypeScript strict, no `any`, one component per file, shared types, no duplicated markup. Parallel agents duplicate helpers (a clipboard hook and star rating were duplicated once): dedupe after merging. See [[kudos-capstone]].
