#!/usr/bin/env node

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const BASE_URL = 'https://xueqiu.com/u/2292705444?page=';
const START_PAGE = 1;
const END_PAGE = 500;
const POSTS_PER_PAGE = 20;

// 存储所有帖子数据
let allPosts = [];

// 确保输出目录存在
const outputDir = path.dirname(OUTPUT_FILE);
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

async function scrapePage(page, pageNum) {
  console.log(`正在抓取第 ${pageNum} 页...`);
  
  try {
    const url = BASE_URL + pageNum;
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    
    // 等待页面内容加载
    await page.waitForSelector('article', { timeout: 10000 });
    
    // 提取帖子数据
    const posts = await page.evaluate(() => {
      const articles = document.querySelectorAll('article');
      const pagePosts = [];
      
      articles.forEach(article => {
        try {
          // 获取帖子链接
          const links = article.querySelectorAll('a[href^="/2292705444/"]');
          let postId = null;
          
          links.forEach(link => {
            const href = link.getAttribute('href');
            const match = href.match(/\/2292705444\/(\d+)/);
            if (match && !postId) {
              postId = match[1];
            }
          });
          
          if (postId) {
            // 获取时间信息
            const timeLink = article.querySelector('a[href*="/2292705444/' + postId + '"]');
            const timeText = timeLink ? timeLink.textContent.trim() : '';
            
            // 获取内容
            const contentElements = article.querySelectorAll('div');
            let content = '';
            contentElements.forEach(el => {
              const text = el.textContent.trim();
              if (text.length > 10 && text.length < 500 && !text.includes('转发') && !text.includes('讨论') && !text.includes('赞')) {
                content = text;
              }
            });
            
            // 获取互动数据
            const repostMatch = article.textContent.match(/转发\s*(\d+)/);
            const commentMatch = article.textContent.match(/讨论\s*(\d+)/);
            const likeMatch = article.textContent.match(/赞\s*(\d+)/);
            
            pagePosts.push({
              id: postId,
              url: `https://xueqiu.com/u/2292705444/${postId}`,
              timestamp: timeText,
              display_time: timeText,
              content: content,
              original_post: null,
              engagement: {
                reposts: repostMatch ? parseInt(repostMatch[1]) : 0,
                comments: commentMatch ? parseInt(commentMatch[1]) : 0,
                likes: likeMatch ? parseInt(likeMatch[1]) : 0
              }
            });
          }
        } catch (err) {
          console.error('解析帖子失败:', err.message);
        }
      });
      
      return pagePosts;
    });
    
    console.log(`第 ${pageNum} 页抓取完成，获取 ${posts.length} 条帖子`);
    return posts;
    
  } catch (error) {
    console.error(`抓取第 ${pageNum} 页失败:`, error.message);
    return [];
  }
}

async function main() {
  console.log('开始抓取 metalslime 的 2025-2026 年帖子数据...');
  console.log(`目标 URL: ${BASE_URL}`);
  console.log(`抓取范围: 第 ${START_PAGE} 页到第 ${END_PAGE} 页`);
  console.log(`筛选条件: 帖子 ID > 300000000 (2025-2026 年)`);
  console.log('---');
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const page = await browser.newPage();
    
    // 设置 User-Agent
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    for (let pageNum = START_PAGE; pageNum <= END_PAGE; pageNum++) {
      const posts = await scrapePage(page, pageNum);
      
      // 筛选 2025-2026 年的帖子 (ID > 300000000)
      const filteredPosts = posts.filter(post => parseInt(post.id) > 300000000);
      allPosts = allPosts.concat(filteredPosts);
      
      // 每 50 页报告一次进度并保存
      if (pageNum % 50 === 0 || pageNum === END_PAGE) {
        console.log(`进度: ${pageNum}/${END_PAGE} 页, 累计抓取 ${allPosts.length} 条 2025-2026 年帖子`);
        
        const result = {
          user: 'metalslime',
          total_pages_scanned: pageNum,
          posts: allPosts
        };
        
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify(result, null, 2));
        console.log(`已保存到 ${OUTPUT_FILE}`);
      }
      
      // 添加小延迟以避免被限流
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
  } finally {
    await browser.close();
  }
  
  console.log('---');
  console.log(`抓取完成! 共抓取 ${allPosts.length} 条 2025-2026 年帖子`);
  console.log(`数据已保存到 ${OUTPUT_FILE}`);
}

main().catch(console.error);
