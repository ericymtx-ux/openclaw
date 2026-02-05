"""
任务复杂度评估器

判断任务是否可自主执行，还是需要升级。
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class Priority(Enum):
    P0 = "P0"  # 立即处理
    P1 = "P1"  # 优先处理
    P2 = "P2"  # 条件处理


class Executability(Enum):
    AUTO = "auto"  # 可自主执行
    NEEDS_REVIEW = "needs_review"  # 需要审核
    NEEDS_OPUS = "needs_opus"  # 需要 Opus


@dataclass
class Task:
    """任务数据结构"""
    id: str
    title: str
    priority: Priority
    estimated_minutes: int
    requires_user_decision: bool = False
    affects_multiple_modules: bool = False
    has_clear_dod: bool = True
    blocked_hours: float = 0.0


@dataclass
class Assessment:
    """评估结果"""
    task: Task
    executability: Executability
    reasons: list[str]
    suggestions: list[str]


def can_auto_execute(task: Task) -> bool:
    """
    判断任务是否可自主执行
    
    可执行条件：
    - 预估时间 ≤ 60 分钟
    - 不需要用户决策
    - 影响范围单模块
    - 有明确 DoD
    """
    reasons = []
    
    if task.estimated_minutes > 60:
        reasons.append(f"任务超过60分钟 ({task.estimated_minutes}min)")
        
    if task.requires_user_decision:
        reasons.append("需要用户决策")
        
    if task.affects_multiple_modules:
        reasons.append("影响多个模块")
        
    if not task.has_clear_dod:
        reasons.append("缺少明确 DoD")
        
    if task.blocked_hours >= 4:
        reasons.append(f"阻塞超过4小时 ({task.blocked_hours}h)")
        
    return len(reasons) == 0


def assess_task(task: Task) -> Assessment:
    """完整评估任务"""
    if can_auto_execute(task):
        return Assessment(
            task=task,
            executability=Executability.AUTO,
            reasons=[],
            suggestions=["可自主执行"]
        )
    
    # 分析原因
    reasons = []
    suggestions = []
    
    if task.estimated_minutes > 60:
        reasons.append(f"任务过大 ({task.estimated_minutes}min)")
        suggestions.append("拆分为多个子任务")
        
    if task.requires_user_decision:
        reasons.append("需要用户决策")
        suggestions.append("创建升级报告，等待 Opus 确认")
        
    if task.affects_multiple_modules:
        reasons.append("跨模块风险")
        suggestions.append("通知 Opus 进行 Code Review")
        
    if not task.has_clear_dod:
        reasons.append("DoD 不明确")
        suggestions.append("补充 DoD 后再执行")
        
    if task.blocked_hours >= 4:
        reasons.append(f"长期阻塞 ({task.blocked_hours}h)")
        suggestions.append("分析阻塞原因，尝试替代方案")
    
    # 判断级别
    if task.requires_user_decision or task.blocked_hours >= 4:
        executability = Executability.NEEDS_OPUS
    else:
        executability = Executability.NEEDS_REVIEW
        
    return Assessment(
        task=task,
        executability=executability,
        reasons=reasons,
        suggestions=suggestions
    )


def parse_task_from_markdown(markdown: str) -> list[Task]:
    """从 BOT_TASKS.md 解析任务列表"""
    tasks = []
    
    # 简化解析：提取表格行
    lines = markdown.split('\n')
    for line in lines:
        if line.startswith('|') and not line.startswith('|---'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4:
                task_id = parts[0]
                title = parts[1]
                priority = Priority.P0 if 'P0' in parts[2] else (
                    Priority.P1 if 'P1' in parts[2] else Priority.P2
                )
                
                # 解析预估时间
                est_str = parts[3]
                if 'h' in est_str:
                    est = int(est_str.replace('h', '')) * 60
                elif 'min' in est_str:
                    est = int(est_str.replace('min', ''))
                else:
                    est = 30  # 默认 30 分钟
                
                tasks.append(Task(
                    id=task_id,
                    title=title,
                    priority=priority,
                    estimated_minutes=est
                ))
    
    return tasks


def select_best_task(tasks: list[Task]) -> Optional[Task]:
    """选择最佳任务"""
    auto_tasks = [t for t in tasks if can_auto_execute(t)]
    
    if not auto_tasks:
        return None
    
    # 按优先级排序
    priority_order = {Priority.P0: 0, Priority.P1: 1, Priority.P2: 2}
    auto_tasks.sort(key=lambda t: (priority_order[t.priority], t.estimated_minutes))
    
    return auto_tasks[0]


if __name__ == "__main__":
    # 测试
    test_task = Task(
        id="T020",
        title="修复 star_adapter.py API 兼容",
        priority=Priority.P0,
        estimated_minutes=30,
        requires_user_decision=False,
        affects_multiple_modules=False
    )
    
    assessment = assess_task(test_task)
    print(f"Task: {assessment.task.title}")
    print(f"Executability: {assessment.executability.value}")
    print(f"Reasons: {assessment.reasons}")
    print(f"Can Auto: {can_auto_execute(test_task)}")
