# OpenCode Team 代码审查报告

**项目**: opencode-team  
**版本**: v0.1.0  
**审查日期**: 2026-02-05  
**审查人**: Claude Code Review  
**状态**: 早期开发阶段

---

## 一、项目概述

### 1.1 项目简介

OpenCode Team 是一个 MCP (Model Context Protocol) 服务器，用于通过 OpenCode/Cursor 终端协调和管理多个 OpenCode Worker。该项目旨在实现并行开发工作流，支持通过 iTerm2 集成创建隔离的 Git worktree 分支，让多个 AI Agent 同时处理不同的任务。

### 1.2 项目定位

- **核心功能**: 多 Worker 编排与状态管理
- **目标用户**: 使用 OpenCode/Cursor 进行 AI 辅助开发的开发者
- **技术栈**: Python 3.10+, MCP Protocol, uv 包管理器

### 1.3 当前版本状态

| 指标 | 状态 |
|------|------|
| 版本 | v0.1.0 |
| 成熟度 | 早期开发 (Alpha) |
| 测试覆盖 | 0% (无测试文件) |
| 文档完整度 | 中等 |

---

## 二、架构分析

### 2.1 项目结构

```
opencode-team/
├── SKILL.md                    # 主要文档 (13,131 bytes)
├── README.md                   # 项目说明
├── TODO.md                     # 开发任务清单
├── RELEASE_NOTES.md            # 发布说明
├── _meta.json                  # Skill 元数据
├── pyproject.toml              # Python 项目配置
├── assets/
│   ├── setup.sh               # launchd 自动启动脚本
│   └── com.opencode-team.plist.template  # launchd 配置模板
└── src/opencode_team_mcp/
    ├── __init__.py            # 包初始化
    ├── __main__.py            # 入口点
    └── server.py              # MCP 服务器实现 (478 行)
```

### 2.2 核心模块分析

#### 2.2.1 server.py (核心模块)

**职责**: 实现所有 MCP 协议处理逻辑

**主要组件**:
- **Worker 状态管理**: 使用全局字典 `workers` 存储 worker 信息
- **持久化层**: 将状态保存到 `~/.opencode-team/memory/worker-tracking.json`
- **MCP 工具注册**: 实现 8 个 MCP 工具
- **命令行参数**: 支持 `--http` 和 `--port` 参数

**代码统计**:
- 总行数: 478 行
- 工具定义: 8 个
- TODO 注释: 1 处
- 函数数量: 15+ 个

#### 2.2.2 未实现的模块

根据文档和项目结构，以下模块应存在但缺失:

| 模块 | 预期功能 | 状态 |
|------|----------|------|
| `workers.py` | Worker 生命周期管理 | ❌ 缺失 |
| `iterm2.py` | iTerm2 终端集成 | ❌ 缺失 |
| `worktree.py` | Git Worktree 操作封装 | ❌ 缺失 |

### 2.3 数据流分析

```
用户 (OpenCode)
    ↓
MCP Client
    ↓
opencode_team_mcp (server.py)
    ↓
┌─────────────────────────────┐
│     Worker 状态管理           │
│  (workers 全局字典)           │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│     持久化存储                │
│  worker-tracking.json       │
└─────────────────────────────┘
    ↓
┌─────────────────────────────┐
│     外部集成 (未实现)         │
│  iTerm2 / Git / OpenCode    │
└─────────────────────────────┘
```

### 2.4 依赖分析

**pyproject.toml 声明的依赖**:

```toml
dependencies = [
    "mcp>=1.0.0",           # MCP 协议实现 ✓ 已安装
    "pyzmq>=26.0.0",        # ZeroMQ 消息传递 - 未使用
    "psutil>=5.9.0",        # 进程管理 - 已导入但未使用
    "python-dateutil>=2.8.0", # 日期处理 - 未使用
    "jq>=1.6.0",           # JSON 处理 - 用于 cron 脚本
]
```

