#!/usr/bin/env python3
"""
雪球数据客户端
用于获取A股行情、社区帖子、组合数据等
"""

import httpx
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

DATA_DIR = Path(__file__).parent.parent / 'data' / 'xueqiu'

class XueqiuClient:
    """雪球HTTP客户端"""
    
    BASE_URL = "https://xueqiu.com"
    STOCK_URL = "https://stock.xueqiu.com"
    
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://xueqiu.com/",
        "Origin": "https://xueqiu.com",
    }
    
    def __init__(self, cookie: Optional[str] = None):
        """
        初始化客户端
        cookie: 可选，用于访问需要登录的数据
        """
        self.client = httpx.Client(timeout=30.0)
        self.client.headers.update(self.DEFAULT_HEADERS)
        
        # 先访问首页获取基础cookie
        self._init_session()
        
        # 如果提供了登录cookie，添加到session
        if cookie:
            self.client.headers["Cookie"] = cookie
        
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def _init_session(self):
        """初始化session，获取必要的cookie"""
        try:
            resp = self.client.get(self.BASE_URL)
            # 雪球会自动设置一些cookie
        except Exception as e:
            print(f"初始化session失败: {e}")
    
    def get_quote(self, symbol: str) -> Dict:
        """
        获取股票实时报价
        symbol: 股票代码，如 SH000001, SZ000001
        """
        url = f"{self.STOCK_URL}/v5/stock/quote.json"
        params = {
            "symbol": symbol,
            "extend": "detail"
        }
        
        resp = self.client.get(url, params=params)
        data = resp.json()
        
        if data.get("error_code") == 0:
            return data.get("data", {}).get("quote", {})
        else:
            raise Exception(f"获取报价失败: {data.get('error_description')}")
    
    def get_kline(self, symbol: str, period: str = "day", count: int = 100) -> List[Dict]:
        """
        获取K线数据
        symbol: 股票代码
        period: day/week/month/quarter/year/120m/60m/30m/15m/5m/1m
        count: 获取数量
        """
        url = f"{self.STOCK_URL}/v5/stock/chart/kline.json"
        params = {
            "symbol": symbol,
            "begin": int(time.time() * 1000),
            "period": period,
            "type": "before",
            "count": -count,
            "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        }
        
        resp = self.client.get(url, params=params)
        data = resp.json()
        
        if data.get("error_code") == 0:
            items = data.get("data", {}).get("item", [])
            columns = data.get("data", {}).get("column", [])
            
            # 转换为字典列表
            result = []
            for item in items:
                row = dict(zip(columns, item))
                result.append(row)
            return result
        else:
            raise Exception(f"获取K线失败: {data.get('error_description')}")
    
    def get_hot_stocks(self, market: str = "CN", count: int = 10) -> List[Dict]:
        """
        获取热门股票
        market: CN=A股, HK=港股, US=美股
        """
        url = f"{self.STOCK_URL}/v5/stock/hot_stock/list.json"
        params = {
            "size": count,
            "type": market,
            "_type": "10"
        }
        
        resp = self.client.get(url, params=params)
        data = resp.json()
        
        if data.get("error_code") == 0:
            return data.get("data", {}).get("items", [])
        else:
            return []
    
    def get_market_status(self) -> Dict:
        """获取市场状态（交易时间等）"""
        url = f"{self.STOCK_URL}/v5/stock/batch/quote.json"
        symbols = "SH000001,SZ399001,SZ399006"  # 上证、深证、创业板
        params = {"symbol": symbols}
        
        resp = self.client.get(url, params=params)
        data = resp.json()
        
        result = {}
        if data.get("error_code") == 0:
            items = data.get("data", {}).get("items", [])
            for item in items:
                quote = item.get("quote", {})
                result[quote.get("symbol")] = {
                    "name": quote.get("name"),
                    "current": quote.get("current"),
                    "percent": quote.get("percent"),
                    "chg": quote.get("chg"),
                    "volume": quote.get("volume"),
                    "amount": quote.get("amount"),
                    "market_capital": quote.get("market_capital"),
                }
        
        return result
    
    def search(self, query: str, count: int = 10) -> List[Dict]:
        """搜索股票"""
        url = f"{self.STOCK_URL}/v5/stock/search.json"
        params = {
            "q": query,
            "size": count
        }
        
        try:
            resp = self.client.get(url, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            if data.get("error_code") == 0:
                return data.get("data", {}).get("stocks", [])
        except Exception as e:
            print(f"搜索失败: {e}")
        return []
    
    def close(self):
        """关闭客户端"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


def test():
    """测试函数"""
    with XueqiuClient() as client:
        # 测试市场状态
        print("=== 市场状态 ===")
        try:
            status = client.get_market_status()
            if status:
                for symbol, data in status.items():
                    pct = data.get('percent') or 0
                    print(f"{data['name']}: {data['current']} ({pct:+.2f}%)")
            else:
                print("(无数据，可能是非交易时间)")
        except Exception as e:
            print(f"获取市场状态失败: {e}")
        
        # 测试热门股票
        print("\n=== 热门股票 ===")
        try:
            hot = client.get_hot_stocks(count=5)
            if hot:
                for stock in hot:
                    q = stock.get('quote', {})
                    pct = q.get('percent') or 0
                    print(f"{q.get('name')}: {q.get('current')} ({pct:+.2f}%)")
            else:
                print("(无数据)")
        except Exception as e:
            print(f"获取热门股票失败: {e}")
        
        # 测试报价
        print("\n=== 平安银行报价 ===")
        try:
            quote = client.get_quote("SZ000001")
            if quote:
                pct = quote.get('percent') or 0
                print(f"{quote.get('name')}: {quote.get('current')} ({pct:+.2f}%)")
        except Exception as e:
            print(f"获取报价失败: {e}")
        
        # 测试K线
        print("\n=== 平安银行K线(最近5日) ===")
        try:
            kline = client.get_kline("SZ000001", period="day", count=5)
            for k in kline[:3]:
                ts = k.get('timestamp', 0)
                if ts:
                    date = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d')
                    print(f"{date}: 收盘 {k.get('close')}")
        except Exception as e:
            print(f"获取K线失败: {e}")


if __name__ == '__main__':
    test()
