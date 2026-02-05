const puppeteer = require('puppeteer');
const fs = require('fs');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const BASE_URL = 'https://xueqiu.com/u/2292705444';
const START_PAGE = 1;
const END_PAGE = 500;

async function scrapeAll() {
  console.log('开始批量抓取 metalslime 帖子数据...');
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
  await page.setViewport({ width: 1280, height: 800 });

  const allPosts = new Map();

  for (let i = START_PAGE; i <= END_PAGE; i++) {
    const url = `${BASE_URL}?page=${i}&sort=time`;
    console.log(`[${i}/${END_PAGE}] 正在抓取...`);
    
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });
      await page.waitForSelector('article', { timeout: 10000 });
      
      // 滚动页面加载内容
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await new Promise(r => setTimeout(r, 1000));

      const posts = await page.evaluate(() => {
        const results = [];
        const articles = document.querySelectorAll('article');
        
        articles.forEach(article => {
          const links = article.querySelectorAll('a[href*="/2292705444/"]');
          links.forEach(link => {
            const href = link.getAttribute('href');
            const match = href.match(/\/2292705444\/(\d+)/);
            if (match) {
              const id = match[1];
              if (parseInt(id) > 300000000) {
                const timeText = link.textContent.trim();
                const articleText = article.textContent;
                
                const repost = articleText.match(/转发\s*(\d+)/)?.[1] || 0;
                const comment = articleText.match(/讨论\s*(\d+)/)?.[1] || 0;
                const like = articleText.match(/赞\s*(\d+)/)?.[1] || 0;
                
                // 提取内容
                const textDivs = article.querySelectorAll('div');
                let content = '';
                textDivs.forEach(div => {
                  const text = div.textContent.trim();
                  if (text.length > 10 && text.length < 500 && 
                      !text.includes('转发') && !text.includes('讨论') && 
                      !text.includes('赞') && !text.match(/\d+小时前/)) {
                    content = text;
                  }
                });

                results.push({
                  id,
                  url: `https://xueqiu.com/u/2292705444/${id}`,
                  timestamp: timeText,
                  display_time: timeText,
                  content,
                  original_post: null,
                  engagement: {
                    reposts: parseInt(repost),
                    comments: parseInt(comment),
                    likes: parseInt(like)
                  }
                });
              }
            }
          });
        });
        
        return results;
      });

      posts.forEach(p => allPosts.set(p.id, p));
      
      // 每 50 页保存一次
      if (i % 50 === 0 || i === END_PAGE) {
        const postsArray = Array.from(allPosts.values());
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
          user: 'metalslime',
          total_pages_scanned: i,
          posts: postsArray
        }, null, 2));
        console.log(`已保存 ${postsArray.length} 条帖子到 ${OUTPUT_FILE}`);
      }
      
      await new Promise(r => setTimeout(r, 2000));
      
    } catch (e) {
      console.error(`[${i}] 失败:`, e.message);
    }
  }

  await browser.close();
  
  const finalPosts = Array.from(allPosts.values());
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
    user: 'metalslime',
    total_pages_scanned: END_PAGE,
    posts: finalPosts
  }, null, 2));
  
  console.log(`\n完成! 共抓取 ${finalPosts.length} 条 2025-2026 年帖子`);
  console.log(`数据保存到: ${OUTPUT_FILE}`);
}

scrapeAll().catch(console.error);
