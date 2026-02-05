# Definition of Done (DoD)

> **Hard completion standards - all must be met before marking a task as Done**

---

## English Version (中英对照)

### Code Level ✅
- [ ] **Build/Pass** - No syntax errors, runs normally
- [ ] **Test Coverage** - At least 1 test case passes
- [ ] **Lint Clean** - No warnings/errors (`pnpm lint`)

### Documentation Level ✅
- [ ] **README Updated** - Installation steps + examples
- [ ] **API Docs** - Function/interface parameters
- [ ] **Code Examples** - Common usage demos

### Verification Level ✅
- [ ] **Core Scenarios** - Main features work correctly
- [ ] **Error Handling** - Edge cases have proper handling
- [ ] **Dependencies** - No new problematic dependencies

### Self-Check Three Questions ✅
Must answer before committing:

1. **Scope** - What files does this affect? Are dependencies compatible?
2. **Tests** - Where are the tests? What scenarios are covered?
3. **Usage** - If user asks "how to use", is there documentation?

---

## 代码层面 ✅

- [ ] **编译/运行通过** - 代码无语法错误，可正常启动
- [ ] **至少1个测试用例通过** - 核心逻辑有测试覆盖
- [ ] **Lint 通过** - 无警告/错误（运行 `pnpm lint` 或对应工具）

---

## 文档层面 ✅

- [ ] **README 更新** - 包含安装步骤、使用示例
- [ ] **API 文档** - 函数/接口参数说明
- [ ] **示例代码** - 常见用法演示

---

## 验证层面 ✅

- [ ] **核心场景测试** - 主要功能正常work
- [ ] **错误场景测试** - 异常输入有合理处理
- [ ] **依赖检查** - 无新增问题依赖

---

## 自检三问 ✅

在提交前必须回答：

1. **影响范围** - 这个改动影响哪些文件？依赖方是否兼容？
2. **测试位置** - 测试用例在哪里？覆盖了哪些场景？
3. **使用说明** - 如果用户问"怎么用"，文档在哪里？

---

## 任务拆解规范

### 子任务拆分原则
- 每个子任务 **≤ 2小时** 可完成
- 超过2小时的任务必须有 **检查点**
- 检查点格式：`[P0] 中期检查 - 预期产出`

### 检查点示例
```markdown
## 检查点 - T006 数据适配层

### 预期产出
- [ ] star_adapter.py API 兼容修复
- [ ] 测试通过

### 实际进度
- [x] 问题定位完成
- [ ] 修复中
- [ ] 待测试
```

---

## 阻塞升级机制

### 升级触发条件
- 任务阻塞超过 **4小时**
- 缺少关键信息/资源
- 发现设计缺陷

### 升级报告格式
```markdown
## 阻塞升级 - [任务ID]

### 阻塞原因
[清晰描述]

### 已尝试
- 方案A：结果
- 方案B：结果

### 需要
- [ ] 用户确认 XXX
- [ ] 授权 XXX
- [ ] 资源 XXX
```

---

## 代码 Review 标准

### 必查项
| 检查项 | 通过标准 |
|--------|----------|
| API 兼容性 | 无版本/参数变化问题 |
| 边界条件 | 空值/异常/超界有处理 |
| 测试覆盖 | 核心逻辑 ≥ 70% |
| 文档同步 | README/API 文档更新 |

### Review 输出
```markdown
## Code Review - [任务名]

### ✅ 通过
- [检查项1]
- [检查项2]

### ⚠️ 需改进
- [问题1] → 建议
- [问题2] → 建议

### ❌ 阻塞
- [问题] → 必须修复
```

---

## 快速回滚规范

### 回滚触发
- 测试失败且 30 分钟内无法修复
- Review 未通过且修改成本高
- 用户反馈重大问题

### 回滚步骤
1. 记录当前 git commit hash
2. 执行 `git checkout HEAD~1` 或指定版本
3. 通知用户回滚原因
4. 创建新任务修复问题

---

## 验收流程

### 任务完成流程
```
[开始] → [编码] → [自测] → [文档] → [Review] → [提交] → [Done]
              ↓
         不通过→返回
```

### 自检清单执行
```bash
# 执行自检
pnpm lint              # 代码质量
pnpm test              # 测试通过
cat DOD.md             # 对照检查
```

---

## 测试覆盖率要求

| 类型 | 要求 |
|------|------|
| 新增代码 | ≥ 70% |
| 关键模块 | ≥ 90% |
| 核心工作流 | 100% 自动化 |

---

*文件位置: /Users/apple/openclaw/DOD.md*
*最后更新: 2026-02-03 07:50 GMT+8*
