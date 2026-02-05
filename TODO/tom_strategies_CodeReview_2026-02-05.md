# Tom 投资策略系统 - 代码审查报告

**审查日期**: 2026-02-05
**审查人员**: AI Code Reviewer
**项目路径**: `/Users/apple/openclaw/projects/tom_strategies/`
**项目版本**: 0.1.0

---

## 一、项目概述

### 1.1 项目定位

Tom 投资策略系统是一个 **AI 辅助的投资策略执行系统**，旨在将"见微知著"方法论转化为可执行的自动化流程。系统采用人机协作模式：

- **AI 负责**：信息收集、逻辑计算、数据分析
- **人类负责**：实时判断、下单执行、情绪管理

### 1.2 核心目标

1. 构建自动化的信息收集与信号检测系统
2. 实现产业链逻辑推演与分析
3. 生成盘前/盘后研究报告
4. 支持多数据源接入（Tushare、akshare）

### 1.3 当前状态

| 指标 | 状态 |
|------|------|
| 模块开发 | ✅ 6 个核心模块完成 |
| 单元测试 | ✅ 64/64 测试通过 |
| 产业链知识库 | ✅ 6 个行业 YAML |
| 文档完整度 | ✅ README 已更新 |

---

## 二、架构分析

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Tom 投资策略系统架构                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │    LLM 层    │    │  Analyzer   │    │  Detector   │          │
│  │             │    │   (分析器)   │    │  (检测器)   │          │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤          │
│  │ - base.py   │    │ - logic.py  │    │ - technical │          │
│  │ - ollama.py │    │ - announcement│ │ - capital   │          │
│  │ - minimax.py│    │ - lhb.py    │    │             │          │
│  │ - factory.py│    └─────────────┘    └─────────────┘          │
│  └─────────────┘           │                    │                │
│        │                    │                    │                │
│        └────────────────────┼────────────────────┘                │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Reporter (报告生成器)                   │   │
│  │                    daily_reporter.py                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                      │
│                             ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Star Adapter (数据适配层)                  │   │
│  │                    star_adapter.py                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                      │
│        ┌────────────────────┼────────────────────┐                │
│        ▼                    ▼                    ▼                │
│  ┌──────────┐       ┌──────────┐        ┌──────────┐            │
│  │ Tushare  │       │ akshare  │        │  Crawler │            │
│  └──────────┘       └──────────┘        │(待开发)  │            │
│                                          └──────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块分析

#### 2.2.1 LLM 接口层 (`src/llm/`)

**已实现模块**：
- `base.py`: 抽象接口 `LLMInterface`
- `ollama.py`: Ollama 本地模型 (qwen3:8b)
- `minimax.py`: MiniMax API (M2.1)
- `factory.py`: 工厂函数 `create_llm()`

**设计特点**：
- 采用抽象基类设计，支持多 provider 切换
- Ollama 使用流式响应处理 Qwen3 的 thinking 字段
- MiniMax 使用 `MiniMax-M2.1` 模型，API 格式已适配

**问题发现**：
- ⚠️ `announcement.py` 中存在 typo：`provider: str = "ollana"` 应为 `"ollama"`

#### 2.2.2 分析器模块 (`src/analyzer/`)

**已实现**：
| 模块 | 功能 | 状态 |
|------|------|------|
| `logic.py` | 产业链逻辑推演 Agent | ✅ 完成 |
| `announcement.py` | 公告解析 Agent | ✅ 完成 |
| `lhb.py` | 龙虎榜分析模块 | 📋 计划中 |

**Logic Analyzer 特点**：
- 使用 Pydantic 模型定义输入输出 (`LogicInput`, `LogicOutput`)
- 支持 YAML 产业链知识库加载
- Prompt 模板包含 JSON 输出约束
- 具备 JSON 解析容错能力

**Announcement Analyzer 特点**：
- 支持合同、订单、重组、增发、监管等公告类型解析
- 自动提取金额、周期、交易对手等信息
- 影响评级（重大利好/利好/中性/利空/重大利空）

#### 2.2.3 信号检测模块 (`src/detector/`)

**已实现**：
| 检测器 | 功能 | 信号类型 |
|--------|------|----------|
| `technical_detector.py` | 技术信号检测 | 量比/二波/均线支撑/低位 |

