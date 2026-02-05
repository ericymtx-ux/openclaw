#!/usr/bin/env python3
"""
Google Calendar OAuth - 完成授权回调
"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import sys
import os

CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "google_calendar.json"
TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
REDIRECT_URI = "http://localhost:8080/callback"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 google_calendar_callback.py <完整回调URL>")
        print("\n等待授权完成后，浏览器会跳转到:")
        print("  http://localhost:8080/callback?code=xxx&state=xxx")
        print("\n请复制完整的 URL 粘贴到这里")
        return

    callback_url = sys.argv[1]
    
    if not CREDENTIALS_FILE.exists():
        print(f"❌ 凭证文件不存在: {CREDENTIALS_FILE}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE), SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    try:
        # 使用回调 URL 获取凭证
        flow.fetch_token(authorization_response=callback_url)
        creds = flow.credentials
        
        # 保存凭证
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        
        print("\n✅ 授权成功！")
        print(f"凭证已保存到: {TOKEN_FILE}")
        
        # 测试读取日历
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        now = datetime.datetime.utcnow()
        events = service.events().list(
            calendarId="primary",
            timeMin=now.isoformat() + "Z",
            maxResults=5,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        print(f"\n📅 今日事件 ({len(events.get('items', []))}个):")
        for event in events.get("items", [])[:5]:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "无标题")
            print(f"  - {start[:10]} | {summary}")
            
    except Exception as e:
        print(f"❌ 授权失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import datetime
    main()
