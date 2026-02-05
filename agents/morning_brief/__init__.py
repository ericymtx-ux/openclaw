"""
Morning Brief Agent - 每日早间简报系统

功能：
- 每日 08:00 自动生成早间简报
- 包含：天气、YouTube 趋势、任务列表、自动化任务推荐
"""

from .morning_brief import (
    MorningBriefAgent,
    MorningBriefReport,
    WeatherModule,
    YouTubeModule,
    TaskModule,
    AutoTaskRecommender
)

__version__ = "1.0"
__all__ = [
    "MorningBriefAgent",
    "MorningBriefReport",
    "WeatherModule",
    "YouTubeModule",
    "TaskModule",
    "AutoTaskRecommender"
]
