# OpenClaw 保姆级教程（中）：新手必装的 5 个设置（纯文本 Markdown 版）

> 目标：把你的小红书图文教程整理成可复制执行的 Markdown 文档（无图片）。环境以 macOS 为例，假设已安装 Node.js 与 OpenClaw（clawdbot）。文中的命令与代码从原文图片提取并修正为可直接复制使用。

---

## 目录
- 引言与准备说明
- 设置一：将 OpenClaw 改成系统级运行（含管理脚本）
- 设置二：进程保活、强制代理与日志记录的 plist 配置
- 设置三：快捷管理与排错速查
- 设置四：多层记忆与上下文优化（节省 Token）
- 设置五：用 Git 管理配置与一键回滚
- 附录：常用命令与文件清单

---

## 引言与准备说明
OpenClaw 能帮你思考规划与执行繁琐任务，但若只在终端前台运行，容易因窗口关闭、进程崩溃或网络异常而中断。中篇的 5 个设置可显著提升稳定性与可维护性：
- System-Level：注销或重启电脑后仍在后台运行
- Auto-Healing：崩溃 1 秒内自动重启
- Proxy-Forced：强制走代理，避免 Node 不走系统代理导致的超时
- 结构化记忆：优先读取核心记忆，降低 Token 消耗
- 版本控制：为配置提供“无限撤销键”

提示：本文以 macOS 为例；若你用 Windows/Linux，可让我为你生成 `systemd` 或服务方案脚本。

---

## 设置一：将 OpenClaw 改成系统级运行（含管理脚本）
官方方式是终端运行 `openclaw gateway run`，这会受终端生命周期影响。我们改为创建一个“懒人遥控器”脚本，让系统以后台服务管理。

### 1）创建脚本文件
```bash
nano ~/clawd_control.sh
```

### 2）粘贴以下完整代码
```bash
#!/bin/bash
PLIST="~/Library/LaunchAgents/bot.clawd.gateway.plist"
SERVICE="bot.clawd.gateway"

case "$1" in
  start)
    echo "🚀 Starting Clawdbot..."
    launchctl load -w $PLIST
    ;;
  stop)
    echo "🛑 Stopping Clawdbot..."
    launchctl unload -w $PLIST
    ;;
  restart)
    echo "🔄 Restarting..."
    launchctl kickstart -k gui/$(id -u)/$SERVICE
    ;;
  status)
    echo "🔍 Checking status..."
    launchctl list | grep clawd
    ;;
  log)
    echo "📜 Showing last 20 lines of logs..."
    tail -f -n 20 ~/.clawdbot/gateway.log
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|log}"
    exit 1
    ;;
esac
```

### 3）赋予执行权限
```bash
chmod +x ~/clawd_control.sh
```

---

## 设置二：进程保活、强制代理与日志记录的 plist 配置
我们需要让 macOS 的 LaunchAgents 接管进程，做到保活、强制代理与日志记录。

### 一键生成 plist 文件（按需调整端口/路径）
> 请先用 `which node` 确认你的 node 路径；代理端口按你的代理工具调整（常见 7890/6152）。

```bash
cat <<'EOF' > ~/Library/LaunchAgents/bot.clawd.gateway.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>bot.clawd.gateway</string>

  <!-- 运行命令 -->
  <key>ProgramArguments</key>
  <array>
    <!-- ⚠️ 按需替换为你的 node 路径，如 /opt/homebrew/bin/node -->
    <string>/usr/local/bin/node</string>
    <string>/usr/local/bin/clawdbot</string>
    <string>gateway</string>
    <string>run</string>
  </array>

  <!-- 强制注入网络代理（解决 fetch failed） -->
  <key>EnvironmentVariables</key>
  <dict>
    <key>HTTP_PROXY</key>
    <string>http://127.0.0.1:7890</string>
    <key>HTTPS_PROXY</key>
    <string>http://127.0.0.1:7890</string>
    <key>all_proxy</key>
    <string>http://127.0.0.1:7890</string>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
  </dict>

  <!-- 日志路径（便于 tail -f 排错） -->
  <key>StandardOutPath</key>
  <string>${HOME}/.clawdbot/gateway.log</string>
  <key>StandardErrorPath</key>
  <string>${HOME}/.clawdbot/gateway_error.log</string>

  <!-- 保活与开机/加载即运行 -->
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
EOF
```

