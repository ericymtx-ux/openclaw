# Everything Claude Code 安装配置

**创建日期**: 2026-02-03
**状态**: 待安装
**优先级**: P2
**预估工时**: 30 分钟

---

## 需求概述

安装配置 Everything Claude Code 插件集，获取：
- 15+ 专用代理 (code-reviewer, planner, security-reviewer 等)
- 30+ 工作流技能 (TDD, coding-standards, backend-patterns 等)
- 20+ 斜杠命令 (/plan, /tdd, /code-review, /e2e 等)
- 全局规则 (安全、编码风格、测试、Git 流程等)

---

## 安装步骤

### 步骤 1: 安装插件

```bash
# 添加到市场
/plugin marketplace add affaan-m/everything-claude-code

# 安装插件
/plugin install everything-claude-code@everything-claude-code
```

### 步骤 2: 手动安装规则 (必需)

```bash
# 克隆仓库
git clone https://github.com/affaan-m/everything-claude-code.git

# 复制规则 (应用于所有项目)
cp -r everything-claude-code/rules/* ~/.claude/rules/

# 可选：复制代理、命令、技能
cp everything-claude-code/agents/*.md ~/.claude/agents/
cp everything-claude-code/commands/*.md ~/.claude/commands/
cp -r everything-claude-code/skills/* ~/.claude/skills/
```

### 步骤 3: 配置 MCP (可选)

将 `mcp-configs/mcp-servers.json` 中需要的条目复制到 `~/.claude.json`

---

## 目录结构

| 目录路径 | 用途 |
|----------|------|
| `~/.claude/agents/` | 子代理定义 |
| `~/.claude/rules/` | 全局规则 |
| `~/.claude/commands/` | 斜杠命令 |
| `~/.claude/skills/` | 工作流技能 |

---

## 核心命令

| 命令 | 用途 |
|------|------|
| `/plan` | 生成实现计划 |
| `/tdd` | TDD 工作流 |
| `/code-review` | 深度代码审查 |
| `/e2e` | E2E 测试 |
| `/verify` | 验证循环 |

---

## 进度追踪

| 任务 | 状态 | 备注 |
|------|------|------|
| 克隆仓库 | ⏳ | - |
| 安装插件 | ⏳ | - |
| 安装规则 | ⏳ | - |
| 配置 MCP | ⏳ | 可选 |

---

*创建时间: 2026-02-03*
