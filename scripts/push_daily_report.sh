#!/bin/bash
# 每日投资报告生成并推送到 Telegram
# 用法: ./push_daily_report.sh [日期YYYYMMDD]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_DIR/.venv"
REPORT_SCRIPT="$SCRIPT_DIR/daily_report.py"

# 获取日期参数，默认为今天
DATE=${1:-$(date +%Y%m%d)}

echo "=== 每日投资报告推送 ==="
echo "日期: $DATE"
echo "时间: $(date)"

# 激活虚拟环境并生成报告
cd "$PROJECT_DIR"
source "$VENV_PATH/bin/activate"

echo "生成报告..."
python3 "$REPORT_SCRIPT" --date "$DATE"

REPORT_FILE="$PROJECT_DIR/data/reports/daily_$DATE.md"

if [ -f "$REPORT_FILE" ]; then
    echo "报告已生成: $REPORT_FILE"
    echo "推送完成！"
else
    echo "错误: 报告文件不存在"
    exit 1
fi
