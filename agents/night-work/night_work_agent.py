"""
统一夜间工作系统主入口

功能：
1. 扫描所有任务来源 (NIGHT_TASKS, BOT_TASKS, TODO/, ideas/)
2. 评估任务可执行性
3. 按优先级调度执行
4. 跟踪进度并生成报告
5. 自动创建 PR
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json

# 导入现有组件
from task_scorer import (
    Task, Priority, Executability, Assessment,
    can_auto_execute, assess_task, parse_task_from_markdown
)
from reporter import (
    NightProgress, CompletedTask, InProgressTask, BlockedTask,
    ProgressReporter, create_progress
)
from scheduler import TaskScheduler, WorkerType, ExecutionResult
from scanner import UnifiedTaskScanner


class NightWorkSystem:
    """统一夜间工作系统"""

    def __init__(self):
        self.workspace = Path("/Users/apple/openclaw")
        self.work_dir = Path.home() / ".openclaw/night_work"
        self.work_dir.mkdir(parents=True, exist_ok=True)

        self.scanner = UnifiedTaskScanner(workspace=self.workspace)
        self.reporter = ProgressReporter()
        self.scheduler = TaskScheduler(workspace=self.workspace)
        self.pr_automator = PRAutomator(self.workspace)

        self.start_time = datetime.now()
        self.completed: List[Dict] = []
        self.in_progress: List[Dict] = []
        self.blocked: List[Dict] = []

    def run(self) -> bool:
        """运行夜间工作流程"""
        print(f"🌙 开始夜间工作: {self.start_time.strftime('%Y-%m-%d %H:%M')}")

        try:
            # Step 1: 扫描任务
            tasks = self.scanner.scan_all()
            print(f"📋 扫描到 {len(tasks)} 个任务")

            # Step 2: 筛选可执行任务
            auto_tasks = self._filter_auto_tasks(tasks)
            print(f"✅ 可自动执行: {len(auto_tasks)} 个任务")

            if not auto_tasks:
                print("⚠️ 没有可自动执行的任务")
                self._save_progress()
                return True

            # Step 3: 按优先级排序
            sorted_tasks = self._sort_by_priority(auto_tasks)
            print(f"📊 优先级排序完成")

            # Step 4: 逐个执行
            for task in sorted_tasks:
                if self._should_stop():
                    print("🛑 达到时间限制，停止执行")
                    break

                result = self.scheduler.execute(task)

                if result.success:
                    self.completed.append({
                        "id": task.id,
                        "title": task.title,
                        "pr_url": result.pr_url,
                        "lines_changed": result.lines_changed
                    })
                else:
                    self.blocked.append({
                        "id": task.id,
                        "title": task.title,
                        "blocked_hours": 0,
                        "reason": result.error,
                        "suggestions": ["检查错误日志", "明天手动处理"]
                    })

            # Step 5: 生成报告
            self._generate_report()

            # Step 6: 创建 PR (如果有变更)
            if self.completed:
                self._create_pr()

            print(f"✅ 夜间工作完成: {len(self.completed)} 个完成, {len(self.blocked)} 个阻塞")
            return True

        except Exception as e:
            print(f"❌ 夜间工作失败: {e}")
            self._save_progress()
            return False

    def _filter_auto_tasks(self, tasks: List[Task]) -> List[Task]:
        """筛选可自动执行的任务"""
        auto_tasks = []
        for task in tasks:
            if can_auto_execute(task):
                auto_tasks.append(task)
        return auto_tasks

    def _sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """按优先级排序"""
        priority_order = {Priority.P0: 0, Priority.P1: 1, Priority.P2: 2, Priority.P3: 3}
        return sorted(tasks, key=lambda t: (priority_order[t.priority], t.estimated_minutes))

    def _should_stop(self) -> bool:
        """检查是否应该停止"""
        # 最大运行 6 小时
        max_hours = 6
        elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        return elapsed >= max_hours

    def _generate_report(self):
        """生成进度报告"""
        end_time = datetime.now()

        progress = create_progress(
            round_num=1,
            start_time=self.start_time,
            end_time=end_time,
            completed=self.completed,
            in_progress=self.in_progress,
            blocked=self.blocked,
            pending_count=0,
            total_tasks=len(self.completed) + len(self.blocked)
        )

        # Markdown 报告
        md_report = self.reporter.generate_markdown_report(progress)
        report_path = self.work_dir / f"night_work_{end_time.strftime('%Y%m%d_%H%M')}.md"
        report_path.write_text(md_report)

        # Telegram 报告
        tg_report = self.reporter.generate_telegram_report(progress)
        tg_path = self.work_dir / f"night_work_{end_time.strftime('%Y%m%d_%H%M')}.txt"
        tg_path.write_text(tg_report)

        print(f"📊 报告已生成: {report_path.name}")

    def _create_pr(self):
        """创建 PR"""
        if not self.completed:
            return

        changes = self._collect_changes()
        pr_url = self.pr_automator.create_pr_from_changes(changes)

        if pr_url:
            print(f"✅ PR 已创建: {pr_url}")
            # 更新完成的 PR URL
            for task in self.completed:
                if "pr_url" not in task:
                    task["pr_url"] = pr_url

    def _collect_changes(self) -> List[Dict]:
        """收集变更文件"""
        # 从 git status 获取变更
        changes = []
        try:
            import subprocess
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    status = line[:2]
                    path = line[3:].strip()
                    changes.append({"status": status, "path": path})
        except Exception as e:
            print(f"⚠️ 收集变更失败: {e}")

        return changes

    def _save_progress(self):
        """保存进度到 MEMORY.md"""
        # 追加到 MEMORY.md
        memory_path = self.workspace / "MEMORY.md"
        if memory_path.exists():
            content = memory_path.read_text()
        else:
            content = ""

        end_time = datetime.now()
        entry = f"""

