# Claude Code install + effort level reference

> Detailed installation paths, auto-update behavior, and effort-level mechanics.
> Read when installing Claude Code, troubleshooting updates, or understanding why
> a `/effort` selection did not persist.

## Installation

Prefer the **native installer**. Migrate off npm and winget when possible.

- macOS: `curl -fsSL https://claude.ai/install.sh | sh`
- Windows (PowerShell, no admin): `irm https://claude.ai/install.ps1 | iex` (requires Git for Windows)
- To migrate from npm: `npm uninstall -g @anthropic-ai/claude-code` first.
- From winget: `winget uninstall Anthropic.ClaudeCode` first.

Native installs auto-update in the background by default. Use `/config` inside Claude Code to set the release channel (`latest` or `stable`). Run `claude doctor` to inspect updater status, and `claude update` to force an immediate update check.

## Disabling auto-updates

Set `DISABLE_AUTOUPDATER=1` in the environment or add `"env": {"DISABLE_AUTOUPDATER": "1"}` to `~/.claude/settings.json`. The env var takes precedence regardless of other flags.

**Caveat:** if you migrated from npm or winget, an earlier install may have left `"autoUpdates": false` at the top level of `~/.claude.json`. Observed behavior is that the native updater daemon never spawns when that flag was already false at launch, even with `autoUpdatesProtectedForNative: true`. Bootstrap now heals this by flipping the stale flag to `true` on every run, so the env-var path is the only supported way to opt out.

## Effort level

As of Claude Code v2.1.111, the `/effort` slider exposes five levels: `low`, `medium`, `high`, `xhigh`, `max`. The persisted `effortLevel` key in `settings.json` accepts `low`, `medium`, `high`, and `xhigh` (v2.1.111 added `xhigh` as a valid persisted value). `max` remains session-only: selecting `max` via `/effort` silently does not persist.

To get `max` as a persistent default across every project and session, set the env var `CLAUDE_CODE_EFFORT_LEVEL=max` in `~/.claude/settings.json` under `"env"`. The shared `user/settings.json` in this repo sets the env var, and bootstrap merges it into `~/.claude/settings.json`, so running bootstrap once on any consuming project lands the user-level default.

### Runtime precedence

`managed policy > CLAUDE_CODE_EFFORT_LEVEL env var > persisted effortLevel (local > project > user) > Claude Code's built-in default`

When the env var is set, it outranks `--effort` at launch and `/effort` inside a session; the slash command prints a warning that the env var is overriding the live effort. When the env var is unset, `--effort <level>` at launch is a session-only override, `/effort low|medium|high|xhigh` updates the persisted user setting, and `/effort max` is session-only.
