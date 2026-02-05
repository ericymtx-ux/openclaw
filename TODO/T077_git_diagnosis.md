# T077: Git 仓库诊断与初始化

> **优先级**: P0 - 紧急
> **创建时间**: 2026-02-05 12:00
> **状态**: 待执行

---

## 任务描述

诊断 `/Users/apple/openclaw` 目录 Git 仓库不可用问题，恢复版本控制功能。

## 问题症状

```
$ git log --since="6 hours ago" --oneline
fatal: not a git repository (or any of the parent directories): .git

$ git status
fatal: not a git repository
```

## 影响范围

- ❌ 无法追踪代码变更
- ❌ 无法创建 commit
- ❌ 无法使用 git log / diff / branch
- ❌ 无法创建 PR
- ❌ 无法回滚问题代码

## 诊断步骤

### Step 1: 检查目录结构
```bash
# 检查是否存在 .git 目录
ls -la /Users/apple/.git
ls -la /Users/apple/openclaw/.git

# 检查是否是符号链接
ls -la /Users/apple/openclaw | grep git
```

### Step 2: 检查 git 配置
```bash
# 检查 git config
git config --list --local

# 检查远程配置
git remote -v
```

### Step 3: 尝试恢复
```bash
cd /Users/apple/openclaw

# 方案A: 如果有备份
if [ -d /Users/apple/.git_backup ]; then
  cp -r /Users/apple/.git_backup /Users/apple/openclaw/.git
  git status
fi

# 方案B: 从远程克隆
cd /Users/apple
git clone https://github.com/openclaw/openclaw.git openclaw_new

# 方案C: 手动初始化 (如果不需要远程)
cd /Users/apple/openclaw
git init
git add .
git commit -m "Initial commit - $(date +%Y-%m-%d)"
```

## 解决方案选择

| 方案 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| A: 备份恢复 | 本地有备份 | 保留历史 | 需要有备份 |
| B: 远程克隆 | 无本地改动 | 完整历史 | 需重新配置 |
| C: 手动初始化 | 新项目 | 简单 | 无历史 |

## 验证标准

- [ ] `git status` 返回 clean/repository 状态
- [ ] `git log` 显示至少 1 个 commit
- [ ] `git remote -v` 显示正确的远程仓库
- [ ] 可以创建新 commit

## 预期时间

- 诊断: 10 分钟
- 恢复: 30 分钟 (取决于选择方案)
- 验证: 10 分钟

## 相关文件

- `/Users/apple/openclaw/reflection/2026-02-05-1200.md`
- `/Users/apple/openclaw/BOT_TASKS.md`

---

*创建: 2026-02-05 12:00*
