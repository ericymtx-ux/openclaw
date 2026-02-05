# NIGHT_TASKS.md - 夜间任务队列

## 任务队列

| 优先级 | 任务 | 预估时间 | 状态 |
|--------|------|----------|------|
| ✅ | Tushare接入 | 30min | done |
| ✅ | 每日报告生成器 | 30min | done |
| ✅ | Tushare接口研读+扩展 | 30min | done |
| ❌ | 雪球HTTP客户端 | 框架完成 | disabled (API被封) |
| ✅ | TODO目录整理 | 15min | done |
| ✅ | ideas目录补充细节 | 30min | done |

## 今晚计划 (2026-02-03 23:00)

### P0 优先
1. **T024: Morning Brief Agent 实现** (3h)
   - 天气模块集成 (weather skill)
   - 任务列表模块 (BOT_TASKS.md 解析)
   - Telegram 发送
   - Cron 配置 (每日 08:00)

2. **T025: Gateway 健康检查** (30min)
   - 检查 gateway 进程状态
   - 验证 cron 任务执行
   - 添加健康检查 cron

### P1 次优先
3. **代码提交** - T020-T023 相关变更
4. **Proactive Coder 框架** - 任务筛选算法设计

## 雪球项目状态 (已禁用)

**原因**: 雪球 API 有严格的 IP/行为检测，HTTP 请求被 403 封禁

**解决方案**: 
- 方案1: 使用 Playwright 浏览器抓取 (需开发)
- 方案2: 改用其他数据源 (东方财富/同花顺)
- 方案3: 等待获取有效 Cookie

**项目位置**: `projects/xueqiu/` (保留代码，待后续处理)

## 任务模板

```markdown
### [任务名称]
- **优先级**: P0/P1/P2
- **预估时间**: Xmin
- **状态**: pending | running | done | failed | blocked
- **阻塞原因**: (如有)
- **产出**: (完成后填写)
```

## 长期任务池

- 代码审查：检查OpenClaw代码质量
- 文档更新：补充缺失文档
- 测试补充：增加单元测试覆盖
- 竞品调研：分析同类产品
- 用户反馈：整理收集到的反馈

---
*每晚23:00自动执行队列中的pending任务*
*完成后通过Telegram通知*