## 🌙 夜间开发进度 - {end_time.strftime('%Y-%m-%d %H:%M')}

### 已完成
{chr(10).join([f'- [{t["id"]}] {t["title"]}' for t in self.completed]) or '- 暂无'}

### 阻塞
{chr(10).join([f'- [{t["id"]}] {t["title"]}: {t["reason"]}' for t in self.blocked]) or '- 暂无'}

---
*Start: {self.start_time.strftime('%H:%M')} | End: {end_time.strftime('%H:%M')}*
"""

        memory_path.write_text(content + entry)
        print(f"💾 进度已保存到 MEMORY.md")


# 注意: UnifiedTaskScanner 已移动到 scanner.py 模块
# 注意: TaskScheduler 已移动到 scheduler.py 模块


class PRAutomator:
    """PR 自动创建器 - 新增"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.work_dir = Path.home() / ".openclaw/night_work"

    def create_pr_from_changes(self, changes: List[Dict]) -> Optional[str]:
        """从变更列表创建 PR"""
        if not changes:
            return None

        date = datetime.now().strftime("%Y-%m-%d")
        branch = f"monday/night-work-{date}"

        try:
            import subprocess

            # 创建分支
            subprocess.run(
                ["git", "checkout", "-b", branch],
                cwd=self.workspace,
                capture_output=True
            )

            # 添加变更
            for change in changes:
                subprocess.run(
                    ["git", "add", change["path"]],
                    cwd=self.workspace,
                    capture_output=True
                )

            # 提交
            commit_msg = f"🌙 Night work: {date} - {len(changes)} changes"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.workspace,
                capture_output=True
            )

            # 推送
            subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=self.workspace,
                capture_output=True
            )

            # 创建 PR
            result = subprocess.run(
                ["gh", "pr", "create", "--head", branch, "--title", commit_msg, "--body", ""],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            return result.stdout.strip() if result.returncode == 0 else None

        except Exception as e:
            print(f"⚠️ PR 创建失败: {e}")
            return None


def main():
    """主入口"""
    system = NightWorkSystem()
    success = system.run()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())


# ============ Command Handlers ============

async def handle_morning_brief() -> str:
    """处理 /morning-brief 命令"""
    try:
        from agents.morning_brief import MorningBriefAgent
        agent = MorningBriefAgent()
        report = await agent.run()
        return report
    except Exception as e:
        return f"❌ Morning Brief 生成失败: {e}"


def handle_night_work() -> str:
    """处理 /night-work 命令"""
    system = NightWorkSystem()
    success = system.run()
    return f"✅ 夜间工作完成: {'成功' if success else '失败'}"


def handle_check_stock_email() -> str:
    """处理 /check-stock-email 命令"""
    try:
        from agents.email_checker.stock_email_checker import EmailChecker
        checker = EmailChecker()
        report = checker.run()
        return report
    except Exception as e:
        return f"❌ 股票邮件检查失败: {e}"


