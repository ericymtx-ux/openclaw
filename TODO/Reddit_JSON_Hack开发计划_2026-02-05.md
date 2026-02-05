# Reddit JSON Hack 开发计划

**创建日期**: 2026-02-05
**优先级**: P2
**预估时间**: 6 小时

---

## 目标

创建 Reddit 痛点挖掘工具，发现创业机会。

---

## 功能规划

### Phase 1: 基础抓取 (3h)

- [ ] Reddit JSON 抓取模块
- [ ] 多版块并行扫描
- [ ] 痛点关键词提取
- [ ] 输出结构化数据

### Phase 2: 分析增强 (2h)

- [ ] 痛点分类 (功能/价格/体验/缺失)
- [ ] 需求优先级排序
- [ ] 竞品提及统计
- [ ] 趋势分析

### Phase 3: 集成 (1h)

- [ ] 集成到 last30days skill
- [ ] Telegram 报告格式
- [ ] Cron 定时监控

---

## 技术栈

- Python + requests + jq
- OpenClaw Browser skill (备选)
- 现有 himalaya skill 结构参考

---

## 输出

1. `scripts/reddit_painpoint.py` - 抓取工具
2. `agents/reddit_analyzer/` - 分析 Agent
3. 更新 `ideas/Reddit_JSON_Hack_*.md`

---

*Plan created: 2026-02-05*
