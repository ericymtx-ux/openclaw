const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const BASE_URL = 'https://xueqiu.com/u/2292705444?page=';
const START_PAGE = 1;
const END_PAGE = 500;

// 存储所有帖子数据
let allPosts = [];

// 确保输出目录存在
const outputDir = path.dirname(OUTPUT_FILE);
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// 解析页面获取帖子数据
async function parsePage(pageNum) {
  console.log(`正在抓取第 ${pageNum} 页...`);
  
  try {
    // 使用 browser 工具访问页面
    const response = await fetch(BASE_URL + pageNum, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
      }
    });
    
    const html = await response.text();
    
    // 简单的正则表达式解析帖子数据
    // 匹配 /2292705444/数字 格式的链接
    const postIdPattern = /\/2292705444\/(\d+)/g;
    const timePattern = /(?:修改于|昨天|前天|\d+小时前|\d+分钟前|\d+天前|\d+月\d+日|今天)\s*\d+:\d+/g;
    const contentPattern = /text">([^<]+)<\/text>/g;
    const repostPattern = /转发\s*(\d+)/g;
    const commentPattern = /讨论\s*(\d+)/g;
    const likePattern = /赞\s*(\d+)/g;
    
    const posts = [];
    const ids = [...html.matchAll(/\/2292705444\/(\d+)/g)].map(m => m[1]);
    const uniqueIds = [...new Set(ids)];
    
    for (const id of uniqueIds) {
      // 筛选 2025-2026 年的帖子 (ID > 300000000)
      if (parseInt(id) > 300000000) {
        // 查找时间信息
        const timeMatch = html.match(new RegExp(`/2292705444/${id}[^>]*>([^<]+?)</a>`));
        const time = timeMatch ? timeMatch[1] : '';
        
        // 查找内容
        const contentMatch = html.match(new RegExp(`/2292705444/${id}[^>]*>[^<]*</a>([\\s\\S]*?)<\/generic>`));
        let content = '';
        if (contentMatch) {
          // 清理内容中的 HTML 标签
          content = contentMatch[1].replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim();
        }
        
        // 查找互动数据
        const repostMatch = html.match(new RegExp(`/2292705444/${id}[\\s\\S]*?转发\\s*(\\d+)`));
        const commentMatch = html.match(new RegExp(`/2292705444/${id}[\\s\\S]*?讨论\\s*(\\d+)`));
        const likeMatch = html.match(new RegExp(`/2292705444/${id}[\\s\\S]*?赞\\s*(\\d+)`));
        
        posts.push({
          id: id,
          url: `https://xueqiu.com/u/2292705444/${id}`,
          timestamp: time,
          display_time: time,
          content: content,
          engagement: {
            reposts: repostMatch ? parseInt(repostMatch[1]) : 0,
            comments: commentMatch ? parseInt(commentMatch[1]) : 0,
            likes: likeMatch ? parseInt(likeMatch[1]) : 0
          }
        });
      }
    }
    
    return posts;
    
  } catch (error) {
    console.error(`抓取第 ${pageNum} 页失败:`, error.message);
    return [];
  }
}

// 主函数
async function main() {
  console.log('开始抓取 metalslime 的 2025-2026 年帖子数据...');
  console.log(`目标 URL: ${BASE_URL}`);
  console.log(`抓取范围: 第 ${START_PAGE} 页到第 ${END_PAGE} 页`);
  console.log(`筛选条件: 帖子 ID > 300000000 (2025-2026 年)`);
  console.log('---');
  
  for (let page = START_PAGE; page <= END_PAGE; page++) {
    const posts = await parsePage(page);
    allPosts = allPosts.concat(posts);
    
    // 每 50 页报告一次进度
    if (page % 50 === 0 || page === END_PAGE) {
      console.log(`进度: ${page}/${END_PAGE} 页, 累计抓取 ${allPosts.length} 条 2025-2026 年帖子`);
      
      // 保存中间结果
      const intermediateResult = {
        user: 'metalslime',
        total_pages_scanned: page,
        posts: allPosts
      };
      fs.writeFileSync(OUTPUT_FILE, JSON.stringify(intermediateResult, null, 2));
      console.log(`已保存到 ${OUTPUT_FILE}`);
    }
  }
  
  console.log('---');
  console.log(`抓取完成! 共抓取 ${allPosts.length} 条 2025-2026 年帖子`);
  console.log(`数据已保存到 ${OUTPUT_FILE}`);
}

main().catch(console.error);
