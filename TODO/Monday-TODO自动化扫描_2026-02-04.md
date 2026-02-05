# Monday-TODO 自动化扫描 Agent

**创建日期**: 2026-02-04
**状态**: ✅ Phase 1-3 已完成
**优先级**: P1

---

## ✅ 已完成

### Phase 1: 日历扫描 ✅
- [x] CalendarScanner 实现
- [x] 读取 Monday-TODO 日历
- [x] 筛选未完成任务

### Phase 2: 聊天记录检查 ✅
- [x] ChatHistoryChecker 实现
- [x] sessions_history 集成
- [x] 任务完成状态判断

### Phase 3: 自动化扫描 ✅
- [x] MondayTodoAgent 主逻辑
- [x] Cron 配置: `0 * * * *` (每小时)
- [x] 命令路由: `/monday-todo-scan`, `/monday-todo-list`

---

## 待完成

### Phase 4: 任务执行 (OpenCode)
- [ ] OpenCodeTask 实现
- [ ] dod.md 流程集成
- [ ] 项目文档生成

### Phase 5: 反思处理
- [ ] ReflectionParser 完善
- [ ] 反思内容添加到日历
- [ ] 经验教训记录

---

## 使用方法

### 命令

```bash
# 手动触发扫描
python3 agents/monday_todo_agent/monday_todo_agent.py --scan

# 列出待完成任务
python3 agents/monday_todo_agent/monday_todo_agent.py --list
```

### Telegram 命令

- `/monday-todo-scan` - 扫描并处理
- `/monday-todo-list` - 列出待完成

### Cron
- **Monday-TODO Scanner**: 每小时执行
- ID: `1ff7a8dd-131f-42a2-a86f-2efdfa5df182`

---

## 文件结构

```
agents/monday_todo_agent/
├── __init__.py
├── monday_todo_agent.py      # 主 Agent
├── calendar_scanner.py       # 日历扫描
└── chat_history_checker.py   # 聊天记录检查
```

---

## 扫描结果示例

```json
{
  "incomplete": 5,
  "completed_in_chat": 0,
  "pending_execution": 5,
  "reflections_found": 0,
  "reflections_added": 0
}
```

---

*最后更新: 2026-02-04 23:47*
