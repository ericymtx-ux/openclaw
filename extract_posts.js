#!/usr/bin/env node
/**
 * Metalslime 帖子数据提取器
 * 从 snapshot JSON 提取帖子数据
 */

const fs = require('fs');
const path = require('path');

// 读取 snapshot (通过命令行参数传入或手动粘贴)
const snapshotPath = process.argv[2];

if (!snapshotPath) {
  console.log('用法: node extract_posts.js <snapshot.json>');
  console.log('或者: node extract_posts.js "手动粘贴的snapshot文本"');
  process.exit(1);
}

let snapshot;
try {
  const content = fs.readFileSync(snapshotPath, 'utf8');
  snapshot = JSON.parse(content);
} catch {
  // 如果不是文件，尝试作为 JSON 字符串解析
  try {
    snapshot = JSON.parse(snapshotPath);
  } catch (e) {
    console.log('无法解析输入数据');
    process.exit(1);
  }
}

function extractPosts(snapshot) {
  const posts = [];
  const articles = snapshot.filter(item => item && item.article && Array.isArray(item.article));
  
  for (const articleWrapper of articles) {
    const article = articleWrapper.article[0];
    if (!article) continue;
    
    // 查找包含帖子 ID 的链接
    const link = article.link?.find(l => 
      l && l.url && l.url.includes('/2292705444/')
    );
    
    if (!link?.url) continue;
    
    const match = link.url.match(/\/2292705444\/(\d+)/);
    if (!match) continue;
    
    const id = parseInt(match[1], 10);
    
    // 提取时间
    const timeLink = article.link?.find(l => 
      l && l.text && (l.text.includes('来自') || l.text.includes('修改于'))
    );
    const time = timeLink?.text || '';
    
    // 提取内容
    let content = '';
    function extractText(obj) {
      if (typeof obj === 'string') {
        content += obj + ' ';
      } else if (Array.isArray(obj)) {
        obj.forEach(extractText);
      } else if (obj && typeof obj === 'object') {
        if (obj.text && typeof obj.text === 'string' && 
            !['转发', '赞', '收藏', '讨论', '回复'].includes(obj.text.trim())) {
          content += obj.text + ' ';
        }
      }
    }
    
    Object.values(article).forEach(extractText);
    content = content.replace(/\s+/g, ' ').trim().substring(0, 2000);
    
    if (content && id > 0) {
      posts.push({
        id,
        time,
        content,
        url: `https://xueqiu.com${link.url}`
      });
    }
  }
  
  return posts;
}

const posts = extractPosts(snapshot);
console.log(`找到 ${posts.length} 篇帖子`);

// 按 ID 排序
posts.sort((a, b) => b.id - a.id);

// 输出
const output = {
  metadata: {
    extractedAt: new Date().toISOString(),
    totalPosts: posts.length,
    oldestPostId: posts.length ? Math.min(...posts.map(p => p.id)) : null,
    newestPostId: posts.length ? Math.max(...posts.map(p => p.id)) : null
  },
  posts
};

console.log('\n帖子列表:');
posts.forEach((p, i) => {
  console.log(`${i + 1}. [${p.id}] ${p.time}: ${p.content.substring(0, 50)}...`);
});

fs.writeFileSync('page_posts.json', JSON.stringify(output, null, 2), 'utf8');
console.log('\n已保存到 page_posts.json');