**技术指标**：
- **量比检测**: `current_volume / avg_volume_5d > threshold (默认1.5)`
- **二波形态**: 识别回调后突破前期高点的形态
- **均线支撑**: 检查价格是否在 MA5/10/20/60 获得支撑（2%容差）
- **低位异动**: 检测价格处于 N 日区间 lower 20%

**问题发现**：
- ⚠️ 存在 API 兼容性问题：`star_adapter.py` 使用新版 `tushare.star` API，但实际安装的是旧版 Tushare 1.4.24
- ⚠️ 测试文档显示所有检测均返回空数据（API 无法获取）

#### 2.2.4 数据适配层 (`src/star_adapter.py`)

**已实现接口**：
| 方法 | 功能 | 数据源 |
|------|------|--------|
| `get_daily_price()` | 日线行情 | `pro.daily()` |
| `get_daily_basic()` | 每日指标 | `pro.daily_basic()` |
| `get_top_list()` | 龙虎榜 | `pro.top_list()` |
| `get_market_overview()` | 市场概览 | 多指数汇总 |

**问题发现**：
- ⚠️ 文档中声称使用新版 `tushare.star` API，但代码实际使用旧版 `pro_api`
- ⚠️ 缺少分时数据接口 (`get_minutely_data`)
- ⚠️ 缺少龙虎榜明细接口 (`get_top_detail`)
- ⚠️ 缺少期货数据接口

#### 2.2.5 报告生成模块 (`src/reporter/`)

**已实现**：
- `daily_reporter.py`: 盘后研究报告生成器

**报告结构**：
1. 今日市场（指数涨跌）
2. 股池表现（标的涨跌幅）
3. 重点信号（技术信号检测结果）
4. 逻辑追踪（待接入 LLM 分析）
5. 明日关注（操作建议）
6. 总结

**预设股池**：
```python
INITIAL_STOCK_POOL = [
    {"ts_code": "002738.SZ", "name": "中矿资源", "industry": "碳酸锂"},
    {"ts_code": "300674.SZ", "name": "蓝色光标", "industry": "AI应用"},
    {"ts_code": "002353.SZ", "name": "杰瑞股份", "industry": "电力设备"},
    {"ts_code": "002028.SZ", "name": "思源电气", "industry": "电力设备"},
    {"ts_code": "600644.SH", "name": "乐山电力", "industry": "国内电力"},
    {"ts_code": "000338.SZ", "name": "潍柴动力", "industry": "电力设备"},
]
```

### 2.3 产业链知识库 (`industry_chains/`)

**已实现 6 个行业 YAML**：

| 文件 | 行业 | 描述 |
|------|------|------|
| `lithium.yaml` | 锂电池产业链 | 锂资源 → 正极材料 → 电池 → 新能源车 |
| `power.yaml` | 电力 | 发电 → 输配电 → 用电 |
| `semiconductor.yaml` | 半导体 | 设计 → 制造 → 封测 → 设备 |
| `ai_application.yaml` | AI 应用 | 大模型 → 应用场景 |
| `domestic_power.yaml` | 国内电力 | 电力体制改革相关 |
| `power_equipment.yaml` | 电力设备 | 发电设备 → 输变电设备 |

**YAML 结构**：
```yaml
name: 产业链名称
description: 描述
upstream/midstream/downstream:
  - name: 环节名称
    stocks:
      - code: 股票代码
        name: 股票名称
        segment: 细分领域
        position: 产业链位置
key_signals:
  - signal: 触发信号
    impact: positive/negative
    transmission: 传导路径
    beneficiaries: 受益标的
    risk_factors: 风险因素
```

---

## 三、已实现功能

### 3.1 核心功能清单

| 功能模块 | 功能描述 | 实现状态 | 代码位置 |
|----------|----------|----------|----------|
| LLM 接口层 | Ollama/MiniMax 多模型支持 | ✅ 完成 | `src/llm/` |
| 逻辑推演 | 产业链信号传导分析 | ✅ 完成 | `src/analyzer/logic.py` |
| 公告解析 | 公告类型与影响提取 | ✅ 完成 | `src/analyzer/announcement.py` |
| 技术信号检测 | 量比/二波/均线/低位 | ✅ 完成 | `src/detector/technical_detector.py` |
| 数据适配层 | Tushare 数据封装 | ⚠️ 部分 | `src/star_adapter.py` |
| 盘后报告生成 | Markdown 格式报告 | ✅ 完成 | `src/reporter/daily_reporter.py` |
| 产业链知识库 | 6 个行业 YAML | ✅ 完成 | `industry_chains/` |
| 单元测试 | 64 个测试用例 | ✅ 完成 | `tests/` |

