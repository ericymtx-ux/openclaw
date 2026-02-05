/**
 * metalslime 雪球帖子自动翻页抓取脚本
 * 目标: 抓取 2025-2026 年帖子 (ID > 300000000)
 * 最多翻 1000 页
 */

import { writeFileSync, readFileSync, existsSync } from 'fs';

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const MAX_PAGES = 1000;
const CHECKPOINT_INTERVAL = 50;

// 帖子 ID 阈值 (2025-2026年帖子 ID > 300000000)
const POST_ID_THRESHOLD = 300000000;

// 存储所有抓取的数据
let allPosts = [];
let currentPage = 1;
let found2025Posts = false;
let pageOf2025Start = 0;

// 加载已有数据（断点续传）
function loadCheckpoint() {
  if (existsSync(OUTPUT_FILE)) {
    try {
      const data = JSON.parse(readFileSync(OUTPUT_FILE, 'utf-8'));
      allPosts = data.posts || [];
      currentPage = data.currentPage || 1;
      found2025Posts = data.found2025Posts || false;
      pageOf2025Start = data.pageOf2025Start || 0;
      console.log(`[断点续传] 已加载 ${allPosts.length} 条帖子，从第 ${currentPage} 页继续`);
    } catch (e) {
      console.log('[新开始] 无法加载已有数据，从头开始');
    }
  }
}

// 保存检查点
function saveCheckpoint(isFinal = false) {
  const data = {
    posts: allPosts,
    currentPage,
    found2025Posts,
    pageOf2025Start,
    timestamp: new Date().toISOString(),
    isFinal
  };
  writeFileSync(OUTPUT_FILE, JSON.stringify(data, null, 2), 'utf-8');
  console.log(`[保存] 已保存 ${allPosts.length} 条帖子到 ${OUTPUT_FILE}`);
}

// 等待页面加载
async function waitForPageLoad() {
  await new Promise(resolve => setTimeout(resolve, 2000));
}

// 点击下一页按钮
async function clickNextPage() {
  const result = await browser({
    action: 'act',
    target: 'host',
    request: {
      kind: 'click',
      ref: 'e787'
    }
  });
  
  if (!result.ok) {
    throw new Error('点击下一页失败');
  }
  
  await waitForPageLoad();
  return result;
}

// 获取当前页面的帖子
async function getCurrentPagePosts() {
  const snapshot = await browser({
    action: 'snapshot',
    refs: 'aria',
    target: 'host'
  });
  
  const posts = [];
  const articles = snapshot.filter(el => el.role === 'article' || el.ref?.startsWith('e') && el.type === 'article');
  
  for (const article of articles) {
    try {
      // 提取帖子链接和时间
      const timeLink = article.children?.find(c => 
        c.ref?.includes('时间') || 
        (c.children?.some && c.children.some(cc => cc.ref?.includes('小时') || cc.ref?.includes('昨天') || cc.ref?.includes('天前')))
      );
      
      // 提取内容
      const content = extractContent(article);
      
      // 提取帖子ID（从URL中）
      const urlLink = article.children?.find(c => c.ref?.includes('URL') || c.ref?.includes('href'));
      const postId = extractPostId(article);
      
      if (postId > 0) {
        posts.push({
          id: postId,
          content,
          time: extractTime(article),
          page: currentPage,
          timestamp: new Date().toISOString()
        });
      }
    } catch (e) {
      console.log(`[解析] 帖子解析失败: ${e.message}`);
    }
  }
  
  return posts;
}

// 辅助函数：提取帖子ID
function extractPostId(article) {
  // 从链接URL中提取ID
  const links = findAllLinks(article);
  for (const link of links) {
    if (link.url && link.url.includes('/2292705444/')) {
      const match = link.url.match(/\/2292705444\/(\d+)/);
      if (match) {
        return parseInt(match[1], 10);
      }
    }
  }
  return 0;
}

// 辅助函数：提取时间
function extractTime(article) {
  const texts = getAllText(article);
  for (const text of texts) {
    if (text.includes('小时前') || text.includes('天前') || text.includes('昨天') || text.includes('前天')) {
      return text;
    }
  }
  return '';
}

