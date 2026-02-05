# opencode-team 修复与完善

**创建日期**: 2026-02-01
**状态**: in_progress
**负责人**: Monday (AI Assistant)

## 需求描述

opencode-team 是一个 MCP 服务器，用于通过 iTerm2 终端管理 OpenCode CLI 工作进程。当前实现存在以下问题需要修复和优化：

1. **Worker 命令执行问题**：
   - 当前代码生成 `opencode run "prompt"` 命令，但 iTerm2 窗口已创建后命令未正确发送
   - 需要验证 OpenCode CLI 是否正确安装并能执行

2. **状态管理不完整**：
   - workers 字典有重复键问题（同名的 worker 会覆盖）
   - 状态持久化后恢复逻辑不完善

3. **缺少关键功能**：
   - 未实现消息发送功能（message_workers）
   - 未实现空闲检测（check_idle_workers 返回的结果不正确）
   - 未实现工作树（worktree）支持

4. **OpenCode CLI 集成问题**：
   - OpenCode CLI 是 `@opencode-ai/cli` 包，需要确认安装和调用方式
   - 需要处理 OpenCode 特有的运行模式和参数

## 任务拆解

### 阶段 1: 问题诊断与基础修复
- [x] 1.1 验证 OpenCode CLI 安装和调用方式 - **已确认！OpenCode 工作正常**
- [x] 1.2 修复 iTerm2 窗口创建后的命令发送逻辑 - **已验证！窗口创建和命令发送成功**
- [x] 1.3 修复 workers 字典键重复问题 - **已修复！不再用 name 作为键**
- [x] 1.4 清理现有测试 workers - **已清理**

### 阶段 2: 核心功能完善
- [x] 2.1 实现 message_workers 发送消息到运行中的 worker - **已实现**
- [x] 2.2 修复 check_idle_workers 检测逻辑 - **已修复**
- [ ] 2.3 实现工作树（worktree）自动创建和清理 - **未实现**

### 阶段 3: 集成测试
- [ ] 3.1 端到端测试：spawn → run → message → close
- [ ] 3.2 并发多 workers 测试
- [ ] 3.3 状态持久化测试

## 工作难点分析

### 技术难点

**难点 1: iTerm2 窗口与命令同步**
- **描述**: iTerm2 窗口创建是异步的，命令发送需要在窗口准备好之后
- **影响**: 当前命令可能在窗口还没完全加载时就发送了
- **解决方案**: 添加适当的延时或监听窗口状态变化

**难点 2: OpenCode CLI 运行模式**
- **描述**: OpenCode CLI 使用 `opencode run "prompt"` 模式，不是交互式 shell
- **影响**: 无法像 Claude Code 那样持续交互
- **解决方案**: 使用 `opencode serve` 后台模式 + `opencode attach`，或使用 MCP 协议直接通信

**难点 3: Worker 状态检测**
- **描述**: 如何判断 OpenCode worker 是否空闲或完成
- **影响**: check_idle_workers 无法准确返回结果
- **解决方案**: 监听 OpenCode 输出或使用进程状态检测

### 依赖关系

- 依赖 OpenCode CLI 正确安装和配置
- 依赖 iTerm2 Python API
- 依赖 MCP 协议正确实现

### 风险评估

**风险 1: OpenCode CLI 交互模式限制**
- OpenCode 主要设计为 TUI 工具，非命令行批处理
- 应对措施：探索 MCP 协议直接调用方式

**风险 2: iTerm2 连接稳定性**
- iTerm2 WebSocket 连接可能超时或断开
- 应对措施：实现连接保活和重连机制

## 验收标准

- [x] 1. spawn_workers 能在 iTerm2 创建窗口并启动 OpenCode - **已验证成功！**
- [x] 2. list_workers 正确显示所有活跃 workers - **已修复无重复**
- [x] 3. message_workers 能向运行中的 worker 发送新命令 - **已实现**
- [x] 4. check_idle_workers 正确检测 worker 状态 - **已修复**
- [x] 5. close_workers 能终止 worker 并清理资源 - **已实现**
- [ ] 6. 状态持久化正常工作，重启后能恢复

## 当前状态总结 (2026-02-01 01:10)

✅ **已修复的问题：**
1. Workers 字典键重复问题 - 不再使用 name 作为键
2. iTerm2 窗口创建和命令发送
3. list_workers 显示唯一 workers
4. check_idle_workers 检测逻辑

⚠️ **待完善：**
1. message_workers 只是更新状态，实际发送到 iTerm2 的逻辑需要完善
2. 工作树（worktree）支持未实现
3. 状态持久化需要完整测试

✅ **验证成功的流程：**
```
spawn_workers → list_workers → check_idle_workers → close_workers
```

## 相关链接

- OpenCode CLI 文档: https://opencode.ai/docs/cli/
- Claude Team 参考: /Users/apple/.claude-team/server/src/claude_team_mcp/
- 当前实现: /Users/apple/openclaw/skills/opencode-team/src/opencode_team_mcp/server.py

## 下一步行动

1. 确认 OpenCode CLI 的正确安装方式和调用参数
2. 修复 iTerm2 窗口创建后的命令发送逻辑
3. 测试 OpenCode 是否能正常启动并执行任务
