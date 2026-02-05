#!/usr/bin/env node
/**
 * Metalslime API 抓取脚本
 * 使用雪球公开 API 获取用户帖子
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = path.join(__dirname, 'metalslime_2025_2026_full.json');
const TARGET_ID_THRESHOLD = 300000000;
const USER_ID = '2292705444';
const API_BASE = 'https://xueqiu.com';

let allPosts = [];
let page = 7;
let hasMore = true;
const MAX_PAGES = 1500;
const DELAY_MS = 2000;

async function fetchWithRetry(url, options = {}, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
          'Accept': 'application/json, text/plain, */*',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Referer': 'https://xueqiu.com/u/2292705444',
          ...options.headers
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.log(`请求失败 (${i + 1}/${maxRetries}): ${error.message}`);
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 3000 * (i + 1)));
    }
  }
}

async function fetchUserPosts(userId, pageNum) {
  // 尝试雪球用户帖子 API
  const url = `${API_BASE}/statuses/user_timeline.json?user_id=${userId}&page=${pageNum}&size=20&source=me`;
  
  const data = await fetchWithRetry(url);
  return data;
}

async function parsePosts(data) {
  const posts = [];
  
  if (!data) return posts;
  
  const list = data.list || data.statuses || data.statuses || [];
  
  for (const item of list) {
    const id = parseInt(item.id, 10);
    
    if (id > TARGET_ID_THRESHOLD) {
      const createdAt = item.created_at ? new Date(item.created_at * 1000).toISOString() : '';
      const time = item.created_at ? new Date(item.created_at * 1000).toLocaleString('zh-CN') : '';
      
      const content = item.text || item.description || item.rawContent || item.title || '';
      const parsedText = content.replace(/<[^>]+>/g, '').substring(0, 2000);
      
      posts.push({
        id,
        time,
        content: parsedText,
        url: `https://xueqiu.com/S/${id}`,
        created_at: createdAt,
        retweet_count: item.retweet_count || 0,
        reply_count: item.reply_count || 0,
        like_count: item.like_count || 0
      });
    }
  }
  
  return posts;
}

async function saveProgress() {
  const posts2025 = allPosts.filter(p => p.id > TARGET_ID_THRESHOLD);
  const minId = allPosts.length ? Math.min(...allPosts.map(p => p.id)) : null;
  const maxId = allPosts.length ? Math.max(...allPosts.map(p => p.id)) : null;
  
  const data = {
    metadata: {
      lastUpdated: new Date().toISOString(),
      currentPage: page,
      totalPostsCollected: allPosts.length,
      posts2025Plus: posts2025.length,
      oldestPostId: minId,
      newestPostId: maxId
    },
    posts: allPosts
  };
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(data, null, 2), 'utf8');
  
  console.log(`💾 进度保存: 页面 ${page}, 共 ${allPosts.length} 篇帖子 (ID: ${minId} - ${maxId}), 2025+年: ${posts2025.length}`);
}

async function main() {
  console.log('🚀 开始抓取 metalslime 帖子 (API 方式)...');
  console.log(`📊 目标: ID > ${TARGET_ID_THRESHOLD} (2025-2026年)`);
  console.log(`📁 输出: ${OUTPUT_FILE}\n`);
  
  // 初始化
  await saveProgress();
  
  for (page = 7; page <= MAX_PAGES && hasMore; page++) {
    console.log(`\n📄 正在抓取 page ${page}...`);
    
    try {
      const data = await fetchUserPosts(USER_ID, page);
      const posts = await parsePosts(data);
      
      console.log(`   找到 ${posts.length} 篇符合条件帖子`);
      
      if (posts.length > 0) {
        const existingIds = new Set(allPosts.map(p => p.id));
        const newPosts = posts.filter(p => !existingIds.has(p.id));
        
        if (newPosts.length > 0) {
          allPosts.push(...newPosts);
          console.log(`   +${newPosts.length} 篇新帖子`);
          
          // 每 50 页保存进度
          if (page % 50 === 0) {
            await saveProgress();
          }
        } else {
          console.log(`   ⚠️ 无新帖子`);
        }
      } else {
        // 检查是否真的没有数据
        const totalCount = data?.count || data?.total || 0;
        if (totalCount === 0) {
          hasMore = false;
          console.log(`   ℹ️  无更多数据，停止抓取`);
        }
      }
      
      // 安全延迟
      await new Promise(r => setTimeout(r, DELAY_MS));
      
    } catch (error) {
      console.error(`   ❌ 错误: ${error.message}`);
      await saveProgress();
      
      // 连续失败则停止
      const failCount = (main.failCount || 0) + 1;
      main.failCount = failCount;
      
      if (failCount >= 5) {
        console.log(`   ⚠️  连续失败 ${failCount} 次，停止抓取`);
        break;
      }
      
      await new Promise(r => setTimeout(r, 5000));
    }
  }
  
  // 最终保存
  await saveProgress();
  
  // 统计
  const posts2025 = allPosts.filter(p => p.id > TARGET_ID_THRESHOLD);
  console.log(`\n🎉 抓取完成!`);
  console.log(`   总页面数: ${page - 1}`);
  console.log(`   总帖子数: ${allPosts.length}`);
  console.log(`   2025+ 年帖子: ${posts2025.length}`);
  
  if (allPosts.length > 0) {
    const minId = Math.min(...allPosts.map(p => p.id));
    const maxId = Math.max(...allPosts.map(p => p.id));
    console.log(`   帖子 ID 范围: ${minId} - ${maxId}`);
  }
}

// 运行
main().catch(console.error);
