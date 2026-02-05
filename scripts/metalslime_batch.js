#!/usr/bin/env node

/**
 * metalslime 雪球帖子批量抓取脚本
 * 使用 OpenClaw browser 工具自动翻页
 */

const fs = require('fs');
const { execSync } = require('child_process');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const TARGET_USER_ID = '2292705444';
const MIN_POST_ID = 300000000; // 2025年帖子ID阈值

// 存储数据
let allPosts = [];

// 辅助函数：执行 browser 命令
function browser(action, args = {}) {
  const cmd = `node -e "
    const http = require('http');
    const options = {
      hostname: '127.0.0.1',
      port: 18792,
      path: '/json',
      method: 'GET'
    };
    http.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const targets = JSON.parse(data);
        const ws = new (require('ws'))(targets[0].webSocketDebuggerUrl);
        ws.on('open', () => {
          const msg = JSON.stringify({ id: 1, method: 'Input.dispatchMouseEvent', params: { type: 'click', x: 100, y: 500 } });
          ws.send(msg);
          ws.close();
        });
      });
    });
  "`;
  console.log('Browser action:', action);
  return { success: true };
}

// 主函数
async function main() {
  console.log('=== metalslime 批量抓取开始 ===\n');

  // 读取现有数据
  if (fs.existsSync(OUTPUT_FILE)) {
    try {
      const existing = JSON.parse(fs.readFileSync(OUTPUT_FILE, 'utf8'));
      if (existing.posts) {
        allPosts = existing.posts;
        console.log(`已加载 ${allPosts.length} 条现有数据`);
      }
    } catch (e) {
      console.log('创建新文件');
    }
  }

  // 开始翻页
  let currentPage = allPosts.length > 0 ? Math.max(...allPosts.map(p => p.page || 1)) : 0;
  let lastPostId = allPosts.length > 0 ? allPosts[0].id : 374687736;

  console.log(`从 page ${currentPage + 1} 开始抓取`);
  console.log(`目标: 帖子 ID < ${MIN_POST_ID} (2025年初)`);
  console.log('');

  const maxPages = 1000;
  const startTime = Date.now();

  for (let i = 0; i < maxPages; i++) {
    currentPage++;

    // 计算预计剩余时间
    const elapsed = (Date.now() - startTime) / 1000 / 60;
    const pagesPerMinute = i > 0 ? i / elapsed : 0;
    const remainingPages = maxPages - currentPage;
    const remainingMinutes = pagesPerMinute > 0 ? remainingPages / pagesPerMinute : 0;

    console.log(`[${new Date().toLocaleTimeString()}] 正在抓取 page ${currentPage}... (${i + 1}/${maxPages}, 预计剩余 ${remainingMinutes.toFixed(1)} 分钟)`);

    // 访问页面
    try {
      execSync(`curl -s "https://xueqiu.com/u/${TARGET_USER_ID}?page=${currentPage}" \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
        -H "Cookie: xq_a_token=YOUR_TOKEN_HERE" \
        -o /tmp/page_${currentPage}.html`, { timeout: 10000 });

      const html = fs.readFileSync(`/tmp/page_${currentPage}.html`, 'utf8');

      // 解析帖子
      const postIds = [...html.matchAll(new RegExp(`/u/${TARGET_USER_ID}/(\\d+)`, 'g'))].map(m => m[1]);
      const uniqueIds = [...new Set(postIds)];

      let newPostsCount = 0;
      for (const id of uniqueIds) {
        const postId = parseInt(id);
        if (postId >= MIN_POST_ID) continue; // 跳过 2025 年之前的数据

        if (postId < lastPostId) {
          lastPostId = postId;
        }

        // 提取时间
        const timeMatch = html.match(new RegExp(`/u/${TARGET_USER_ID}/${id}[^>]*>([^<]*${id}[^<]*</a>)`));
        const time = timeMatch ? timeMatch[1].replace(/<[^>]+>/g, '').trim() : '';

        // 提取内容
        const contentMatch = html.match(new RegExp(`id">[^"]*${id}[^<]*</a>[^<]*<[^>]*>([^<]{10,200}?)</`));
        const content = contentMatch ? contentMatch[1].replace(/<[^>]+>/g, ' ').trim() : '';

        if (content && content.length > 5) {
          allPosts.unshift({
            id: id,
            page: currentPage,
            time: time,
            content: content,
            timestamp: new Date().toISOString()
          });
          newPostsCount++;
        }
      }

      if (newPostsCount > 0) {
        console.log(`  → 获取 ${newPostsCount} 条新帖子`);
      }

    } catch (e) {
      console.log(`  ⚠️ page ${currentPage} 抓取失败: ${e.message}`);
    }

    // 每 10 页保存一次
    if (currentPage % 10 === 0) {
      fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
        posts: allPosts,
        currentPage: currentPage,
        lastPostId: lastPostId,
        updatedAt: new Date().toISOString()
      }, null, 2));
      console.log(`  💾 已保存 (${allPosts.length} 条)\n`);
    }

    // 检查是否到达目标
    if (lastPostId < MIN_POST_ID) {
      console.log(`\n🎉 到达目标！帖子 ID ${lastPostId} < ${MIN_POST_ID}`);
      break;
    }
  }

  // 最终保存
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
    posts: allPosts,
    currentPage: currentPage,
    lastPostId: lastPostId,
    updatedAt: new Date().toISOString()
  }, null, 2));

  const totalTime = (Date.now() - startTime) / 1000 / 60;

  console.log('\n=== 抓取完成 ===');
  console.log(`总页面: ${currentPage}`);
  console.log(`总帖子: ${allPosts.length}`);
  console.log(`最后帖子 ID: ${lastPostId}`);
  console.log(`用时: ${totalTime.toFixed(1)} 分钟`);
  console.log(`保存到: ${OUTPUT_FILE}`);
}

main().catch(console.error);
