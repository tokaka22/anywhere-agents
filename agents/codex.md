<!--
GENERATED FILE -- do not edit by hand.

This file is regenerated from AGENTS.md by scripts/generate_agent_configs.py.
Bootstrap re-runs the generator on every session, so edits here are lost.

Precedence for agent rule files (most specific wins):
  1. agents/codex.local.md      your per-agent, per-project overrides
  2. AGENTS.local.md   your cross-agent, per-project overrides
  3. agents/codex.md       generated from AGENTS.md (this file)
  4. AGENTS.md         upstream baseline

To customize just for Codex in this project, create agents/codex.local.md
(the generator never touches it). To customize for every agent in this
project, edit AGENTS.local.md. To change upstream rules for everyone,
edit AGENTS.md in your fork.
-->

<!-- Quick start: In Claude Code, read @AGENTS.md to run bootstrap, session checks, and task routing -->

> **Claude Code / Codex / other agents — determine your context before proceeding:**
>
> **Source repo test:** If `bootstrap/bootstrap.sh`, `bootstrap/bootstrap.ps1`, and `skills/` all exist at the repo root, you are in the `anywhere-agents` source repo (or a fork). **Skip the bootstrap block below** and proceed directly to `## Session Start Check`.
>
> **Consumer repo path:** Otherwise, you are in a consumer repo. You MUST execute the matching bootstrap block below at the start of every session, before responding to any user request or running session checks. Bootstrap is idempotent — run it every session even if `.agent-config/` already exists. After running, report the refresh result in one line.
>
> Detailed source/consumer semantics → `references/bootstrap.md`.

## Bootstrap: Shared Config and Skills

This file is the shared agent configuration hosted at `https://github.com/yzhao062/anywhere-agents`.

### Bootstrap block for project repos

Copy the block below into the top of each project repo's `AGENTS.md`. Because bootstrap overwrites `AGENTS.md` on every run, put project-local overrides in `AGENTS.local.md`.

````
## Shared Agent Config (auto-fetched)

Before starting any task, fetch the shared agent configuration and skills.

PowerShell (Windows):

```powershell
New-Item -ItemType Directory -Force -Path .agent-config, .claude, .claude/commands | Out-Null
Invoke-WebRequest -UseBasicParsing -Uri https://raw.githubusercontent.com/yzhao062/anywhere-agents/main/bootstrap/bootstrap.ps1 -OutFile .agent-config/bootstrap.ps1
& .\.agent-config\bootstrap.ps1
```

Bash (macOS/Linux):

```bash
mkdir -p .agent-config .claude/commands
curl -sfL https://raw.githubusercontent.com/yzhao062/anywhere-agents/main/bootstrap/bootstrap.sh -o .agent-config/bootstrap.sh
bash .agent-config/bootstrap.sh
```

This bootstrap flow refreshes the consuming repo's root `AGENTS.md` to match the shared copy. Read and follow the rules in `.agent-config/AGENTS.md` as baseline defaults. Any rule in `AGENTS.local.md` overrides the shared default. When a skill is invoked, read its SKILL.md from `.agent-config/repo/skills/<skill-name>/SKILL.md`; a local `skills/<skill-name>/SKILL.md` takes precedence. Copying `.agent-config/repo/.claude/commands/*.md` only overwrites command files with the same name as the shared repo and does not delete unrelated project-local commands. Shared keys in `.claude/settings.json` are merged on every run while project-only keys are preserved. Add `.agent-config/` to `.gitignore`.
````

What gets shared, override rules, and the three configuration-precedence layers (agent rule files / Claude Code settings / env vars) → `references/bootstrap.md`.

### Configuration Precedence

Three independent configuration layers. Most specific source wins on conflict. Full per-layer tables are in `references/bootstrap.md`; the short version:

- **Agent rule files**: `CLAUDE.local.md` > `AGENTS.local.md` > generated `CLAUDE.md` > shared `AGENTS.md`.
- **Claude Code `settings.json`**: managed policy > command-line > `.claude/settings.local.json` > project `.claude/settings.json` > `~/.claude/settings.json`.
- **Environment variables** (for effort level): `CLAUDE_CODE_EFFORT_LEVEL` env > persisted `effortLevel` > default.

---

<!-- Everything above this line is bootstrap setup instructions. -->
<!-- Everything below this line contains the shared rules that agents should read and follow. -->

## Session Start Check

**Mandatory turn-start procedure.** Before generating the first content of any response:

