#!/bin/bash
# 模型切换工具 - 用于反思任务中切换模型

set -e

CONFIG_FILE="$HOME/.openclaw/openclaw.json"
BACKUP_FILE="$HOME/.openclaw/openclaw.json.bak"

# 备份配置
backup_config() {
    cp "$CONFIG_FILE" "$BACKUP_FILE"
}

# 恢复配置
restore_config() {
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$CONFIG_FILE"
    fi
}

# 获取当前模型
get_current_model() {
    node -e "
const config = require('$CONFIG_FILE');
console.log(config.agents?.defaults?.model?.primary || 'minimax/MiniMax-M2.1');
"
}

# 切换模型
switch_model() {
    local model="$1"
    node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$CONFIG_FILE', 'utf8'));
if (!config.agents) config.agents = {};
if (!config.agents.defaults) config.agents.defaults = {};
config.agents.defaults.model = { primary: '$model' };
fs.writeFileSync('$CONFIG_FILE', JSON.stringify(config, null, 2));
console.log('Model switched to $model');
"
}

# 恢复原模型
restore_model() {
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" "$CONFIG_FILE"
        echo "Config restored from backup"
    fi
}

# 主逻辑
case "$1" in
    get)
        get_current_model
        ;;
    backup)
        backup_config
        ;;
    restore)
        restore_model
        ;;
    switch)
        backup_config
        switch_model "$2"
        ;;
    restore-model)
        restore_model
        ;;
    *)
        echo "Usage: $0 {get|backup|switch <model>|restore|restore-model}"
        exit 1
        ;;
esac