**问题发现**:
- `pyzmq`, `psutil`, `python-dateutil` 已声明为依赖但代码中未实际使用
- `jq` 依赖主要用于 cron 监控脚本，而非 MCP 服务器核心

---

## 三、已实现功能

### 3.1 MCP 工具列表

| 工具名称 | 功能描述 | 实现状态 | 代码行数 |
|----------|----------|----------|----------|
| `spawn_workers` | 创建新的 Worker 会话 | ✅ 已实现 | ~50 行 |
| `list_workers` | 列出所有管理的 Worker | ✅ 已实现 | ~30 行 |
| `message_workers` | 向 Worker 发送消息 | ⚠️ 部分实现 | ~25 行 |
| `check_idle_workers` | 检查空闲 Worker | ✅ 已实现 | ~15 行 |
| `wait_idle_workers` | 等待 Worker 空闲 | ⚠️ 占位实现 | ~15 行 |
| `read_worker_logs` | 获取会话历史 | ⚠️ 占位实现 | ~15 行 |
| `examine_worker` | 获取 Worker 详细信息 | ✅ 已实现 | ~15 行 |
| `close_workers` | 终止 Worker 会话 | ✅ 已实现 | ~20 行 |

### 3.2 核心功能详情

#### 3.2.1 Worker 命名系统

实现了 Marx Brothers + Lord of the Rings 主题的 Worker 命名:

```python
WORKER_NAMES = [
    "Groucho", "Harpo", "Chico", "Zeppo", "Gummo",
    "Aragorn", "Gandalf", "Legolas", "Gimli", "Frodo",
    "Merry", "Pippin", "Samwise", "Boromir", "Gollum"
]
```

**评价**: ✅ 创意十足，便于识别和记忆

#### 3.2.2 状态持久化

```python
# 保存路径
~/.opencode-team/memory/worker-tracking.json

# 数据结构
{
  "workers": {
    "session_id": {
      "session_id": "uuid",
      "name": "Groucho",
      "project_path": "/path/to/repo",
      "status": "ready|busy|closed",
      "bead": "issue-id",
      "annotation": "任务描述",
      "started_at": "ISO8601",
      "last_activity": "ISO8601"
    }
  },
  "last_updated": "ISO8601"
}
```

**评价**: ✅ 结构清晰，支持状态恢复

#### 3.2.3 launchd 自动启动

支持通过 launchd 实现系统登录时自动启动:

```bash
./assets/setup.sh
```

**功能**:
- 自动检测 uv 路径
- 创建必要的目录结构
- 生成并安装 launchd plist
- 验证服务状态

**评价**: ✅ 完整的部署体验

### 3.3 文档完整性

| 文档 | 状态 | 质量 |
|------|------|------|
| SKILL.md | ✅ 完整 | 高 |
| README.md | ⚠️ 简略 | 中 |
| TODO.md | ✅ 详细 | 高 |
| RELEASE_NOTES.md | ✅ 存在 | 中 |

---

## 四、待完成功能 (TODO 列表)

### 4.1 代码 TODO 注释

| 位置 | 描述 | 优先级 |
|------|------|--------|
| `server.py:331` | `message_workers`: 发送消息到实际终端会话 | 高 |

```python
# server.py 第 331 行
# TODO: Send message to actual terminal session
```

### 4.2 TODO.md 中的任务清单

#### P0 - Critical (关键)

| 任务 | 状态 | 说明 |
|------|------|------|
| Add pyproject.toml with all dependencies | ✅ 完成 | 已有 pyproject.toml |
| Add unit tests for worker management | ❌ 未开始 | 无测试文件 |
| Complete missing implementation files (workers.py, iterm2.py, worktree.py) | ❌ 未开始 | 核心模块缺失 |

#### P1 - High Priority (高优先级)

