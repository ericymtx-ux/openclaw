# OpenClaw 必备终端命令速查

> 从《OpenClaw必备终端命令手册》精简提取的命令清单，复制即用。

## 命令快速清单

- `openclaw onboard --install-daemon`
- `openclaw gateway restart`
- `openclaw gateway status`
- `openclaw gateway --force`
- `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway`
- `openclaw gateway logs -f`
- `openclaw gateway logs --lines 50`
- `openclaw doctor`
- `openclaw status`
- `openclaw skills list`
- `openclaw skills install`
- `openclaw config get`
- `openclaw configure`
- `openclaw cron list`

---

## 分类与用途简述

### 安装与初始化
- `openclaw onboard --install-daemon`：注册守护进程，启用开机自启与崩溃自动重启。

### Gateway 服务管理
- `openclaw gateway restart`：配置变更后重载服务。
- `openclaw gateway status`：查看服务运行状态。
- `openclaw gateway --force`：清理端口冲突并启动。
- `launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway`：macOS 底层 Kill & Restart。

### 日志监控与诊断
- `openclaw gateway logs -f`：实时追踪日志（Follow 模式）。
- `openclaw gateway logs --lines 50`：查看最近 50 行日志。
- `openclaw doctor`：系统体检并给出建议。
- `openclaw status`：查看频道在线状态。

### 技能与配置管理
- `openclaw skills list`：列出已安装技能及版本。
- `openclaw skills install`：安装新技能。
- `openclaw config get`：查看当前生效配置。
- `openclaw configure`：交互式快速重新配置。
- `openclaw cron list`：查看已注册定时任务。
