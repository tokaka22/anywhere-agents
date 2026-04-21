# Codex MCP integration reference

> Detailed setup, troubleshooting, and platform notes for the Codex MCP server.
> The one-liner registration command lives in `AGENTS.md` Codex section.

## Registration

Register Codex once at the user level so it applies to all projects and terminals (including PyCharm):

```
claude mcp add codex -s user -- codex mcp-server -c approval_policy=on-failure
```

This writes to `~/.claude.json` top-level `mcpServers`. A session restart is required after registration for `/mcp` to pick it up.

### Migrating an existing registration

If Codex was registered without `-c approval_policy=on-failure`, remove and re-add:

```
claude mcp remove codex -s user
claude mcp add codex -s user -- codex mcp-server -c approval_policy=on-failure
```

On Windows, adjust the path as shown below.

### Gotcha

Do not register under a project scope (e.g., from a specific working directory without `-s user`). That creates a project-scoped entry under `projects["<path>"].mcpServers` in `~/.claude.json`, which does not propagate to other directories.

## Prerequisites

Node.js installed, Codex CLI installed (`npm install -g @openai/codex`), and `OPENAI_API_KEY` set.

## Recommended Codex defaults (as of April 2026)

Add or update these keys in `~/.codex/config.toml` on macOS/Linux or `%USERPROFILE%\.codex\config.toml` on Windows (create the file if it does not exist) so that both interactive sessions and the MCP server use the recommended default model with fast inference:

```toml
model = "gpt-5.4"
model_reasoning_effort = "xhigh"
service_tier = "fast"

[features]
fast_mode = true
```

`service_tier = "fast"` selects the fast inference tier (1.5x speed, no quality reduction). For ChatGPT-authenticated users this costs 2x credits; API-key users pay standard API pricing. The `[features].fast_mode` flag gates the feature and defaults to `true`; set it explicitly alongside `service_tier` to persist the default in `config.toml`. Omit both if you prefer lower cost over latency. The MCP server reads the same `config.toml`, so these settings apply to both interactive sessions and MCP. These settings work identically on macOS, Linux, and Windows.

## MCP tools available after registration

`codex` (new prompt) and `codex-reply` (continue an existing session).

## Windows note

Claude Code launches MCP servers through bash, not cmd or PowerShell. This means `.cmd` wrappers and PowerShell variables like `$env:APPDATA` do not work. If `codex` is not on `PATH`, use the full path with forward slashes and **no `.cmd` extension** (npm installs a bash-compatible script alongside the `.cmd`):

```
claude mcp add codex -s user -- C:/Users/<you>/AppData/Roaming/npm/codex mcp-server -c approval_policy=on-failure
```

Run `where codex` (cmd) or `Get-Command codex` (PowerShell) to find the actual path.

## MCP approval policy

By default the Codex MCP server prompts for approval on every shell command, which surfaces as "MCP server requests your input" dialogs in Claude Code. Pass `-c approval_policy=on-failure` in the registration command (shown above) so commands auto-approve and only prompt on failures. The same key can be set in `config.toml` (`approval_policy = "on-failure"`) for interactive sessions.

## Bitdefender false positives (Windows)

Bitdefender Advanced Threat Defense may flag Codex and Claude Code shell commands as "Malicious command lines detected." To suppress this, add exceptions in Bitdefender → Protection → Manage Exceptions. For each exception, enable the **Advanced Threat Defense** toggle (not just Antivirus). Recommended exceptions:

- `C:\Program Files\nodejs\node.exe` (process)
- `C:\Users\<you>\.local\bin\claude.exe` (process)
- `C:\Users\<you>\AppData\Roaming\npm\codex` (process)
- `C:\Users\<you>\AppData\Roaming\npm\codex.cmd` (process)
- `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe` (process, if Codex invokes PowerShell)

## Windows recommendation: use the terminal path

On Windows (11 Build 26200+), the MCP path still has rough edges — residual approval prompts and Bitdefender false positives add friction even after the mitigations above. The terminal path (relay reviews via the Codex interactive terminal window) avoids both issues. Prefer the terminal path on Windows; use MCP on macOS/Linux where it works smoothly.
