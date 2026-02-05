# 🌙 Unified Night Work System - 统一夜间工作系统

**版本**: 2.0
**日期**: 2026-02-03
**状态**: 整合现有架构

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Cron Trigger (23:00)                             │
│                    systemEvent: "/night-work"                       │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Night Work Agent                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Task Scanner                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│  │  │ NIGHT_   │ │ BOT_     │ │ TODO/    │ │ ideas/   │       │   │
│  │  │ TASKS.md │ │ TASKS.md │ │ *.md     │ │ *.md     │       │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │   │
│  └───────────────────────┬─────────────────────────────────────┘   │
│                          │                                           │
│                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Task Filter & Scorer                            │   │
│  │  - can_auto_execute() ← 已有 (task_scorer.py)               │   │
│  │  - assess_task() ← 已有 (task_scorer.py)                    │   │
│  │  - Priority Sort (P0-P3)                                    │   │
│  └───────────────────────┬─────────────────────────────────────┘   │
│                          │                                           │
│                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Execution Engine                                │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                    │   │
│  │  │OpenCode  │ │Claude    │ │ Scripts  │                    │   │
│  │  │Scheduler │ │Code      │ │ Runner   │                    │   │
│  │  └──────────┘ └──────────┘ └──────────┘                    │   │
│  └───────────────────────┬─────────────────────────────────────┘   │
│                          │                                           │
│                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Progress Tracker ← 已有 (reporter.py)          │   │
│  │  - NightProgress 数据结构                                   │   │
│  │  - Markdown/Telegram 报告生成                               │   │
│  └───────────────────────┬─────────────────────────────────────┘   │
│                          │                                           │
│                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              PR Creator ← 新增                              │   │
│  │  - 自动创建分支                                              │   │
│  │  - 自动提交                                                  │   │
│  │  - 自动创建 PR                                               │   │
│  └───────────────────────┬─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、现有组件复用

| 组件 | 文件 | 复用方式 |
|------|------|----------|
| 任务评估 | `task_scorer.py` | 复用 `can_auto_execute()`, `assess_task()` |
| 进度报告 | `reporter.py` | 复用 `NightProgress`, `ProgressReporter` |
| 自我反思 | `reflection_tool.py` | 独立运行，不整合到夜间工作流 |
| Cron 服务 | `src/cron/service.ts` | 复用触发机制 |

---

## 三、新增组件

### 3.1 任务扫描器增强

**新增功能**：扫描 TODO/ 和 ideas/

```python
# agents/night-work/scanner.py (新增)

from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, field

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

    def scan_all(self) -> List[Task]:
        """扫描所有任务来源"""
        tasks = []
        for source in SOURCES:
            source_tasks = self.scan_source(source)
            for task in source_tasks:
                task.source_priority = source.base_priority
            tasks.extend(source_tasks)
        return tasks

    def scan_source(self, source: TaskSource) -> List[Task]:
        """扫描单个来源"""
        path = Path.cwd() / source.path

        if path.is_file():
            return self._parse_markdown_file(path)
        elif path.is_dir():
            return self._parse_directory(path)

        return []

    def _parse_markdown_file(self, path: Path) -> List[Task]:
        """解析 Markdown 任务文件 (NIGHT_TASKS.md, BOT_TASKS.md)"""
        # 复用 task_scorer.parse_task_from_markdown()
        pass

    def _parse_directory(self, path: Path) -> List[Task]:
        """解析 TODO/ 目录"""
        tasks = []
        for md_file in path.glob("*.md"):
            if md_file.name == "index.md":
                continue
            task = self._parse_todo_file(md_file)
            if task:
                tasks.append(task)
        return tasks

    def _parse_todo_file(self, path: Path) -> Optional[Task]:
        """解析 TODO 文件"""
        content = path.read_text()
        # 提取标题、状态、工时估算
        pass
```

### 3.2 PR 自动创建器

```python
# agents/night-work/pr_creator.py (新增)

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class PRInfo:
    """PR 信息"""
    branch: str
    title: str
    body: str
    files_changed: list[str]


class PRAutomator:
    """PR 自动创建器"""

    def __init__(self, workspace: Path = Path.cwd()):
        self.workspace = workspace
        self.work_dir = Path.home() / ".openclaw/night_work"

    def create_pr_from_changes(self, changes: list[dict]) -> Optional[str]:
        """从变更列表创建 PR"""
        date = datetime.now().strftime("%Y-%m-%d")

        # Step 1: 创建分支
        branch = f"monday/night-work-{date}"
        self._git_checkout(branch)

        # Step 2: 添加变更
        for change in changes:
            self._git_add(change["path"])

        # Step 3: 提交
        commit_msg = f"🌙 Night work: {date} - {len(changes)} changes"
        self._git_commit(commit_msg)

        # Step 4: 推送到远程
        self._git_push(branch)

        # Step 5: 创建 PR
        pr_url = self._gh_pr_create(branch, commit_msg)
        return pr_url

    def generate_pr_body(self, changes: list[dict], progress: dict) -> str:
        """生成 PR 内容"""
        completed = progress.get("completed", [])
        blocked = progress.get("blocked", [])

        body = f"""## 🌙 Night Work - {datetime.now().strftime("%Y-%m-%d")}

### 完成内容
"""
        for task in completed:
            body += f"- [{task['id']}] {task['title']}\n"

        body += """
### 变更文件
"""
        for change in changes:
            status = change.get("status", "M")
            body += f"- `{status}` {change['path']}\n"

        if blocked:
            body += "\n### 阻塞任务\n"
            for task in blocked:
                body += f"- [{task['id']}] {task['title']} - {task.get('reason', '')}\n"

        body += f"""
---
*由 Monday 在夜间自动完成*
"""
        return body

    def _git_checkout(self, branch: str):
        subprocess.run(
            ["git", "checkout", "-b", branch],
            cwd=self.workspace,
            check=True
        )

    def _git_add(self, path: str):
        subprocess.run(
            ["git", "add", path],
            cwd=self.workspace,
            check=True
        )

    def _git_commit(self, message: str):
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.workspace,
            check=True
        )

    def _git_push(self, branch: str):
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            cwd=self.workspace,
            check=True
        )

    def _gh_pr_create(self, branch: str, title: str) -> str:
        # 使用 GitHub CLI 创建 PR
        result = subprocess.run(
            ["gh", "pr", "create", "--head", branch, "--title", title, "--body", ""],
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
```

