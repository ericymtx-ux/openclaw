# T078: Gateway 服务重启

> **优先级**: P0 - 紧急
> **创建时间**: 2026-02-05 12:00
> **状态**: 待执行

---

## 任务描述

重启 Gateway 服务，解决超时问题，恢复 Cron、Telegram、Morning Brief 等自动化任务。

## 问题症状

```
$ pnpm openclaw cron list
Error: gateway timeout after 10000ms

$ pnpm openclaw gateway status
[可能也超时]
```

## 影响范围

- ❌ T010 Telegram 报告集成 (72+ 小时)
- ❌ 股票邮件监控无法验证
- ❌ Morning Brief 无法定时发送
- ❌ 夜间开发任务无法触发
- ❌ 所有 Cron 任务

## 重启步骤

### Step 1: 检查当前状态
```bash
# 检查进程
ps aux | grep openclaw-gateway

# 检查端口
ss -ltnp | grep 18789

# 查看日志
tail -n 50 /tmp/openclaw-gateway.log
```

### Step 2: 强制停止
```bash
# 停止现有进程
pkill -9 -f openclaw-gateway || true

# 确认停止
ps aux | grep openclaw-gateway
```

### Step 3: 启动新实例
```bash
# 启动 Gateway
nohup openclaw gateway run --bind loopback --port 18789 --force > /tmp/openclaw-gateway.log 2>&1 &

# 等待启动
sleep 5
```

### Step 4: 验证
```bash
# 检查状态
openclaw gateway status

# 检查 Cron
pnpm openclaw cron list

# 检查进程
ps aux | grep openclaw-gateway
```

## 验证标准

- [ ] `openclaw gateway status` 返回 running
- [ ] `pnpm openclaw cron list` 正常显示
- [ ] Cron 任务可以手动触发 (`pnpm openclaw cron run <job-id>`)
- [ ] 日志无明显错误

## 预期时间

- 停止: 5 秒
- 启动: 10 秒
- 验证: 30 秒
- 总计: < 1 分钟

## 如果重启失败

### 方案 B: 检查配置文件
```bash
# 检查配置文件
cat ~/.openclaw/openclaw.json | grep -A 5 gateway

# 检查端口占用
lsof -i :18789
```

### 方案 C: 查看完整日志
```bash
# 查看详细日志
cat /tmp/openclaw-gateway.log

# 搜索错误
grep -i error /tmp/openclaw-gateway.log
```

## 相关文件

- `/Users/apple/openclaw/reflection/2026-02-05-1200.md`
- `/Users/apple/openclaw/BOT_TASKS.md`

---

*创建: 2026-02-05 12:00*
