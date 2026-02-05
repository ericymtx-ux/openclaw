#!/usr/bin/env node
/**
 * Metalslime 完整翻页抓取脚本 (Playwright)
 * 自动翻页直到覆盖 2025 年全部数据
 */

const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = path.join(__dirname, 'metalslime_2025_2026_full.json');
const TARGET_ID_THRESHOLD = 300000000;
const USER_URL = 'https://xueqiu.com/u/2292705444';
const PAGES_BETWEEN_REPORTS = 100;
const MAX_CONSECUTIVE_EMPTY_PAGES = 10;

let allPosts = [];
let currentPage = 7;
let totalPagesScraped = 0;
let consecutiveEmptyPages = 0;

async function saveProgress() {
  const posts2025 = allPosts.filter(p => p.id > TARGET_ID_THRESHOLD);
  const minId = allPosts.length ? Math.min(...allPosts.map(p => p.id)) : null;
  const maxId = allPosts.length ? Math.max(...allPosts.map(p => p.id)) : null;
  
  const data = {
    metadata: {
      lastUpdated: new Date().toISOString(),
      currentPage,
      totalPagesScraped,
      totalPostsCollected: allPosts.length,
      posts2025Plus: posts2025.length,
      oldestPostId: minId,
      newestPostId: maxId
    },
    posts: allPosts
  };
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(data, null, 2), 'utf8');
  
  console.log(`💾 进度: 页面 ${currentPage}, 共 ${allPosts.length} 篇帖子 (ID: ${minId} - ${maxId}), 2025+: ${posts2025.length}`);
}

async function extractPosts(page) {
  return await page.evaluate(() => {
    const articles = document.querySelectorAll('article');
    const result = [];
    
    articles.forEach(article => {
      // 查找包含帖子 ID 的链接
      const link = Array.from(article.querySelectorAll('a')).find(a => 
        a.href && a.href.includes('/2292705444/')
      );
      
      if (!link) return;
      
      const match = link.href.match(/\/2292705444\/(\d+)/);
      if (!match) return;
      
      const id = parseInt(match[1], 10);
      
      // 提取时间
      const timeElement = Array.from(article.querySelectorAll('a')).find(a => 
        a.textContent.includes('来自') || a.textContent.includes('修改于')
      );
      const time = timeElement ? timeElement.textContent.trim() : '';
      
      // 提取内容 - 收集所有文本节点
      let content = '';
      const textNodes = article.childNodes.filter(n => n.nodeType === Node.TEXT_NODE);
      textNodes.forEach(node => {
        const text = node.textContent.trim();
        if (text && !['转发', '赞', '收藏', '讨论', '回复'].includes(text)) {
          content += text + ' ';
        }
      });
      content = content.replace(/\s+/g, ' ').trim().substring(0, 2000);
      
      if (content && id > 0) {
        result.push({
          id,
          time,
          content,
          url: `https://xueqiu.com${link.href}`
        });
      }
    });
    
    return result;
  });
}

async function hasNextPage(page) {
  try {
    const nextButton = await page.$('a:has-text("下一页")');
    return !!nextButton;
  } catch {
    return false;
  }
}

async function clickNextPage(page) {
  try {
    const nextButton = await page.$('a:has-text("下一页")');
    if (nextButton) {
      await nextButton.click();
      // 等待新内容加载
      await page.waitForSelector('article', { timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(2000); // 等待动画完成
      return true;
    }
    return false;
  } catch (error) {
    console.log(`点击下一页失败: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('🚀 开始抓取 metalslime 帖子...');
  console.log(`📊 目标: ID > ${TARGET_ID_THRESHOLD} (2025-2026年)`);
  console.log(`📁 输出: ${OUTPUT_FILE}\n`);
  
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  try {
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    });
    
    const page = await context.newPage();
    
    // 访问初始页面
    console.log(`📍 访问 ${USER_URL}?page=${currentPage}`);
    await page.goto(`${USER_URL}?page=${currentPage}`, {
      waitUntil: 'networkidle',
      timeout: 30000
    });
    
    console.log(`✅ 页面加载成功\n`);
    
    // 主循环
    while (true) {
      // 提取帖子
      const posts = await extractPosts(page);
      console.log(`📄 Page ${currentPage}: ${posts.length} 篇帖子`);
      
      if (posts.length > 0) {
        const existingIds = new Set(allPosts.map(p => p.id));
        const newPosts = posts.filter(p => !existingIds.has(p.id));
        
        if (newPosts.length > 0) {
          allPosts.push(...newPosts);
          consecutiveEmptyPages = 0;
          console.log(`   +${newPosts.length} 篇新帖子`);
        } else {
          consecutiveEmptyPages++;
          console.log(`   ⚠️ 无新帖子 (连续: ${consecutiveEmptyPages})`);
        }
        
        // 定期保存进度
        if (totalPagesScraped % PAGES_BETWEEN_REPORTS === 0) {
          await saveProgress();
        }
      } else {
        consecutiveEmptyPages++;
        console.log(`   ⚠️ 页面无帖子 (连续: ${consecutiveEmptyPages}/${MAX_CONSECUTIVE_EMPTY_PAGES})`);
      }
      
      totalPagesScraped++;
      
      // 检查是否到达旧帖子
      if (posts.length > 0) {
        const oldestPostId = Math.min(...posts.map(p => p.id));
        if (oldestPostId < TARGET_ID_THRESHOLD) {
          console.log(`\n🎉 已到达 2024 年帖子 (ID: ${oldestPostId})，任务完成!`);
          break;
        }
      }
      
      // 检查是否连续多页无新帖子
      if (consecutiveEmptyPages >= MAX_CONSECUTIVE_EMPTY_PAGES) {
        console.log(`\n⚠️ 连续 ${MAX_CONSECUTIVE_EMPTY_PAGES} 页无有效帖子，停止抓取`);
        break;
      }
      
      // 点击下一页
      const hasNext = await hasNextPage(page);
      if (!hasNext) {
        console.log(`\n⚠️ 没有更多页面了`);
        break;
      }
      
      console.log(`   → 下一页`);
      await clickNextPage(page);
      currentPage++;
    }
    
  } catch (error) {
    console.error(`❌ 错误: ${error.message}`);
    await saveProgress();
  } finally {
    await browser.close();
  }
  
  // 最终保存
  await saveProgress();
  
  // 统计
  const posts2025 = allPosts.filter(p => p.id > TARGET_ID_THRESHOLD);
  console.log(`\n🎉 抓取完成!`);
  console.log(`   总页面数: ${totalPagesScraped}`);
  console.log(`   总帖子数: ${allPosts.length}`);
  console.log(`   2025+ 年帖子: ${posts2025.length}`);
  if (allPosts.length > 0) {
    const minId = Math.min(...allPosts.map(p => p.id));
    const maxId = Math.max(...allPosts.map(p => p.id));
    console.log(`   帖子 ID 范围: ${minId} - ${maxId}`);
  }
}

main().catch(console.error);
