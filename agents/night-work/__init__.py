"""
统一夜间工作系统

功能：
- 任务扫描 (NIGHT_TASKS, BOT_TASKS, TODO/, ideas/)
- 任务评估与筛选
- 任务调度 (OpenCode / Claude Code)
- 进度跟踪与报告
- 自动 PR 创建
"""

from .night_work_agent import NightWorkSystem, main
from .scanner import UnifiedTaskScanner, TaskSource, SOURCES
from .scheduler import TaskScheduler, WorkerType, ExecutionResult
from .task_scorer import Task, Priority, Executability, Assessment
from .reporter import ProgressReporter, NightProgress

__version__ = "2.0"
__all__ = [
    "NightWorkSystem",
    "UnifiedTaskScanner",
    "TaskSource",
    "SOURCES",
    "TaskScheduler",
    "WorkerType",
    "ExecutionResult",
    "Task",
    "Priority",
    "Executability",
    "Assessment",
    "ProgressReporter",
    "NightProgress",
    "main",
]