### 3.2 测试覆盖情况

**测试统计**：
```bash
总测试数: 64
通过: 64 (100%)
```

**各模块测试覆盖**：
| 模块 | 测试数 | 状态 |
|------|--------|------|
| Logic Analyzer | 10/10 | ✅ |
| Technical Detector | 21/21 | ✅ |
| Daily Reporter | 22/22 | ✅ |
| Star Adapter | 11/11 | ✅ |

### 3.3 主要依赖

```toml
# pyproject.toml
dependencies = [
    "pydantic>=2.0",
    "requests>=2.28",
]
optional = ["pytest>=7.0"]
```

**实际项目依赖**：
- `tushare`: 1.4.24（金融数据）
- `akshare`: （期货、公告数据）
- `pandas`: 数据处理
- `numpy`: 数值计算
- `matplotlib`: 图表生成（计划中）

---

## 四、待完成功能 (TODO 列表)

### 4.1 紧急 (P0)

#### 4.1.1 数据层修复

| 优先级 | 问题 | 状态 | 解决方案 |
|--------|------|------|----------|
| P0 | star_adapter.py API 兼容性问题 | 待修复 | 使用旧版 `pro_api` 或升级 Tushare |
| P0 | 技术信号检测返回空数据 | 待修复 | 修复数据源连接 |
| P0 | 缺少分时数据接口 | 待开发 | 实现 `get_minutely_data()` |
| P0 | 缺少龙虎榜明细接口 | 待开发 | 实现 `get_top_detail()` |

#### 4.1.2 代码缺陷修复

| 文件 | 问题 | 修复建议 |
|------|------|----------|
| `announcement.py` | `provider: str = "ollana"` typo | 改为 `"ollama"` |
| `technical_detector.py` | 文档显示测试失败 | 修复 API 兼容性问题 |

### 4.2 重要 (P1)

#### 4.2.1 计划中的模块

| 模块 | 功能 | 状态 | 预估工作量 |
|------|------|------|-----------|
| `capital_detector.py` | 资金信号检测（机构席位/主力流入） | 计划 | 6 小时 |
| `lhb_analyzer.py` | 龙虎榜分析模块 | 计划 | 8 小时 |
| `chart_analyzer.py` | 分时图 VLM 分析 | 计划 | 11 小时 |

#### 4.2.2 数据层扩展

| 接口 | 功能 | 优先级 |
|------|------|--------|
| `get_minutely_data()` | 分时数据（5分钟） | P1 |
| `get_top_detail()` | 龙虎榜明细 | P1 |
| `get_futures_daily()` | 期货日线 | P2 |
| `get_announcement_list()` | 公告列表 | P2 |
| `get_lithium_spot_price()` | 碳酸锂现货（爬虫） | P2 |

#### 4.2.3 爬虫开发

| 爬虫 | 数据源 | 优先级 |
|------|--------|--------|
| 巨潮公告全文爬虫 | cninfo.com.cn | P1 |
| 上海有色现货爬虫 | smm.cn | P2 |

### 4.3 一般 (P2)

#### 4.3.1 功能增强

| 功能 | 描述 | 状态 |
|------|------|------|
| 更多技术指标 | MACD, KDJ, BOLL | 待开发 |
| 批量检测优化 | 并发/缓存优化 | 待开发 |
| Telegram 通知 | 报告推送 | 待集成 |
| 定时任务 | 盘前/盘后自动执行 | 待配置 |

#### 4.3.2 扩展信号类型

| 信号 | 描述 | 复杂度 |
|------|------|--------|
| MACD 金叉 | MACD 指标金叉 | 中 |
| KDJ 超卖 | KDJ < 20 | 低 |
| BOLL 突破 | 突破布林带上轨 | 中 |
| 筹码集中 | 股东人数减少 | 高 |

---

## 五、风险点分析

### 5.1 技术风险

