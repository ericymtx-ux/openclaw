"""
Agents 目录
"""
import sys
from pathlib import Path

# 添加子目录到路径
_agent_dir = Path(__file__).resolve().parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))
