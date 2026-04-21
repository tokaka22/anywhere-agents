# Mechanical enforcement gates reference

> Implementation detail of the `guard.py` PreToolUse hook. Agents do not need to
> read this; the hook enforces the rules regardless. Read when troubleshooting a
> denied tool call or designing an exception.

Bootstrap deploys `scripts/guard.py` to `~/.claude/hooks/guard.py` and wires it as a `PreToolUse` hook in `~/.claude/settings.json`. The hook runs before every tool call and mechanically enforces the following:

| Gate | Tool scope | Trigger | Action |
|---|---|---|---|
| Writing-style | `Write`, `Edit`, `MultiEdit` on `.md` / `.tex` / `.rst` / `.txt` | Outgoing content contains a banned AI-tell word (see `references/writing-banned-words.md`) | **deny** with hit list |
| Banner emission | Any tool except `Read`, `Grep`, `Glob`, `Skill`, `Task`, `TodoWrite`, `BashOutput`, `WebFetch`, `WebSearch`, `ToolSearch`, `LS`, `NotebookRead`; plus `Write`/`Edit`/`MultiEdit` whose target path exactly equals `<project-root>/.agent-config/banner-emitted.json` after absolute-path normalization and Windows case folding | `<project-root>/.agent-config/session-event.json.ts > <project-root>/.agent-config/banner-emitted.json.ts`. `<project-root>` is found by walking up from `cwd` until `.agent-config/bootstrap.{sh,ps1}` is present. Source repos (no `.agent-config/`) and unrelated directories skip the gate entirely | **deny** with instruction to emit banner + write acknowledgment to the per-project ack file |
| Compound `cd` | `Bash` | Command contains `cd <path> && <cmd>` or `cd <path>; <cmd>` | **deny** with suggestion to use `git -C` or path arguments |
| Destructive git | `Bash` | `git push`, `git commit`, `git merge`, `git rebase`, `git reset --hard`, `git clean`, `git branch -d/-D`, `git tag -d`, `git stash drop/clear` | **ask** (user confirms) |
| Destructive gh | `Bash` | `gh pr create`, `gh pr merge`, `gh pr close`, `gh repo delete` | **ask** (user confirms) |

## Escape hatch

Set env var `AGENT_CONFIG_GATES=off` (or `0`/`disabled`/`false`) via the `env` block in `~/.claude/settings.json` to disable the two new gates (writing-style and banner). The compound-cd / destructive-git / destructive-gh checks remain active regardless, since they guard against muscle-memory mistakes that do not tolerate false positives.

Setting the escape hatch is the right move when a legitimate write has a banned word in *meta-discussion* context (for example, a style-guide document that quotes banned words as examples of what to avoid), or when a prompt-layer failure is blocking legitimate work. Fix the false positive, then remove the override.
