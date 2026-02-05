#!/usr/bin/env python3
"""
Android Phone Agent - OpenClaw 集成

功能：
- 连接/断开 Android 真机
- 点击、滑动、输入等操作
- 截图、录屏
- 启动/停止 scrcpy 投屏
"""

from pathlib import Path
from typing import Dict, Any
import subprocess
import sys

# 导入 MCP tools (动态加载)
def get_mcp_tools():
    """从 MCP server 导入工具"""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".." / "projects" / "android-phone-mcp" / "src"))
        from android_phone.server import app
        return app._tools
    except ImportError as e:
        return {"error": str(e)}


class AndroidPhoneAgent:
    """Android Phone Agent 主类"""
    
    def __init__(self):
        self.workspace = Path("/Users/apple/openclaw")
    
    async def connect(self) -> str:
        """连接设备"""
        result = subprocess.run(
            ["python3", "-c", "from android_phone.server import app; print(app.tools['connect'].call())"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def click(self, x: int, y: int) -> str:
        """点击"""
        result = subprocess.run(
            ["python3", "-c", f"from android_phone.server import app; print(app.tools['click'].call(x={x}, y={y}))"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: float = 0.5) -> str:
        """滑动"""
        result = subprocess.run(
            ["python3", "-c", f"from android_phone.server import app; print(app.tools['swipe'].call(x1={x1}, y1={y1}, x2={x2}, y2={y2}, duration={duration}))"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def input_text(self, text: str) -> str:
        """输入"""
        result = subprocess.run(
            ["python3", "-c", f"from android_phone.server import app; print(app.tools['input_text'].call(text='{text}'))"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def screenshot(self, path: str = "/tmp/android_phone_screen.png") -> str:
        """截图"""
        result = subprocess.run(
            ["python3", "-c", f"from android_phone.server import app; print(app.tools['screenshot'].call(path='{path}'))"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def get_info(self) -> str:
        """获取设备信息"""
        result = subprocess.run(
            ["python3", "-c", "from android_phone.server import app; print(app.tools['get_info'].call())"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def start_scrcpy(self) -> str:
        """启动 scrcpy"""
        result = subprocess.run(
            ["python3", "-c", "from android_phone.server import app; print(app.tools['start_scrcpy'].call())"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr
    
    async def stop_scrcpy(self) -> str:
        """停止 scrcpy"""
        result = subprocess.run(
            ["python3", "-c", "from android_phone.server import app; print(app.tools['stop_scrcpy'].call())"],
            capture_output=True,
            text=True,
            cwd=str(self.workspace / "projects" / "android-phone-mcp" / "src")
        )
        return result.stdout or result.stderr


async def main():
    """测试入口"""
    agent = AndroidPhoneAgent()
    
    print("📱 Android Phone Agent 测试")
    print("=" * 40)
    
    # 连接测试
    print("\n1. 连接设备...")
    info = await agent.get_info()
    print(info)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
