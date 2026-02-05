# metalslime 雪球帖子数据抓取报告

## 任务状态

**部分完成** - 由于技术限制，仅收集了部分数据

## 技术限制

1. **API认证要求**：雪球API需要有效的 `xq_a_token` 认证
2. **JavaScript动态渲染**：页面内容通过JavaScript动态加载，curl/web_fetch无法获取
3. **内容混淆**：页面内容经过混淆保护

## 当前收集的数据

- **帖子数量**：19条（来自可见页面快照）
- **时间范围**：2026年1月初至2026年2月初
- **用户信息**：已获取基本资料
  - ID: 2292705444
  - 昵称: metalslime
  - 粉丝: 204,485
  - 关注: 361
  - 帖子总数: 24,830

## 文件列表

```
raw_data/
├── metalslime_2025_2026.json    # 主要数据文件（当前19条记录）
├── metalslime_scraper.py        # 基础抓取脚本
└── metalslime_full_scraper.py   # 完整抓取脚本（需要认证token）
```

## 完整数据抓取方法

### 方法1：使用浏览器控制（推荐）

1. 确保OpenClaw Gateway正在运行
2. 在Chrome浏览器中打开 https://xueqiu.com/u/2292705444
3. 点击OpenClaw浏览器扩展图标连接
4. 运行浏览器控制脚本进行翻页抓取

### 方法2：使用认证token

1. 从浏览器获取 `xq_a_token` cookie
2. 运行抓取脚本：

```bash
cd /Users/apple/openclaw/raw_data
python3 metalslime_full_scraper.py --token <your_token> --pages 1200
```

### 方法3：手动浏览器操作

1. 打开Chrome开发者工具
2. 访问 https://xueqiu.com/u/2292705444
3. 翻页并复制每页的帖子数据
4. 保存到JSON文件

## 数据格式

```json
{
  "user_info": {
    "id": "2292705444",
    "nickname": "metalslime",
    "fans": 204485,
    "follows": 361,
    "total_posts": 24830
  },
  "posts": [
    {
      "id": "374687736",
      "url": "https://xueqiu.com/2292705444/374687736",
      "timestamp": "2026-02-03T21:27:00.000Z",
      "content": "帖子内容...",
      "original_post": {
        "author": "原贴作者",
        "content": "原贴内容..."
      },
      "engagement": {
        "reposts": 0,
        "comments": 10,
        "likes": 58
      }
    }
  ]
}
```

## 后续步骤

1. **获取认证token**：从已登录的浏览器会话中提取
2. **完整抓取**：运行 `metalslime_full_scraper.py`
3. **数据验证**：检查时间范围是否覆盖2025-2026年
4. **增量更新**：定期运行以获取新帖子

## 注意事项

- 雪球有反爬虫机制，请适度控制请求频率
- 部分转发帖子的原文需要单独访问获取
- 页面时间显示为相对时间，需要转换为精确时间戳
- 预计2025年数据约占总数据的前1000-1200页

---
生成时间: 2026-02-03
