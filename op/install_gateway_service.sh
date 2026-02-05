#!/bin/bash
set -e

# Configuration
PLIST_NAME="bot.clawd.gateway.plist"
SERVICE_NAME="bot.clawd.gateway"
CONTROL_SCRIPT_PATH="$HOME/clawd_control.sh"
LOG_DIR="$HOME/.clawdbot/logs"
LOG_FILE_PATTERN="$LOG_DIR/gateway-%Y-%m-%d.log"
CURRENT_LOG_FILE="$LOG_DIR/gateway-$(date +%Y-%m-%d).log"
ERROR_LOG_FILE="$LOG_DIR/gateway_error.log"

# Detect Environment
NODE_PATH="$(which node)"
if [ -z "$NODE_PATH" ]; then
  echo "Error: Node.js not found in PATH."
  exit 1
fi

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "=== OpenClaw Service Installer ==="
echo "Node Path: $NODE_PATH"
echo "Repo Dir:  $REPO_DIR"
echo "Log Dir:   $LOG_DIR"
echo "----------------------------------"

# 1. Create Directories
mkdir -p "$LOG_DIR"
mkdir -p "$LAUNCH_AGENTS_DIR"

# 3. Generate Log Rotation Script
LOG_ROTATE_SCRIPT="$HOME/.clawdbot/rotate_logs.sh"
cat <<EOF > "$LOG_ROTATE_SCRIPT"
#!/bin/bash
LOG_DIR="$LOG_DIR"
# Delete logs older than 10 days
find "\$LOG_DIR" -name "gateway-*.log" -type f -mtime +10 -delete
EOF
chmod +x "$LOG_ROTATE_SCRIPT"

# 4. Generate PLIST
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$SERVICE_NAME</string>

  <!-- Run Command: Uses run-node.mjs to ensure build is up-to-date -->
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-c</string>
    <!-- Rotate logs first, then start node and redirect output to today's log file -->
     <string>$LOG_ROTATE_SCRIPT &amp;&amp; exec $NODE_PATH $REPO_DIR/scripts/run-node.mjs gateway run &gt;&gt; $LOG_DIR/gateway-\$(date +%Y-%m-%d).log 2&gt;&amp;1</string>
  </array>

  <!-- Environment Variables -->
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>$PATH</string>
    <!-- 
      Proxy settings from design doc. 
      Uncomment and adjust if you need to force a proxy.
    -->
    <!--
    <key>HTTP_PROXY</key>
    <string>http://127.0.0.1:7890</string>
    <key>HTTPS_PROXY</key>
    <string>http://127.0.0.1:7890</string>
    <key>all_proxy</key>
    <string>http://127.0.0.1:7890</string>
    -->
  </dict>

  <!-- Working Directory -->
  <key>WorkingDirectory</key>
  <string>$REPO_DIR</string>

  <!-- Keep Alive: Auto-restart on crash -->
  <key>KeepAlive</key>
  <true/>
  
  <!-- RunAtLoad: Start automatically on login -->
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
EOF
echo "✅ Generated $PLIST_PATH"

# 5. Generate Control Script
cat <<EOF > "$CONTROL_SCRIPT_PATH"
#!/bin/bash
PLIST="$PLIST_PATH"
SERVICE="$SERVICE_NAME"
LOG_DIR="$LOG_DIR"

case "\$1" in
  start)
    echo "🚀 Starting Clawdbot..."
    launchctl load -w "\$PLIST"
    ;;
  stop)
    echo "🛑 Stopping Clawdbot..."
    launchctl unload -w "\$PLIST"
    ;;
  restart)
    echo "🔄 Restarting..."
    launchctl kickstart -k gui/\$(id -u)/\$SERVICE
    ;;
  status)
    echo "🔍 Checking status..."
    launchctl list | grep clawd
    ;;
  log)
    TODAY_LOG="\$LOG_DIR/gateway-\$(date +%Y-%m-%d).log"
    echo "📜 Showing last 20 lines of logs (\$TODAY_LOG)..."
    if [ -f "\$TODAY_LOG" ]; then
        tail -f -n 20 "\$TODAY_LOG"
    else
        echo "Log file not found: \$TODAY_LOG"
    fi
    ;;
  *)
    echo "Usage: \$0 {start|stop|restart|status|log}"
    exit 1
    ;;
esac
EOF
chmod +x "$CONTROL_SCRIPT_PATH"
echo "✅ Generated $CONTROL_SCRIPT_PATH"

echo ""
echo "=== Installation Complete ==="
echo "To start the service, run:"
echo "  $CONTROL_SCRIPT_PATH start"
echo ""
echo "To check status:"
echo "  $CONTROL_SCRIPT_PATH status"
echo ""
echo "To view logs:"
echo "  $CONTROL_SCRIPT_PATH log"
