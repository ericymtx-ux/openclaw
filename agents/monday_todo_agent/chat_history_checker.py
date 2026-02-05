#!/usr/bin/env python3
"""
Monday-TODO Chat History Checker - 聊天记录检查模块

功能：
1. 扫描会话历史
2. 检查任务是否已完成
3. 提取反思内容
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass
import subprocess
import sys

# 添加 OpenClaw 路径
OPENCLAW_PATH = Path("/Users/apple/openclaw")
OPENCLAW_SESSIONS = Path.home() / ".openclaw" / "agents"


@dataclass
class ReflectionItem:
    """反思项"""
    date: str
    content: str
    source: str
    lessons: List[str]
    good_patterns: List[str]
    bad_patterns: List[str]


class ChatHistoryChecker:
    """聊天记录检查器"""

    def __init__(self):
        self.sessions_dir = OPENCLAW_SESSIONS

    def _get_recent_sessions(self, days: int = 3) -> List[Dict]:
        """获取最近会话"""
        sessions = []
        cutoff = datetime.now() - timedelta(days=days)

        try:
            # 查找所有会话
            for agent_dir in self.sessions_dir.iterdir():
                if not agent_dir.is_dir():
                    continue

                sessions_file = agent_dir / "sessions.json"
                if not sessions_file.exists():
                    continue

                try:
                    data = json.loads(sessions_file.read_text())
                    for session in data:
                        last_active = datetime.fromisoformat(
                            session.get("lastActiveAt", "2000-01-01")
                        )
                        if last_active > cutoff:
                            sessions.append({
                                "agent": agent_dir.name,
                                "key": session.get("key", ""),
                                "last_active": last_active,
                                "messages": len(session.get("messages", []))
                            })
                except Exception:
                    continue

            # 按最后活跃时间排序
            sessions.sort(key=lambda x: x["last_active"], reverse=True)
            return sessions

        except Exception as e:
            print(f"⚠️ 获取会话失败: {e}")
            return []

    async def _get_session_history(self, session_key: str) -> List[Dict]:
        """获取特定会话的历史"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "openclaw", "sessions", "history", session_key],
                capture_output=True,
                text=True,
                cwd=OPENCLAW_PATH,
                timeout=30
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            return []

        except Exception as e:
            print(f"⚠️ 获取历史失败: {e}")
            return []

    def _check_task_keywords(self, text: str, task_title: str) -> Dict:
        """检查任务关键词匹配"""
        keywords = self._extract_keywords(task_title)
        text_lower = text.lower()

        matches = []
        for kw in keywords:
            if kw.lower() in text_lower:
                matches.append(kw)

        return {
            "matched": len(matches) > 0,
            "matched_keywords": matches,
            "total_keywords": len(keywords),
            "confidence": len(matches) / len(keywords) if keywords else 0
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 移除标记词
        text = text.replace("【已完成】", "").replace("【反思】", "")
        text = text.replace("[已完成]", "").replace("[反思]", "")

        # 分割成词
        words = re.findall(r'[\w\u4e00-\u9fff]+', text)
        # 过滤停用词
        stop_words = {"的", "在", "和", "与", "或", "了", "是", "我", "你", "他", "她", "这", "那", "个", "们"}
        words = [w for w in words if len(w) > 2 and w not in stop_words]

        return words[:10]  # 最多10个关键词

    async def check_completed(self, task: "TodoItem") -> Dict:
        """检查任务是否已完成"""
        # 获取最近会话
        sessions = self._get_recent_sessions(days=3)

        all_text = []
        for session in sessions[:5]:  # 只检查最近5个会话
            history = await self._get_session_history(session["key"])
            for msg in history:
                content = msg.get("content", "")
                if content:
                    all_text.append(content)

        # 合并所有文本
        full_text = " ".join(all_text)

        # 检查匹配
        check_result = self._check_task_keywords(full_text, task.title)

        return {
            "task_id": task.id,
            "task_title": task.title,
            "completed": check_result["confidence"] > 0.3,
            "confidence": check_result["confidence"],
            "matched_keywords": check_result["matched_keywords"],
            "sessions_checked": len(sessions)
        }

    async def scan_reflections(self, days: int = 3) -> List[ReflectionItem]:
        """扫描反思内容"""
        sessions = self._get_recent_sessions(days=days)
        reflections = []

        for session in sessions[:10]:
            history = await self._get_session_history(session["key"])

            for msg in history:
                content = msg.get("content", "")
                if not content:
                    continue

                # 检测反思关键词
                if any(kw in content for kw in ["今晚又搞定了", "🌙 今晚", "反思", "经验教训"]):
                    reflection = self._parse_reflection(
                        content,
                        session["agent"],
                        session["last_active"].strftime("%Y-%m-%d")
                    )
                    if reflection:
                        reflections.append(reflection)

        return reflections

    def _parse_reflection(self, content: str, source: str, date: str) -> Optional[ReflectionItem]:
        """解析反思内容"""
        # 提取经验教训
        lessons = []
        good_patterns = []
        bad_patterns = []

        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 提取列表项
            if line.startswith("- "):
                text = line[2:].strip()
                if "做得好" in text or "good" in text.lower() or "成功" in text:
                    good_patterns.append(text)
                elif "做得差" in text or "bad" in text.lower() or "问题" in text:
                    bad_patterns.append(text)
                else:
                    lessons.append(text)

        if not (lessons or good_patterns or bad_patterns):
            return None

        return ReflectionItem(
            date=date,
            content=content[:500],  # 限制长度
            source=source,
            lessons=lessons,
            good_patterns=good_patterns,
            bad_patterns=bad_patterns
        )


# 便捷函数
_checker = None


def get_checker() -> ChatHistoryChecker:
    global _checker
    if _checker is None:
        _checker = ChatHistoryChecker()
    return _checker


async def check_task_completed(task: "TodoItem") -> Dict:
    return await get_checker().check_completed(task)


async def scan_reflections(days: int = 3) -> List[ReflectionItem]:
    return await get_checker().scan_reflections(days)


if __name__ == "__main__":
    import re

    async def test():
        checker = ChatHistoryChecker()

        print("🔄 测试聊天记录检查...\n")

        # 获取最近会话
        sessions = checker._get_recent_sessions(days=3)
        print(f"最近会话: {len(sessions)} 个")
        for s in sessions[:3]:
            print(f"  - {s['agent']}: {s['messages']} 条消息")

        # 测试关键词提取
        test_title = "查看股票邮件"
        keywords = checker._extract_keywords(test_title)
        print(f"\n关键词测试: {test_title}")
        print(f"  -> {keywords}")

        # 测试反思扫描
        reflections = await checker.scan_reflections(days=7)
        print(f"\n反思: {len(reflections)} 个")

    asyncio.run(test())
