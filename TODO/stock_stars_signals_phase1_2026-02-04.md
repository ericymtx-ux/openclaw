# stock_stars signals 模块 Phase 1 开发计划

**创建日期**: 2026-02-04 15:21
**开发者**: OpenCode
**状态**: 进行中
**Phase**: 1 - 基础框架

---

## 📋 开发目标

在 `stock_stars` 项目中创建 `signals` 模块，实现：
1. SignalParser - 邮件信号解析器
2. SignalStorage - SQLite 数据存储
3. 数据库表初始化
4. 单元测试

---

## 🔧 实施步骤

### Step 1: 创建模块目录结构

```bash
cd /Users/apple/openclaw/projects/stock_stars

# 创建目录
mkdir -p modules/signals
mkdir -p data/signals/daily
mkdir -p data/signals/temp

# 创建文件
touch modules/signals/__init__.py
```

**验收标准**:
- [ ] `modules/signals/` 目录存在
- [ ] `data/signals/` 目录结构完整

---

### Step 2: 实现 SignalParser (4h)

**文件**: `modules/signals/signal_parser.py`

**核心功能**:
```python
@dataclass
class StockSignal:
    code: str           # 股票代码
    name: str          # 股票名称
    action: str        # 操作: 开/持/平
    price: float       # 收盘价
    change_pct: str   # 涨跌幅
    volume_relation: str  # 量价关系
    heat_rank: int    # 热度排名
    heat_value: int   # 热度值
    net_amount: str   # 大单净额
    signal_date: str  # 信号日期
    source: str       # 来源
    industry: Optional[str] = None  # 行业板块

class SignalParser:
    def parse_email(self, html_content: str, email_id: str) -> List[StockSignal]
    def extract_table_rows(self, html: str) -> List[dict]
    def parse_action(self, cell: str) -> str
    def validate_code(self, code: str) -> bool
```

**关键逻辑**:
- HTML 表格列顺序: 日期(-4), 代码(-3), 名称(-2), 收盘价(-1), ..., 操作(i), 热度(i+3)
- 解析操作类型: 🔴开/🟡持/⚪空
- 验证股票代码格式: 6位数字 + .SZ/.SH

**验收标准**:
- [ ] StockSignal 数据类定义完整
- [ ] parse_email 返回 List[StockSignal]
- [ ] 解析测试通过 (sample HTML)
- [ ] 无 lint 错误

---

### Step 3: 实现 SignalStorage (4h)

**文件**: `modules/signals/signal_storage.py`

**数据库表结构**:
```sql
CREATE TABLE signal_tracking (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT,
    action TEXT NOT NULL,
    signal_date DATE NOT NULL,
    heat_rank INTEGER,
    heat_value INTEGER,
    price_at_signal REAL,
    change_pct TEXT,
    volume_relation TEXT,
    net_amount TEXT,
    industry TEXT,
    source TEXT,
    email_id TEXT,
    price_n1 REAL,
    price_n3 REAL,
    price_n5 REAL,
    price_n10 REAL,
    verified INTEGER DEFAULT 0,
    verification_result TEXT,
    verification_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code, signal_date, action)
);

CREATE TABLE emotion_index (
    id INTEGER PRIMARY KEY,
    trade_date DATE NOT NULL,
    top10_heat_concentration REAL,
    holding_signal_ratio REAL,
    emotion_score REAL,
    interpretation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(trade_date)
);

CREATE TABLE industry_mapping (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    industry TEXT NOT NULL,
    concept TEXT,
    confidence REAL DEFAULT 1.0,
    source TEXT DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code)
);
```

**核心功能**:
```python
class SignalStorage:
    def __init__(self, db_path: str = None)
    def _init_schema(self)
    def save_signals(self, signals: List[StockSignal])
    def get_unverified_signals(self, limit: int = 100) -> List[Dict]
    def update_performance(self, signal_id: str, n1: float, n3: float, 
                          n5: float, n10: float)
    def get_statistics(self, start_date: str = None, end_date: str = None,
                       industry: str = None, action: str = None) -> Dict
    def close(self)
```

**验收标准**:
- [ ] 数据库表初始化成功
- [ ] save_signals 保存信号
- [ ] get_unverified_signals 返回未验证信号
- [ ] get_statistics 返回统计结果
- [ ] 无 lint 错误

