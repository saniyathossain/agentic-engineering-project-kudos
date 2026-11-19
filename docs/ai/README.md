# AI workflow in this repository

Everything that steers or records the AI-assisted work lives in the repo, so it travels with the code and a reviewer can read it.

| What | Where | Purpose |
|---|---|---|
| Project instructions | [`CLAUDE.md`](../../CLAUDE.md) | Commands, layout, coding standards, logging/resilience/i18n rules, Docker notes. Loaded by Claude Code every session |
| Product and design brief | [`PRODUCT.md`](../../PRODUCT.md), [`DESIGN.md`](../../DESIGN.md) | Users, voice, principles; design system rules |
| Requirements and data model | [`docs/prd.md`](../prd.md), [`docs/data-model.md`](../data-model.md) | What to build |
| Plans | [`plans/`](plans/) | The plan written before each body of work (001 capstone, 002 platform hardening, 003 security/performance/API docs) |
| Course research | [`research/course-videos.md`](research/course-videos.md) | What the course videos showed, distilled |
| Memory snapshot | [`memory/`](memory/) | Copy of the assistant's persistent memory (preferences and project facts). The live copy is in `~/.claude/projects/<project>/memory/`; refresh this snapshot with `cp` when it changes |
| AI-DLC (AWS) | [`.claude/`](../../.claude), [`aidlc/`](../../aidlc), [`aidlc/spaces/default/memory/project.md`](../../aidlc/spaces/default/memory/project.md) | Installed AI-DLC 2.11.4 (harness `claude`): its agents, skills, hooks and the project memory with this project's rules (way of working, code style, stack, forbidden, mandated). Start a workflow with `/aidlc` |
| Subagent | [`.claude/agents/critic.md`](../../.claude/agents/critic.md) | Fresh-eyes reviewer: reads the diff against the plan and the standards, runs the checks, answers `Approved` or `Changes requested` |
| Skill | [`.claude/skills/verify-feature/SKILL.md`](../../.claude/skills/verify-feature/SKILL.md) | The verification loop: tests, Pint, Larastan, `tsc`, i18n and logging checks, UI smoke, critic |
| Hooks | [`scripts/hooks/`](../../scripts/hooks), wired in [`.claude/settings.json`](../../.claude/settings.json) | `protect-env.sh` blocks edits to secret env files; `pint-on-edit.sh` formats PHP after edits |
| MCP | [`.mcp.json`](../../.mcp.json) | Playwright MCP for UI checks |
| Scripts the AI relies on | [`scripts/`](../../scripts) | `audit.sh` (security), `lighthouse*.sh` (performance), `codes/scripts/lang_add.py` (translations) |

## How a piece of work runs
1. **Plan** in Plan Mode (or `/aidlc` for the full lifecycle); the plan is saved under `plans/`.
2. **Implement** on a branch; independent parts go to subagents or git worktrees and are merged with `--no-ff`.
3. **Verify**: the `verify-feature` skill, then the `critic` subagent. Findings are fixed before the commit.
4. **Record**: the plan is updated with what happened, CLAUDE.md / project memory get any new rule.

## Rules that came from the owner (also in CLAUDE.md and the AI-DLC project memory)
Latest stable versions of everything; DTOs, enums, strict types, PSR-12, early returns, DRY, SOLID; JSON 5W logs with request id and device info; no bare 500s, retry with backoff configurable from the env file; all text in `lang/en.json`; design with light/dark, frosted glass, chips, date pickers, animated icons and no AI slop; no link underlines; no `Co-Authored-By` trailers; Docker limits, hardening and no known vulnerabilities.