| 任务 | 状态 | 说明 |
|------|------|------|
| Add API reference documentation (docs/API.md) | ❌ 未开始 | 缺失 API 文档 |
| Add troubleshooting section to SKILL.md | ❌ 未开始 | 缺失故障排除指南 |
| Add error handling documentation | ❌ 未开始 | 缺失错误处理文档 |
| Add security considerations documentation | ❌ 未开始 | 缺失安全考虑文档 |
| Add performance benchmarks | ❌ 未开始 | 缺失性能基准 |

#### P2 - Medium Priority (中优先级)

| 任务 | 状态 | 说明 |
|------|------|------|
| Add integration tests for MCP server | ❌ 未开始 | 缺失集成测试 |
| Add integration tests for iTerm2 integration | ❌ 未开始 | 缺失 iTerm2 测试 |
| Add launchd setup validation | ❌ 未开始 | 缺失启动验证 |
| Add Docker support documentation | ❌ 未开始 | 缺失 Docker 支持 |
| Add monitoring/observability documentation | ❌ 未开始 | 缺失监控文档 |

#### 技术债务

| 任务 | 状态 | 说明 |
|------|------|------|
| Add type hints throughout server.py | ⚠️ 部分 | 缺少完整类型注解 |
| Add docstrings to all public functions | ⚠️ 部分 | 缺少部分文档字符串 |
| Add proper logging configuration | ❌ 未开始 | 缺少日志配置 |
| Add configuration file support (config.yaml) | ❌ 未开始 | 缺少配置文件支持 |
| Add validation for worker inputs | ❌ 未开始 | 缺少输入验证 |

#### 测试

| 任务 | 状态 | 说明 |
|------|------|------|
| Add unit tests for all MCP tools | ❌ 未开始 | 0% 覆盖率 |
| Add integration tests for worktree creation | ❌ 未开始 | 缺失 |
| Add tests for worker state persistence | ❌ 未开始 | 缺失 |
| Achieve 80% test coverage | ❌ 距离目标 | 当前 0% |

#### 文档

| 任务 | 状态 | 说明 |
|------|------|------|
| Add example workflows (docs/EXAMPLES.md) | ❌ 未开始 | 缺失示例 |
| Add comparison with claude-team | ⚠️ 部分 | SKILL.md 中已有 |
| Add debugging guide (docs/DEBUGGING.md) | ❌ 未开始 | 缺失 |
| Add architecture diagram | ❌ 未开始 | 缺失 |

### 4.3 功能缺失矩阵

| 功能 | 预期 | 当前 | 差距 |
|------|------|------|------|
| Worker 实际执行 | iTerm2 脚本 | 无 | 缺失集成 |
| HTTP 传输模式 | streamable-http | 仅 stdio | 未实现 |
| 消息实时传递 | ZeroMQ/WebSocket | 无 | 缺失 |
| Worktree 自动创建 | 完整实现 | 占位函数 | 缺失集成 |
| 进程监控 | psutil | 无 | 依赖未使用 |

---

## 五、风险点分析

### 5.1 高风险项

#### 5.1.1 核心集成缺失 ⚠️ 严重

**描述**: `workers.py`, `iterm2.py`, `worktree.py` 模块完全缺失，导致 Worker 无法真正执行任务。

**影响**:
- 项目功能不完整
- 用户无法实现并行开发
- 浪费用户时间

**建议**: 优先实现 iTerm2 集成模块

```python
# 期望的 iterm2.py 集成
import iterm2

async def create_terminal_window(project_path: str, prompt: str) -> str:
    """创建 iTerm2 窗口并启动 OpenCode"""
    pass

async def send_to_terminal(terminal_id: str, message: str) -> bool:
    """发送消息到终端会话"""
    pass
```

#### 5.1.2 HTTP 模式未实现 ⚠️ 严重

**描述**: `--http` 参数已声明，但 `run_server()` 函数中的 HTTP 模式仅为占位符。

**影响**:
- 无法使用持久连接
- 无法实现真正的后台服务
- MCP over HTTP 场景不可用

