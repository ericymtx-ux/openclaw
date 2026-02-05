#!/bin/bash
# Start Monday Dashboard on port 18790
# Updated path to projects/monday-dashboard

# Navigate to the correct directory or run from root
# Since we are using "pnpm openclaw gateway run", we need to make sure
# OpenClaw knows about this plugin.
# However, `openclaw gateway run` usually loads plugins from extensions/ or configured paths.
# If monday-dashboard is now in projects/, we might need to symlink it back or run it as a standalone app if possible.
# But `openclaw`CLI might not support running a plugin from an arbitrary path easily without config.

# Workaround: Create a symlink in extensions/ temporarily or permanently?
# Or check if we can pass the plugin path.

# Let's assume for now we create a symlink back to extensions/monday-dashboard for OpenClaw to pick it up.
# This keeps the "project" structure but allows the gateway to run it.

if [ ! -L "extensions/monday-dashboard" ]; then
  echo "Creating symlink for Monday Dashboard..."
  ln -s ../projects/monday-dashboard extensions/monday-dashboard
fi

export OPENCLAW_ALLOW_MULTI_GATEWAY=1
export OPENCLAW_GATEWAY_PORT=18790

# Isolate configuration to prevent Telegram/Channel conflicts
# This ensures Monday Dashboard doesn't load the main openclaw.json
export OPENCLAW_STATE_DIR="$HOME/.openclaw-monday"
mkdir -p "$OPENCLAW_STATE_DIR"

# Explicitly disable channels via config file
# This overrides any environment variables loaded from .env
export OPENCLAW_CONFIG_PATH="$(pwd)/projects/monday-dashboard/no-channels.json"

# Set a dummy gateway token to satisfy auth requirements
export OPENCLAW_GATEWAY_TOKEN="monday-dashboard-secret"

echo "Starting Monday Dashboard Gateway on port 18790..."
nohup pnpm openclaw gateway run --bind loopback --port 18790 --force > /tmp/openclaw-gateway-monday.log 2>&1 &

echo "Monday Dashboard is running at http://localhost:18790/monday/"
echo "Logs: tail -f /tmp/openclaw-gateway-monday.log"