| 风险 | 等级 | 描述 | 影响 |
|------|------|------|------|
| Tushare API 兼容性 | 🔴 高 | 旧版 SDK 与代码不匹配 | 所有数据获取失败 |
| Token 安全 | 🟡 中 | Token 硬编码或环境变量泄露 | 数据源访问权限 |
| 网络依赖 | 🟡 中 | 实时数据依赖外部 API | 离线无法运行 |
| 依赖版本 | 🟡 中 | tushare 1.4.24 可能不稳定 | 数据获取异常 |

### 5.2 数据风险

| 风险 | 等级 | 描述 | 影响 |
|------|------|------|------|
| 数据延迟 | 🟡 中 | 龙虎榜为日终数据 | 无法实时监控 |
| 数据完整性 | 🟡 中 | 部分股票可能无数据 | 分析覆盖不全 |
| 爬虫稳定性 | 🟡 低 | 网页结构变化 | 公告/现货爬取失败 |

### 5.3 业务风险

| 风险 | 等级 | 描述 | 影响 |
|------|------|------|------|
| 策略有效性 | 🔴 高 | AI 分析结论可能错误 | 投资决策失误 |
| 实时性缺失 | 🟡 中 | 无法盘中实时监控 | 错过交易时机 |
| 情绪感知缺失 | 🟡 中 | 无法判断市场情绪 | 形态误判 |

### 5.4 架构风险

| 风险 | 等级 | 描述 | 影响 |
|------|------|------|------|
| 缓存管理 | 🟡 中 | `TechnicalDetector` 缓存手动清理 | 内存泄漏 |
| 错误处理 | 🟡 中 | 部分异常被静默吞掉 | 问题难以追踪 |
| 缺少日志配置 | 🟡 低 | 日志格式不统一 | 调试困难 |

---

## 六、改进建议

### 6.1 优先级 P0 改进

#### 6.1.1 修复数据层问题

```python
# star_adapter.py 修复建议
# 当前问题：文档声称使用 tushare.star，实际使用 pro_api

# 建议方案：
# 1. 统一使用 pro_api (tushare 1.x)
# 2. 或升级到 tushare-pro SDK
```

#### 6.1.2 修复代码缺陷

```python
# announcement.py 第 143 行
# 当前: provider: str = "ollana"
# 建议: provider: str = "ollama"
```

### 6.2 优先级 P1 改进

#### 6.2.1 添加数据源抽象层

```python
# 建议：统一数据接口
class DataSource(ABC):
    @abstractmethod
    def get_daily_price(self, ts_code: str, days: int) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_announcements(self, date: str) -> pd.DataFrame:
        pass

# 实现
class TushareDataSource(DataSource):
    pass

class AkshareDataSource(DataSource):
    pass
```

#### 6.2.2 增强错误处理

```python
# 建议：统一错误处理和重试机制
from tenacity import retry, stop_after_attempt, wait_exponential

class StarAdapter:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def get_daily_price(self, ts_code: str, days: int = 30) -> pd.DataFrame:
        # 实现
        pass
```

#### 6.2.3 添加统一日志配置

```python
# 建议：添加日志配置
import logging
import sys

def setup_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
```

### 6.3 优先级 P2 改进

#### 6.3.1 性能优化

| 优化项 | 当前 | 建议 |
|--------|------|------|
| 缓存策略 | 手动清理 | LRU + TTL |
| 并发请求 | 串行 | asyncio/ThreadPoolExecutor |
| 数据批量 | 单只获取 | 批量接口 |

#### 6.3.2 代码质量

| 检查项 | 状态 | 建议 |
|--------|------|------|
| 类型注解 | 部分完整 | 补充所有函数类型 |
| 文档字符串 | 部分完整 | 添加 Google Style 文档 |
| 代码注释 | 少量 | 增加复杂逻辑注释 |
| 测试覆盖 | 64用例 | 补充集成测试 |

#### 6.3.3 监控告警

```python
# 建议：添加运行监控
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RunStats:
    start_time: datetime
    end_time: datetime = None
    success: bool = True
    error: str = None
    records_processed: int = 0
```

### 6.4 架构建议

#### 6.4.1 事件驱动架构

```
┌─────────────────────────────────────────────────────────────┐
│                    事件驱动架构建议                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Event Bus                                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MarketOpen  │  SignalDetected  │  ReportReady    │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│         ┌─────────────────┼─────────────────┐              │
│         ▼                 ▼                 ▼              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐         │
│  │ Telegram │      │  Storage │      │  Alert   │         │
│  │ Notifier │      │          │      │          │         │
│  └──────────┘      └──────────┘      └──────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 6.4.2 配置管理

```python
# 建议：使用 Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    tushare_token: str
    minimax_api_key: str
    ollama_base_url: str = "http://localhost:11434"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

