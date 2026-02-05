/**
 * metalslime 雪球帖子批量抓取脚本
 * 使用 browser 工具的 snapshot 解析
 */

const fs = require('fs');

const OUTPUT_FILE = '/Users/apple/openclaw/raw_data/metalslime_2025_2026.json';
const TARGET_USER_ID = '2292705444';
const MIN_POST_ID = 300000000; // 2025年帖子ID阈值

// 从快照解析帖子数据
function parsePosts(snapshot) {
  const posts = [];
  
  // 查找所有 article 元素
  const articles = snapshot.filter(node => 
    node.type === 'article' || 
    (node.generic && node.generic.some(g => g.type === 'article'))
  );
  
  // 简化解析逻辑
  if (snapshot[0]?.generic) {
    const generic = snapshot[0].generic;
    
    // 查找分页区域，获取当前页码
    let currentPage = 1;
    generic.forEach(item => {
      if (item.generic) {
        item.generic.forEach(sub => {
          if (sub.generic) {
            sub.generic.forEach(g => {
              if (g.link && g.link[0]?.text === '下一页') {
                console.log('Found pagination: next page button');
              }
            });
          }
        });
      }
    });
    
    // 查找所有文章链接
    generic.forEach(item => {
      if (item.generic) {
        item.generic.forEach(g => {
          if (g.generic) {
            g.generic.forEach(gg => {
              if (gg.link) {
                gg.link.forEach(link => {
                  // 匹配帖子链接 /2292705444/数字
                  if (link.url && link.url.startsWith('/' + TARGET_USER_ID + '/')) {
                    const postId = link.url.split('/').pop();
                    const id = parseInt(postId);
                    
                    if (id >= MIN_POST_ID) {
                      posts.push({
                        id: id,
                        url: `https://xueqiu.com${link.url}`,
                        timestamp: '',
                        content: ''
                      });
                    }
                  }
                });
              }
            });
          }
        });
      }
    });
  }
  
  return posts;
}

// 保存数据
function savePosts(posts, page) {
  let existing = [];
  
  if (fs.existsSync(OUTPUT_FILE)) {
    try {
      existing = JSON.parse(fs.readFileSync(OUTPUT_FILE, 'utf8'));
    } catch (e) {}
  }
  
  // 合并去重
  const existingIds = new Set(existing.map(p => p.id));
  const newPosts = posts.filter(p => !existingIds.has(p.id));
  const allPosts = [...newPosts, ...existing];
  
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify({
    user: 'metalslime',
    total_posts: allPosts.length,
    current_page: page,
    posts: allPosts
  }, null, 2));
  
  return allPosts.length;
}

console.log('=== metalslime 批量抓取工具 ===');
console.log('使用方法:');
console.log('1. 使用 browser.navigate() 访问页面');
console.log('2. 使用 browser.snapshot() 获取快照');
console.log('3. 复制快照到脚本运行');
console.log('');
console.log('当前状态: 等待 browser 快照数据...');