**当前代码**:
```python
async def run_server(port: int = DEFAULT_PORT, http: bool = False):
    if http:
        # HTTP mode - would use mcp.server.http
        # This is a placeholder for HTTP transport
        print(f"OpenCode Team MCP Server running on port {port}")
        print("HTTP mode is not yet implemented. Use stdio mode instead.")
        return
```

**建议**: 实现完整的 HTTP 传输或移除该参数

### 5.2 中风险项

#### 5.2.1 输入验证缺失 ⚠️ 中

**位置**: `spawn_opencode_session()`, `call_tool()`

**问题**: 所有用户输入直接使用，无验证

**风险**: 
- 空 project_path 导致错误
- 恶意输入可能影响系统
- 状态文件损坏

**建议**: 添加 Pydantic 或手动验证

#### 5.2.2 错误处理不完整 ⚠️ 中

**问题**:
- `create_worktree()` 捕获异常但仅打印日志
- `message_workers` 的 `wait_idle_workers` 实现为占位符
- 无超时机制

**建议**: 添加完整的异常处理和超时控制

#### 5.2.3 资源泄漏风险 ⚠️ 中

**问题**:
- Worker 关闭后可能未清理资源
- 无心跳检测机制
- 僵尸进程可能产生

**建议**: 实现进程健康检查和自动清理

### 5.3 低风险项

#### 5.3.1 依赖未使用 ⚠️ 低

**问题**: `pyzmq`, `psutil`, `python-dateutil` 已声明但未使用

**建议**: 移除未使用的依赖或实现其功能

#### 5.3.2 日志配置缺失 ⚠️ 低

**问题**: 使用 `print()` 而非 `logging` 模块

**影响**: 生产环境难以调试

**建议**: 添加 proper logging 配置

#### 5.3.3 类型注解不完整 ⚠️ 低

**问题**: 部分函数缺少返回类型注解

**建议**: 补全类型注解

---

## 六、改进建议

### 6.1 短期改进 (1-2 周)

#### 6.1.1 优先实现 iTerm2 集成

```python
# src/opencode_team_mcp/iterm2.py (建议实现)

import asyncio
import iterm2
from typing import Optional

class Iterm2Manager:
    """iTerm2 终端管理器"""
    
    async def get_connection(self) -> iterm2.Connection:
        """获取 iTerm2 连接"""
        pass
    
    async def create_worker_window(
        self,
        project_path: str,
        prompt: str,
        name: str
    ) -> str:
        """
        创建 Worker 窗口
        
        Returns:
            terminal_id: 用于后续消息发送
        """
        pass
    
    async def send_message(
        self,
        terminal_id: str,
        message: str
    ) -> bool:
        """发送消息到终端"""
        pass
    
    async def close_terminal(self, terminal_id: str) -> bool:
        """关闭终端"""
        pass
```

#### 6.1.2 添加输入验证

```python
# src/opencode_team_mcp/validators.py

from pydantic import BaseModel, validator
from pathlib import Path

class WorkerConfig(BaseModel):
    project_path: str
    bead: Optional[str] = None
    annotation: Optional[str] = None
    prompt: Optional[str] = ""
    use_worktree: bool = True
    skip_permissions: bool = False
    
    @validator("project_path")
    def validate_project_path(cls, v):
        if v != "auto":
            path = Path(v)
            if not path.exists():
                raise ValueError(f"Project path does not exist: {v}")
        return v
```

#### 6.1.3 实现 HTTP 传输

```python
# 替换 run_server 中的占位符
async def run_server(port: int = DEFAULT_PORT, http: bool = False):
    from mcp.server.http import HttpServer
    
    if http:
        http_server = HttpServer("opencode-team", host="0.0.0.0", port=port)
        # ... 配置路由
        await http_server.run()
    else:
        # 现有 stdio 模式
        pass
```

### 6.2 中期改进 (1 个月)

#### 6.2.1 添加测试覆盖

