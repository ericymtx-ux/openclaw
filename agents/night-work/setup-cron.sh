#!/bin/bash
# Night Work Cron 集成脚本
# 用法: ./setup-cron.sh [--remove]

set -e

JOB_ID="night-work"
SCHEDULE="0 23 * * *"  # 每天 23:00
TIMEZONE="Asia/Shanghai"

# 检查是否需要删除
if [ "$1" = "--remove" ]; then
    echo "🗑️ 移除夜间工作 cron job..."
    openclaw cron remove "$JOB_ID" 2>/dev/null || echo "Job 不存在，跳过"
    echo "✅ 已移除"
    exit 0
fi

# 检查 job 是否已存在
echo "🔍 检查现有 cron job..."
EXISTING=$(openclaw cron list 2>/dev/null | grep "$JOB_ID" || true)

if [ -n "$EXISTING" ]; then
    echo "ℹ️ Job 已存在: $JOB_ID"
    echo "   $EXISTING"
    read -p "是否更新? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "跳过"
        exit 0
    fi
    openclaw cron remove "$JOB_ID"
fi

# 添加 cron job
echo "📅 添加夜间工作 cron job..."
echo "   Schedule: 每天 23:00 ($TIMEZONE)"

openclaw cron add <<EOF
{
  "id": "$JOB_ID",
  "name": "Night Work",
  "description": "自动执行夜间开发任务 (23:00-06:00)",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "$SCHEDULE",
    "tz": "$TIMEZONE"
  },
  "sessionTarget": "main",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "systemEvent",
    "text": "/night-work"
  }
}
EOF

echo "✅ Cron job 已添加"
echo ""
echo "📋 当前 cron 状态:"
openclaw cron status
echo ""
echo "📝 列出所有 jobs:"
openclaw cron list
