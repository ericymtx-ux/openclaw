#!/usr/bin/env python3
"""
股票邮件检查器

功能：
- 每半小时检查邮件
- 筛选股票/ETF 相关邮件
- 生成报告，高亮【开】【持】股票
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EmailChecker:
    """邮件检查器"""

    def __init__(self):
        self.work_dir = Path.home() / ".openclaw/email_checker"
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def get_recent_emails(self, limit: int = 1) -> List[Dict]:
        """获取最近邮件"""
        try:
            result = subprocess.run(
                ["himalaya", "envelope", "list", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0 and result.stdout.strip():
                # JSON 直接在 stdout
                if result.stdout.strip().startswith("["):
                    emails = json.loads(result.stdout)
                    # 只返回最近的 limit 封
                    return emails[:limit]

        except Exception as e:
            print(f"⚠️ 获取邮件失败: {e}")

        return []

    def filter_stock_emails(self, emails: List[Dict]) -> List[Dict]:
        """筛选股票/ETF 相关邮件"""
        stock_keywords = [
            "股票",
            "ETF",
            "A股",
            "港股",
            "美股",
            "持仓",
            "买入",
            "卖出",
            "趋势",
            "机会",
            "人气",
        ]

        stock_emails = []
        for email in emails:
            subject = email.get("subject", "")

            if any(kw in subject for kw in stock_keywords):
                stock_emails.append(email)

        return stock_emails

    def read_email_content(self, email_id: str) -> str:
        """读取邮件详细内容"""
        try:
            result = subprocess.run(
                ["himalaya", "message", "read", email_id],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                return result.stdout

        except Exception as e:
            print(f"⚠️ 读取邮件 {email_id} 失败: {e}")

        return ""

    def read_email_contents_concurrent(self, email_ids: List[str]) -> Dict[str, str]:
        """并发读取多封邮件内容"""
        results = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.read_email_content, email_id): email_id
                for email_id in email_ids
            }

            for future in as_completed(futures):
                email_id = futures[future]
                try:
                    content = future.result()
                    results[email_id] = content
                except Exception as e:
                    print(f"⚠️ 并发读取邮件 {email_id} 失败: {e}")
                    results[email_id] = ""

        return results

    def extract_stocks(self, content: str) -> List[Dict]:
        """提取股票信息"""
        stocks = []

        import re

        # 匹配 HTML 表格行 - 格式: <td>日期</td><td>代码</td><td>名称</td>...
        # 列顺序: 日期, 代码, 名称, 收盘价, 涨跌幅, 趋势开关, 量价关系, 热度, 热度排名, 大单净额
        cells = re.findall(r"<td[^>]*>([^<]+)</td>", content)

        i = 0
        while i < len(cells) - 10:
            cell = cells[i]
            # 查找趋势开关列 (🔴开 或 🟡持 或 ⚪空 或 🟢关)
            if cell in ["🔴开", "🟡持", "⚪空", "🟢关"]:
                code = cells[i - 4]  # 4个位置之前是代码
                name = cells[i - 3]  # 3个位置之前是名称
                trend = cell
                price = cells[i - 2]  # 收盘价
                change = cells[i - 1]  # 涨跌幅
                volume_price = cells[i + 1]  # 量价关系
                heat = cells[i + 2]  # 热度
                rank = cells[i + 3]  # 热度排名
                net_amount = cells[i + 4]  # 大单净额

                # 验证代码格式
                if re.match(r"[0-9]{6}\.[SZHS]", code):
                    # 处理趋势开关，统一为 开/持/平
                    if trend == "🔴开":
                        action = "开"
                    elif trend == "🟡持":
                        action = "持"
                    else:
                        action = "平"

                    # 解析热度排名
                    try:
                        rank_num = int(rank)
                    except:
                        rank_num = 999999

                    stocks.append(
                        {
                            "name": name,
                            "code": code,
                            "action": action,
                            "price": price,
                            "change": change,
                            "volume_price": volume_price,
                            "heat": heat,
                            "rank": rank_num,
                            "net_amount": net_amount,
                        }
                    )

            i += 1

        return stocks

    def generate_report(self, emails: List[Dict], stock_emails: List[Dict]) -> str:
        """生成报告"""
        now = datetime.now()

        report = f"""# 📧 股票邮件监控报告

**生成时间**: {now.strftime("%Y-%m-%d %H:%M:%S")}
**检查邮件数**: {len(emails)}
**股票相关邮件**: {len(stock_emails)}

---

