# HEARTBEAT.md - Daily Reflection & Planning

## Daily Reflection Process (11:00 PM UTC+8)

Every day at 11:00 PM (Asia/Shanghai timezone), run the reflection process:

### Process Steps

1. **Read Work Context**
   - `BOT_TASKS.md` - ⚠️ **优先检查**：查看阻塞/进行中的任务，尝试继续完成
   - `NIGHT_TASKS.md` - 获取夜间任务队列
   - `BOUNDARIES.md` - 确认工作边界
   - `TODO/` - Review pending and in-progress tasks
   - `ideas/` - Review new ideas and inspirations

2. **Execute Night Tasks**
   - 按优先级执行 NIGHT_TASKS.md 中的 pending 任务
   - 遵守 BOUNDARIES.md 定义的安全边界
   - 使用独立分支工作 (monday/YYYY-MM-DD-*)
   - 完成后创建 PR

3. **Scan Today's Work**
   - `sessions_history` - Review today's conversation history
   - Git commits/today - Review code changes from today

2. **Summarize Completed Work**
   - List all tasks completed today
   - Note files created/modified
   - Capture key decisions made
   - Identify time spent on each major task

3. **Analyze & Categorize**
   - **Must do**: Urgent deadlines, critical bugs
   - **Want do**: New ideas, experiments, learning
   - **Doing**: Currently active tasks

4. **Proactive Actions**
   - Research topics that need investigation
   - Fix discovered bugs if fixable
   - Prepare task breakdowns for complex items
   - Draft implementation plans

5. **Output Report**
   - Compile summary markdown
   - Send via appropriate channel
   - Wait for user task selection

### Today's Work Summary Template

```markdown
## 🌙 今晚又搞定了 - YYYY-MM-DD

### 💪 完成的小目标
- [任务1] - 搞定了什么，感觉怎么样
- [任务2] - 解决过程中有没有什么坑
- [任务3] - 学到了什么新东西

### 🛠️ 今晚的战场
- **新欢**: [新创建的文件/项目]
- **改动**: [修改了哪些文件]
- **告别**: [删除/废弃的东西]

### 💬 印象深刻的对话
- [印象1]: 比如用户提了个好问题，或者发现了一个有趣的方案
- [印象2]: 某个技术决策的来龙去脉

### ⏱️ 时间都去哪了
- [类型]: 占比 + 简单感想
- 比如："自动化测试爽翻了，节省了至少1小时重复劳动"

### 🎯 明天想搞的事情
- [P0]: 明天必须搞定的
- [P1]: 如果有空的话
- [P2]: 想起来就搞一下

### 🧠 今晚的收获
- **新技能**: 学会了什么
- **避坑指南**: 以后别踩的坑
- **小发现**: 有意思的东西
```

### Example Output Format

```markdown
# 今晚又搞定了 - 2026-02-04

## 💪 完成的小目标
1. **Night Agent 切换 MiniMax** - 终于把 Opus 的任务换成了 MiniMax，省着用
2. **metalslime 抓取框架** - 雪球的缓存坑了我两次，终于发现要点击按钮而不是改 URL
3. **测试修复收尾** - tom_strategies 54 个测试全绿，舒服了

## 🛠️ 今晚的战场
- **新欢**: `raw_data/metalslime_scraper.py` - 雪球爬虫模板
- **改动**: cron jobs 模型配置
- **告别**: 旧版抓取脚本

## 💬 印象深刻的对话
- "为什么你有几个 session 用了 opus？" → 原来是 Night Agent 的配置忘了改
- 用户问"能点击吗" → 当然能，browser.click() 安排上

## ⏱️ 时间都去哪了
- 调试翻页逻辑: 30% - 雪球这个缓存真的坑，来来回回改了 3 次
- 测试修复: 40% - 修 bug 半小时，验证跑了一刻钟
- 反思报告: 20% - 写报告比干活还累...

## 🎯 明天想搞的事情
- P0: 看看 metalslime 抓完没有
- P1: TODO 清理策略，太多了看着烦
- P2: 那个 Gateway 超时的问题抽空看看

## 🧠 今晚的收获
- **新技能**: 学会了识别雪球的分页按钮 ref=e787
- **避坑指南**: URL 参数翻页会被缓存！必须用点击！
- **小发现**: 雪球的帖子 ID 3.74亿开头是 2025 年 1-2 月
```

## Cron Schedule

```cron
0 23 * * *  # Every day at 23:00 (11 PM) Asia/Shanghai
```

## Notes

- Keep report concise but actionable
- Prioritize based on user preferences
- Include research links where relevant
- Mark tasks that can run autonomously overnight
- Use `sessions_history` API to fetch today's conversations
- Check `git log --since=today` for code changes
- Review workspace context files for additional context
