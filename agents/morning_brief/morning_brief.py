#!/usr/bin/env python3
"""
Morning Brief Agent - 每日早间简报系统

功能：
- 每日 08:00 自动生成早间简报
- 包含：天气、YouTube 趋势、任务列表、自动化任务推荐
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json
import sys
import importlib.util

# 动态导入 night_work.task_scorer
NIGHT_WORK_DIR = Path(__file__).resolve().parent.parent / "night-work"
TASK_SCORER_PATH = NIGHT_WORK_DIR / "task_scorer.py"

spec = importlib.util.spec_from_file_location("task_scorer", str(TASK_SCORER_PATH))
task_scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task_scorer)

Task = task_scorer.Task
Priority = task_scorer.Priority
parse_task_from_markdown = task_scorer.parse_task_from_markdown
can_auto_execute = task_scorer.can_auto_execute

# 日历模块已重新启用（2026-02-05）
from .calendar_module import CalendarModule


class WeatherModule:
    """天气模块 - 集成 weather skill"""

    def __init__(self):
        self.initialized = False
        self.cities = ["Shenzhen", "New York"]

    async def get_weather(self, location: str = "Beijing") -> Dict:
        """获取天气信息 - 使用 wttr.in"""
        try:
            import subprocess
            import urllib.parse

            # URL 编码空格
            encoded_location = urllib.parse.quote(location)

            # 使用 wttr.in 获取天气
            result = subprocess.run(
                ["curl", "-s", f"wttr.in/{encoded_location}?format=%l:+%c+%t+%h"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                # 解析输出: "Beijing: ⛅️ +15°C 45%"
                parts = output.split(":")
                if len(parts) >= 2:
                    loc = parts[0].strip()
                    rest = parts[1].strip()
                    # 提取温度和状况
                    import re
                    temp_match = re.search(r'([+-]?\d+°[CF])', rest)
                    cond_match = re.search(r'([🌤️☀️🌧️❄️☁️🌩️🔥]+)', rest)
                    hum_match = re.search(r'(\d+%)', rest)

                    return {
                        "location": loc,
                        "temperature": temp_match.group(1) if temp_match else "N/A",
                        "condition": cond_match.group(1) if cond_match else "N/A",
                        "humidity": hum_match.group(1) if hum_match else "N/A"
                    }

        except Exception as e:
            print(f"⚠️ 获取天气失败: {e}")

        return {
            "location": location,
            "temperature": "N/A",
            "condition": "Unknown",
            "humidity": "N/A"
        }

    async def get_all_weather(self) -> List[Dict]:
        """获取所有关注城市的天气"""
        weather_list = []
        for city in self.cities:
            weather = await self.get_weather(city)
            weather_list.append(weather)
        return weather_list


class YouTubeModule:
    """YouTube 趋势模块"""

    def __init__(self):
        self.interests = [
            "AI", "LLM", "machine learning",
            "quant trading", "investment",
            "independent developer", "SaaS",
            "productivity tools", "Python"
        ]

    async def fetch_trending(self, max_results: int = 5) -> List[Dict]:
        """获取 YouTube 趋势视频"""
        # TODO: 实现 YouTube API 调用
        return [
            {
                "title": "Sample Video",
                "channel": "Tech Channel",
                "views": "100K",
                "url": "https://youtube.com/watch?v=..."
            }
        ][:max_results]


class TaskModule:
    """任务列表模块"""

    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.cwd()

    async def get_today_tasks(self) -> List[Task]:
        """获取今日任务列表"""
        tasks = []

        # 扫描 BOT_TASKS.md
        bot_tasks_path = self.workspace / "BOT_TASKS.md"
        if bot_tasks_path.exists():
            tasks.extend(self._parse_bot_tasks(bot_tasks_path))

        # 扫描 TODO/ 目录
        todo_dir = self.workspace / "TODO"
        if todo_dir.exists():
            tasks.extend(self._parse_todo_dir(todo_dir))

        return tasks

    def _parse_bot_tasks(self, path: Path) -> List[Task]:
        """解析 BOT_TASKS.md"""
        return parse_task_from_markdown(path.read_text())

    def _parse_todo_dir(self, path: Path) -> List[Task]:
        """解析 TODO 目录"""
        tasks = []
        for md_file in path.glob("*.md"):
            if md_file.name in ["index.md", "README.md"]:
                continue
            task = self._parse_todo_file(md_file)
            if task:
                tasks.append(task)
        return tasks

    def _parse_todo_file(self, path: Path) -> Optional[Task]:
        """解析单个 TODO 文件"""
        content = path.read_text()
        title = ""
        priority = Priority.P2

        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
            elif '优先级' in line or 'Priority' in line:
                if 'P0' in line:
                    priority = Priority.P0
                elif 'P1' in line:
                    priority = Priority.P1

        if not title:
            return None

        return Task(
            id=path.stem,
            title=title,
            priority=priority,
            estimated_minutes=60
        )


class AutoTaskRecommender:
    """自动化任务推荐模块"""

    async def suggest_auto_tasks(self, tasks: List[Task]) -> List[Task]:
        """推荐可自动完成的任务"""
        auto_tasks = []
        for task in tasks:
            if can_auto_execute(task):
                auto_tasks.append(task)
        return auto_tasks


class MorningBriefReport:
    """早间简报生成器"""

    def __init__(self, workspace: Path = None):
        self.workspace = workspace or Path.cwd()
        self.weather = WeatherModule()
        self.youtube = YouTubeModule()
        self.calendar = CalendarModule()  # 日历模块已重新启用
        self.tasks = TaskModule(workspace)
        self.auto_recommender = AutoTaskRecommender()

    async def generate(self) -> str:
        """生成早间简报"""
        now = datetime.now()

        # 获取各模块数据
        weather_list = await self.weather.get_all_weather()
        youtube_videos = await self.youtube.fetch_trending(5)
        # calendar_events = await self.calendar.get_today_events()  # 日历已禁用
        calendar_events = []  # 日历已禁用
        all_tasks = await self.tasks.get_today_tasks()
        auto_tasks = await self.auto_recommender.suggest_auto_tasks(all_tasks)

        # 生成报告
        report = f"# 🌅 Morning Brief - {now.strftime('%Y-%m-%d %H:%M')}\n\n"

        # 天气 - 多城市
        report += "## ☀️ 天气\n"
        for weather in weather_list:
            report += f"- **{weather.get('location', 'N/A')}**: {weather.get('temperature', 'N/A')} {weather.get('condition', 'N/A')} 💧{weather.get('humidity', 'N/A')}\n"
        report += "\n"

        # 日历 - 今日事件
        report += "## 📅 日程\n"
        if calendar_events:
            for event in calendar_events[:5]:
                start = event["start"].get("dateTime", event["start"].get("date"))
                summary = event.get("summary", "无标题")
                if "T" in start:
                    dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    time_str = dt.strftime("%H:%M")
                else:
                    time_str = "全天"
                report += f"- {time_str} | {summary}\n"
        else:
            report += "- 今日无日程 ✨"
        report += "\n"

        report += f"""## 📺 YouTube 趋势
