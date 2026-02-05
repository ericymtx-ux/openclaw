# Memory Vector DB Skill

基于 Chroma + Ollama 的向量化知识库，用于语义搜索 Monday 的记忆。

## 功能

- **语义搜索**: 用自然语言搜索历史记忆
- **自动同步**: 监听 memory/ 目录变化
- **知识管理**: 新增/更新/删除记忆

## 前置条件

1. **Ollama 服务**
   ```bash
   ollama serve
   ollama pull qwen3-embedding:0.6b
   ```

2. **Python 依赖**
   ```bash
   pip install chromadb ollama
   ```

## 使用方式

### 导入模块

```python
import sys
sys.path.insert(0, "/Users/apple/openclaw/projects/memory-vector-db/src")
from memory_vector_db import MemoryVectorDB
```

### 初始化

```python
db = MemoryVectorDB(
    db_path="./memory_vector_db",  # 数据存储路径
    ollama_model="qwen3-embedding:0.6b"
)
```

### 语义搜索

```python
results = db.search("今天的开发任务", n_results=5)
for r in results:
    print(f"{r['id']}: {r['document'][:200]}...")
```

### 导入目录

```python
# 首次导入
db.import_from_directory("./memory")

# 增量同步
db.sync_with_directory("./memory")
```

### 示例命令

```bash
# 搜索记忆
python -c "
from memory_vector_db import MemoryVectorDB
db = MemoryVectorDB()
for r in db.search('语音识别'):
    print(r['id'], r['distance'])
"
```

## 目录结构

```
projects/memory-vector-db/
├── src/
│   └── memory_vector_db.py    # 核心类
├── memory_vector_db/           # Chroma 数据存储
└── README.md

skills/memory-vector-db/
└── SKILL.md                    # Skill 配置
```

## 下一步开发

- [ ] 与 OpenClaw 搜索命令集成

```bash
# 启动文件监听
cd /Users/apple/openclaw/projects/memory-vector-db
python watch_memory.py /Users/apple/openclaw/memory

# 或后台运行
nohup python watch_memory.py ./memory > memory_watcher.log 2>&1 &
```

**功能:**
- 监听创建/修改/删除/移动事件
- 防抖处理（5秒间隔，避免频繁触发）
- 自动同步到 ChromaDB
- 支持多目录监听（memory/ideas/projects）

## 相关文件

- 项目: `projects/memory-vector-db/`
- 调研: `TODO/Chroma向量知识库调研_2026-02-03.md`