---

### Step 4: 创建单元测试

**文件**: `tests/unit/test_signal_parser.py`

```python
def test_parse_email_with_valid_html():
    parser = SignalParser()
    html = get_sample_email_html()
    signals = parser.parse_email(html, "test_email_123")
    
    assert len(signals) > 0
    assert signals[0].code == "000547.SZ"
    assert signals[0].action == "持"
    assert signals[0].heat_rank == 2

def test_validate_code():
    parser = SignalParser()
    assert parser.validate_code("000547.SZ") == True
    assert parser.validate_code("600519.SH") == True
    assert parser.validate_code("INVALID") == False
```

**文件**: `tests/unit/test_signal_storage.py`

```python
def test_save_and_retrieve_signals():
    storage = SignalStorage(":memory:")
    signals = [create_test_signal()]
    storage.save_signals(signals)
    
    retrieved = storage.get_unverified_signals()
    assert len(retrieved) == 1
    assert retrieved[0]['code'] == "000547.SZ"

def test_statistics():
    storage = SignalStorage(":memory:")
    # ... 添加测试数据 ...
    stats = storage.get_statistics()
    assert stats['total_signals'] > 0
```

**验收标准**:
- [ ] test_signal_parser.py 存在且通过
- [ ] test_signal_storage.py 存在且通过
- [ ] 测试覆盖率 > 70%

---

## 📊 开发数据

### 时间分配

| 任务 | 预估时间 | 实际时间 |
|------|----------|----------|
| Step 1: 目录结构 | 0.5h | - |
| Step 2: SignalParser | 4h | - |
| Step 3: SignalStorage | 4h | - |
| Step 4: 单元测试 | 2h | - |
| **总计** | **10.5h** | - |

### 代码量预估

| 文件 | 代码行数 |
|------|----------|
| modules/signals/__init__.py | 10 |
| modules/signals/signal_parser.py | 200 |
| modules/signals/signal_storage.py | 250 |
| tests/unit/test_signal_parser.py | 100 |
| tests/unit/test_signal_storage.py | 100 |
| **总计** | **~660 行** |

---

## 🧪 测试数据

### Sample HTML (用于测试)

从 `agents/email_checker/stock_email_*.md` 获取真实邮件 HTML

### 预期输出

```python
# StockSignal 示例
StockSignal(
    code="000547.SZ",
    name="航天发展",
    action="持",
    price=34.05,
    change_pct="+5.16%",
    volume_relation="量缩价涨",
    heat_rank=2,
    heat_value=9853086,
    net_amount="-8.98亿",
    signal_date="2026-02-04",
    source="人气与趋势-2026-02-04 10"
)
```

---

## 🚀 执行命令

```bash
# 1. 创建目录
cd /Users/apple/openclaw/projects/stock_stars
mkdir -p modules/signals data/signals/daily data/signals/temp
touch modules/signals/__init__.py

# 2. 开发 SignalParser
# 文件: modules/signals/signal_parser.py

# 3. 开发 SignalStorage
# 文件: modules/signals/signal_storage.py

# 4. 运行测试
python -m pytest tests/unit/ -v

# 5. 检查 lint
pnpm lint
```

---

## ✅ Definition of Done

### 代码层面
- [ ] 代码编译/运行通过
- [ ] 至少 5 个测试用例通过
- [ ] 无 lint 错误

### 文档层面
- [ ] README 更新 (安装/使用)
- [ ] API 文档注释完整

### 验证层面
- [ ] 核心场景手动测试通过
- [ ] 错误场景有处理

### 自检三问
- [ ] 影响范围: stock_stars 项目
- [ ] 测试用例: tests/unit/
- [ ] 使用说明: README.md

---

## 📁 输出文件

```
projects/stock_stars/
├── modules/
│   └── signals/
│       ├── __init__.py
│       ├── signal_parser.py
│       └── signal_storage.py
├── data/
│   └── signals/
│       ├── tracking.db
│       ├── daily/
│       └── temp/
└── tests/
    └── unit/
        ├── test_signal_parser.py
        └── test_signal_storage.py
```

---

*创建时间: 2026-02-04 15:21*
*开发者: OpenCode*