"""

        for i, video in enumerate(youtube_videos, 1):
            report += f"{i}. **{video['title']}**\n"
            report += f"   - 频道: {video['channel']}\n"
            report += f"   - 观看: {video['views']}\n\n"

        report += f"""## 📋 今日任务 ({len(all_tasks)} 个)
"""

        # 按优先级分组
        by_priority = {p: [] for p in Priority}
        for task in all_tasks:
            by_priority[task.priority].append(task)

        for priority in [Priority.P0, Priority.P1, Priority.P2]:
            if by_priority[priority]:
                report += f"\n### {priority.value} ({len(by_priority[priority])} 个)\n"
                for task in by_priority[priority]:
                    report += f"- [{task.id}] {task.title}\n"

        report += f"""

## 🤖 自动化推荐 ({len(auto_tasks)} 个)
"""
        if auto_tasks:
            for task in auto_tasks:
                report += f"- `[{task.id}]` {task.title}\n"
        else:
            report += "暂无可自动完成的任务\n"

        report += f"""
---
*Generated by Morning Brief Agent*
"""

        return report

    async def generate_telegram(self, auto_task_count: int = 0, pending_count: int = 0) -> str:
        """生成 Telegram 格式简报（短版）"""
        now = datetime.now()
        weather_list = await self.weather.get_all_weather()

        # calendar_events = await self.calendar.get_today_events()  # 日历已禁用
        calendar_events = []  # 日历已禁用

        weather_text = []
        for w in weather_list:
            weather_text.append(f"{w.get('location', '')}: {w.get('temperature', 'N/A')} {w.get('condition', 'N/A')}")

        # 日历事件
        if calendar_events:
            cal_text = []
            for event in calendar_events[:3]:
                start = event["start"].get("dateTime", event["start"].get("date"))
                summary = event.get("summary", "无标题")[:20]
                if "T" in start:
                    dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    time_str = dt.strftime("%H:%M")
                else:
                    time_str = "全天"
                cal_text.append(f"{time_str} {summary}")
            calendar_text = "\n📅 " + ", ".join(cal_text)
        else:
            calendar_text = "\n📅 今日无日程"

        return f"""🌅 **Morning Brief** - {now.strftime('%m/%d %H:%M')}

☀️ {', '.join(weather_text)}
{calendar_text}

📋 今日任务: {pending_count} 个待执行
🤖 自动化任务: {auto_task_count} 个推荐

详情 → 全量报告
"""


class MorningBriefAgent:
    """Morning Brief Agent 主类"""

    def __init__(self):
        self.workspace = Path("/Users/apple/openclaw")
        self.report = MorningBriefReport(self.workspace)

    async def run(self) -> str:
        """运行 Morning Brief"""
        return await self.report.generate()


async def main():
    """测试入口"""
    agent = MorningBriefAgent()
    report = await agent.run()

    output_path = Path.home() / ".openclaw/morning_brief/latest.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)

    print(f"✅ Morning Brief 已生成: {output_path}")
    print(f"\n{report[:500]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