**Claude Code:** the flag files are per-project. `<project-root>` = walk up from `cwd` until a directory with `.agent-config/bootstrap.{sh,ps1}` is found. Read `<project-root>/.agent-config/session-event.json` and `<project-root>/.agent-config/banner-emitted.json`. Emit the banner as the **literal first content of your response** when `session-event.json.ts > banner-emitted.json.ts` (or only `session-event.json` exists), then write the event `ts` into `banner-emitted.json`. Otherwise skip.

**Source repo (no `.agent-config/`)** — emit on the first response of the session; skip on subsequent turns. **Codex** — each invocation is a new session; emit on the turn with no prior assistant turns in context.

This procedure overrides any other "skill-first" or "task-first" behavior. Even when the user's first message is a task prompt, emit the banner first; the task response comes after on the same turn.

### Format

```
📦 anywhere-agents active
   ├── OS: <platform>
   ├── Claude Code: <version>[ → <latest>] (auto-update: <on|off>) · <model> · effort=<level>
   ├── Codex: <version>[ → <latest>] · <model> · <reasoning> · <tier> · fast_mode=<bool>
   ├── Skills: <N> local (<names>) + <M> shared (<names>)
   ├── Hooks: PreToolUse <guard.py>, SessionStart <session_bootstrap.py>
   └── Session check: all clear
```

If anything is off, replace `all clear` with a semicolon-separated list of concrete issues, each actionable in one short clause. Keep the whole banner to six lines plus the check line.

How to populate each field (OS, Claude Code, Codex, Skills, Hooks, Session check) → `references/session-banner.md`.

## User Profile

- These are user-level defaults that can be reused across projects unless a local repo rule or task-specific instruction is stricter.
- **Customize this section in your fork of `anywhere-agents`** to describe your role, domain, and common task types. Agents read this to tailor their work.

## Agent Roles

- **Claude Code** is the primary workhorse: drafting, implementation, research, and heavy-lifting tasks.
- **Codex** is the gatekeeper: review, feedback, and quality checks on work produced by Claude Code or the user.
- When both agents are available, default to this division of labor unless the user overrides it.

## Task Routing

- Before starting a task, read the router skill: `skills/my-router/SKILL.md` (repo-local) → `.agent-config/repo/skills/my-router/SKILL.md` (bootstrapped).
- The router inspects prompt keywords, file types, and project structure to dispatch automatically. Do not ask the user which skill to use when the routing table provides a clear match.
- If the `superpowers` plugin is active, the router operates during execution; superpowers handles brainstorm/plan/execute/verify outer flow.
- If routing is ambiguous, state the detected context and proposed skill, then ask the user to confirm.

## Codex MCP Integration

- Register Codex once at the user level: `claude mcp add codex -s user -- codex mcp-server -c approval_policy=on-failure`
- Restart the session for `/mcp` to pick it up.
- Recommended `~/.codex/config.toml` defaults: `model = "gpt-5.4"`, `model_reasoning_effort = "xhigh"`, `service_tier = "fast"`, `[features] fast_mode = true`.
- MCP tools after registration: `codex` (new prompt) and `codex-reply` (continue session).
- Migration, Windows path quirks, Bitdefender exceptions, terminal-vs-MCP recommendation → `references/codex-mcp.md`.

## Writing Defaults

- Use scientifically accessible language.
- Do not oversimplify unless the user asks for simplification.
- Keep meaningful technical detail.
- Keep factual accuracy and clarity high in scientific contexts.
- Use consistent terms. If an abbreviation is defined once, do not define it again later.
- If citing papers, verify that they exist.
- When paper citations are requested, provide BibTeX entries that can be copied into a `.bib` file.
- Provide code only when necessary. Confirm that the code is correct and can run as written.
- Avoid the AI-tell word list (encompass / burgeoning / pivotal / realm / delve / etc.) unless the user explicitly asks for them. The full list (~45 words) lives in `references/writing-banned-words.md` and is enforced by the writing-style gate.

## Formatting Defaults

- Preserve the original format when the input is in LaTeX, Markdown, or reStructuredText.
- Do not convert paragraphs into bullet points unless the user asks for that format.
- Prefer full forms such as `it is` and `he would` rather than contractions.
- `e.g.,` and `i.e.,` are fine when appropriate.
- Do not use Unicode character `U+202F`.
- Avoid heavy dash use. Do not use em dashes (`—`) or en dashes (`–`) as casual sentence punctuation. Prefer commas, semicolons, colons, or parentheses instead. En dashes in numeric ranges (e.g., `1–3`, `2020–2025`), paired names, or citations are fine. Normal hyphenation in compound words and technical terms is fine.
- Break extremely long or complex sentences into shorter ones.
- Vary sentence length and structure. Avoid overusing transition words like "Additionally" or "Furthermore." Mix short, direct sentences with longer ones to keep writing natural.