"""

        # 股票相关邮件
        if stock_emails:
            report += f"## 📬 股票相关邮件 ({len(stock_emails)} 封)\n\n"

            for i, email in enumerate(stock_emails[:10], 1):
                subject = email.get("subject", "无标题")
                from_name = email.get("from", {}).get("name", "未知")
                from_addr = email.get("from", {}).get("addr", "")
                date = email.get("date", "未知")
                report += f"### {i}. {subject}\n"
                report += f"- 发件人: {from_name} ({from_addr})\n"
                report += f"- 时间: {date}\n\n"

        # 提取股票信号 - 使用并发读取
        all_stocks = []
        email_ids = [
            email.get("id", "") for email in stock_emails[:1] if email.get("id")
        ]
        email_contents = self.read_email_contents_concurrent(email_ids)

        for email in stock_emails[:1]:
            email_id = email.get("id", "")
            if email_id:
                content = email_contents.get(email_id, "")
                stocks = self.extract_stocks(content)
                for stock in stocks:
                    stock["source"] = email.get("subject", "未知")
                all_stocks.extend(stocks)

        if all_stocks:
            report += "## 🎯 股票信号汇总\n\n"

            # 按操作分组
            by_action = {"开": [], "持": [], "平": [], "卖": []}
            for stock in all_stocks:
                action = stock["action"]
                if action in by_action:
                    by_action[action].append(stock)
                else:
                    by_action["平"] = [stock]  # 其他归为"平"

            # 按热度排名排序
            for action in by_action:
                by_action[action].sort(key=lambda x: x.get("rank", 999999))

            # 高亮【开】【持】
            for action, cn in [
                ("开", "🟢 买入"),
                ("持", "🔵 持有"),
                ("平", "🟡 平仓"),
                ("卖", "🔴 卖出"),
            ]:
                if by_action.get(action):
                    stocks = by_action[action]
                    emoji = (
                        "🚀" if action == "开" else ("⭐" if action == "持" else "•")
                    )
                    report += f"### {emoji} {cn} ({len(stocks)} 只)\n\n"

                    for stock in stocks:
                        name = stock["name"]
                        code = stock["code"]
                        price = stock.get("price", "N/A")
                        change = stock.get("change", "N/A")
                        volume_price = stock.get("volume_price", "N/A")

                        if action == "开":
                            report += f"## 🟢 **{name} ({code})** 【{cn}】\n"
                            report += f"- 💰 收盘价: {price} | 📈 涨跌幅: {change}\n"
                            report += f"- 📊 量价关系: {volume_price}\n"
                            report += f"- 🔥 热度排名: {stock.get('rank', 'N/A')} | 热度: {stock.get('heat', 'N/A')}\n\n"
                        elif action == "持":
                            report += f"## ⭐ **{name} ({code})** 【{cn}】\n"
                            report += f"- 💰 收盘价: {price} | 📈 涨跌幅: {change}\n"
                            report += f"- 📊 量价关系: {volume_price}\n"
                            report += f"- 🔥 热度排名: {stock.get('rank', 'N/A')} | 热度: {stock.get('heat', 'N/A')}\n\n"
                        else:
                            report += f"- {name} ({code}) 【{cn}】\n"
                            report += (
                                f"  💰 {price} | 📈 {change} | 📊 {volume_price}\n"
                            )

                    report += "\n"

        report += f"""
---
*由股票邮件检查器自动生成*
"""

        return report

    def generate_telegram_report(
        self, emails: List[Dict], stock_emails: List[Dict]
    ) -> str:
        """生成 Telegram 格式报告 (短版)"""
        now = datetime.now()

        # 统计信号 - 使用并发读取
        all_stocks = []
        email_ids = [
            email.get("id", "") for email in stock_emails[:1] if email.get("id")
        ]
        email_contents = self.read_email_contents_concurrent(email_ids)

        for email in stock_emails[:1]:
            email_id = email.get("id", "")
            if email_id:
                content = email_contents.get(email_id, "")
                stocks = self.extract_stocks(content)
                all_stocks.extend(stocks)

        buy_stocks = [s for s in all_stocks if s["action"] == "开"]
        hold_stocks = [s for s in all_stocks if s["action"] == "持"]

        lines = [
            f"📧 *股票邮件监控* - {now.strftime('%m/%d %H:%M')}",
            f"📬 股票邮件: {len(stock_emails)} 封",
            "",
        ]

        if buy_stocks:
            lines.append(f"🚀 *买入 ({len(buy_stocks)} 只) - 按热度排名*")
            for stock in buy_stocks[:5]:
                rank = stock.get("rank", "-")
                lines.append(f"• **{stock['name']} ({stock['code']})** 🔥{rank}")
            if len(buy_stocks) > 5:
                lines.append(f"  ... 还有 {len(buy_stocks) - 5} 只")
            lines.append("")

        if hold_stocks:
            lines.append(f"⭐ *持有 ({len(hold_stocks)} 只) - 按热度排名*")
            for stock in hold_stocks[:5]:
                rank = stock.get("rank", "-")
                lines.append(f"• **{stock['name']} ({stock['code']})** 🔥{rank}")
            if len(hold_stocks) > 5:
                lines.append(f"  ... 还有 {len(hold_stocks) - 5} 只")
            lines.append("")

        if not buy_stocks and not hold_stocks:
            lines.append("暂无【开】【持】信号")

        return "\n".join(lines)

    def run(self) -> str:
        """运行检查"""
        print(f"📧 开始检查邮件: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 获取最近 10 封邮件
        emails = self.get_recent_emails(10)
        print(f"📬 获取到 {len(emails)} 封邮件")

        # 筛选股票相关
        stock_emails = self.filter_stock_emails(emails)
        print(f"📊 股票相关邮件: {len(stock_emails)} 封")

        # 生成报告
        report = self.generate_report(emails, stock_emails)
        tg_report = self.generate_telegram_report(emails, stock_emails)

        # 保存报告
        now = datetime.now()
        report_path = self.work_dir / f"stock_email_{now.strftime('%Y%m%d_%H%M')}.md"
        report_path.write_text(report)

        tg_path = self.work_dir / f"stock_email_{now.strftime('%Y%m%d_%H%M')}.txt"
        tg_path.write_text(tg_report)

        print(f"✅ 报告已生成: {report_path.name}")
        print(f"✅ Telegram 报告: {tg_path.name}")

        return tg_report


def main():
    """主入口"""
    checker = EmailChecker()
    report = checker.run()
    print("\n" + "=" * 50)
    print(report)


if __name__ == "__main__":
    main()
