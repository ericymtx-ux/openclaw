# metalslime 雪球帖子数据抓取说明

## 任务概述
从 https://xueqiu.com/u/2292705444 抓取 2025-2026 年所有帖子数据

## 当前状态
- 已创建抓取脚本
- 已创建样本数据文件

## 文件说明
- `metalslime_complete.cjs` - 完整抓取脚本（Puppeteer）
- `metalslime_puppeteer.js` - Puppeteer 抓取脚本
- `metalslime_batch.cjs` - 批量抓取脚本
- `raw_data/metalslime_2025_2026_full.json` - 输出数据文件

## 注意事项
1. 分页可能有缓存问题，需要使用 `?page=N&sort=time` 参数
2. 建议分批抓取，每 50 页保存一次
3. 需要安装 puppeteer: `npm install puppeteer`
4. 抓取 500 页需要较长时间，建议在后台运行

## 输出格式
```json
{
  "user": "metalslime",
  "total_pages_scanned": 500,
  "posts": [
    {
      "id": "帖子ID",
      "url": "https://xueqiu.com/u/2292705444/ID",
      "timestamp": "精确时间",
      "display_time": "页面显示时间",
      "content": "帖子内容",
      "original_post": {
        "author": "原贴作者",
        "url": "原文链接",
        "content": "原文内容"
      },
      "engagement": {"reposts": N, "comments": N, "likes": N}
    }
  ]
}
```
