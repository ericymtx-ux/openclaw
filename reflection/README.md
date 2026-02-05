# Reflection Directory

自我反思报告目录，每6小时自动生成。

## 文件格式

文件名: `YYYY-MM-DD-HHMM.md`

## 报告内容

- 工作状态概览（任务统计、文件变更）
- 问题发现（紧急问题、改进建议、经验总结）
- 需要修改的文件（TODO、BOT_TASKS、夜间计划）
- 明日重点
- 关键指标

## 自动触发

由 cron 任务 `self-reflection` 每6小时触发：
- 时间: `0 */6 * * *` (00:00, 06:00, 12:18, 18:00)
- 模式: 切换到 opus 模型执行深度反思
- 输出: 生成报告 + 更新相关文件 + 发送 Telegram

## 手动执行

```bash
# 运行反思脚本
python agents/night-agent/reflection_tool.py

# 或直接运行 agent
pnpm openclaw message send --message "执行深度反思" --channel telegram
```

## 相关文件

- `agents/prompts/self-reflection-agent.md` - 反思 Agent 系统提示词
- `agents/night-agent/reflection_tool.py` - 反思工具脚本
- `agents/night-agent/switch-model.sh` - 模型切换脚本
