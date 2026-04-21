# GitHub Actions standards reference

> Action version minimums for Node.js 24 compatibility. Read when reviewing or
> updating workflow YAML.

GitHub is deprecating Node.js 20 actions. Runners begin using Node.js 24 by default on June 2, 2026, and GitHub's public changelog currently says Node.js 20 removal will happen later in fall 2026. Keep workflow action pins at or above the first Node.js 24 major for the GitHub-maintained actions below:

| Action | Minimum version (Node.js 24) | Replaces |
|--------|------------------------------|----------|
| `actions/checkout` | **v5** | v3, v4 |
| `actions/setup-python` | **v6** | v5 |
| `actions/setup-node` | **v5** | v4 |
| `actions/upload-artifact` | **v6** | v4, v5 |
| `actions/download-artifact` | **v7** | v4, v5, v6 |

When the session start check detects older versions, list the affected files and suggest the minimum Node.js 24 version from this table. If a repository intentionally wants the latest major instead of the minimum compatible major, flag that as a separate manual upgrade because later majors can include behavior changes. If a workflow pins a SHA instead of a tag (e.g., `actions/checkout@abc123`), flag it for manual review rather than auto-suggesting a tag. For self-hosted runners, also remind the user that these Node.js 24 actions require an Actions Runner version that supports Node.js 24.
