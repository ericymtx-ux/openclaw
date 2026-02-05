#!/bin/bash
# OpenCode Team HTTP Server Setup
# Run this to configure launchd auto-start

set -e

# Detect paths
UV_PATH=$(which uv 2>/dev/null || echo "/opt/homebrew/bin/uv")
HOME_DIR="$HOME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check prerequisites
if ! command -v uv &> /dev/null; then
    echo "Error: uv not found. Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    echo "Error: pyproject.toml not found at $PROJECT_DIR"
    exit 1
fi

# Create directories
mkdir -p "$HOME/.opencode-team/logs"
mkdir -p "$HOME/.opencode-team/memory"

# Template file
TEMPLATE="$SCRIPT_DIR/com.opencode-team.plist.template"
if [ ! -f "$TEMPLATE" ]; then
    echo "Error: plist template not found at $TEMPLATE"
    exit 1
fi

# Generate plist from template
PLIST_DEST="$HOME/Library/LaunchAgents/com.opencode-team.plist"
sed -e "s|{{UV_PATH}}|$UV_PATH|g" \
    -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" \
    -e "s|{{HOME}}|$HOME_DIR|g" \
    "$TEMPLATE" > "$PLIST_DEST"

echo "✅ Created: $PLIST_DEST"

# Unload if already loaded
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Load the service
launchctl load "$PLIST_DEST"
echo "✅ Loaded launchd service"

# Verify
sleep 2
if launchctl list | grep -q com.opencode-team; then
    echo "✅ opencode-team HTTP server is running"
    echo "   Logs: ~/.opencode-team/logs/"
    echo "   Port: 8767"
else
    echo "⚠️  Service loaded but may not be running. Check logs."
fi

echo ""
echo "Next steps:"
echo "1. Add to OpenCode MCP settings (~/.cursor/mcp.json):"
echo '{
  "mcpServers": {
    "opencode-team-http": {
      "transport": "streamable-http",
      "url": "http://127.0.0.1:8767/mcp",
      "lifecycle": "keep-alive"
    }
  }
}'
echo ""
echo "2. Restart OpenCode to load the new MCP server"