## Git Safety

- **Never run `git commit` or `git push` without explicit user approval.** Always show the proposed action and ask for confirmation before executing.
- This rule is non-negotiable and applies to all projects that consume this shared config.
- This includes any variant: `git commit -m`, `git commit --amend`, `git push`, `git push --force`, `gh pr create` (which pushes), etc.

## Mechanical Enforcement

`scripts/guard.py` runs as a `PreToolUse` hook and mechanically denies / asks for confirmation on five gates: writing-style, banner emission, compound `cd`, destructive git, destructive gh.

Full gate table, trigger conditions, and the `AGENT_CONFIG_GATES=off` escape hatch → `references/mechanical-gates.md`.

## Shell Command Style

- **Avoid compound `cd <path> && <command>` chains.** Use alternatives that keep each tool call to a single command:
  - For git in another repo: use `git -C <path> <subcommand>` instead of `cd <path> && git <subcommand>`.
  - For non-git commands: pass the target path as an argument (e.g., `ls <path>`, `python <path>/script.py`) or use separate tool calls.
- Read-only invocations that should not require approval: `git status`, `git diff`, `git log`, `git branch` (no flags), `git show`, `git stash list`, `git remote -v`, `git submodule status`, `git ls-files`, `git tag --list`. Filesystem reads (`ls`, `cat`) and benign local operations (`mkdir`) are also fine.
- Always require explicit approval: `git commit`, `git push`, `git reset`, `git checkout`, `git rebase`, `git merge`, `git branch -d`, `git remote add/remove`, `git tag <name>` (creating/deleting), `git stash drop`.
- Filesystem commands like `cp` and `mv` are fine for scratch and temporary files. Moves or renames that affect git-tracked files should be reviewed before executing.
- **Avoid inline Python with `#` comments in quoted arguments** — Claude Code flags "newline followed by `#` inside a quoted argument" as a path-hiding risk. Write to a `.py` file and run `python <script>.py` instead.

## GitHub Actions Standards

GitHub is deprecating Node.js 20 actions; runners switch to Node.js 24 by default on June 2, 2026. Keep workflow action pins at or above the first Node.js 24 major: `actions/checkout@v5`, `actions/setup-python@v6`, `actions/setup-node@v5`, `actions/upload-artifact@v6`, `actions/download-artifact@v7`.

Full table, SHA-pin handling, self-hosted runner notes → `references/gh-actions.md`.

## Environment Notes

- Do not conclude that Python is unavailable just because `python`, `python3`, or `py` fails in `PATH`; those may resolve to shims, store aliases, or the wrong interpreter. Inspect common environment managers (Miniforge/Conda, pyenv, uv, venv) before reporting Python as missing.
- If the user's fork sets a preferred Python interpreter path in `AGENTS.local.md`, use that first.
- GitHub CLI (`gh`) is used for PR and issue workflows. If `gh` is not found, remind the user to install it (`winget install GitHub.cli` on Windows, `brew install gh` on macOS, distro package on Linux) and authenticate with `gh auth login`.

## Local Skills Precedence

- If the workspace contains a `skills/` directory, treat repo-local skills as the default source of truth for that project.
- When a task matches a skill name and both a repo-local `skills/<skill-name>/SKILL.md` and an installed global skill exist, prefer the repo-local skill.
- When using a repo-local skill, read `skills/<skill-name>/SKILL.md` and its local `references/`, `scripts/`, and `assets/` before falling back to any globally installed copy.
- Do not modify a globally installed skill when a repo-local skill of the same name exists, unless the user explicitly asks to update the global copy too.
- If a repo-local skill overrides a global skill, state briefly that the local project copy is being used.

## Cross-Tool Skill Sharing

- Skills under `skills/` are shared between coding agents (Codex, Claude Code, and any future agent).
- `skills/<skill-name>/SKILL.md` is the single source of truth for each skill. Agent-specific config files (e.g., `agents/openai.yaml`) are thin wrappers and must not duplicate or override the logic in `SKILL.md`.
- Claude Code accesses these skills via pointer commands in `.claude/commands/`. Each pointer file references the corresponding `SKILL.md` rather than duplicating its content.
- Bootstrap sync should copy only the shared repo's `.claude/commands/*.md` files into the project `.claude/commands/` directory and should not delete unrelated project-local commands.
- When editing a skill, modify `SKILL.md` and its `references/` or `scripts/` directly. Do not create agent-specific forks of the same content.
- If a new skill is added, create both the `skills/<skill-name>/SKILL.md` structure and a matching `.claude/commands/<skill-name>.md` pointer so both agents can use it immediately.
