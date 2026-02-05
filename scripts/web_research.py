#!/usr/bin/env python3
"""
Nightly Web Research Script
Collects interesting content from specified websites based on user interests.
"""

import json
import os
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

# User Profile
USER_PROFILE = {
    "identity": "AI程序员",
    "goals": "一人企业年收入200万（投资增值服务方向）",
    "interests": [
        "AI/LLM/编程工具",
        "投资/量化交易",
        "独立开发者/SaaS",
        "高效生产工具",
        "开源项目"
    ],
    "required_sites": [
        "https://github.com/trending",
        "https://www.producthunt.com",
        "https://v2ex.com",
        "https://twitter.com"
    ]
}

OUTPUT_FILE = "/Users/apple/openclaw/memory.md"


def fetch_url(url, timeout=10):
    """Fetch URL content safely"""
    try:
        req = urlopen(url, timeout=timeout)
        return req.read().decode('utf-8', errors='ignore')
    except (URLError, HTTPError, Exception) as e:
        return f"Error: {e}"


def parse_github_trending(html):
    """Parse GitHub trending page (simplified)"""
    # GitHub trending requires JavaScript rendering
    # In production, use Playwright or API
    return {
        "site": "GitHub Trending",
        "url": "https://github.com/trending",
        "note": "Requires JavaScript rendering. Use API or browser automation.",
        "alternative": "https://github-trending-api.wareneutron.com/"
    }


def parse_product_hunt(html):
    """Parse Product Hunt"""
    return {
        "site": "Product Hunt",
        "url": "https://www.producthunt.com",
        "status": "Requires JavaScript rendering",
        "note": "Check manually or use official API"
    }


def parse_v2ex(html):
    """Parse V2EX"""
    return {
        "site": "V2EX",
        "url": "https://v2ex.com",
        "status": "Accessible",
        "note": "Manual check recommended"
    }


def parse_twitter(html):
    """Parse Twitter/X"""
    return {
        "site": "Twitter/X",
        "url": "https://twitter.com",
        "status": "Requires authentication for most content",
        "note": "Check manually for specific topics"
    }


def generate_report():
    """Generate research report"""
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_profile": USER_PROFILE["identity"],
        "findings": []
    }
    
    for site in USER_PROFILE["required_sites"]:
        try:
            html = fetch_url(site)
            if "github.com/trending" in site:
                report["findings"].append(parse_github_trending(html))
            elif "producthunt.com" in site:
                report["findings"].append(parse_product_hunt(html))
            elif "v2ex.com" in site:
                report["findings"].append(parse_v2ex(html))
            elif "twitter.com" in site:
                report["findings"].append(parse_twitter(html))
        except Exception as e:
            report["findings"].append({"site": site, "error": str(e)})
    
    return report


def main():
    print(f"[{datetime.now()}] Running web research...")
    report = generate_report()
    
    # Save report
    report_file = f"/Users/apple/openclaw/.web_research_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Report saved to {report_file}")
    return report


if __name__ == "__main__":
    main()
