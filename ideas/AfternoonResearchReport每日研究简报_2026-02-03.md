# Afternoon Research Report - 每日研究简报

**创建日期**: 2026-02-03
**状态**: 待开发
**执行时间**: 每日 16:00-18:00 (Asia/Shanghai)

---

## 需求概述

每天下午生成研究简报，帮助用户持续学习和改进。

**内容类型**:
1. **概念深度解析** - 用户感兴趣的技术/业务概念
2. **工作流改进** - 提升协作效率的方法
3. **行业趋势** - 与用户业务相关的动态
4. **竞品分析** - 竞争对手动向
5. **工具推荐** - 提升效率的生产力工具

**触发时间**: 每日 16:00 (下午 4 点)

---

## 研究主题来源

### 优先级排序

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | 用户明确表达的兴趣 | 对话中提到的想了解的概念 |
| 2 | 当前项目相关 | 开发中遇到的技术挑战 |
| 3 | 行业趋势 | AI/LLM/量化交易/独立开发 |
| 4 | 工作流优化 | 基于历史数据分析 |

### 兴趣标签

基于用户资料，优先研究:

```
#AI/LLM
- 大模型训练/推理
- RAG/知识库
- Agent 系统

#量化交易
- 选股策略
- 技术分析
- 情绪指标

#独立开发
- SaaS 增长
- 开发者工具
- 生产力系统

#Python/编程
- 异步编程
- 类型系统
- 测试策略
```

---

## 报告模板

```markdown
# 📊 Afternoon Research Report - YYYY-MM-DD

## 🎯 今日主题

### 主题名称
[一句话描述今日研究主题]

### 研究背景
[为什么研究这个主题]

---

## 📖 核心概念

### 概念 1: [名称]
**定义**: [简明定义]

**详解**:
[3-5 段详细解释]

**应用场景**:
- 场景1
- 场景2

**代码示例**:
```python
# 示例代码
```

### 概念 2: [名称]
...

---

## 🔧 实践指南

### 实现步骤
1. 步骤1
2. 步骤2
3. 步骤3

### 工具推荐
- 工具1: [用途]
- 工具2: [用途]

### 注意事项
- 注意1
- 注意2

---

## 💡 洞察与建议

### 对用户的价值
1. 价值点1
2. 价值点2

### 如何应用
- 应用场景1
- 应用场景2

### 与现有工作的结合
- [当前项目] + [新概念] = [改进点]

---

## 🔗 延伸资源

### 文章
- [标题](URL)

### 视频
- [标题](URL)

### 开源项目
- [项目名](URL)

---

## 📈 趋势观察

### 行业动态
- 动态1
- 动态2

### 竞品动向
- 竞品1: [动向]
- 竞品2: [动向]

---

## 🎯 明日建议

基于今日研究，建议:
1. [建议1]
2. [建议2]

---

*Generated at 16:00*
*研究耗时: 约 60 分钟*
```

---

## 研究流程

### 每日工作流

```
16:00 - 触发研究任务
    ↓
选择研究主题 (基于用户兴趣 + 当前项目)
    ↓
信息收集 (Web Search + Web Fetch)
    ↓
深度分析 (LLM 总结)
    ↓
生成报告 (Markdown)
    ↓
17:00 - 发送报告
```

### 主题选择算法

```python
def select_research_topic():
    """
    选择今日研究主题:
    
    1. 检查用户最近表达的兴趣
    2. 检查当前项目的技术需求
    3. 检查行业趋势
    4. 轮换不同领域
    """
    topics = []
    
    # 用户兴趣
    topics.extend(get_user_interests())
    
    # 项目需求
    topics.extend(get_project_requirements())
    
    # 行业趋势
    topics.extend(get_industry_trends())
    
    # 去重 + 排序
    return select_balanced_topic(topics)
```

---

## 信息来源

### 必逛网站

