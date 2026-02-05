# 🌙 Unified Night Work System

**统一夜间工作系统** - 渐进合并现有架构

## 📊 合并状态

| 组件 | 状态 | 说明 |
|------|------|------|
| NIGHT_WORK_SYSTEM.md | ✅ 完成 | 架构设计文档 |
| night_work_agent.py | ✅ 完成 | 主入口 + 整合代码 |
| scanner.py | ✅ 完成 | 统一任务扫描器 |
| pr_creator.py | ✅ 完成 | PR 自动创建器 |
| scheduler.py | ✅ 完成 | 任务调度器 |
| task_scorer.py | 🔄 复用 | 已有，复用 |
| reporter.py | 🔄 复用 | 已有，复用 |

**总进度**: 5/7 核心组件完成 (70%)

## 📁 文件结构

```
agents/night-work/
├── __init__.py                    # 导出
├── NIGHT_WORK_SYSTEM.md           # 架构设计
├── night_work_agent.py            # 主入口 ⬅️ 新
├── scanner.py                     # 任务扫描 ⬅️ 新
├── pr_creator.py                  # PR 创建 ⬅️ 新
├── scheduler.py                   # 任务调度 ⬅️ 新
├── task_scorer.py                 # 复用已有
├── reporter.py                    # 复用已有
├── reflection_tool.py             # 独立运行
├── templates/
└── tests/
```

## 🚀 使用方式

### 手动触发

```bash
cd /Users/apple/openclaw
python -m agents.night_work.night_work_agent
```

### Cron 配置

```bash
openclaw cron add --name "night-work" \
  --schedule "0 23 * * *" \
  --payload '/night-work'
```

## 📈 任务来源优先级

| 优先级 | 来源 | 权重 |
|--------|------|------|
| 1 | NIGHT_TASKS.md | 1.0 |
| 2 | BOT_TASKS.md | 0.8 |
| 3 | TODO/*.md | 0.6 |
| 4 | ideas/*.md | 0.4 |

## 🔧 核心功能

1. **任务扫描**: 扫描所有任务来源
2. **任务筛选**: 判断是否可自动完成
3. **优先级排序**: P0 > P1 > P2 > P3
4. **执行调度**: OpenCode / Claude Code
5. **进度跟踪**: 实时更新 + 报告生成
6. **PR 创建**: 自动创建分支 + 提交 + PR

## 📝 进度追踪

- ✅ 架构设计
- ✅ 主入口 (night_work_agent.py)
- ✅ 任务扫描器 (scanner.py)
- ✅ PR 创建器 (pr_creator.py)
- ✅ 任务调度器 (scheduler.py)
- ⏳ OpenCode 集成
- ⏳ Claude Code 集成
- ⏳ 端到端测试

## 📚 相关文档

- [Proactive Coder 设计方案](/Users/apple/openclaw/TODO/ProactiveCoder主动编码工作流_2026-02-03.md)
- [现有夜间开发回顾](/Users/apple/openclaw/MEMORY.md)
- [OpenClaw Cron 文档](/Users/apple/openclaw/docs/cli/cron.md)

---

*最后更新: 2026-02-03*
