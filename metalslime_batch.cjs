const puppeteer = require('puppeteer');
const fs = require('fs');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const BASE_URL = 'https://xueqiu.com/u/2292705444?page=';
const START_PAGE = 1;
const END_PAGE = 500;

let allPosts = [];
let browser;

async function scrapeBatch(startPage, endPage) {
  browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');

  for (let i = startPage; i <= endPage; i++) {
    try {
      await page.goto(BASE_URL + i, { waitUntil: 'networkidle2', timeout: 30000 });
      await page.waitForSelector('article', { timeout: 10000 });

      const posts = await page.evaluate(() => {
        const articles = document.querySelectorAll('article');
        const results = [];
        
        articles.forEach(article => {
          const links = article.querySelectorAll('a[href^="/2292705444/"]');
          links.forEach(link => {
            const href = link.getAttribute('href');
            const match = href.match(/\/2292705444\/(\d+)/);
            if (match) {
              const id = match[1];
              if (parseInt(id) > 300000000) {
                const timeText = link.textContent.trim();
                const text = article.textContent;
                
                const repost = text.match(/转发\s*(\d+)/)?.[1] || 0;
                const comment = text.match(/讨论\s*(\d+)/)?.[1] || 0;
                const like = text.match(/赞\s*(\d+)/)?.[1] || 0;
                
                results.push({
                  id,
                  url: `https://xueqiu.com/u/2292705444/${id}`,
                  timestamp: timeText,
                  display_time: timeText,
                  content: '',
                  original_post: null,
                  engagement: { reposts: parseInt(repost), comments: parseInt(comment), likes: parseInt(like) }
                });
              }
            }
          });
        });
        
        return results;
      });

      allPosts = [...allPosts, ...posts];
      
      if (i % 50 === 0 || i === END_PAGE) {
        const unique = [...new Map(allPosts.map(p => [p.id, p])).values()];
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
          user: 'metalslime',
          total_pages_scanned: i,
          posts: unique
        }, null, 2));
        console.log(`进度: ${i}/${END_PAGE} 页, 累计 ${unique.length} 条帖子`);
      }
      
      await new Promise(r => setTimeout(r, 1500));
    } catch (e) {
      console.error(`第 ${i} 页失败:`, e.message);
    }
  }
  
  await browser.close();
}

scrapeBatch(START_PAGE, END_PAGE).then(() => {
  console.log('完成!');
}).catch(console.error);
