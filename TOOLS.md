# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## 模型切换

配置文件：`~/.openclaw/openclaw.json`

- **"切换 opus"** → 设置默认模型为 `anthropic/claude-opus-4-5`
- **"切换 minimax"** → 设置默认模型为 `minimax/MiniMax-M2.1`
- **"切换 kimi"** → 设置默认模型为 `kimi-coding/k2p5`

## Opus 经验记录（复杂任务）

当使用 **Opus 模型**执行复杂任务并出色完成后：
- 在工作目录创建 `opus_experts/` 文件夹
- 用 `.md` 文件记录：收到的指令 + 思考过程 + 行动步骤
- 文件标题：简短英文概括任务 + 当日日期（格式：`Task-Summary_2026-01-31.md`）

**Minimax 借鉴：**
当使用 **Minimax 模型**时，先去 `opus_experts/` 搜索相关经验，参考 Opus 的处理方式提高回答质量。

---

## 股票分时图截图流程

**使用 browserautomation skill 获取股票分时图：**

### 步骤
1. **找股票代码**: 从 stock_stars 股票列表读取
   ```
   文件: /Users/apple/openclaw/projects/stock_stars/data/stocklist.csv
   格式: ts_code,symbol,name,area,industry
   示例: 688031.SH,688031,星环科技,上海,软件服务
   ```

2. **构建搜狐股票 URL**
   ```
   https://q.stock.sohu.com/cn/股票代码数字/index.shtml?
   示例: https://q.stock.sohu.com/cn/688031/index.shtml?
   ```

3. **使用 agent-browser 截图**
   ```bash
   agent-browser screenshot \
     --url "https://q.stock.sohu.com/cn/688031/index.shtml?" \
     --output /tmp/stock_screenshot.png \
     --viewport-width 1920 \
     --viewport-height 1080
   ```

4. **发送图片到 Telegram**
   ```bash
   pnpm openclaw message send \
     --target 559389757 \
     --media /tmp/stock_screenshot.png
   ```

### 常用命令
```bash
# 安装/更新 browserautomation skill
pnpm clawhub install browserautomation

# 查看 agent-browser 帮助
agent-browser --help

# 截图示例
agent-browser screenshot --url "https://q.stock.sohu.com/cn/688031/index.shtml?" --output /tmp/test.png
```

### 示例：获取星环科技分时图
```bash
# 1. 截图
agent-browser screenshot \
  --url "https://q.stock.sohu.com/cn/688031/index.shtml?" \
  --output /tmp/star_ring_tech.png

# 2. 发送到 Telegram
pnpm openclaw message send --target 559389757 --media /tmp/star_ring_tech.png
```

### 注意事项
-搜狐股票 URL 后面的 `?` 不能省略
- 截图可能需要等待页面完全加载
- Telegram 发送需要指定 target (用户ID)