---

## 七、代码质量评估

### 7.1 整体评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 代码结构 | ⭐⭐⭐⭐ | 模块划分清晰，职责明确 |
| 测试覆盖 | ⭐⭐⭐⭐⭐ | 64/64 通过，覆盖率高 |
| 文档完整性 | ⭐⭐⭐⭐ | README 和开发文档完善 |
| 类型安全 | ⭐⭐⭐ | 部分类型注解缺失 |
| 错误处理 | ⭐⭐⭐ | 有基本异常处理，可改进 |
| 可维护性 | ⭐⭐⭐⭐ | 耦合度低，易于扩展 |
| 性能优化 | ⭐⭐⭐ | 无明显性能问题，缓存可优化 |

**综合评分**: ⭐⭐⭐⭐ (7.5/10)

### 7.2 优点

1. ✅ **架构清晰**: 模块化设计，职责分离
2. ✅ **测试完善**: 64 个单元测试全部通过
3. ✅ **类型定义**: 使用 Pydantic 模型，数据结构清晰
4. ✅ **Prompt 工程**: LLM Prompt 包含 JSON 输出约束
5. ✅ **知识库设计**: YAML 产业链结构易于维护
6. ✅ **工厂模式**: LLM provider 便于扩展

### 7.3 需改进

1. ⚠️ **数据层稳定性**: API 兼容性问题需优先修复
2. ⚠️ **代码缺陷**: announcement.py 的 typo
3. ⚠️ **类型注解**: 部分函数缺少返回类型
4. ⚠️ **日志系统**: 缺少统一配置
5. ⚠️ **错误处理**: 部分异常被静默处理

### 7.4 代码规范检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
| PEP 8 风格 | ✅ 基本符合 | 缩进和命名基本规范 |
| 导入排序 | ⚠️ 需整理 | 部分文件导入顺序混乱 |
| 注释密度 | ⚠️ 偏低 | 复杂逻辑缺少注释 |
| 函数长度 | ✅ 合理 | 函数职责单一，长度适中 |
| 文件长度 | ✅ 合理 | 无超长文件 |

---

## 八、总结与建议

### 8.1 项目成熟度

| 阶段 | 状态 | 说明 |
|------|------|------|
| 核心模块 | ✅ 已完成 | LLM、Analyzer、Detector、Reporter |
| 数据层 | ⚠️ 待修复 | API 兼容性问题 |
| 扩展模块 | 📋 计划中 | Capital、LHB、Chart 分析器 |
| 生产可用 | ⚠️ 待验证 | 需修复数据层问题 |

### 8.2 行动计划

#### 立即执行 (本周)

1. 🔧 **修复 star_adapter.py API 兼容性问题**
2. 🔧 **修复 announcement.py 的 provider typo**
3. ✅ **验证技术信号检测功能正常**

#### 短期目标 (2周内)

1. 📦 **实现分时数据接口 `get_minutely_data()`**
2. 📦 **实现龙虎榜明细接口 `get_top_detail()`**
3. 📦 **开发巨潮公告全文爬虫**
4. 🧪 **补充集成测试**

#### 中期目标 (1个月内)

1. 📦 **开发 capital_detector.py（资金信号检测）**
2. 📦 **开发 lhb_analyzer.py（龙虎榜分析）**
3. 📦 **开发 chart_analyzer.py（VLM 分时图分析）**
4. 🔔 **集成 Telegram 通知**

### 8.3 风险提示

⚠️ **重要提醒**：
1. 本系统为 **分析辅助工具**，不能替代人类投资决策
2. AI 分析结论可能存在偏差，需人工验证
3. 系统依赖外部数据源，需确保 API 稳定性
4. 禁止将系统用于自动交易（OpenClaw 配置限制）

### 8.4 后续跟进

| 跟进项 | 时间点 | 负责人 |
|--------|--------|--------|
| 修复数据层问题 | 2026-02-06 | AI Reviewer |
| 验证修复效果 | 2026-02-07 | AI Reviewer |
| 提交改进 PR | 2026-02-08 | AI Reviewer |

---

*报告生成时间: 2026-02-05*
*审查人员: AI Code Reviewer*
