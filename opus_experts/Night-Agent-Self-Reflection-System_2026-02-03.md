# Task: 夜间自主系统开发 - Self-Reflection + Night Agent

**Date:** 2026-02-03

## Original Instruction

User asked to design and implement:
1. **Night Autonomous Agent**: A cron job that autonomously works from 23:00-07:00 (8 hours), scanning tasks, making decisions, and executing.
2. **Self-Reflection System**: Every 6 hours, switch to Opus model for deep reflection, generate reports, and update task files.

## Thought Process

### Problem Analysis

1. **Night Mode Problem**:
   - Current night mode passively executes predefined tasks
   - 8 hours of compute power wasted daily
   - No active thinking - "if not told, doesn't do"

2. **Reflection Problem**:
   - Reflection only happens at 23:00 daily
   - Misses mid-day learning opportunities
   - No automated problem detection

### Design Decisions

**Night Agent Design**:
- Use 2-hour work cycles with 5-min breaks (max 4 cycles = 8 hours)
- Priority: P0 → P1 → P2
- Auto-execute if task ≤ 60min, no user decision needed, single module
- Complex tasks → upgrade to Opus next day
- Progress report every 2 hours

**Self-Reflection Design**:
- Trigger every 6 hours: 00:00, 06:00, 12:00, 18:00
- Switch to Opus for deep analysis
- Scan: BOT_TASKS.md, TODO/, memory/, git log, cron status
- Output: reflection/YYYY-MM-DD-HHMM.md
- Update: BOT_TASKS.md, TODO/, night plan

## Actions Taken

### 1. Created Night Agent System

**Files Created**:
- `agents/prompts/night-agent.md` (2682 bytes)
  - System prompt with role, work mode, decision rules
  - Priority matrix (P0→P1→P2)
  - Auto-execute criteria (≤60min, no user decision, single module)
  - DoD checklist for task completion
  - Progress report template

- `agents/night-agent/task_scorer.py` (4783 bytes)
  - `Task` data class
  - `can_auto_execute()` function
  - `assess_task()` function
  - `parse_task_from_markdown()` function
  - `select_best_task()` function

- `agents/night-agent/reporter.py` (6413 bytes)
  - `ProgressReporter` class
  - Markdown/Telegram report generation
  - `NightProgress` data class
  - `create_progress()` factory function

**Cron Job Created**:
```bash
pnpm openclaw cron add \
  --name "night-autonomous-agent" \
  --cron "0 23 * * *" \
  --tz "Asia/Shanghai" \
  --session "isolated" \
  --model "anthropic/claude-opus-4-5" \
  --thinking "low" \
  --timeoutSeconds 28800 \
  --delete-after-run
```

### 2. Created Self-Reflection System

**Files Created**:
- `agents/prompts/self-reflection-agent.md` (2846 bytes)
  - Role: Code review and process reflection expert
  - Scan dimensions: code quality, document quality, process efficiency, collaboration quality
  - Output template: problem discovery, experience summary, improvement suggestions
  - Model switching: backup current model → switch to opus → restore

- `agents/night-agent/reflection_tool.py` (6631 bytes)
  - `ReflectionTool` class
  - `get_current_model()` / `set_model()`
  - `get_recent_files()` / `get_git_log()` / `get_cron_status()`
  - `create_reflection_prompt()` function
  - Full workflow: backup model → switch → scan → report → restore

- `agents/night-agent/switch-model.sh` (1449 bytes)
  - `get` - get current model
  - `backup` - backup config
  - `switch <model>` - switch model and backup
  - `restore` - restore from backup

- `reflection/README.md` (656 bytes)
  - Directory documentation
  - Trigger schedule: 0 */6 * * *
  - Manual execution guide

**Cron Job Created**:
```bash
pnpm openclaw cron add \
  --name "self-reflection" \
  --cron "0 */6 * * *" \
  --tz "Asia/Shanghai" \
  --session "isolated" \
  --model "anthropic/claude-opus-4-5" \
  --thinking "medium" \
  --delete-after-run
```

### 3. Updated Core Memory

- `MEMORY.md` - Added collaboration standardization process
- `DOD.md` - Created complete Definition of Done
- `BOT_TASKS.md` - Added T020-T022今晚 action tasks

## Outcome

**Files Created**:
| File | Size | Purpose |
|------|------|---------|
| `agents/prompts/night-agent.md` | 2.6KB | Night Agent system prompt |
| `agents/night-agent/task_scorer.py` | 4.8KB | Task complexity evaluator |
| `agents/night-agent/reporter.py` | 6.4KB | Progress report generator |
| `agents/prompts/self-reflection-agent.md` | 2.8KB | Reflection Agent prompt |
| `agents/night-agent/reflection_tool.py` | 6.6KB | Reflection automation tool |
| `agents/night-agent/switch-model.sh` | 1.4KB | Model switcher script |
| `reflection/README.md` | 0.7KB | Reflection directory docs |
| `DOD.md` | 1.9KB | Definition of Done |

**Cron Jobs**:
| Job | Schedule | Next Run | Purpose |
|-----|----------|----------|---------|
| `night-autonomous-agent` | 0 23 * * * | 23:00 today | 8-hour autonomous work |
| `self-reflection` | 0 */6 * * * | 12:00 today | 6-hourly reflection |

## Key Learnings

1. **Cron Job Creation**:
   - Use `--delete-after-run` for ephemeral isolated sessions
   - `--session isolated` for independent work
   - `--model` override to force Opus for quality