**建议测试结构**:

```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   ├── test_server.py
│   ├── test_worker_state.py
│   └── test_validators.py
└── integration/
    ├── test_mcp_tools.py
    └── test_worktree_creation.py
```

**目标覆盖率**: 80%

#### 6.2.2 添加日志和监控

```python
import logging
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("opencode-team")

@asynccontextmanager
async def worker_monitor(session_id: str):
    """Worker 活动监控上下文"""
    logger.info(f"Worker {session_id} started")
    try:
        yield
    finally:
        logger.info(f"Worker {session_id} ended")
```

#### 6.2.3 实现 Worktree 完整功能

```python
# src/opencode_team_mcp/worktree.py

import subprocess
from pathlib import Path
from typing import Optional

class WorktreeManager:
    """Git Worktree 管理器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
    
    def create_branch(self, branch_name: str) -> bool:
        """创建新分支"""
        pass
    
    def create_worktree(
        self,
        branch_name: str,
        worktree_path: Path
    ) -> bool:
        """创建 worktree"""
        result = subprocess.run(
            ["git", "worktree", "add", str(worktree_path), branch_name],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def cleanup_worktree(self, worktree_path: Path) -> bool:
        """清理 worktree"""
        pass
```

### 6.3 长期改进 (3 个月)

#### 6.3.1 完整功能路线图

1. **Worker 生命周期管理**
   - 启动、监控、重启
   - 超时处理
   - 资源限制

2. **并行任务编排**
   - 任务依赖图
   - 结果聚合
   - 冲突检测

3. **监控和告警**
   - 状态变化通知
   - 性能指标
   - 异常告警

#### 6.3.2 配置外部化

```yaml
# config.yaml

opencode_team:
  port: 8767
  mode: stdio  # or http
  
  workers:
    max_concurrent: 10
    default_timeout: 3600
    worktree_base: ~/.opencode-team/worktrees
    
  iterm2:
    auto_split: true
    layout: grid  # or auto
    
  logging:
    level: INFO
    format: "%(asctime)s - %(message)s"
```

---

## 七、代码质量评估

### 7.1 评分卡

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | 3/10 | 核心集成缺失 |
| 代码可读性 | 7/10 | 结构清晰，命名规范 |
| 错误处理 | 4/10 | 缺少完整异常处理 |
| 测试覆盖 | 0/10 | 无测试 |
| 文档质量 | 7/10 | SKILL.md 完善 |
| 架构设计 | 6/10 | 模块化设计良好 |
| 类型安全 | 5/10 | 部分类型注解 |
| 依赖管理 | 6/10 | 有未使用依赖 |

**综合评分**: 4.8/10

### 7.2 代码亮点

#### 7.2.1 Worker 命名创意

```python
WORKER_NAMES = [
    "Groucho", "Harpo", "Chico", "Zeppo", "Gummo",
    "Aragorn", "Gandalf", "Gimli "Legolas",", "Frodo",
    "Merry", "Pippin", "Samwise", "Boromir", "Gollum"
]
```

✅ 便于识别和记忆

#### 7.2.2 状态持久化设计

```python
def save_worker_state():
    """Save worker state to persistent storage."""
    state_file = DEFAULT_MEMORY_DIR / "worker-tracking.json"
    state = {
        "workers": workers,
        "last_updated": datetime.utcnow().isoformat()
    }
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
```

✅ 清晰的结构，支持状态恢复

#### 7.2.3 launchd 集成

完整的 setup.sh 脚本提供开箱即用的部署体验

### 7.3 代码问题

#### 7.3.1 全局状态管理

```python
# Worker state storage
workers: dict[str, dict] = {}
worker_counter = 0
```

⚠️ 问题: 全局可变状态在 MCP 服务器中可能导致并发问题

**建议**: 使用类封装或 asyncio.Lock

#### 7.3.2 硬编码路径

