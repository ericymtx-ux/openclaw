# Reddit JSON Hack - 用户痛点挖掘方法论

**创建日期**: 2026-02-05
**标签**: 创业, Reddit, 用户研究, 机会发现
**优先级**: P2

---

## 核心方法

```
1. 找到目标细分版块 (subreddit)
2. 帖子 URL + /.json
3. 抓取完整对话数据
4. 分析痛点、需求、抱怨
5. 发现创业机会
```

---

## 应用场景

| 场景 | 示例 |
|------|------|
| 痛点发现 | "这个功能太难用了" → 改进机会 |
| 需求挖掘 | "希望有 X 功能" → 新产品方向 |
| 竞品分析 | 用户抱怨竞品的问题 → 差异化机会 |
| 市场验证 | 多人抱怨同一问题 → 值得投入 |

---

## 技术实现

```bash
# 示例: r/startups 板块
curl -s "https://www.reddit.com/r/startups/.json" | jq '.data.children[].data' | head -100

# 提取痛点关键词
jq '[.title, .selfreddit] | join(": ")' posts.json
```

---

## 商业价值

- **低成本市场验证**
- **发现 $10k MRR 机会**
- **理解真实用户需求**
- **发现被忽视的细分市场**

---

## 集成建议

1. **扩展 last30days skill**
   - 添加 Reddit JSON 抓取模块
   - 自动痛点/需求分类
   - 生成机会报告

2. **独立创业情报工具**
   - 监控目标版块
   - 痛点趋势分析
   - 机会优先级排序

---

## 参考资源

- Reddit API: https://www.reddit.com/dev/api
- jq 用法: https://stedolan.github.io/jq/tutorial/

---

*来源: @ssaarrttssee (Telegram, 2026-02-05)*
