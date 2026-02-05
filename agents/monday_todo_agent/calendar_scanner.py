#!/usr/bin/env python3
"""
Monday-TODO Calendar Scanner - 日历扫描模块

功能：
1. 读取 Monday-TODO 日历
2. 筛选未完成任务
3. 添加/更新事件
"""

from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "google_calendar.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]  # 读写权限

# Monday-TODO 日历 ID
MONDAY_TODO_CALENDAR = "c26036ec2fc528be65aa0ab3cf7bbade1ae434ed409f3565830717a75e724b8e@group.calendar.google.com"


@dataclass
class TodoItem:
    """TODO 项"""
    id: str
    title: str
    date: str
    description: str = ""
    completed: bool = False
    is_reflection: bool = False


class CalendarScanner:
    """日历扫描器"""

    def __init__(self):
        self.service = None
        self.initialized = False

    def init(self) -> bool:
        """初始化"""
        try:
            if not TOKEN_FILE.exists():
                print("⚠️ Google Calendar 未授权")
                return False

            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    return False

            self.service = build("calendar", "v3", credentials=creds)
            self.initialized = True
            return True
        except Exception as e:
            print(f"⚠️ Calendar 初始化失败: {e}")
            return False

    def _is_completed(self, title: str) -> bool:
        """检查是否标记为已完成"""
        return "【已完成】" in title or "[已完成]" in title or "✅" in title

    def _is_reflection(self, title: str) -> bool:
        """检查是否是反思"""
        return "【反思】" in title or "[反思]" in title

    async def scan_incomplete(self, days: int = 7) -> List[TodoItem]:
        """扫描未完成的 TODO"""
        if not self.initialized:
            if not self.init():
                return []

        try:
            now = datetime.datetime.now()
            start = now.replace(tzinfo=datetime.timezone.utc)
            end = (now + datetime.timedelta(days=days)).replace(tzinfo=datetime.timezone.utc)

            events = self.service.events().list(
                calendarId=MONDAY_TODO_CALENDAR,
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            items = events.get("items", [])
            todos = []

            for event in items:
                title = event.get("summary", "")
                # 跳过已完成和反思
                if self._is_completed(title) or self._is_reflection(title):
                    continue

                start_date = event["start"].get("dateTime", event["start"].get("date"))[:10]
                description = event.get("description", "")

                todos.append(TodoItem(
                    id=event["id"],
                    title=title,
                    date=start_date,
                    description=description,
                    completed=False,
                    is_reflection=False
                ))

            return todos

        except Exception as e:
            print(f"⚠️ 扫描日历失败: {e}")
            return []

    async def get_all_events(self, days: int = 7) -> List[Dict]:
        """获取所有事件"""
        if not self.initialized:
            if not self.init():
                return []

        try:
            now = datetime.datetime.now()
            start = now.replace(tzinfo=datetime.timezone.utc)
            end = (now + datetime.timedelta(days=days)).replace(tzinfo=datetime.timezone.utc)

            events = self.service.events().list(
                calendarId=MONDAY_TODO_CALENDAR,
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            return events.get("items", [])

        except Exception as e:
            print(f"⚠️ 获取事件失败: {e}")
            return []

    async def mark_completed(self, event_id: str, title: str = "") -> bool:
        """标记为已完成"""
        if not self.initialized:
            if not self.init():
                return False

        try:
            new_title = f"【已完成】 {title}" if title else "【已完成】"

            self.service.events().update(
                calendarId=MONDAY_TODO_CALENDAR,
                eventId=event_id,
                body={
                    "summary": new_title,
                    "status": "confirmed"
                }
            ).execute()

            print(f"✅ 已标记完成: {new_title}")
            return True

        except Exception as e:
            print(f"⚠️ 标记失败: {e}")
            return False

    async def add_reflection(self, date: str, content: str) -> bool:
        """添加反思事件"""
        if not self.initialized:
            if not self.init():
                return False

        try:
            event = {
                "summary": f"【反思】{date}",
                "description": content,
                "start": {"date": date},
                "end": {"date": date}
            }

            self.service.events().insert(
                calendarId=MONDAY_TODO_CALENDAR,
                body=event
            ).execute()

            print(f"✅ 已添加反思: {date}")
            return True

        except Exception as e:
            print(f"⚠️ 添加反思失败: {e}")
            return False

    async def add_todo(self, title: str, date: str, description: str = "") -> bool:
        """添加 TODO"""
        if not self.initialized:
            if not self.init():
                return False

        try:
            event = {
                "summary": title,
                "description": description,
                "start": {"date": date},
                "end": {"date": date}
            }

            self.service.events().insert(
                calendarId=MONDAY_TODO_CALENDAR,
                body=event
            ).execute()

            print(f"✅ 已添加 TODO: {title}")
            return True

        except Exception as e:
            print(f"⚠️ 添加 TODO 失败: {e}")
            return False


# 便捷函数
_scanner = None


def get_scanner() -> CalendarScanner:
    global _scanner
    if _scanner is None:
        _scanner = CalendarScanner()
    return _scanner


async def scan_incomplete(days: int = 7) -> List[TodoItem]:
    return await get_scanner().scan_incomplete(days)


async def mark_completed(event_id: str, title: str = "") -> bool:
    return await get_scanner().mark_completed(event_id, title)


async def add_reflection(date: str, content: str) -> bool:
    return await get_scanner().add_reflection(date, content)


if __name__ == "__main__":
    import asyncio

    async def test():
        scanner = CalendarScanner()
        scanner.init()

        print("📅 Monday-TODO 扫描测试\n")

        # 扫描未完成
        todos = await scanner.scan_incomplete()
        print(f"未完成任务: {len(todos)} 个\n")
        for t in todos[:5]:
            print(f"  - {t.date} | {t.title}")

        # 所有事件
        events = await scanner.get_all_events()
        print(f"\n总事件数: {len(events)}")

    asyncio.run(test())