| 网站 | 用途 | 频率 |
|------|------|------|
| Hacker News | 技术趋势 | 每日 |
| Twitter/X | 行业动态 | 每日 |
| V2EX | 开发者讨论 | 每日 |
| Product Hunt | 新工具 | 每日 |
| GitHub Trending | 开源项目 | 每日 |

### 深度来源

| 来源 | 用途 |
|------|------|
| arXiv | 学术论文 (AI/ML) |
| Medium | 技术博客 |
| Dev.to | 开发者社区 |
| Reddit | 社区讨论 |

---

## 研究深度

### 级别定义

| 级别 | 深度 | 耗时 |
|------|------|------|
| L1 概览 | 概念简介 | 15min |
| L2 理解 | 原理解释 | 30min |
| L3 实践 | 代码示例 | 45min |
| L4 精通 | 深度分析 | 60min+ |

### 级别选择

```python
def determine_depth(topic):
    """根据主题类型确定研究深度"""
    
    if is_conceptual(topic):
        return "L2"  # 理解级别
    elif is_practical(topic):
        return "L3"  # 实践级别
    elif is_trending(topic):
        return "L1"  # 概览级别
    else:
        return "L2"
```

---

## 发送渠道

**首选**: Telegram
**格式**: Markdown

```python
def send_research_report(report):
    message.send(
        channel="telegram",
        content=format_markdown(report),
        parse_mode="Markdown"
    )
```

---

## 与现有系统整合

### 数据流

```
用户对话 → 提取兴趣标签 → 主题选择 → 研究 → 报告 → 发送
                            ↓
                      更新 Second Brain
                            ↓
                      归档到 ideas/
```

### 与 Second Brain 整合

```python
def save_to_second_brain(report):
    """
    研究报告保存到 Second Brain:
    - 核心概念 → Notes/
    - 代码示例 → Scripts/
    - 每日报告 → Journal/
    """
    pass
```

---

## 示例报告

### 示例: RAG 知识库优化

```
# 📊 Afternoon Research Report - 2026-02-03

## 🎯 今日主题: RAG 知识库检索优化

### 研究背景
用户正在开发 Second Brain，需要优化 RAG 检索效果

## 📖 核心概念

### 概念 1: 向量检索
**定义**: 将文本转为向量，在向量空间中相似度搜索

### 概念 2: 重排序 (Reranking)
**定义**: 在初筛后对结果进行精细排序

...

## 🔧 实践指南

实现步骤:
1. 使用 BGE 嵌入模型
2. 添加重排序模型
3. 优化检索参数

## 💡 洞察与建议

对用户的价值:
- 知识检索准确率提升 30%
- 支持更复杂的查询

## 🎯 明日建议

1. 尝试 BGE-Rerank 模型
2. 测试不同 chunk size
```

---

## Cron 配置

```json
{
  "name": "afternoon-research",
  "schedule": {
    "kind": "cron",
    "expr": "0 16 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "/research-report"
  },
  "sessionTarget": "main",
  "enabled": true
}
```

---

## 依赖模块

| 模块 | 状态 | 说明 |
|------|------|------|
| Web Search | ✅ 已存在 | 信息收集 |
| Web Fetch | ✅ 已存在 | 内容提取 |
| LLM 分析 | ✅ 已存在 | 深度总结 |
| Telegram | ✅ 已存在 | 发送报告 |
| Second Brain | 待开发 | 知识沉淀 |

---

## TODO

- [ ] 实现主题选择算法
- [ ] 实现信息收集自动化
- [ ] 实现报告生成
- [ ] 实现 Second Brain 整合
- [ ] 配置 Cron 定时任务
- [ ] 测试研究质量
- [ ] 建立反馈机制 (用户评价报告质量)

---

## 相关文档

- [Second Brain](/Users/apple/openclaw/ideas/SecondBrain知识库-2026-02-01.md)
- [Web Search skill](/Users/apple/openclaw/skills/web_search/)
- [用户兴趣来源](/Users/apple/openclaw/USER.md)

---

*创建时间：2026-02-03*