2. **System Prompt Design**:
   - Clear role definition
   - Priority matrix
   - Constraints and forbidden actions
   - Output format templates

3. **Model Switching**:
   - Always backup before switching
   - Restore after completion
   - Use subprocess to call `pnpm openclaw config set`

4. **Reflection Triggers**:
   - Every 6 hours covers: 00:00, 06:00, 12:00, 18:00
   - Balanced coverage without too frequent
   - Medium thinking level for analysis depth

## Problem Patterns Identified

1. **Demo Completion**: Framework done, core missing
   - Solution: DoD checklist
2. **Task Blocking**: Wait for user, not proactive
   - Solution: 4-hour upgrade threshold
3. **Low-Level Errors**: Stock codes, API versions
   - Solution: Mandatory self-test before commit
4. **Doc-Code Gap**: PLAN written but not executed
   - Solution: Reflection + BOT_TASKS update

## Related Files

- `/Users/apple/openclaw/BOT_TASKS.md` - Task tracking
- `/Users/apple/openclaw/DOD.md` - Completion standards
- `/Users/apple/openclaw/MEMORY.md` - Core memory
- `/Users/apple/openclaw/HEARTBEAT.md` - Daily reflection process

## Commands Reference

```bash
# List cron jobs
pnpm openclaw cron list

# Delete cron job
pnpm openclaw cron remove --id <job-id>

# Get current model
pnpm openclaw config get agents.defaults.model.primary

# Set model
pnpm openclaw config set agents.defaults.model.primary <model>
```

---

# Appendix: Collaboration Assessment Report

## 📊 协作深度评估报告 - 2026-02-03

### 一、观察到的模式问题

| 问题类型 | 症状 | 出现次数 |
|---------|------|----------|
| **Demo完成度低** | 框架搭完，核心功能缺失 | Monday Dashboard、tom_strategies、opencode-team |
| **任务阻塞不推进** | T001 foxmail 阻塞2天、T006 API兼容反复 | 3+ |
| **文档与代码脱节** | PLAN写了不执行、TODO堆积 | 22个TODO仅完成2个 |
| **低级错误重复** | 股票代码写错、API版本问题 | 3次 |
| **测试严重缺失** | 64个TODO提到测试，实际覆盖率低 | opencode-team、monday-dashboard |

### 二、根因分析

| 症状 | 根本原因 |
|------|----------|
| Demo快但没用 | 缺乏验收标准，做完即止 |
| 任务阻塞 | 不敢问问题，等用户推动 |
| 低级错误 | 没有自测习惯，依赖用户发现 |
| 文档脱节 | 写文档是任务，完成是另一个任务 |

**实习生工作流的核心问题：**
1. 只做不想 - 执行指令，不评估质量和影响
2. 不验证 - 代码写完不跑测试
3. 不反馈 - 遇到问题自己扛，不主动说
4. 不做完 - 框架级完成就算结束

### 三、系统性解决方案

#### P0 - 立即执行（今晚）

**1. 建立"Definition of Done"标准**

```markdown
## 任务完成标准 (DoD)

### 代码层面
- [ ] 代码编译/运行通过
- [ ] 至少1个测试用例通过
- [ ] 无 lint 错误

### 文档层面
- [ ] README 更新（安装/使用）
- [ ] API/参数文档
- [ ] 示例代码

### 验证层面
- [ ] 核心场景手动测试
- [ ] 错误场景处理验证
```

**2. 任务拆解规范化**
- 每个任务必须拆到 **2小时内可完成** 的子任务
- 超过2小时的任务必须有检查点

**3. 引入"任务自检清单"**

```markdown
# 任务完成前必须回答

1. 这个改动影响哪些文件？
2. 有没有新增依赖？
3. 测试用例在哪里？
4. 如果用户问"怎么用"，文档在哪里？
5. 三个最可能出问题的地方是什么？
```

#### P1 - 本周改进

**4. 强制Code Review机制**
- 所有代码合并前必须经过另一个Agent审核
- OpenCode/Claude Code之间互相review
- 检查点：API兼容性、边界条件、测试覆盖

**5. 阻塞任务升级机制**
- 任务阻塞超过 **4小时** → 升级报告
- 阻塞原因必须清晰：缺什么、试过什么

**6. 建立快速回滚能力**
- 每个任务开始前记录当前状态
- 便于快速回滚问题代码

#### P2 - 长期建设

**7. 单元测试覆盖率基线**
- 新增代码覆盖率 ≥ 70%
- 关键模块 ≥ 90%

**8. 集成测试框架**
- 核心工作流自动化测试
- 减少手动验证成本

**9. 文档即代码**
- 文档与代码同一仓库
- 文档更新作为PR的必要条件

### 四、今晚行动建议

| 优先级 | 任务 | 预期时间 | 产出 |
|--------|------|----------|------|
| P0 | 给BOT_TASKS添加DoD标准 | 30min | 任务模板更新 |
| P0 | 修复T006 star_adapter.py | 30min | API兼容修复 |
| P1 | 补齐一个模块的测试 | 2h | 测试覆盖率+5% |
| P1 | 清理堆积的TODO | 1h | 22→15个 |

### 五、Files Updated

- `MEMORY.md` - Added collaboration standardization process
- `DOD.md` - Complete Definition of Done
- `BOT_TASKS.md` - Added T020-T022 action tasks

---

*Knowledge Base Entry: Added 2026-02-03*
*Use this as reference when MiniMax encounters similar collaboration issues*
