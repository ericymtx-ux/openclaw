# Morning Brief 每日早间简报系统

**创建日期**: 2026-02-03
**状态**: 进行中 (Proactive Coder)
**优先级**: P1
**负责人**: Monday (AI Autonomous)
**预估总工时**: 12 小时

---

## 需求概述

每日 08:00 自动生成并发送早间简报，包含天气、YouTube 趋势、任务列表、自动化任务推荐、趋势故事、生产力建议。

---

## 实现方案

### 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Cron Trigger (08:00)                  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    MorningBrief Agent                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Weather  │ │ YouTube  │ │  Tasks   │ │ Trending │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│          │          │          │          │            │
│          └──────────┴──────────┴──────────┘            │
│                          │                              │
│                          ▼                              │
│               ┌─────────────────────┐                   │
│               │  Report Generator   │                   │
│               └─────────────────────┘                   │
│                          │                              │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Telegram Send                         │
└─────────────────────────────────────────────────────────┘
```

### 模块实现

| 模块 | 实现方式 | 依赖 |
|------|----------|------|
| 天气 | weather skill | 已存在 |
| YouTube | YouTube Data API + RSS | 新开发 |
| 任务列表 | 读取 BOT_TASKS.md | 已存在 |
| 趋势聚合 | Web Search + 规则过滤 | 已存在 |
| 报告生成 | Agent Template | 新开发 |
| Telegram 发送 | message tool | 已存在 |

---

## 任务拆分

### Phase 1: 基础架构 (4h)

#### T1.1: 创建 Morning Brief Agent 模板
- **工时**: 1h
- **验收**: `agents/morning_brief.py` 存在
- **内容**:
  - Agent 配置
  - 输入参数定义
  - 输出格式定义

```python
# agents/morning_brief.py
from datetime import datetime
from typing import Dict, List

class MorningBriefAgent:
    def __init__(self):
        self.weather_skill = load_skill("weather")
        self.youtube_skill = YouTubeTrending()
        self.tasks_skill = TaskLoader()
        self.trending_skill = TrendingCollector()

    def generate(self) -> str:
        """生成早间简报"""
        weather = self.get_weather()
        youtube = self.get_youtube()
        tasks = self.get_tasks()
        trending = self.get_trending()

        return format_brief(weather, youtube, tasks, trending)
```

#### T1.2: 实现天气模块集成
- **工时**: 0.5h
- **验收**: 天气 skill 返回格式正确
- **内容**:
  - 调用 weather skill
  - 格式化天气信息

#### T1.3: 实现任务列表模块
- **工时**: 0.5h
- **验收**: 正确读取 BOT_TASKS.md
- **内容**:
  - 解析任务列表
  - 按优先级排序
  - 筛选今日任务

#### T1.4: 创建报告模板
- **工时**: 1h
- **验收**: Markdown 模板完整
- **内容**:
  - 天气格式化
  - 任务列表格式化
  - 趋势摘要格式化

### Phase 2: YouTube + 趋势模块 (4h)

#### T2.1: 实现 YouTube Trending 抓取
- **工时**: 2h
- **验收**: 返回 5 个视频，包含标题、频道、观看量
- **实现**:
  - YouTube Data API (或 RSS)
  - 按兴趣标签过滤
  - 错误处理

```python
class YouTubeTrending:
    def __init__(self):
        self.interests = [
            "AI", "LLM", "machine learning",
            "quant trading", "investment",
            "independent developer", "SaaS",
            "productivity tools", "Python"
        ]

    def fetch(self, max_results: int = 5) -> List[Dict]:
        # 实现 YouTube API 调用
        pass

    def filter_by_interests(self, videos: List[Dict]) -> List[Dict]:
        # 按兴趣过滤
        pass
```

#### T2.2: 实现趋势故事聚合
- **工时**: 2h
- **验收**: 返回 3-5 条趋势故事
- **实现**:
  - Twitter/X Trending (Web Search)
  - Hacker News Top
  - V2EX 热门
  - 按兴趣过滤

### Phase 3: 自动化推荐 + Cron (4h)

#### T3.1: 实现自动化任务推荐算法
- **工时**: 2h
- **验收**: 正确识别可自动完成的任务
- **实现**:
  - 任务分类 (可自动 / 需确认)
  - 能力匹配
  - 风险评估

```python
def suggest_auto_tasks(tasks: List[Task]) -> List[Task]:
    """
    判断任务是否可以自动完成

    可自动:
    - 有明确验收标准
    - 不需要用户决策
    - 有现有代码库参考
    - 不涉及外部依赖

    返回: 可自动完成的任务列表
    """
    auto_tasks = []
    for task in tasks:
        if can_auto_complete(task):
            auto_tasks.append(task)
    return auto_tasks
```

#### T3.2: 配置 Cron 定时任务
- **工时**: 1h
- **验收**: 每日 08:00 自动触发
- **配置**:

```json
{
  "name": "morning-brief",
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "/morning-brief"
  },
  "sessionTarget": "main",
  "enabled": true
}
```

#### T3.3: 端到端测试
- **工时**: 1h
- **验收**: 完整流程测试通过
- **内容**:
  - 手动触发测试
  - 检查输出格式
  - 验证发送成功

---

## 验收标准 (DoD)

- [ ] Cron 任务配置正确
- [ ] 天气模块返回格式化信息
- [ ] YouTube 返回 5 个视频
- [ ] 任务列表正确读取 BOT_TASKS.md
- [ ] 自动化任务推荐准确
- [ ] 报告格式符合模板
- [ ] Telegram 发送成功
- [ ] 端到端流程测试通过

---

## 依赖

| 依赖 | 状态 | 说明 |
|------|------|------|
| weather skill | ✅ 已存在 | 获取天气 |
| Web Search | ✅ 已存在 | 趋势收集 |
| Telegram | ✅ 已存在 | 发送渠道 |
| BOT_TASKS.md | ✅ 已存在 | 任务来源 |

---

## 风险

| 风险 | 应对措施 |
|------|----------|
| YouTube API 限制 | 使用 RSS 备选 |
| 趋势收集失败 | 返回空列表，不阻塞整体 |
| Cron 未触发 | 添加手动触发命令 |

---

## 进度追踪

| 任务 | 状态 | 负责人 | 完成时间 |
|------|------|--------|----------|
| T1.1 Agent 模板 | ✅ | Monday | 2026-02-03 |
| T1.2 天气模块 | 🔄 进行中 | Monday | - |
| T1.3 任务列表 | ✅ | Monday | 2026-02-03 |
| T1.4 报告模板 | ✅ | Monday | 2026-02-03 |
| T2.1 YouTube | 🔄 进行中 | Monday | - |
| T2.2 趋势聚合 | ⏳ | - | - |
| T3.1 自动推荐 | ✅ | Monday | 2026-02-03 |
| T3.2 Cron 配置 | ✅ | Monday | 2026-02-03 |
| T3.3 端到端测试 | ⏳ | - | - |

---

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-02-03 | Morning Brief Agent 基础架构完成 (T1.1, T1.3, T1.4, T3.1) |
| 2026-02-03 | Cron 已配置 (每日 08:00) |
| 2026-02-03 | 开始 Phase 1: 创建 Morning Brief Agent 模板 |
| 2026-02-03 | 添加到 Proactive Coder 自动开发队列 |

---

*创建时间: 2026-02-03*
