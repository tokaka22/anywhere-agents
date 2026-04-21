# Bootstrap reference

> Detailed explanation of the bootstrap mechanism. The actual one-liner consumers
> need is in `AGENTS.md`. Read this only when troubleshooting bootstrap, designing
> a new override, or onboarding a new agent.

## Source vs consumer detection

Agents decide whether to run the bootstrap block by inspecting the working
directory:

- **Source repo:** `bootstrap/bootstrap.sh`, `bootstrap/bootstrap.ps1`, and
  `skills/` all exist at the repo root → you are in `anywhere-agents` (or a
  fork with the same layout). Skip the bootstrap block — it would try to
  bootstrap itself.
- **Consumer repo:** otherwise. Run the matching bootstrap block at the start
  of every session, before responding to any user request or running session
  checks. Bootstrap is idempotent: re-runs refresh shared config / skills /
  settings from upstream before any work begins. Treat the block as a runtime
  command, not reference documentation.

## What gets shared

| Content | Source | How fetched |
|---------|--------|-------------|
| User profile, writing defaults, formatting rules, environment notes | `AGENTS.md` (this file) | `curl` raw file |
| Per-agent rule files (`CLAUDE.md`, `agents/codex.md`) | Generated from `AGENTS.md` by `scripts/generate_agent_configs.py` | Regenerated locally on every bootstrap; hand-authored files preserved + warned |
| Shared skills (`implement-review`, `my-router`, `ci-mockup-figure`, `readme-polish`) | `skills/` directory (committed only) | sparse `git clone` |
| Reference docs | `references/` directory | sparse `git clone` |
| Claude pointer commands for shared skills | `.claude/commands/` | sparse `git clone` plus non-destructive copy into the project `.claude/commands/` |
| Claude project defaults (`permissions`, `attribution`, etc.) | `.claude/settings.json` | sparse `git clone` plus key-level merge into the project `.claude/settings.json` on every run |
| User-level hooks (`guard.py`, `session_bootstrap.py`) + settings | `scripts/` + `user/settings.json` | Scripts copied to `~/.claude/hooks/`; settings merged into `~/.claude/settings.json` (shared permissions, PreToolUse guard, SessionStart bootstrap hook, `CLAUDE_CODE_EFFORT_LEVEL=max`) |

## Override rules

- If `AGENTS.local.md` exists in the project root, read and follow it after `AGENTS.md`. Rules in `AGENTS.local.md` override the shared defaults.
- Rules in `AGENTS.local.md` always win over shared defaults. Do not edit the root `AGENTS.md` for local overrides, as bootstrap will overwrite it.
- Project-local `skills/<name>/SKILL.md` always wins over the shared copy of the same skill.
- Shared keys in `.claude/settings.json` are updated on every bootstrap run. Project-only keys are preserved. To override a shared key locally, use `.claude/settings.local.json`.
- If a shared skill does not exist locally, the agent should use the fetched copy from `.agent-config/repo/skills/`.

## Configuration precedence

Three independent configuration layers, each with its own precedence rules. When two rules conflict, the more specific source wins.

**1. Agent rule files (Markdown)** — most specific wins:

| Layer | File | Scope |
|---|---|---|
| 1 | `CLAUDE.local.md` / `agents/codex.local.md` | Per-agent + project-local. Hand-authored; never touched by bootstrap. |
| 2 | `AGENTS.local.md` | Cross-agent + project-local. Hand-authored; never touched by bootstrap. |
| 3 | `CLAUDE.md` / `agents/codex.md` | Per-agent, generated from `AGENTS.md` by `scripts/generate_agent_configs.py`. |
| 4 | `AGENTS.md` | Cross-agent, synced from upstream on every bootstrap. |

The generated `CLAUDE.md` and `agents/codex.md` carry a `GENERATED FILE` header. If a consumer project has a hand-authored `CLAUDE.md` (or `agents/codex.md`) without that header, the generator preserves it and warns loudly — it never silently overrides user work. To adopt upstream rules in that case, rename the hand-authored file to `CLAUDE.local.md` (which still wins via layer 1).

**2. Claude Code settings (`settings.json`)** — follow Claude Code's own precedence: `managed policy` > `command-line arguments` > `.claude/settings.local.json` > `.claude/settings.json` > `~/.claude/settings.json`. Bootstrap only writes to the project-shared and user-level layers, and merges shared keys while preserving project-only keys.

**3. Environment variables** — for effort level specifically: `managed policy > CLAUDE_CODE_EFFORT_LEVEL env var > persisted effortLevel > default`.
