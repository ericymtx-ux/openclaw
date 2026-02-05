#!/usr/bin/env python3
"""
Monday-TODO Agent - 主 Agent

功能：
1. 每小时扫描 Monday-TODO 日历
2. 检查任务完成状态
3. 自动完成任务
4. 处理反思
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import json

# 直接导入模块（相对于当前文件）
from calendar_scanner import CalendarScanner, TodoItem, scan_incomplete, mark_completed, add_reflection
from chat_history_checker import ChatHistoryChecker, check_task_completed, scan_reflections


class MondayTodoAgent:
    """Monday-TODO 自动化 Agent"""

    def __init__(self):
        self.workspace = Path("/Users/apple/openclaw")
        self.calendar = CalendarScanner()
        self.checker = ChatHistoryChecker()
        self.today = datetime.now().strftime("%Y-%m-%d")

    async def scan_and_process(self) -> Dict:
        """扫描并处理所有 TODO"""
        results = {
            "scan_time": datetime.now().isoformat(),
            "incomplete": 0,
            "completed_in_chat": 0,
            "pending_execution": 0,
            "reflections_found": 0,
            "reflections_added": 0,
            "errors": []
        }

        print(f"🔄 Monday-TODO 扫描开始: {self.today}\n")

        # Step 1: 扫描未完成 TODO
        todos = await scan_incomplete(days=7)
        results["incomplete"] = len(todos)

        print(f"📅 扫描到 {len(todos)} 个未完成任务\n")

        # Step 2: 检查每个 TODO
        for todo in todos:
            try:
                print(f"检查: {todo.title}")

                # 检查聊天记录
                check_result = await check_task_completed(todo)

                if check_result["completed"]:
                    # 聊天中已完成，标记为完成
                    print(f"  ✅ 聊天中已完成 (置信度: {check_result['confidence']:.0%})")
                    await mark_completed(todo.id, todo.title)
                    results["completed_in_chat"] += 1
                else:
                    # 未完成，需要执行
                    print(f"  ⏳ 未完成 (置信度: {check_result['confidence']:.0%})")
                    print(f"     匹配关键词: {check_result['matched_keywords']}")
                    results["pending_execution"] += 1

                print()

            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                results["errors"].append({"todo": todo.title, "error": str(e)})

        # Step 3: 扫描反思
        print("\n🔍 扫描反思内容...")
        reflections = await scan_reflections(days=3)
        results["reflections_found"] = len(reflections)

        for ref in reflections:
            # 检查是否已存在
            existing = await self._check_reflection_exists(ref.date, ref.content[:100])
            if not existing:
                # 添加到日历
                content = self._format_reflection(ref)
                await add_reflection(ref.date, content)
                results["reflections_added"] += 1
                print(f"  ✅ 添加反思: {ref.date}")
            else:
                print(f"  ⏳ 已存在: {ref.date}")

        # 汇总
        print(f"\n{'='*50}")
        print("📊 扫描完成")
        print(f"  未完成任务: {results['incomplete']}")
        print(f"  聊天完成: {results['completed_in_chat']}")
        print(f"  待执行: {results['pending_execution']}")
        print(f"  反思: {results['reflections_found']} 发现, {results['reflections_added']} 添加")
        if results["errors"]:
            print(f"  错误: {len(results['errors'])}")
        print(f"{'='*50}\n")

        return results

    async def _check_reflection_exists(self, date: str, content_preview: str) -> bool:
        """检查反思是否已存在"""
        events = await self.calendar.get_all_events(days=7)
        for event in events:
            if "【反思】" in event.get("summary", ""):
                if date in event.get("summary", ""):
                    return True
        return False

    def _format_reflection(self, ref) -> str:
        """格式化反思内容"""
        lines = ["## 经验总结", ""]

        if ref.good_patterns:
            lines.append("### ✅ 做得好")
            for p in ref.good_patterns[:5]:
                lines.append(f"- {p}")
            lines.append("")

        if ref.bad_patterns:
            lines.append("### ⚠️ 需要改进")
            for p in ref.bad_patterns[:5]:
                lines.append(f"- {p}")
            lines.append("")

        if ref.lessons:
            lines.append("### 📝 经验教训")
            for l in ref.lessons[:5]:
                lines.append(f"- {l}")
            lines.append("")

        lines.append(f"来源: {ref.source}")

        return "\n".join(lines)

    async def list_pending(self) -> str:
        """列出待完成任务"""
        todos = await scan_incomplete(days=7)

        if not todos:
            return "✅ 暂无待完成的 TODO"

        lines = [f"📋 待完成 TODO ({len(todos)} 个)\n"]
        for i, t in enumerate(todos, 1):
            lines.append(f"{i}. **{t.title}**")
            lines.append(f"   📅 {t.date}")
            if t.description:
                lines.append(f"   📝 {t.description[:50]}...")
            lines.append("")

        return "\n".join(lines)

    async def force_execute(self, task_id: str) -> str:
        """强制执行某个任务"""
        # TODO: 集成 OpenCode
        return f"🔧 任务执行功能待实现: {task_id}"


async def main():
    """主入口"""
    agent = MondayTodoAgent()
    results = await agent.scan_and_process()

    # 保存结果
    result_file = Path.home() / ".openclaw/monday_todo_scan.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monday-TODO Agent")
    parser.add_argument("--scan", action="store_true", help="扫描并处理 TODO")
    parser.add_argument("--list", action="store_true", help="列出待完成任务")
    parser.add_argument("--execute", type=str, help="执行特定任务")

    args = parser.parse_args()

    if args.scan:
        asyncio.run(main())
    elif args.list:
        asyncio.run(MondayTodoAgent().list_pending())
    elif args.execute:
        asyncio.run(MondayTodoAgent().force_execute(args.execute))
    else:
        print("用法:")
        print("  python3 monday_todo_agent.py --scan    # 扫描并处理")
        print("  python3 monday_todo_agent.py --list    # 列出待完成")
        print("  python3 monday_todo_agent.py --execute <id>  # 执行任务")