```python
DEFAULT_PORT = 8767
DEFAULT_LOG_DIR = Path.home() / ".opencode-team" / "logs"
DEFAULT_MEMORY_DIR = Path.home() / ".opencode-team" / "memory"
```

⚠️ 问题: 路径硬编码，不易配置

**建议**: 支持环境变量覆盖

#### 7.3.3 TODO 占位符

```python
# In a full implementation, we would:
# 1. Create terminal pane via iTerm2 Python API or OpenCode terminal
# 2. Start Claude Code with appropriate flags
# 3. Capture the PID for monitoring
```

⚠️ 问题: 大量占位注释表明功能未完成

**建议**: 实现或移除占位代码

### 7.4 代码风格

| 指标 | 状态 |
|------|------|
| PEP 8 遵循 | ✅ 良好 |
| 命名一致性 | ✅ 良好 |
| 注释质量 | ⚠️ 中等 |
| 函数长度 | ✅ 适中 |
| 文件组织 | ✅ 良好 |

---

## 八、结论与行动建议

### 8.1 总体评价

OpenCode Team 项目拥有清晰的设计愿景和完善的文档，但在当前版本 (v0.1.0) 中，核心功能尚未完全实现。项目更像是一个"骨架"，需要填充肌肉组织（iTerm2 集成、HTTP 传输、Worker 实际执行）才能发挥其价值。

### 8.2 优先级排序

#### 立即行动 (本周)

1. **实现 iTerm2 集成** - 最高优先级
   - 创建 `iterm2.py` 模块
   - 实现终端创建和消息发送
   - 集成到 `spawn_workers`

2. **实现 HTTP 传输** - 高优先级
   - 替换占位代码
   - 或移除 `--http` 参数

#### 短期目标 (2 周内)

3. **添加输入验证**
4. **实现 Worktree 管理**
5. **添加错误处理**

#### 中期目标 (1 个月内)

6. **添加单元测试**
7. **完善日志系统**
8. **实现配置外部化**

### 8.3 下一步工作建议

对于项目维护者：

1. **明确版本定位**: 当前状态更适合标记为 "技术预览" 而非正式版本
2. **制定发布计划**: 根据 TODO.md 优先级制定版本路线图
3. **补充核心模块**: 优先实现 `iterm2.py`, `workers.py`, `worktree.py`
4. **添加测试**: 建立 CI/CD 和测试覆盖率检查

对于用户：

1. **谨慎使用**: 当前版本功能不完整，不建议在生产环境使用
2. **关注开发**: 等待核心集成实现后再尝试完整工作流
3. **贡献代码**: 核心模块实现是很好的贡献机会

---

## 九、附录

### A. 文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| SKILL.md | 13,131 bytes | 主文档 |
| README.md | 152 bytes | 简短说明 |
| TODO.md | 1,344 bytes | 任务清单 |
| RELEASE_NOTES.md | 758 bytes | 发布说明 |
| pyproject.toml | 681 bytes | 项目配置 |
| server.py | 478 行 | 核心实现 |
| setup.sh | ~100 行 | 部署脚本 |

### B. MCP 工具参数详情

#### spawn_workers

```json
{
  "workers": [{
    "project_path": "string (required)",
    "bead": "string (optional)",
    "annotation": "string (optional)",
    "prompt": "string (optional)",
    "use_worktree": "boolean (default: true)",
    "skip_permissions": "boolean (default: false)",
    "name": "string (optional)"
  }],
  "layout": "auto | new (default: auto)"
}
```

#### message_workers

```json
{
  "session_ids": ["string (required)"],
  "message": "string (required)",
  "wait_mode": "none | any | all (default: none)"
}
```

### C. 参考资源

- MCP Protocol: https://modelcontextprotocol.io/
- iTerm2 Python API: https://iterm2.com/python-api
- Git Worktree: https://git-scm.com/docs/git-worktree

---

*报告生成时间: 2026-02-05 12:16 GMT+8*
*审查工具: Claude Code Review*