### 3.3 执行调度器

```python
# agents/night-work/scheduler.py (新增)

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

class WorkerType(Enum):
    OPENCODE = "opencode"
    CLAUDE_CODE = "claude-code"
    SCRIPT = "script"


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    success: bool
    output: str
    files_changed: list[str]
    error: Optional[str] = None


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.opencode_skill = None  # 后续注入
        self.claude_code_skill = None

    def select_worker(self, task: Task) -> WorkerType:
        """选择执行 Worker"""
        # 复用 task_scorer 评估结果
        if task.estimated_minutes <= 60 and not task.affects_multiple_modules:
            return WorkerType.OPENCODE
        else:
            return WorkerType.CLAUDE_CODE

    def execute(self, task: Task) -> ExecutionResult:
        """执行任务"""
        worker = self.select_worker(task)

        if worker == WorkerType.OPENCODE:
            return self._execute_opencode(task)
        elif worker == WorkerType.CLAUDE_CODE:
            return self._execute_claude_code(task)
        else:
            return self._execute_script(task)

    def _execute_opencode(self, task: Task) -> ExecutionResult:
        """通过 OpenCode 执行"""
        # 调用 opencode-team skill
        pass

    def _execute_claude_code(self, task: Task) -> ExecutionResult:
        """通过 Claude Code 执行"""
        # 调用 claude-team skill
        pass

    def _execute_script(self, task: Task) -> ExecutionResult:
        """执行脚本"""
        pass
```

---

## 四、文件结构

```
agents/
├── night-work/                   ← 夜间工作系统
│   ├── __init__.py
│   ├── NIGHT_WORK_SYSTEM.md
│   ├── README.md
│   ├── night_work_agent.py       ← 主 Agent 入口 (+ 命令路由)
│   ├── scanner.py
│   ├── scheduler.py              ← 任务调度器 (OpenCode + Claude Code)
│   ├── pr_creator.py
│   ├── task_scorer.py
│   ├── reporter.py
│   └── setup-cron.sh
│
└── morning_brief/                ← 早间简报系统
    ├── __init__.py
    └── morning_brief.py          ← Morning Brief Agent
```

---

## 五、整合步骤

| 步骤 | 内容 | 工时 | 状态 |
|------|------|------|------|
| 1 | 创建 `scanner.py` 扫描 TODO/ | 2h | ✅ 完成 |
| 2 | 创建 `pr_creator.py` 自动 PR | 2h | ✅ 完成 |
| 3 | 创建 `night_work_agent.py` 主入口 | 1h | ✅ 完成 |
| 4 | 创建 `scheduler.py` 调度器 | 2h | ✅ OpenCode + Claude Code 完成 |
| 5 | 整合 Cron 触发 | 1h | ✅ 完成 |
| 6 | 端到端测试 | 2h | ⏳ 待完成 |

**总工时**: 10h
**已完成**: 9h
**剩余**: 1h (测试)

---

## 六、使用方式

### 手动触发

```bash
# 夜间工作模式
cd agents/night-work && python3 night_work_agent.py

# 或通过 OpenClaw (需要 Gateway 运行)
openclaw message send --message "/night-work"
```

### Cron 配置 (已自动添加)

```bash
# 查看 cron 状态
pnpm openclaw cron list | grep "Night Work"

# 手动测试触发
pnpm openclaw cron run <job-id>

# 删除 cron job
pnpm openclaw cron remove night-work-main
```

**已添加的 Cron Job**:
- `Night Work Main`: 每天 23:00 (Asia/Shanghai) 触发
- Session: main
- Payload: `/night-work` (systemEvent)

---

## 七、向后兼容性

| 旧组件 | 新位置 | 变更说明 |
|--------|--------|----------|
| `task_scorer.py` | `night-work/task_scorer.py` | 复制，保持 API 不变 |
| `reporter.py` | `night-work/progress_tracker.py` | 重命名，添加持久化 |
| `reflection_tool.py` | 保持独立 | 不整合到夜间工作流 |
| `NIGHT_TASKS.md` | 保持兼容 | 最高优先级扫描 |
| `BOT_TASKS.md` | 保持兼容 | 高优先级扫描 |

---

## 八、验收标准

- [ ] 正确扫描 NIGHT_TASKS.md + BOT_TASKS.md + TODO/ + ideas/
- [ ] 任务可自动完成性判断准确
- [ ] 优先级排序正确 (P0 > P1 > P2 > P3)
- [ ] OpenCode/Claude Code 调度正常
- [ ] 进度报告生成正确 (Markdown + Telegram)
- [ ] 自动创建 PR 成功
- [ ] 现有 NIGHT_TASKS.md 任务优先处理
- [ ] Cron 定时触发正常

---

*文档更新时间: 2026-02-03*
