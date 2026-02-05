"""
统一任务扫描器

功能：
- 扫描 NIGHT_TASKS.md (优先级 1.0)
- 扫描 BOT_TASKS.md (优先级 0.8)
- 扫描 TODO/ 目录 (优先级 0.6)
- 扫描 ideas/ 目录 (优先级 0.4)
"""

from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from task_scorer import Task, Priority, parse_task_from_markdown


@dataclass
class TaskSource:
    """任务来源配置"""
    path: str
    base_priority: float  # 0.0 - 1.0
    description: str


SOURCES = [
    TaskSource("NIGHT_TASKS.md", 1.0, "今夜任务队列"),
    TaskSource("BOT_TASKS.md", 0.8, "主任务列表"),
    TaskSource("TODO/", 0.6, "待办任务"),
    TaskSource("ideas/", 0.4, "新想法"),
]


class UnifiedTaskScanner:
    """统一任务扫描器"""

    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.cwd()
        self.work_dir = Path.home() / ".openclaw/night_work"
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def scan_all(self) -> List[Task]:
        """扫描所有任务来源"""
        tasks = []
        stats = {"total": 0, "by_source": {}}

        for source in SOURCES:
            source_tasks = self.scan_source(source)
            for task in source_tasks:
                task.source_priority = source.base_priority
            tasks.extend(source_tasks)
            stats["by_source"][source.path] = len(source_tasks)

        stats["total"] = len(tasks)
        self._save_scan_stats(stats)

        return tasks

    def scan_source(self, source: TaskSource) -> List[Task]:
        """扫描单个来源"""
        path = self.workspace / source.path

        if not path.exists():
            return []

        if path.is_file():
            return self._parse_markdown_file(path, source)
        elif path.is_dir():
            return self._parse_directory(path, source)

        return []

    def _parse_markdown_file(self, path: Path, source: TaskSource) -> List[Task]:
        """解析 Markdown 任务文件"""
        tasks = []

        if path.name in ["NIGHT_TASKS.md", "BOT_TASKS.md"]:
            # 复用现有解析器
            raw_tasks = parse_task_from_markdown(path.read_text())
            for task in raw_tasks:
                task.source = source.path
            tasks.extend(raw_tasks)
        elif path.name.endswith(".md"):
            # 单个 TODO 文件
            task = self._parse_single_todo_file(path, source)
            if task:
                tasks.append(task)

        return tasks

    def _parse_directory(self, path: Path, source: TaskSource) -> List[Task]:
        """解析目录 (TODO/, ideas/)"""
        tasks = []

        for md_file in sorted(path.glob("*.md")):
            # 跳过索引文件
            if md_file.name in ["index.md", "README.md"]:
                continue

            # 跳过特殊文件
            if md_file.name.startswith("."):
                continue

            task = self._parse_single_todo_file(md_file, source)
            if task:
                tasks.append(task)

        return tasks

    def _parse_single_todo_file(self, path: Path, source: TaskSource) -> Optional[Task]:
        """解析单个 TODO 文件"""
        content = path.read_text()

        # 提取任务信息
        title = ""
        priority = Priority.P2
        estimated_minutes = 60
        requires_user_decision = False
        affects_multiple_modules = False
        has_clear_dod = True

        lines = content.split('\n')
        for line in lines:
            line = line.strip()

            # 标题
            if line.startswith('# '):
                title = line[2:].strip()

            # 优先级
            elif '优先级' in line or 'Priority' in line:
                if 'P0' in line or '🔴' in line:
                    priority = Priority.P0
                elif 'P1' in line or '🟡' in line:
                    priority = Priority.P1
                elif 'P2' in line or '🟢' in line:
                    priority = Priority.P2

            # 预估时间
            elif '预估' in line or 'Estimated' in line:
                est = self._parse_time(line)
                if est:
                    estimated_minutes = est

        # 跳过没有标题的任务
        if not title:
            return None

        # 从文件名生成 ID
        task_id = self._generate_task_id(path, source)

        return Task(
            id=task_id,
            title=title,
            priority=priority,
            estimated_minutes=estimated_minutes,
            requires_user_decision=requires_user_decision,
            affects_multiple_modules=affects_multiple_modules,
            has_clear_dod=has_clear_dod
        )

    def _parse_time(self, line: str) -> Optional[int]:
        """从行中解析时间"""
        import re

        # 匹配小时
        hour_match = re.search(r'(\d+)\s*h', line)
        if hour_match:
            return int(hour_match.group(1)) * 60

        # 匹配分钟
        min_match = re.search(r'(\d+)\s*min', line)
        if min_match:
            return int(min_match.group(1))

        return None

    def _generate_task_id(self, path: Path, source: TaskSource) -> str:
        """生成任务 ID"""
        # 命名规则: {来源前缀}_{文件名}
        prefix_map = {
            "NIGHT_TASKS.md": "NIGHT",
            "BOT_TASKS.md": "BOT",
            "TODO": "T",
            "ideas": "IDEA",
        }

        prefix = prefix_map.get(source.path, source.path[:4].upper())
        return f"{prefix}_{path.stem}"

    def _save_scan_stats(self, stats: dict):
        """保存扫描统计"""
        stats_path = self.work_dir / "scan_stats.json"
        stats_path.write_text(
            json.dumps({
                **stats,
                "timestamp": datetime.now().isoformat()
            }, indent=2, ensure_ascii=False)
        )

    def get_scan_summary(self) -> str:
        """获取扫描摘要"""
        stats_path = self.work_dir / "scan_stats.json"

        if not stats_path.exists():
            return "尚未执行扫描"

        stats = json.loads(stats_path.read_text())

        lines = [f"📋 扫描完成: {stats['total']} 个任务"]
        for source, count in stats.get("by_source", {}).items():
            lines.append(f"  - {source}: {count}")

        return '\n'.join(lines)


if __name__ == "__main__":
    # 测试扫描器
    scanner = UnifiedTaskScanner()

    print("🔍 开始扫描任务...")
    tasks = scanner.scan_all()

    print(f"\n📊 扫描结果:")
    print(f"  总任务数: {len(tasks)}")

    # 按来源分组统计
    by_source = {}
    for task in tasks:
        source = getattr(task, 'source', 'unknown')
        by_source.setdefault(source, 0)
        by_source[source] += 1

    for source, count in by_source.items():
        print(f"  - {source}: {count}")

    # 按优先级统计
    by_priority = {}
    for task in tasks:
        by_priority.setdefault(task.priority.value, 0)
        by_priority[task.priority.value] += 1

    print(f"\n📈 优先级分布:")
    for priority, count in sorted(by_priority.items()):
        print(f"  - {priority}: {count}")

    # 显示前 5 个任务
    print(f"\n📝 前 5 个任务 (按优先级排序):")
    for task in tasks[:5]:
        print(f"  [{task.id}] {task.title} ({task.priority.value})")
