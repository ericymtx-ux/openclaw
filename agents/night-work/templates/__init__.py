#!/usr/bin/env python3
"""
进度报告模板

生成夜间开发进度报告，支持 Markdown 和 Telegram 格式。
"""

# Markdown 模板
MARKDOWN_TEMPLATE = """## 🌙 夜间开发进度 - 第 {round_num} 轮 - {time}

### 已完成
{completed}

### 进行中
{in_progress}

### 阻塞升级
{blocked}

### 待明天处理
{pending}

---
*Start: {start_time} | End: {end_time}*
"""

# Telegram 模板
TELEGRAM_TEMPLATE = """🌙 夜间进度 - 第 {round_num} 轮

✅ 完成: {completed_count} 个
⏳ 进行中: {in_progress_count} 个
⚠️ 阻塞: {blocked_count} 个
📋 待处理: {pending_count} 个

完成列表: {completed_list}
阻塞: {blocked_list}"""


def format_completed(tasks: list) -> str:
    """格式化已完成任务"""
    if not tasks:
        return "- 暂无"
    return '\n'.join([
        f"- [{t.get('id', '?')}] {t.get('title', '?')}"
        for t in tasks
    ])


def format_in_progress(tasks: list) -> str:
    """格式化进行中任务"""
    if not tasks:
        return "- 暂无"
    return '\n'.join([
        f"- [{t.get('id', '?')}] {t.get('title', '?')} | 剩余 {t.get('remaining', '?')}min"
        for t in tasks
    ])


def format_blocked(tasks: list) -> str:
    """格式化阻塞任务"""
    if not tasks:
        return "- 暂无"
    return '\n'.join([
        f"- [{t.get('id', '?')}] {t.get('title', '?')} | {t.get('blocked_hours', 0)}h+ | {t.get('reason', '?')}"
        for t in tasks
    ])


def format_pending(count: int) -> str:
    """格式化待处理任务"""
    if count <= 5:
        return "- 暂无具体列表（见 BOT_TASKS.md）"
    return f"- 还有 {count} 个任务待处理（见 BOT_TASKS.md）"
