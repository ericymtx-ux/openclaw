#!/usr/bin/env python3
"""
Google Calendar - 列出所有日历
"""

from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main():
    if not TOKEN_FILE.exists():
        print("❌ 未授权，请先运行 scripts/google_calendar_auth.py")
        return

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    service = build("calendar", "v3", credentials=creds)

    # 列出所有日历
    print("📅 所有日历:\n")
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get("items", [])

    for cal in calendars:
        summary = cal.get("summary", "Unknown")
        primary = "⭐ 主要" if cal.get("primary") else ""
        print(f"  - {summary} {primary}")

    print("\n" + "="*50)

    # 读取 Monday-TODO 日历
    print("\n🔍 查找 'Monday-TODO' 日历...\n")

    found = None
    for cal in calendars:
        if "monday" in cal.get("summary", "").lower():
            found = cal
            print(f"找到: {cal['summary']} (ID: {cal['id']})")
            break

    if not found:
        print("未找到 'Monday-TODO' 日历")
        print("\n日历 ID 列表:")
        for cal in calendars:
            print(f"  - {cal['summary']}: {cal['id']}")
        return

    # 读取该日历的事件
    cal_id = found["id"]
    print(f"\n📅 {found['summary']} 的事件:\n")

    now = datetime.datetime.utcnow()
    events = service.events().list(
        calendarId=cal_id,
        timeMin=now.isoformat() + "Z",
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    items = events.get("items", [])
    print(f"找到 {len(items)} 个事件\n")

    for event in items:
        start = event["start"].get("dateTime", event["start"].get("date"))
        summary = event.get("summary", "无标题")
        print(f"  - {start[:10]} | {summary}")


if __name__ == "__main__":
    main()
