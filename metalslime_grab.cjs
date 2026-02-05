#!/usr/bin/env node

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

// 从 HTML 快照解析帖子数据
function parsePostsFromSnapshot(html, pageNum) {
  const posts = [];
  
  // 匹配所有帖子 ID
  const idPattern = /\/2292705444\/(\d+)/g;
  const matches = [...html.matchAll(idPattern)];
  const ids = [...new Set(matches.map(m => m[1]))];
  
  for (const id of ids) {
    const postId = parseInt(id);
    
    // 筛选 2025-2026 年的帖子 (ID > 300000000)
    if (postId > 300000000) {
      // 提取时间信息
      const timePattern = new RegExp(`/2292705444/${id}[^>]*>([^<]*(?:修改于|昨天|前天|\\d+小时前|\\d+分钟前|\\d+天前|\\d+月\\d+日|今天)[^<]*)</a>`);
      const timeMatch = html.match(timePattern);
      const timeText = timeMatch ? timeMatch[1].replace(/<[^>]+>/g, ' ').trim() : '';
      
      // 提取内容
      const contentPattern = new RegExp(`/2292705444/${id}[^>]*>[^<]*</a>\\s*<[^>]*>([^<]{10,300}?)</`);
      const contentMatch = html.match(contentPattern);
      const content = contentMatch 
        ? contentMatch[1].replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' ').trim()
        : '';
      
      // 提取互动数据
      const postSection = html.substring(html.indexOf(`/2292705444/${id}`), html.indexOf(`/2292705444/${id}`) + 2000);
      const repostMatch = postSection.match(/转发\\s*(\\d+)/);
      const commentMatch = postSection.match(/讨论\\s*(\\d+)/);
      const likeMatch = postSection.match(/赞\\s*(\\d+)/);
      
      // 判断是否为转发帖
      const isRepost = postSection.includes('blockquote') || postSection.includes('转发');
      let originalPost = null;
      
      if (isRepost) {
        // 尝试提取原文信息
        const originalAuthorMatch = postSection.match(/@([^\\s：]+)/);
        if (originalAuthorMatch) {
          originalPost = {
            author: originalAuthorMatch[1],
            url: '',
            content: ''
          };
        }
      }
      
      posts.push({
        id: id,
        url: `https://xueqiu.com/u/2292705444/${id}`,
        timestamp: timeText,
        display_time: timeText,
        content: content,
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

// 手动添加一些已知的帖子数据样本
function addSampleData() {
  const samplePosts = [
    {
      id: "374467454",
      url: "https://xueqiu.com/u/2292705444/374467454",
      timestamp: "修改于昨天 19:15",
      display_time: "修改于昨天 19:15",
      content: "New year resolution 1.减肥。 2.保持健康。 今年减肥失败我就从这里跳下去。",
      original_post: null,
      engagement: { reposts: 3, comments: 200, likes: 372 }
    },
    {
      id: "374687736",
      url: "https://xueqiu.com/u/2292705444/374687736",
      timestamp: "3小时前",
      display_time: "3小时前",
      content: "回复@和顺的稳赚小蓝鲸: 没花时间看过，不懂。",
      original_post: {
        author: "GODIFAR",
        url: "/swag888",
        content: "26年以来几乎全程满仓国产区，压力确实有点大了..."
      },
      engagement: { reposts: 0, comments: 11, likes: 64 }
    },
    {
      id: "374500345",
      url: "https://xueqiu.com/u/2292705444/374500345",
      timestamp: "昨天 23:17",
      display_time: "昨天 23:17",
      content: "从英国用改良盖伦帆船取代卡拉克帆船并大量采用长管炮之后，西班牙就逐步失去了海上的霸主地位。那么你看到两条航母同时建设然后变得不再信任美元也并不是一个简单的叙事而已。",
      original_post: null,
      engagement: { reposts: 5, comments: 97, likes: 255 }
    },
    {
      id: "374504338",
      url: "https://xueqiu.com/u/2292705444/374504338",
      timestamp: "修改于24小时前",
      display_time: "修改于24小时前",
      content: "川普操纵一次数字货币行情导致大量人爆仓之后，我的主流资产关注列表里就剔除了btc，之前我还是非常喜欢btc的，无论是从稀释黄金的稀缺性还是收藏品角度看都相对年轻。",
      original_post: null,
      engagement: { reposts: 1, comments: 98, likes: 459 }
    }
  ];
  
  return samplePosts;
}

// 保存结果
function saveResult(currentPage) {
  // 去重
  const uniquePosts = [];
  const seenIds = new Set();
  
  for (const post of allPosts) {
    if (!seenIds.has(post.id)) {
      seenIds.add(post.id);
      uniquePosts.push(post);
    }
  }
  
  const result = {
    user: 'metalslime',
    total_pages_scanned: currentPage,
    posts: uniquePosts
  };
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(result, null, 2));
  console.log(`进度: ${currentPage}/${END_PAGE} 页, 累计抓取 ${uniquePosts.length} 条 2025-2026 年帖子`);
  console.log(`已保存到 ${OUTPUT_FILE}`);
}

async function main() {
  console.log('metalslime 数据抓取工具已准备就绪');
  console.log(`输出文件: ${OUTPUT_FILE}`);
  console.log(`抓取范围: 第 ${START_PAGE} 页到第 ${END_PAGE} 页`);
  console.log(`筛选条件: 帖子 ID > 300000000 (2025-2026 年)`);
  console.log('');
  
  // 添加样本数据
  const samplePosts = addSampleData();
  allPosts = allPosts.concat(samplePosts);
  console.log(`已添加 ${samplePosts.length} 条样本数据`);
  
  // 保存初始结果
  saveResult(0);
  
  console.log('');
  console.log('使用方法:');
  console.log('1. 使用 browser 工具访问页面: https://xueqiu.com/u/2292705444?page=1 到 ?page=500');
  console.log('2. 对每个页面执行 browser.snapshot() 获取 HTML');
  console.log('3. 将 HTML 保存到文件或传递给 parsePostsFromSnapshot() 函数');
  console.log('4. 调用 saveResult() 保存数据');
  console.log('');
  console.log('提示: 由于需要访问 500 页，建议分批执行，每 50 页保存一次');
}

main();
