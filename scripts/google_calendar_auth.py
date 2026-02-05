#!/usr/bin/env python3
"""
Google Calendar OAuth - 获取授权 URL
"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CREDENTIALS_FILE = Path.home() / ".openclaw" / "credentials" / "google_calendar.json"
TOKEN_FILE = Path.home() / ".openclaw" / "tokens" / "google_calendar.token"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
REDIRECT_URI = "http://localhost:8080/callback"

def main():
    if not CREDENTIALS_FILE.exists():
        print(f"❌ 凭证文件不存在: {CREDENTIALS_FILE}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE), SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    
    print("\n" + "="*60)
    print("📅 Google Calendar 授权")
    print("="*60)
    print("\n请在浏览器中访问以下链接:\n")
    print(auth_url)
    print("\n" + "="*60)
    print("\n步骤:")
    print("1. 登录 Google 账号 (jackmanayang@gmail.com)")
    print("2. 点击 '允许' 授权日历访问")
    print("3. 浏览器会跳转，复制完整 URL 粘贴到终端\n")

if __name__ == "__main__":
    main()