// 辅助函数：提取内容
function extractContent(article) {
  const texts = getAllText(article);
  // 过滤掉用户信息、互动数据等
  return texts.filter(t => 
    !t.includes('metalslime') &&
    !t.includes('来自') &&
    !t.includes('小时前') &&
    !t.includes('昨天') &&
    !t.includes('转发') &&
    !t.includes('评论') &&
    !t.includes('赞') &&
    !t.includes('收藏') &&
    t.trim().length > 0
  ).join('\n').trim();
}

// 辅助函数：获取所有文本
function getAllText(element) {
  const texts = [];
  if (element.text) texts.push(element.text);
  if (element.children) {
    for (const child of element.children) {
      texts.push(...getAllText(child));
    }
  }
  return texts;
}

// 辅助函数：查找所有链接
function findAllLinks(element, links = []) {
  if (element.type === 'link' || element.role === 'link') {
    links.push({
      text: element.text,
      url: element.url || element.href
    });
  }
  if (element.children) {
    for (const child of element.children) {
      findAllLinks(child, links);
    }
  }
  return links;
}

// 检查是否还有下一页
function hasNextPage(snapshot) {
  return snapshot.some(el => el.ref === 'e787');
}

// 主循环
async function main() {
  console.log('='.repeat(60));
  console.log('metalslime 雪球帖子抓取开始');
  console.log(`目标: 抓取 2025-2026 年帖子 (ID > ${POST_ID_THRESHOLD})`);
  console.log(`最多翻 ${MAX_PAGES} 页`);
  console.log('='.repeat(60));
  
  loadCheckpoint();
  
  try {
    while (currentPage <= MAX_PAGES) {
      console.log(`\n[页面 ${currentPage}] 正在获取页面数据...`);
      
      // 获取当前页面快照
      const snapshot = await browser({
        action: 'snapshot',
        refs: 'aria',
        target: 'host'
      });
      
      // 解析帖子
      const posts = await getCurrentPagePosts();
      console.log(`[页面 ${currentPage}] 发现 ${posts.length} 条帖子`);
      
      // 处理每条帖子
      for (const post of posts) {
        if (post.id > POST_ID_THRESHOLD) {
          allPosts.push(post);
          
          // 标记进入2025年
          if (!found2025Posts) {
            found2025Posts = true;
            pageOf2025Start = currentPage;
            console.log(`[里程碑] 第 ${currentPage} 页开始出现 2025-2026 年帖子`);
          }
        }
      }
      
      console.log(`[统计] 目前共抓取 ${allPosts.length} 条 2025-2026 年帖子`);
      
      // 检查是否需要继续
      if (currentPage >= MAX_PAGES) {
        console.log(`[完成] 已达到最大页数限制 (${MAX_PAGES})`);
        break;
      }
      
      // 检查是否还有下一页
      if (!hasNextPage(snapshot)) {
        console.log(`[完成] 没有更多页面了`);
        break;
      }
      
      // 每50页保存一次
      if (currentPage % CHECKPOINT_INTERVAL === 0) {
        saveCheckpoint();
        console.log(`[进度] 已完成 ${currentPage} 页，保存中间结果`);
      }
      
      // 点击下一页
      console.log(`[翻页] 点击下一页...`);
      await clickNextPage();
      currentPage++;
      
      // 礼貌性等待
      await new Promise(resolve => setTimeout(resolve, 1500));
    }
  } catch (e) {
    console.error(`[错误] 抓取出错: ${e.message}`);
    console.log('[保存] 保存当前进度...');
    saveCheckpoint();
  }
  
  // 最终保存
  saveCheckpoint(true);
  
  console.log('\n' + '='.repeat(60));
  console.log('抓取完成！');
  console.log(`总共翻页: ${currentPage} 页`);
  console.log(`2025-2026 年帖子: ${allPosts.length} 条`);
  if (found2025Posts) {
    console.log(`2025年帖子起始页: ${pageOf2025Start}`);
  }
  console.log(`数据已保存到: ${OUTPUT_FILE}`);
  console.log('='.repeat(60));
  
  return {
    totalPages: currentPage,
    totalPosts2025: allPosts.length,
    pageOf2025Start,
    outputFile: OUTPUT_FILE
  };
}

// 运行
const result = await main();
