#!/usr/bin/env node
/**
 * metalslime 帖子抓取脚本
 * 从 page=7 开始翻页抓取，筛选 2025 年帖子 (ID > 300000000)
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = path.join(__dirname, 'metalslime_2025_2026_full.json');
const TARGET_ID_THRESHOLD = 300000000;
const PAGES_BETWEEN_REPORTS = 100;

let allPosts = [];
let currentPage = 7;
let totalPagesScraped = 0;
let hasMorePages = true;
let consecutiveEmptyPages = 0;
const MAX_EMPTY_PAGES = 5;

async function saveProgress() {
  const data = {
    metadata: {
      lastUpdated: new Date().toISOString(),
      currentPage,
      totalPagesScraped,
      totalPostsCollected: allPosts.length,
      posts2025Plus: allPosts.filter(p => p.id > TARGET_ID_THRESHOLD).length
    },
    posts: allPosts
  };
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(data, null, 2), 'utf8');
  console.log(`💾 已保存进度: ${allPosts.length} 篇帖子, ${data.metadata.posts2025Plus} 篇符合条件 (ID > 3亿)`);
}

async function extractPostsFromPage(snapshot) {
  const posts = [];
  const articles = snapshot.filter(item => item.article);
  
  for (const article of articles) {
    const articleData = article.article[0];
    if (!articleData) continue;
    
    // 提取时间戳 - 通常在链接中包含 ID
    const timeLink = articleData.link?.find(l => l.ref?.startsWith?.('e') && l.url?.includes?.('/2292705444/'));
    if (!timeLink?.url) continue;
    
    const match = timeLink.url.match(/\/2292705444\/(\d+)/);
    if (!match) continue;
    
    const postId = parseInt(match[1], 10);
    
    // 提取时间
    const timeText = articleData.link?.find(l => 
      l.text?.includes('来自') || l.text?.includes('修改于')
    )?.text || '';
    
    // 提取内容 - 收集所有非链接文本
    let content = '';
    const extractText = (obj) => {
      if (typeof obj === 'string') {
        content += obj + ' ';
      } else if (Array.isArray(obj)) {
        obj.forEach(extractText);
      } else if (obj && typeof obj === 'object') {
        if (obj.text) content += obj.text + ' ';
        Object.values(obj).forEach(extractText);
      }
    };
    extractText(articleData);
    content = content.trim().replace(/\s+/g, ' ').substring(0, 2000);
    
    if (content && postId) {
      posts.push({
        id: postId,
        time: timeText,
        content: content,
        url: `https://xueqiu.com${timeLink.url}`
      });
    }
  }
  
  return posts;
}

async function scrapePage(pageNum) {
  console.log(`\n📄 正在抓取 page ${pageNum}...`);
  
  // 发送导航命令
  const navResponse = await fetch(`https://xueqiu.com/u/2292705444?page=${pageNum}`, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Accept': 'text/html,application/xhtml+xml',
      'Cookie': '' // 需要用户登录 cookie
    }
  });
  
  if (!navResponse.ok) {
    console.log(`❌ 页面 ${pageNum} 请求失败: ${navResponse.status}`);
    return { posts: [], hasMore: false };
  }
  
  const html = await navResponse.text();
  
  // 解析帖子数据
  const posts = parsePostsFromHTML(html);
  console.log(`   找到 ${posts.length} 篇帖子`);
  
  // 检查是否有更多页面
  const hasMore = html.includes('下一页') || html.includes('next');
  
  return { posts, hasMore };
}

function parsePostsFromHTML(html) {
  const posts = [];
  
  // 尝试从 JSON 数据中提取
  const jsonMatch = html.match(/window\.\w+\s*=\s*(\{[\s\S]*?\});/);
  if (jsonMatch) {
    try {
      const data = JSON.parse(jsonMatch[1]);
      if (data.statuses || data.list || data.posts) {
        const list = data.statuses || data.list || data.posts;
        for (const item of list) {
          if (item.id > TARGET_ID_THRESHOLD) {
            posts.push({
              id: item.id,
              time: item.created_at ? new Date(item.created_at).toISOString() : '',
              content: item.text || item.description || item.rawContent || '',
              url: item.target || `https://xueqiu.com${item.url || '/S/' + item.id}`
            });
          }
        }
      }
    } catch (e) {
      console.log('JSON 解析失败，尝试其他方法...');
    }
  }
  
  // 备用方法：从 HTML 中提取
  if (posts.length === 0) {
    const articleRegex = /<article[^>]*data-snb[^>]*id["']?\s*[:=]\s*["']?(\d+)["']?[^>]*>[\s\S]*?<\/article>/gi;
    let match;
    while ((match = articleRegex.exec(html)) !== null) {
      const id = parseInt(match[1], 10);
      if (id > TARGET_ID_THRESHOLD) {
        const contentMatch = match[0].match(/>([^<]{10,500})</);
        posts.push({
          id,
          time: '',
          content: contentMatch ? contentMatch[1].replace(/<[^>]+>/g, '') : '',
          url: `https://xueqiu.com/S/${id}`
        });
      }
    }
  }
  
  return posts;
}

async function main() {
  console.log('🚀 开始抓取 metalslime 的帖子...');
  console.log(`📊 目标: ID > ${TARGET_ID_THRESHOLD} (2025-2026年)`);
  console.log(`📁 输出文件: ${OUTPUT_FILE}\n`);
  
  // 初始化输出文件
  saveProgress();
  
  while (hasMorePages && consecutiveEmptyPages < MAX_EMPTY_PAGES) {
    try {
      const { posts, hasMore } = await scrapePage(currentPage);
      
      if (posts.length > 0) {
        allPosts.push(...posts);
        consecutiveEmptyPages = 0;
        
        // 每 100 页保存一次进度
        if (totalPagesScraped % PAGES_BETWEEN_REPORTS === 0) {
          console.log(`\n📊 进度报告 - 页面 ${totalPagesScraped}, 共 ${allPosts.length} 篇帖子`);
          await saveProgress();
        }
      } else {
        consecutiveEmptyPages++;
        console.log(`⚠️  页面 ${currentPage} 无新帖子 (连续空页: ${consecutiveEmptyPages}/${MAX_EMPTY_PAGES})`);
      }
      
      totalPagesScraped++;
      hasMorePages = hasMore;
      currentPage++;
      
    } catch (error) {
      console.error(`❌ 抓取页面 ${currentPage} 时出错:`, error.message);
      await saveProgress();
      await new Promise(r => setTimeout(r, 5000)); // 等待后重试
    }
  }
  
  if (consecutiveEmptyPages >= MAX_EMPTY_PAGES) {
    console.log(`\n⚠️  连续 ${MAX_EMPTY_PAGES} 页无新帖子，停止抓取`);
  }
  
  // 最终保存
  await saveProgress();
  
  // 统计
  const posts2025 = allPosts.filter(p => p.id > TARGET_ID_THRESHOLD);
  console.log(`\n🎉 抓取完成!`);
  console.log(`   总页面数: ${totalPagesScraped}`);
  console.log(`   总帖子数: ${allPosts.length}`);
  console.log(`   2025+ 年帖子: ${posts2025.length}`);
  console.log(`   最早帖子 ID: ${allPosts.length ? Math.min(...allPosts.map(p => p.id)) : 'N/A'}`);
  console.log(`   最晚帖子 ID: ${allPosts.length ? Math.max(...allPosts.map(p => p.id)) : 'N/A'}`);
}

main().catch(console.error);
