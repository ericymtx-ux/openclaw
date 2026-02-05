#!/usr/bin/env python3
"""
测试 Monday-TODO 日历 (直接复制代码)
"""
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Monday-TODO 日历 ID
MONDAY_TODO_CALENDAR = "c26036ec2fc528be65aa0ab3cf7bbade1ae434ed409f3565830717a75e724b8e@group.calendar.google.com"


def main():
    if not TOKEN_FILE.exists():
        print("❌ 未授权")
        return

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    service = build("calendar", "v3", credentials=creds)

    now = datetime.datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=datetime.timezone.utc)

    # 读取 Monday-TODO
    events = service.events().list(
        calendarId=MONDAY_TODO_CALENDAR,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    items = events.get("items", [])

    print("📅 Monday-TODO 今日事件:\n")
    if items:
        for e in items:
            start_time = e["start"].get("dateTime", e["start"].get("date"))
            summary = e.get("summary", "无标题")
            print(f"  - {start_time[:10]} | {summary}")
    else:
        print("  今日无事件 ✨")

    # 本周
    end_week = now + datetime.timedelta(days=7)
    events_week = service.events().list(
        calendarId=MONDAY_TODO_CALENDAR,
        timeMin=now.isoformat() + "Z",
        timeMax=end_week.isoformat() + "Z",
        maxResults=20,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    items_week = events_week.get("items", [])
    print(f"\n📅 Monday-TODO 本周事件 ({len(items_week)} 个):\n")
    for e in items_week:
        start_time = e["start"].get("dateTime", e["start"].get("date"))
        summary = e.get("summary", "无标题")
        print(f"  - {start_time[:10]} | {summary}")


if __name__ == "__main__":
    main()
