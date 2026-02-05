---
name: opencode-team
description: Orchestrate multiple OpenCode workers via iTerm2 terminal. Spawn workers with git worktrees, monitor progress, and coordinate parallel development work.
homepage: https://github.com/openclaw/openclaw
metadata: {"clawdbot":{"emoji":"🚀","os":["darwin"],"requires":{"bins":["uv","iterm2","opencode"]}}}
---

# OpenCode Team

MCP server for managing OpenCode worker sessions via iTerm2 terminal.

**Workers run OpenCode CLI (`opencode run "prompt"`) in iTerm2 windows.**

## Quick Start

### 1. Install OpenCode CLI

```bash
# Check if opencode is installed
which opencode

# If not installed, install via npm/pnpm/bun
npm install -g @opencode-ai/cli
# or
pnpm add -g @opencode-ai/cli
# or  
bun add -g @opencode-ai/cli
```

### 2. Configure in OpenCode/Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "opencode-team": {
      "command": "uv",
      "args": ["--directory", "/Users/apple/openclaw/skills/opencode-team", "run", "python", "-m", "opencode_team_mcp"],
      "transport": "stdio"
    }
  }
}
```

Then restart OpenCode/Cursor.

### 3. Available Tools

- **spawn_workers** - Create new OpenCode worker sessions in iTerm2
- **list_workers** - List all managed workers
- **message_workers** - Send messages to workers
- **check_idle_workers** - Check which workers are idle
- **close_workers** - Terminate worker sessions

## Example Usage

```json
// Spawn workers
{
  "workers": [
    {
      "project_path": "/path/to/repo",
      "annotation": "Implement feature X",
      "prompt": "Search for 平安银行 in stock data"
    }
  ],
  "layout": "new"
}
```

## How It Works

1. MCP server receives tool calls from OpenCode/Cursor
2. Creates iTerm2 windows/tabs for each worker
3. Spawns `opencode run "prompt"` in each terminal
4. Workers run independently in iTerm2
5. Manager can send follow-up messages and monitor status

## Notes

- Workers persist in `~/.opencode-team/memory/worker-tracking.json`
- Worker names: Groucho, Harpo, Chico, Zeppo, Gummo, Aragorn, Gandalf...
- Use worktrees for isolated parallel development
- OpenCode CLI must be installed: `pnpm add -g @opencode-ai/cli`

## License

MIT
