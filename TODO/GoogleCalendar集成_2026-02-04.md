# Google Calendar 集成 - 开发任务

**创建日期**: 2026-02-04
**状态**: ✅ 已完成 (OAuth + 基础功能)
**优先级**: P2

---

## ✅ 已完成

### Phase 1: 基础认证 ✅

- [x] 创建 `scripts/google_calendar.py` - CLI 工具
- [x] 实现 OAuth 2.0 认证流程
- [x] 保存/加载 token 到 `~/.openclaw/tokens/google_calendar.token`
- [x] 测试认证流程

### Phase 2: 核心功能 ✅

- [x] `calendar today` - 查看今日事件
- [x] `calendar week` - 查看本周事件

### Phase 3: OpenClaw 集成 ✅

- [x] 创建 `agents/morning_brief/calendar_module.py`
- [x] 集成到 `MorningBriefReport`
- [x] 支持 Telegram 消息格式输出

---

## 使用方法

### 读取日历

```bash
# 查看今日事件
python3 scripts/google_calendar.py today

# 查看本周事件
python3 scripts/google_calendar.py week
```

### 重新授权（如果 token 过期）

```bash
python3 scripts/google_calendar_auth.py
# 访问生成的链接授权
```
