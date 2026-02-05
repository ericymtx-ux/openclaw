#!/usr/bin/env python3
"""
Google Calendar CLI - 读取和管理日历事件
"""

import os
import json
import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 配置
CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "google_calendar.json"
TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CALENDAR_ID = "c26036ec2fc528be65aa0ab3cf7bbade1ae434ed409f3565830717a75e724b8e@group.calendar.google.com"  # Monday-TODO


def get_credentials():
    """获取或刷新 OAuth 凭证"""
    creds = None

    # 加载已保存的 token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # 如果没有有效的凭证，进行 OAuth 认证
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 刷新 token
            creds.refresh(Request())
        else:
            # 进行完整的 OAuth 流程
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"凭证文件不存在: {CREDENTIALS_FILE}\n"
                    "请先在 Google Cloud Console 配置 OAuth 2.0 凭据"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 保存凭证供下次使用
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def get_calendar_service():
    """获取 Google Calendar 服务实例"""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


def list_today_events(service, max_results=10):
    """获取今日事件"""
    now = datetime.datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])


def list_upcoming_events(service, max_results=10):
    """获取即将发生的事件（未来7天）"""
    now = datetime.datetime.utcnow()
    end_date = now + datetime.timedelta(days=7)

    events_result = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=now.isoformat() + "Z",
            timeMax=end_date.isoformat() + "Z",
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])


def format_event(event):
    """格式化事件输出"""
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

    result = f"📅 {date_str} {time_str} | {summary}"
    if location:
        result += f"\n   📍 {location}"
    if description:
        # 截取描述的前100个字符
        desc_short = description[:100].replace("\n", " ")
        result += f"\n   📝 {desc_short}..."

    return result


def main():
    """主函数 - 命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 google_calendar.py [today|week]")
        print("  today - 查看今日事件")
        print("  week  - 查看本周事件")
        sys.exit(1)

    command = sys.argv[1]

    try:
        service = get_calendar_service()
        print("✅ 已连接 Google Calendar\n")

        if command == "today":
            events = list_today_events(service)
            print("📅 今日日程:")
            if not events:
                print("   今日没有日程 ✨")
        elif command == "week":
            events = list_upcoming_events(service)
            print("📅 本周日程 (未来7天):")
            if not events:
                print("   本周没有日程 ✨")
        else:
            print(f"未知命令: {command}")
            sys.exit(1)

        print()
        for i, event in enumerate(events, 1):
            print(f"{i}. {format_event(event)}")
            print()

        # 输出 JSON 格式供程序使用
        print("---JSON---")
        print(json.dumps(events, ensure_ascii=False, indent=2, default=str))

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
