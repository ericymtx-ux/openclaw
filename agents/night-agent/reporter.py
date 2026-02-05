"""
进度报告生成器

生成夜间开发进度报告，支持 Markdown 和 Telegram 格式。
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CompletedTask:
    """已完成任务"""
    id: str
    title: str
    pr_url: Optional[str] = None
    lines_changed: Optional[str] = None


@dataclass
class InProgressTask:
    """进行中任务"""
    id: str
    title: str
    remaining_minutes: int


@dataclass
class BlockedTask:
    """阻塞任务"""
    id: str
    title: str
    blocked_hours: float
    reason: str
    suggestions: list[str]


@dataclass
class NightProgress:
    """夜间进度数据"""
    round_num: int  # 第几轮
    start_time: datetime
    end_time: datetime
    completed: list[CompletedTask]
    in_progress: list[InProgressTask]
    blocked: list[BlockedTask]
    pending_count: int
    total_tasks: int


class ProgressReporter:
    """进度报告生成器"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        
    def generate_markdown_report(self, progress: NightProgress) -> str:
        """生成 Markdown 格式报告"""
        time_str = progress.end_time.strftime("%H:%M")
        
        completed_items = []
        for task in progress.completed:
            pr_part = f" | PR: {task.pr_url}" if task.pr_url else ""
            lines_part = f" | {task.lines_changed}" if task.lines_changed else ""
            completed_items.append(f"- [{task.id}] {task.title} ✅{pr_part}{lines_part}")
        
        in_progress_items = []
        for task in progress.in_progress:
            in_progress_items.append(
                f"- [{task.id}] {task.title} | 剩余 {task.remaining_minutes}min"
            )
        
        blocked_items = []
        for task in progress.blocked:
            suggestions = ", ".join(task.suggestions[:2])
            blocked_items.append(
                f"- [{task.id}] {task.title} | {task.blocked_hours}h+ | {task.reason} → {suggestions}"
            )
        
        completed_str = "\n".join(completed_items) or "- 暂无"
        in_progress_str = "\n".join(in_progress_items) or "- 暂无"
        blocked_str = "\n".join(blocked_items) or "- 暂无"
        
        pending_list = self._get_pending_list(progress.pending_count)
        
        return f"""## 🌙 夜间开发进度 - 第 {progress.round_num} 轮 - {time_str}

### 已完成
{completed_str}

### 进行中
{in_progress_str}

### 阻塞升级
{blocked_str}

### 待明天处理
{pending_list}

---
*Start: {progress.start_time.strftime('%H:%M')} | End: {progress.time_str()}*
"""
    
    def generate_telegram_report(self, progress: NightProgress) -> str:
        """生成 Telegram 格式报告（精简）"""
        completed_count = len(progress.completed)
        blocked_count = len(progress.blocked)
        pending = progress.pending_count
        
        # 简化的完成列表
        completed_short = ", ".join(
            [f"{t.id}" for t in progress.completed]
        ) or "暂无"
        
        # 阻塞列表
        blocked_short = ", ".join(
            [f"{t.id}({t.blocked_hours}h+)" for t in progress.blocked]
        ) or "无"
        
        return f"""🌙 夜间进度 - 第 {progress.round_num} 轮

✅ 完成: {completed_count} 个
⏳ 进行中: {len(progress.in_progress)} 个
⚠️ 阻塞: {blocked_count} 个
📋 待处理: {pending} 个

完成列表: {completed_short}
阻塞: {blocked_short}"""
    
    def generate_blocked_upgrade_report(self, task: BlockedTask) -> str:
        """生成阻塞升级报告"""
        suggestions = "\n- ".join(task.suggestions)
        
        return f"""## ⚠️ 阻塞升级 - {task.id}

### 任务信息
- **任务**: {task.title}
- **阻塞时长**: {task.blocked_hours}h+
- **原因**: {task.reason}

### 已尝试
- 方案A: [尝试结果]
- 方案B: [尝试结果]

### 建议方案
- {suggestions}

### 等待确认
- [ ] Opus 确认方案"""

    def _get_pending_list(self, count: int, max_show: int = 5) -> str:
        """获取待处理任务简述"""
        if count <= max_show:
            return "- 暂无具体列表（见 BOT_TASKS.md）"
        return f"- 还有 {count} 个任务待处理（见 BOT_TASKS.md）"
    
    def format_pr_summary(self, prs: list[dict]) -> str:
        """格式化 PR 汇总"""
        if not prs:
            return "无 PR"
        
        lines = []
        for pr in prs:
            lines.append(f"- {pr.get('id', 'N/A')}: {pr.get('title', '')} | {pr.get('url', '')}")
        
        return "\n".join(lines)


# 便捷函数
def create_progress(
    round_num: int,
    start_time: datetime,
    end_time: datetime,
    completed: list[dict],
    in_progress: list[dict],
    blocked: list[dict],
    pending_count: int,
    total_tasks: int
) -> NightProgress:
    """创建进度数据"""
    return NightProgress(
        round_num=round_num,
        start_time=start_time,
        end_time=end_time,
        completed=[
            CompletedTask(
                id=c.get('id', ''),
                title=c.get('title', ''),
                pr_url=c.get('pr_url'),
                lines_changed=c.get('lines_changed')
            ) for c in completed
        ],
        in_progress=[
            InProgressTask(
                id=i.get('id', ''),
                title=i.get('title', ''),
                remaining_minutes=i.get('remaining_minutes', 0)
            ) for i in in_progress
        ],
        blocked=[
            BlockedTask(
                id=b.get('id', ''),
                title=b.get('title', ''),
                blocked_hours=b.get('blocked_hours', 0),
                reason=b.get('reason', ''),
                suggestions=b.get('suggestions', [])
            ) for b in blocked
        ],
        pending_count=pending_count,
        total_tasks=total_tasks
    )


if __name__ == "__main__":
    # 测试报告生成
    reporter = ProgressReporter()
    
    progress = NightProgress(
        round_num=1,
        start_time=datetime(2026, 2, 3, 23, 0),
        end_time=datetime(2026, 2, 4, 1, 0),
        completed=[
            CompletedTask("T020", "修复 star_adapter.py API 兼容", "#123", "+45/-12"),
            CompletedTask("T021", "补齐单元测试", "#124", "+89/-5")
        ],
        in_progress=[
            InProgressTask("T022", "清理 TODO 堆积", 30)
        ],
        blocked=[
            BlockedTask(
                "T006",
                "数据适配层开发",
                4.5,
                "API 版本兼容问题",
                ["等待 Opus 确认升级方案", "尝试回退 Tushare 版本"]
            )
        ],
        pending_count=19,
        total_tasks=22
    )
    
    print("=== Markdown Report ===")
    print(reporter.generate_markdown_report(progress))
    print("\n=== Telegram Report ===")
    print(reporter.generate_telegram_report(progress))
