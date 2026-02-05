const { chromium } = require('playwright');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const BASE_URL = 'https://xueqiu.com/u/2292705444?page=';
const MIN_POST_ID = 300000000;
const PAGES = 500;

let allPosts = [];

async function scrape() {
  console.log('🚀 启动 Playwright 抓取...');
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.evaluate(() => {
    Object.defineProperty(navigator, 'userAgent', { value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' });
  });

  for (let i = 1; i <= PAGES; i++) {
    try {
      console.log(`📄 正在抓取 page ${i}/${PAGES}...`);
      
      await page.goto(BASE_URL + i, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForSelector('article', { timeout: 10000 });
      
      const posts = await page.evaluate(() => {
        const articles = document.querySelectorAll('article');
        const results = [];
        
        articles.forEach(article => {
          const links = article.querySelectorAll('a[href*="/2292705444/"]');
          links.forEach(link => {
            const href = link.getAttribute('href');
            const match = href.match(/\/2292705444\/(\d+)/);
            if (match) {
              const id = parseInt(match[1]);
              if (id > 300000000) {
                const text = article.textContent || '';
                const timeMatch = text.match(/(\d{4}-\d{2}-\d{2}|\d+[分钟小时天周月年]+前)/);
                const time = timeMatch ? timeMatch[0] : '';
                
                const repost = text.match(/转发\s*(\d+)/)?.[1] || '0';
                const comment = text.match(/评论\s*(\d+)|讨论\s*(\d+)/)?.[1] || text.match(/讨论\s*(\d+)/)?.[2] || '0';
                const like = text.match(/赞\s*(\d+)/)?.[1] || '0';
                
                results.push({
                  id: id.toString(),
                  url: `https://xueqiu.com/u/2292705444/${id}`,
                  timestamp: time,
                  content: text.substring(0, 200),
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

      allPosts = [...allPosts, ...posts];
      const uniquePosts = [...new Map(allPosts.map(p => [p.id, p])).values()];
      allPosts = uniquePosts;
      
      if (i % 10 === 0 || i === PAGES) {
        const fs = require('fs');
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
          user: 'metalslime',
          currentPage: i,
          totalPosts: allPosts.length,
          posts: allPosts
        }, null, 2));
        console.log(`💾 已保存 ${allPosts.length} 条帖子 (page ${i})`);
      }
      
      // 避免被封，延迟一下
      await page.waitForTimeout(1500);
      
    } catch (e) {
      console.error(`❌ page ${i} 失败:`, e.message);
      await page.waitForTimeout(3000);
    }
  }
  
  await browser.close();
  console.log(`\n🎉 完成！共抓取 ${allPosts.length} 条帖子`);
}

scrape().catch(console.error);
