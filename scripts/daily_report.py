#!/usr/bin/env python3
"""
每日投资报告生成器
"""

import json
from datetime import datetime
from pathlib import Path

def get_market_data():
    """获取市场数据（从缓存或 API）"""
    # TODO: 实现真实数据获取
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "indices": [
            {"name": "上证指数", "code": "sh000001", "close": 4117.95, "change": -0.96},
            {"name": "深证成指", "code": "sz399001", "close": 14205.89, "change": -0.66},
            {"name": "创业板指", "code": "sz399006", "close": 3346.36, "change": 1.27},
            {"name": "科创50", "code": "sh000688", "close": 1509.40, "change": 0.12},
        ],
        "stats": {
            "up": 2453,
            "down": 2896,
            "flat": 113,
            "涨停": 73,
            "跌停": 74
        }
    }

def generate_report(date=None):
    """生成投资报告"""
    date = date or datetime.now().strftime("%Y-%m-%d")
    data = get_market_data()
    
    report = f"""# 📊 每日投资报告 - {date}

*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## 📈 市场概览

| 指数 | 收盘价 | 涨跌幅 |
|------|--------|--------|
"""
    
    for idx in data["indices"]:
        emoji = "🟢" if idx["change"] > 0 else "🔴"
        report += f"| {idx['name']} | {idx['close']:.2f} | {emoji}{idx['change']:.2f}% |\n"
    
    report += f"""
## 📊 市场统计

- **上涨**: {data['stats']['up']} 只
- **下跌**: {data['stats']['down']} 只  
- **平盘**: {data['stats']['flat']} 只
- **涨停**: {data['stats']['涨停']} 只
- **跌停**: {data['stats']['跌停']} 只

## 💡 策略建议

暂无

---
*数据来源: Tushare/Akshare | 仅供参考，不构成投资建议*
"""
    
    return report

def main():
    """主函数"""
    date = datetime.now().strftime("%Y%m%d")
    report = generate_report(date)
    
    # 保存报告
    report_dir = Path("/Users/apple/openclaw/data/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = report_dir / f"daily_{date}.md"
    report_file.write_text(report)
    
    print(f"✅ 报告已生成: {report_file}")
    print(f"\n{report}")

if __name__ == "__main__":
    main()