def handle_memory_search(query: str = "") -> str:
    """处理 /memory search 命令"""
    if not query:
        return """📚 **Memory Search 命令使用**

用法:
`/memory search <关键词>`

示例:
- `/memory search 产业链`
- `/memory search VLM 分时图`
- `/memory search 一号文件`

搜索知识库中的记忆，返回语义相关的结果。"""
    
    try:
        # 动态导入，避免循环依赖
        import sys
        from pathlib import Path
        
        # 添加 projects 路径
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "projects" / "memory-vector-db" / "src"))
        
        from memory_vector_db import MemoryVectorDB
        
        db = MemoryVectorDB(
            db_path="./memory_vector_db",
            ollama_model="qwen3-embedding:0.6b"
        )
        
        # 搜索
        results = db.search(query, n_results=5)
        
        if not results:
            return f"🔍 没有找到与 '{query}' 相关的记忆"
        
        output = f"🔍 搜索: `{query}`\n\n"
        
        for i, r in enumerate(results, 1):
            fname = r['id'].split('/')[-1][:50]
            sim = 1 - r['distance']
            output += f"**{i}. [{sim:.0%}] {fname}**\n"
            content = r['document'][:200].replace('\n', ' ')
            output += f"   {content}...\n\n"
        
        output += f"📊 共 {len(results)} 条结果，知识库总计 {db.count()} 条记忆"
        
        return output
    except Exception as e:
        return f"❌ 搜索失败: {e}"


def handle_memory(query: str = "") -> str:
    """处理 /memory 命令 (别名: /memory search)"""
    return handle_memory_search(query)


def handle_sync_memory() -> str:
    """处理 /sync-memory 命令 - 同步 memory 目录到 ChromaDB"""
    try:
        import sys
        from pathlib import Path
        
        # 添加 projects 路径
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "projects" / "memory-vector-db" / "src"))
        
        from memory_vector_db import MemoryVectorDB
        from sync_watcher import MemorySyncWatcher
        
        db = MemoryVectorDB(
            db_path="./memory_vector_db",
            ollama_model="qwen3-embedding:0.6b"
        )
        
        watcher = MemorySyncWatcher(
            db=db,
            watch_dirs=["/Users/apple/openclaw/memory"],
            poll_interval=5.0,
            auto_sync=False
        )
        
        stats = watcher.sync_all()
        
        return f"""✅ Memory 同步完成

📊 同步统计:
- 新增: {stats['new']} 个
- 更新: {stats['updated']} 个
- 删除: {stats['deleted']} 个
- 未变化: {stats.get('unchanged', 0)} 个

📚 知识库总计: {db.count()} 条记忆"""
    except Exception as e:
        return f"❌ 同步失败: {e}"


# ============ Monday-TODO 命令处理器 ============

async def handle_monday_todo_scan() -> str:
    """处理 /monday-todo-scan 命令 - 扫描并处理 TODO"""
    try:
        from agents.monday_todo_agent import MondayTodoAgent
        agent = MondayTodoAgent()
        results = await agent.scan_and_process()

        return f"""✅ Monday-TODO 扫描完成

📊 扫描结果:
- 未完成任务: {results['incomplete']} 个
- 聊天完成: {results['completed_in_chat']} 个
- 待执行: {results['pending_execution']} 个
- 反思: {results['reflections_found']} 发现, {results['reflections_added']} 添加

详细结果已保存到: ~/.openclaw/monday_todo_scan.json
"""
    except Exception as e:
        return f"❌ 扫描失败: {e}"


async def handle_monday_todo_list() -> str:
    """处理 /monday-todo-list 命令 - 列出待完成任务"""
    try:
        from agents.monday_todo_agent import MondayTodoAgent
        return await MondayTodoAgent().list_pending()
    except Exception as e:
        return f"❌ 获取列表失败: {e}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command in COMMANDS:
            result = route_command(command)
            print(result)
        else:
            print(f"可用命令: {', '.join(COMMANDS.keys())}")
    else:
        print("用法: python night_work_agent.py <命令>")
        print(f"可用命令: {', '.join(COMMANDS.keys())}")


# ============ 命令路由 ============

COMMANDS = {
    "/night-work": handle_night_work,
    "/morning-brief": handle_morning_brief,
    "/check-stock-email": handle_check_stock_email,
    "/memory": handle_memory,
    "/memory-search": handle_memory_search,
    "/sync-memory": handle_sync_memory,
    "/monday-todo-scan": handle_monday_todo_scan,
    "/monday-todo-list": handle_monday_todo_list,
}


def route_command(command: str) -> str:
    """路由命令到对应处理器"""
    handler = COMMANDS.get(command)
    if handler:
        if asyncio.iscoroutinefunction(handler):
            import asyncio
            return asyncio.run(handler())
        else:
            return handler()
    return f"未知命令: {command}"
