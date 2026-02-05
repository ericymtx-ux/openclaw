#!/usr/bin/env node

/**
 * metalslime 批量抓取 - 使用 browser 工具
 */

const fs = require('fs');
const http = require('http');

const CDP_PORT = 18792;
const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026_full.json';
const TARGET_USER_ID = '2292705444';
const MIN_POST_ID = 300000000;

let allPosts = [];
let currentPage = 1;
let lastPostId = 374700000;

// 加载现有数据
if (fs.existsSync(OUTPUT_FILE)) {
  try {
    const data = JSON.parse(fs.readFileSync(OUTPUT_FILE, 'utf8'));
    if (data.posts) allPosts = data.posts;
    if (data.currentPage) currentPage = data.currentPage;
    if (data.lastPostId) lastPostId = data.lastPostId;
    console.log(`已加载 ${allPosts.length} 条数据，从 page ${currentPage} 继续`);
  } catch (e) {}
}

// CDP 连接
function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ id: Date.now(), method, params });
    const req = http.request({
      hostname: '127.0.0.1',
      port: CDP_PORT,
      path: '/json/protocol',
      method: 'GET'
    }, (res) => {
      res.on('data', chunk => {
        try {
          const parts = chunk.toString().split('\n');
          parts.forEach(p => {
            if (p.startsWith('{')) {
              try { resolve(JSON.parse(p)); } catch (e) {}
            }
          });
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// 访问页面并获取 HTML
async function fetchPage(pageNum) {
  console.log(`正在访问 page ${pageNum}...`);

  const result = await new Promise((resolve) => {
    const req = http.request({
      hostname: '127.0.0.1',
      port: CDP_PORT,
      path: '/json',
      method: 'GET'
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const targets = JSON.parse(data);
          if (targets[0] && targets[0].webSocketDebuggerUrl) {
            const WebSocket = require('ws');
            const ws = new WebSocket(targets[0].webSocketDebuggerUrl);
            ws.on('open', () => {
              ws.send(JSON.stringify({ id: 1, method: 'Page.navigate', params: { url: `https://xueqiu.com/u/${TARGET_USER_ID}?page=${pageNum}` } }));
              setTimeout(() => {
                ws.send(JSON.stringify({ id: 2, method: 'Page.getFrameTree' }));
                setTimeout(() => ws.close(), 1000);
              }, 2000);
            });
            ws.on('message', (msg) => {
              if (msg.toString().includes('getFrameTree')) resolve(msg.toString());
            });
            setTimeout(() => resolve(''), 5000);
          }
        } catch (e) { resolve(''); }
      });
    });
    req.on('error', () => resolve(''));
    req.end();
  });

  return result;
}

async function main() {
  console.log(`\n=== metalslime 抓取开始 ===`);
  console.log(`从 page ${currentPage} 开始，ID 阈值: ${MIN_POST_ID}\n`);

  const startTime = Date.now();

  for (let i = 0; i < 1000; i++) {
    const elapsed = (Date.now() - startTime) / 1000 / 60;
    const pagesPerMin = i > 0 ? i / elapsed : 0;
    const remaining = (1000 - currentPage) / (pagesPerMin || 1);

    console.log(`[${new Date().toLocaleTimeString()}] page ${currentPage} (预计剩余 ${remaining.toFixed(0)} 分钟)`);

    await fetchPage(currentPage);

    // 检查是否完成
    if (lastPostId < MIN_POST_ID) {
      console.log(`\n🎉 完成！帖子 ID ${lastPostId} < ${MIN_POST_ID}`);
      break;
    }

    currentPage++;

    // 每 50 页保存
    if (currentPage % 50 === 0) {
      fs.writeFileSync(OUTPUT_FILE, JSON.stringify({ posts: allPosts, currentPage, lastPostId }, null, 2));
      console.log(`💾 已保存 ${allPosts.length} 条\n`);
    }
  }

  // 最终保存
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify({ posts: allPosts, currentPage, lastPostId }, null, 2));

  console.log(`\n=== 完成 ===`);
  console.log(`页面: ${currentPage}, 帖子: ${allPosts.length}`);
}

main().catch(console.error);
