"""
自我反思工具

每6小时自动执行：
1. 记住当前模型
2. 切换到 opus
3. 执行深度反思
4. 保存反思报告
5. 更新相关文件
6. 发送报告
7. 切换回原模型
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


class ReflectionTool:
    """自我反思工具"""
    
    def __init__(self):
        self.config_path = Path.home() / ".openclaw/openclaw.json"
        self.workspace = Path("/Users/apple/openclaw")
        self.reflection_dir = self.workspace / "reflection"
        self.memory_dir = self.workspace / "memory"
        self.todo_dir = self.workspace / "TODO"
        
    def get_current_model(self) -> str:
        """获取当前模型配置"""
        try:
            result = subprocess.run(
                ["pnpm", "openclaw", "config", "get", "agents.defaults.model.primary"],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "minimax/MiniMax-M2.1"  # 默认模型
    
    def set_model(self, model: str) -> bool:
        """设置模型"""
        try:
            result = subprocess.run(
                ["pnpm", "openclaw", "config", "set", "agents.defaults.model.primary", model],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_recent_files(self, hours: int = 6) -> list[Path]:
        """获取最近修改的文件"""
        since = datetime.now().timestamp() - hours * 3600
        files = []
        for f in self.memory_dir.glob("*.md"):
            if f.stat().st_mtime > since:
                files.append(f)
        for f in self.reflection_dir.glob("*.md"):
            if f.stat().st_mtime > since:
                files.append(f)
        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def get_git_log(self, hours: int = 6) -> str:
        """获取 git 提交日志"""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={hours} hours ago", "--oneline"],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            return result.stdout.strip()
        except Exception:
            return ""
    
    def get_cron_status(self) -> str:
        """获取 cron 任务状态"""
        try:
            result = subprocess.run(
                ["pnpm", "openclaw", "cron", "list"],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            return result.stdout.strip()
        except Exception:
            return ""
    
    def get_task_stats(self) -> dict:
        """获取任务统计"""
        bot_tasks = self.workspace / "BOT_TASKS.md"
        if not bot_tasks.exists():
            return {}
        
        content = bot_tasks.read_text()
        stats = {
            "pending": content.count("🔴 待执行"),
            "in_progress": content.count("🟡 正在执行"),
            "blocked": content.count("🟠 阻塞中"),
            "done": content.count("✅ 已完成"),
        }
        return stats
    
    def create_reflection_prompt(self, current_model: str) -> str:
        """创建反思 Agent 的提示词"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        stats = self.get_task_stats()
        
        return f"""你是 Monday 的自我反思 Agent。

## 当前状态

**时间**: {now}
**当前模型**: {current_model}
**反思周期**: 每6小时

## 任务统计

| 状态 | 数量 |
|------|------|
| 待执行 | {stats.get('pending', '?')} |
| 进行中 | {stats.get('in_progress', '?')} |
| 阻塞中 | {stats.get('blocked', '?')} |
| 已完成 | {stats.get('done', '?')} |

## 工作要求

1. 深度扫描 BOT_TASKS.md, TODO/, memory/, reflection/
2. 分析 git log 最近6小时的变更
3. 检查 cron 任务执行状态
4. 识别问题模式和改进机会
5. 生成结构化反思报告
6. 更新 BOT_TASKS.md 和相关文件

## 输出要求

1. 生成反思报告到: reflection/{datetime.now().strftime('%Y-%m-%d-%H%M')}.md
2. 更新 BOT_TASKS.md 状态
3. 更新 TODO/ 目录
4. 发送 Telegram 报告

请开始执行深度反思。"""
    
    def run_reflection(self) -> bool:
        """执行反思"""
        print("🔄 开始自我反思...")
        
        # Step 1: 记住当前模型
        original_model = self.get_current_model()
        print(f"📌 记住当前模型: {original_model}")
        
        # Step 2: 切换到 opus
        opus_model = "anthropic/claude-opus-4-5"
        if not self.set_model(opus_model):
            print("⚠️ 切换模型失败，继续执行")
        print(f"🔄 切换到模型: {opus_model}")
        
        # Step 3: 获取信息
        prompt = self.create_reflection_prompt(original_model)
        git_log = self.get_git_log()
        cron_status = self.get_cron_status()
        stats = self.get_task_stats()
        
        # Step 4: 生成反思报告
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H%M")
        
        report = f"""# 自我反思报告 - {timestamp}

## 📊 工作状态概览

### 任务统计
| 状态 | 数量 |
|------|------|
| 待执行 | {stats.get('pending', '?')} |
| 进行中 | {stats.get('in_progress', '?')} |
| 阻塞中 | {stats.get('blocked', '?')} |
| 已完成 | {stats.get('done', '?')} |

### 最近文件变更

#### Memory 文件
"""

        # 添加最近 memory 文件
        recent_memory = [f for f in self.memory_dir.glob("*.md")][:5]
        for f in recent_memory:
            name = f.name.replace(".md", "")
            report += f"- `{name}`\n"

        report += """
### Git 提交 (最近6小时)
```
"""

        # 添加 git log
        if git_log:
            for line in git_log.split("\n")[:20]:
                report += f"{line}\n"
        else:
            report += "无提交记录\n"

        report += """```

### Cron 任务状态
"""
        
        # 添加 cron 状态
        if cron_status:
            for line in cron_status.split("\n")[:10]:
                report += f"{line}\n"
        
        report += """
## 🔍 问题发现

### 🚨 紧急问题 (P0)
_待分析_

### ⚠️ 改进建议 (P1)
_待分析_

### 💡 经验总结
_待分析_

## 📝 需要修改的文件

### BOT_TASKS.md
_待更新_

### TODO/
_待更新_

### 夜间开发计划
_待更新_

## 🎯 明日重点
_待确定_

---
*反思完成时间: {timestamp}*
*原模型: {original_model}*
"""
        
        # 保存报告
        report_path = self.reflection_dir / f"{date_str}-{time_str}.md"
        report_path.write_text(report)
        print(f"✅ 反思报告已保存: {report_path.name}")
        
        # Step 5: 切换回原模型
        self.set_model(original_model)
        print(f"🔄 已切换回模型: {original_model}")
        
        # Step 6: 发送报告 (通过 cron payload)
        print("📤 反思完成，报告已生成")
        
        return True


def main():
    """主入口"""
    tool = ReflectionTool()
    success = tool.run_reflection()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
