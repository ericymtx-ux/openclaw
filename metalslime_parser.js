const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const START_PAGE = 1;
const END_PAGE = 500;

// 存储所有帖子数据
let allPosts = [];

// 确保输出目录存在
const outputDir = path.dirname(OUTPUT_FILE);
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// 解析 HTML 获取帖子数据
function parsePosts(html, pageNum) {
  const posts = [];
  
  // 匹配帖子的 ID (格式: /2292705444/数字)
  const idPattern = /\/2292705444\/(\d+)/g;
  const ids = [...html.matchAll(idPattern)].map(m => m[1]);
  const uniqueIds = [...new Set(ids)];
  
  for (const id of uniqueIds) {
    // 筛选 2025-2026 年的帖子 (ID > 300000000)
    const postId = parseInt(id);
    if (postId > 300000000) {
      // 匹配时间信息 - 查找帖子 ID 后面的时间链接
      const timePattern = new RegExp(`/2292705444/${id}[^>]*>([^<]*?)\\s*(${getTimePatterns()})([^<]*?)</a>`);
      const timeMatch = html.match(timePattern);
      
      // 匹配内容 - 查找时间后面的大量文本内容
      const contentPattern = new RegExp(`/2292705444/${id}[^>]*>[^<]*</a>[^<]*<[^>]*>([^<]{10,200}?)</generic>`);
      const contentMatch = html.match(contentPattern);
      
      // 匹配互动数据 (转发、评论、点赞)
      const repostMatch = html.match(new RegExp(`/2292705444/${id}[\\s\\S]{0,500}?转发\\s*(\\d+)`));
      const commentMatch = html.match(new RegExp(`/2292705444/${id}[\\s\\S]{0,500}?讨论\\s*(\\d+)`));
      const likeMatch = html.match(new RegExp(`/2292705444/${id}[\\s\\S]{0,500}?赞\\s*(\\d+)`));
      
      // 匹配是否转发帖
      const isRepost = html.includes(`href="/2292705444/${id}"`) && 
                       html.includes('转发') && 
                       html.match(new RegExp(`/2292705444/${id}[\\s\\S]{0,100}?转发`));
      
      let originalPost = null;
      if (isRepost) {
        // 尝试提取原文信息
        const originalAuthorMatch = html.match(new RegExp(`/swag888|/@[\\w]+|/@[^\\s：]+`));
        if (originalAuthorMatch) {
          originalPost = {
            author: originalAuthorMatch[0].replace('/', ''),
            url: '',
            content: ''
          };
        }
      }
      
      posts.push({
        id: id,
        url: `https://xueqiu.com/u/2292705444/${id}`,
        timestamp: timeMatch ? `${timeMatch[1]}${timeMatch[2]}${timeMatch[3]}`.trim() : '',
        display_time: timeMatch ? timeMatch[0].replace(/<\/?[^>]+>/g, '').trim() : '',
        content: contentMatch ? contentMatch[1].replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim() : '',
        original_post: originalPost,
        engagement: {
          reposts: repostMatch ? parseInt(repostMatch[1]) || 0 : 0,
          comments: commentMatch ? parseInt(commentMatch[1]) || 0 : 0,
          likes: likeMatch ? parseInt(likeMatch[1]) || 0 : 0
        }
      });
    }
  }
  
  return posts;
}

function getTimePatterns() {
  return '(?:修改于|昨天|前天|\\d+小时前|\\d+分钟前|\\d+天前|\\d+月\\d+日|今天)\\s*\\d+:\\d+';
}

// 保存结果
function saveResult(pageNum) {
  const result = {
    user: 'metalslime',
    total_pages_scanned: pageNum,
    posts: allPosts
  };
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(result, null, 2));
  console.log(`进度: ${pageNum}/${END_PAGE} 页, 累计抓取 ${allPosts.length} 条 2025-2026 年帖子`);
  console.log(`已保存到 ${OUTPUT_FILE}`);
}

console.log('metalslime 数据抓取脚本已准备就绪');
console.log(`输出文件: ${OUTPUT_FILE}`);
console.log(`抓取范围: 第 ${START_PAGE} 页到第 ${END_PAGE} 页`);
console.log(`筛选条件: 帖子 ID > 300000000 (2025-2026 年)`);
console.log('');
console.log('请使用 browser 工具手动遍历页面，然后使用此脚本解析 HTML 内容');
console.log('');
console.log('执行步骤:');
console.log('1. 使用 browser 访问 https://xueqiu.com/u/2292705444?page=1 到 ?page=500');
console.log('2. 对每个页面执行 browser.snapshot() 获取 HTML');
console.log('3. 将 HTML 传递给 parsePosts() 函数解析');
console.log('4. 调用 saveResult() 保存数据');
