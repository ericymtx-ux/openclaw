# Morning Brief System - 每日早间简报系统

**创建日期**: 2026-02-03
**状态**: 待开发
**执行时间**: 每日 08:00 (Asia/Shanghai)

---

## 需求概述

每天早上 8:00 自动生成并发送早间简报，包含以下内容：

1. **当日天气** - 本地天气预报
2. **YouTube 趋势** - 基于兴趣的 trending 视频
3. **任务列表** - BOT_TASKS.md 中的待办
4. **我可以完成的任务** - 基于我的能力预估可自动完成的工作
5. **趋势故事** - 基于兴趣的新闻/趋势
6. **生产力建议** - 提升今日效率的推荐

---

## 触发条件

```cron
0 8 * * *  # 每天 08:00 Asia/Shanghai
```

---

## 简报内容模板

```markdown
# ☀️ Morning Brief - YYYY-MM-DD

## 🌤️ 今日天气
- [天气状况] [温度] [风力]
- 出行建议: [简短建议]

## 📺 YouTube Trending
1. **[视频标题]**
   - 频道: [频道名]
   - 观看: [播放量]
   - 链接: [URL]
2. ...

## 📋 今日任务
### 需关注
- [ ] 任务1 (优先级)
- [ ] 任务2

### 自动化任务
- 我将为你完成:
  - [ ] 任务A
  - [ ] 任务B

## 🔥 Trending Stories
1. [话题1] - [简述]
2. [话题2] - [简述]

## 💡 生产力建议
1. [建议1]
2. [建议2]

---
*Generated at 08:00*
```

---

## 模块实现

### 1. 天气模块

**依赖**: `weather` skill (已存在)

```python
from skills.weather import get_weather

def get_morning_weather():
    return get_weather()  # 返回格式化天气信息
```

### 2. YouTube Trending 模块

**实现方式**: YouTube Data API 或 RSS 订阅

**兴趣标签**:
- AI/LLM/机器学习
- 量化交易/投资
- 独立开发者/SaaS
- 生产效率工具
- Python/编程

```python
def get_youtube_trending():
    # 搜索 YouTube trending
    videos = youtube.search().trending(
        max_results=5,
        category="tech",  # 或自定义关键词
        region="US"
    )
    return format_videos(videos)
```

### 3. 任务列表模块

**来源**: BOT_TASKS.md

```python
def get_today_tasks():
    tasks = read_bot_tasks()
    pending = [t for t in tasks if t.status == "pending"]
    return format_tasks(pending[:5])
```

### 4. 自动化任务推荐模块

**判断逻辑**: 基于任务类型 + 我的能力

```python
def suggest_auto_tasks():
    """
    判断哪些任务可以自动完成:
    - 代码开发类 → OpenCode
    - 测试/验证 → 自动化测试
    - 文档编写 → 自动生成
    - 数据处理 → 脚本执行
    """
    tasks = get_pending_tasks()
    auto_tasks = []
    
    for task in tasks:
        if can_auto_complete(task):
            auto_tasks.append(task)
    
    return auto_tasks
```

### 5. 趋势故事模块

**来源**:
- Twitter/X Trending
- Hacker News
- V2EX
- Product Hunt

```python
def get_trending_stories():
    stories = []
    
    # Twitter trending
    stories.extend(get_twitter_trending())
    
    # Hacker News
    stories.extend(get_hacker_news_top())
    
    # 按兴趣过滤
    return filter_by_interests(stories)
```

### 6. 生产力建议模块

**规则**:
- 基于时间 (周一/周五 不同策略)
- 基于任务量 (任务多时建议分批)
- 基于历史效率数据

```python
def get_productivity_tips():
    tips = []
    
    # 基础建议
    tips.append("今日有 X 个待办，建议优先处理 P0 任务")
    
    # 基于时间的建议
    if is_monday():
        tips.append("周一适合处理复杂任务")
    elif is_friday():
        tips.append("周五适合收尾和规划")
    
    return tips
```

---

## 发送渠道

**首选**: Telegram
**备用**: 其他配置渠道

```python
def send_morning_brief(brief_content):
    message.send(
        channel="telegram",
        content=brief_content,
        format="markdown"
    )
```

---

## Cron 配置

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

---

## 依赖模块

| 模块 | 状态 | 说明 |
|------|------|------|
| weather skill | ✅ 已存在 | 获取天气 |
| YouTube API | 待开发 | Trending 视频 |
| BOT_TASKS | ✅ 已存在 | 任务列表 |
| Twitter/X | 待开发 | Trending |
| Hacker News | 待开发 | 技术新闻 |
| Telegram | ✅ 已存在 | 发送渠道 |

---

## TODO

- [ ] 实现天气模块集成
- [ ] 实现 YouTube Trending 抓取
- [ ] 实现任务列表格式化
- [ ] 实现自动化任务推荐算法
- [ ] 实现趋势故事聚合
- [ ] 实现生产力建议生成
- [ ] 整合为完整简报
- [ ] 配置 Cron 定时任务
- [ ] 测试端到端流程

---

## 相关文档

- [天气 skill](/Users/apple/openclaw/skills/weather/SKILL.md)
- [Telegram 集成](/Users/apple/openclaw/src/telegram)
- [BOT_TASKS.md](/Users/apple/openclaw/BOT_TASKS.md)

---

*创建时间：2026-02-03*