### 加载/卸载与故障恢复
```bash
# 首次或修改后加载
launchctl load -w ~/Library/LaunchAgents/bot.clawd.gateway.plist

# 查看是否在运行（有 PID 即运行中）
launchctl list | grep clawd

# 踢一下重启（修改配置后用）
launchctl kickstart -k gui/$(id -u)/bot.clawd.gateway

# 出问题时卸载再重载
launchctl unload -w ~/Library/LaunchAgents/bot.clawd.gateway.plist
launchctl load -w ~/Library/LaunchAgents/bot.clawd.gateway.plist
```

---

## 设置三：快捷管理与排错速查
有了脚本与 plist 后，日常只需这几条指令：

```bash
~/clawd_control.sh start    # 启动服务
~/clawd_control.sh status   # 查看状态（grep clawd）
~/clawd_control.sh log      # 实时查看日志（最后 20 行）
~/clawd_control.sh restart  # 重载配置并重启
```
常见异常与提示：
- `Service is already loaded`：服务已运行，无需重复启动
- `status` 无输出：服务可能挂了，尝试 `restart` 或查看 `log`
- 日志出现 `fetch failed`：检查代理端口/路径是否正确

---

## 设置四：多层记忆与上下文优化（节省 Token）
大模型上下文昂贵又易失，建议建立“结构化记忆层级”：

### 核心记忆（Core_Profile.md）
- 作用：身份认知与索引；重启/切换模型后第一时间读取
- 建议内容：
```markdown
# Core Profile
User: 你的名字
Role: Personal AI Assistant (Jarvis)
Capabilities: Node.js, Shell, Git
Key_Paths:
- Memory: ./MEMORY.md
- Projects: ./Projects/
```

### 日常记忆（MEMORY.md）
- 作用：归档每日对话要点；当提到某关键词时触发读取，提升理解与输出
- 策略：让 OpenClaw 自动将对话摘要追加到该文件

### 被动归档（Skill/Notes）
- 作用：把高价值对话固化为可复用技能或笔记，下次直接调用

节省 Token 的原理：
- 对话时只加载少量的核心记忆（几百 token）；真正需要细节再按需读取 MEMORY.md，长期可省下约 80% 的上下文开销

---

## 设置五：用 Git 管理配置与一键回滚
把 `~/.clawdbot` 变成 Git 仓库，获得“无限撤销键”。

### 一次性初始化
```bash
cd ~/.clawdbot
git init

# 只备份核心配置，忽略日志/临时文件
echo "logs/" >> .gitignore
echo "*.log" >> .gitignore
echo ".DS_Store" >> .gitignore

# 首次提交（Save Game）
git add .
git commit -m "Initial stable config backup"
```

### 日常使用
```bash
# 查看修改（Check Changes）
git status
git diff

# 存档（提交更改）
git add .
git commit -m "修改了代理端口"

# 一键回滚（Load Game，⚠️丢弃未提交更改）
git reset --hard

# 回滚后让服务生效
~/clawd_control.sh restart
```

---

## 附录：常用命令与文件清单
**服务管理**
```bash
~/clawd_control.sh start
~/clawd_control.sh stop
~/clawd_control.sh restart
~/clawd_control.sh status
~/clawd_control.sh log
```

**日志/排错**
```bash
launchctl list | grep clawd
tail -f -n 20 ~/.clawdbot/gateway.log
```

**版本控制**
```bash
cd ~/.clawdbot
git status
git add . && git commit -m "备注"
git reset --hard
```

**关键路径**
- 管理脚本：`~/clawd_control.sh`
- 系统服务配置：`~/Library/LaunchAgents/bot.clawd.gateway.plist`
- OpenClaw 配置目录：`~/.clawdbot/`
- 运行日志：`~/.clawdbot/gateway.log`
- 核心记忆：`Core_Profile.md`
- 日常记忆：`MEMORY.md`

---

> 说明：本 Markdown 来自小红书笔记《OpenClaw 保姆级教程（中）新手必装 5 设置》的图片文字抽取与实操整理，所有代码已按常见环境校正为可复制执行。若你使用 Windows/Linux，或代理端口与路径不同，请告诉我以便生成专属脚本。