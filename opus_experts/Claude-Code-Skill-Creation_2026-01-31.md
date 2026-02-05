# Claude Code Skill Creation - 2026-01-31

## 任务
深度阅读 Claude Code 官方文档，为 OpenClaw 创建 claude-code skill。

## 思考过程
1. 系统性阅读文档的各个子页面
2. 理解 Claude Code 核心概念：CLI、权限模式、会话管理
3. 提取最重要的命令和模式
4. 设计适合 OpenClaw 调用的 skill 结构

## 阅读的文档页面
1. **Overview** - 产品概述、安装方法、核心功能
2. **Quickstart** - 快速入门、基本命令
3. **CLI Reference** - 完整 CLI 标志和命令参考
4. **Common Workflows** - 常见工作流程（调试、重构、测试）
5. **How Claude Code Works** - 架构、工具、会话管理
6. **Best Practices** - 最佳实践、上下文管理、提示技巧
7. **Features Overview** - 扩展功能（Skills、MCP、Hooks）
8. **Skills** - Skill 创建和配置
9. **Interactive Mode** - 键盘快捷键、命令

## Claude Code 核心概念

### 运行模式
- **Interactive**: `claude` 启动交互式会话
- **Headless**: `claude -p "query"` 非交互式执行
- **Continue**: `claude -c` 继续最近会话
- **Resume**: `claude -r "name"` 恢复特定会话

### 权限模式
- **Default**: 文件编辑和命令都需确认
- **Auto-accept**: 自动接受文件编辑
- **Plan Mode**: 只读模式，先规划再执行

### 核心 CLI 标志
```bash
-p, --print          # 非交互模式
-c, --continue       # 继续最近会话
-r, --resume         # 恢复特定会话
--model              # 选择模型
--verbose            # 详细输出
--permission-mode    # 权限模式
--dangerously-skip-permissions  # 跳过所有权限
```

## 创建的 Skill 结构

```
/Users/apple/openclaw/skills/claude-code/
├── SKILL.md        # 主要指南（安装、命令、模式、示例）
└── reference.md    # 高级参考（完整标志、高级模式、配置）
```

## 行动步骤
1. 使用 web_fetch 逐页获取文档内容
2. 提取核心命令、标志、工作流程
3. 创建 SKILL.md（5336 字节）- 涵盖安装、命令、模式、示例
4. 创建 reference.md（5636 字节）- 完整标志、高级模式、配置

## 关键洞察
- Claude Code 的核心价值是 "agentic loop"：收集上下文 → 执行操作 → 验证结果
- 上下文管理是最重要的资源约束
- Skills 是扩展功能的首选方式
- 最佳实践：提供验证方式、先规划后执行、具体化提示
