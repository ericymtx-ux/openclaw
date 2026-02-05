#!/usr/bin/env python3
"""
metalslime 雪球帖子抓取脚本
"""

import json
import time
import random
from datetime import datetime

# 数据存储
collected_data = {
    "user": "metalslime",
    "user_id": "2292705444",
    "total_pages_scanned": 0,
    "posts": [],
    "scraped_at": datetime.now().isoformat()
}

def save_intermediate_data(page_num):
    """保存中间结果"""
    output_file = f"/Users/apple/openclaw/raw_data/metalslime_2025_2026_intermediate_{page_num}.json"
    collected_data["total_pages_scanned"] = page_num
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(collected_data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存中间结果到 {output_file}")
    return output_file

def parse_post_from_snapshot(snapshot_data):
    """从快照数据中解析帖子信息"""
    posts = []
    
    if not snapshot_data or 'article' not in str(snapshot_data):
        return posts
    
    # 提取article元素
    articles = []
    if isinstance(snapshot_data, list):
        for item in snapshot_data:
            if isinstance(item, dict) and 'article' in item:
                articles.append(item['article'])
    
    for article in articles:
        try:
            post = {}
            
            # 提取帖子ID和时间
            for elem in article:
                if isinstance(elem, dict) and 'ref' in elem:
                    ref = elem['ref']
                    url = elem.get('url', '')
                    
                    # 查找帖子链接获取ID
                    if '/2292705444/' in str(url):
                        # 提取帖子ID
                        parts = url.split('/')
                        if len(parts) >= 4:
                            try:
                                post_id = int(parts[-1])
                                post['id'] = post_id
                            except:
                                pass
            
            # 提取时间
            for elem in article:
                if isinstance(elem, dict):
                    text_list = elem.get('text', [])
                    if isinstance(text_list, list):
                        for text in text_list:
                            if '小时前' in text or '天前' in text or '昨天' in text or '前天' in text:
                                post['time'] = text
                                break
            
            # 提取内容
            content_parts = []
            for elem in article:
                if isinstance(elem, str):
                    content_parts.append(elem)
                elif isinstance(elem, dict):
                    text = elem.get('text', '')
                    if text and '来自' not in text and '转发' not in text and '讨论' not in text and '赞' not in text:
                        if not any(kw in text for kw in ['metalslime', 'article', 'link']):
                            content_parts.append(text)
            
            post['content'] = ' '.join(content_parts)
            
            if post.get('id') and post.get('content'):
                posts.append(post)
                
        except Exception as e:
            continue
    
    return posts

# 模拟数据（实际使用时需要从browser工具获取）
def simulate_scraping(max_pages=100):
    """模拟抓取过程"""
    for page in range(1, max_pages + 1):
        print(f"正在处理第 {page} 页...")
        
        # 模拟从browser工具获取数据
        # 实际代码中，这里需要调用browser工具
        
        # 模拟获取帖子
        sample_posts = [
            {
                "id": 374687736 - page * 20,
                "time": f"{3 + page}小时前",
                "content": f"这是第{page}页的第1条帖子内容..."
            },
            {
                "id": 374687735 - page * 20,
                "time": f"{4 + page}小时前",
                "content": f"这是第{page}页的第2条帖子内容..."
            }
        ]
        
        for post in sample_posts:
            # 只保留2025-2026年的帖子（ID > 300000000）
            if post['id'] > 300000000:
                collected_data['posts'].append(post)
        
        # 每10页报告进度
        if page % 10 == 0:
            print(f"进度报告：已扫描 {page} 页，获取 {len(collected_data['posts'])} 条帖子")
        
        # 每50页保存中间结果
        if page % 50 == 0:
            save_intermediate_data(page)
        
        # 随机延迟，避免被封
        time.sleep(random.uniform(1, 3))
    
    # 保存最终结果
    final_file = "/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json"
    collected_data["total_pages_scanned"] = max_pages
    
    with open(final_file, 'w', encoding='utf-8') as f:
        json.dump(collected_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n抓取完成！")
    print(f"总页数: {max_pages}")
    print(f"帖子总数: {len(collected_data['posts'])}")
    print(f"结果保存到: {final_file}")
    
    return collected_data

if __name__ == "__main__":
    import sys
    
    max_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    print(f"开始抓取 metalslime 的帖子，最多 {max_pages} 页...")
    result = simulate_scraping(max_pages)
