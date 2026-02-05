#!/usr/bin/env python3
"""
Google Calendar 模块 - 集成到 Morning Brief (修复版)
"""

from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import json

CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "google_calendar.json"
TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class CalendarModule:
    """日历模块"""

    # Monday-TODO 日历 ID
    MONDAY_TODO_CALENDAR = "c26036ec2fc528be65aa0ab3cf7bbade1ae434ed409f3565830717a75e724b8e@group.calendar.google.com"

    def __init__(self):
        self.service = None
        self.initialized = False

    def init(self) -> bool:
        """初始化日历服务"""
        try:
            if not TOKEN_FILE.exists():
                print("⚠️ Google Calendar 未授权，请先运行: python3 scripts/google_calendar_auth.py")
                return False

            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

            # 检查是否有效
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
            print(f"⚠️ Google Calendar 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def get_today_events(self, max_results: int = 10) -> list:
        """获取今日事件（Monday-TODO 日历）"""
        if not self.initialized:
            if not self.init():
                return []

        try:
            now = datetime.datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=datetime.timezone.utc)

            events_result = (
                self.service.events()
                .list(
                    calendarId=self.MONDAY_TODO_CALENDAR,  # Monday-TODO
                    timeMin=start_of_day.isoformat(),
                    timeMax=end_of_day.isoformat(),
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            return events_result.get("items", [])

        except Exception as e:
            print(f"⚠️ 获取今日事件失败: {e}")
            return []

    async def get_week_events(self, max_results: int = 20) -> list:
        """获取本周事件"""
        if not self.initialized:
            if not self.init():
                return []

        try:
            now = datetime.datetime.utcnow()
            end_date = now + datetime.timedelta(days=7)

            events_result = (
                self.service.events()
                .list(
                    calendarId=self.MONDAY_TODO_CALENDAR,  # Monday-TODO
                    timeMin=now.isoformat() + "Z",
                    timeMax=end_date.isoformat() + "Z",
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            return events_result.get("items", [])

        except Exception as e:
            print(f"⚠️ 获取本周事件失败: {e}")
            return []

    def format_events(self, events: list) -> str:
        """格式化事件列表"""
        if not events:
            return "📅 今日无日程 ✨"

        result = "📅 **今日日程**\n"
        for i, event in enumerate(events, 1):
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "无标题")
            location = event.get("location", "")
            description = event.get("description", "")

            # 解析时间
            if "T" in start:
                dt = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M")
                date_str = dt.strftime("%m/%d")
            else:
                dt = datetime.datetime.fromisoformat(start)
                time_str = "全天"
                date_str = dt.strftime("%m/%d")

            result += f"\n{i}. **{date_str} {time_str}** | {summary}"
            if location:
                result += f"\n   📍 {location}"
            if description:
                desc_short = description[:80].replace("\n", " ")
                result += f"\n   📝 {desc_short}..."

        return result

    def format_events_telegram(self, events: list) -> str:
        """Telegram 格式的事件列表（短版）"""
        if not events:
            return "📅 今日无日程"

        lines = ["📅 **今日日程**"]
        for event in events[:5]:  # 最多显示5个
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "无标题")

            if "T" in start:
                dt = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M")
            else:
                time_str = "全天"

            lines.append(f"• {time_str} {summary[:30]}")

        if len(events) > 5:
            lines.append(f"... 还有 {len(events) - 5} 个事件")

        return "\n".join(lines)


# 便捷函数
_calendar_module = None


def get_calendar() -> CalendarModule:
    """获取日历模块单例"""
    global _calendar_module
    if _calendar_module is None:
        _calendar_module = CalendarModule()
    return _calendar_module


async def get_today_events() -> list:
    """获取今日事件"""
    return await get_calendar().get_today_events()


async def get_week_events() -> list:
    """获取本周事件"""
    return await get_calendar().get_week_events()


if __name__ == "__main__":
    import asyncio

    calendar = CalendarModule()

    # 测试
    print("🔄 测试 Google Calendar 连接...\n")

    events_today = asyncio.run(calendar.get_today_events())
    events_week = asyncio.run(calendar.get_week_events())

    print(f"📅 今日: {len(events_today)} 个事件")
    print(f"📅 本周: {len(events_week)} 个事件\n")

    print("=" * 50)
    print("今日日程:")
    print("=" * 50)
    print(calendar.format_events(events_today))

    print("\n" + "=" * 50)
    print("Telegram 格式:")
    print("=" * 50)
    print(calendar.format_events_telegram(events_today))
