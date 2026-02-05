# Android USB 调试控制方案

**创建日期**: 2026-02-05
**标签**: Android, USB调试, Mac mini, 自动化
**优先级**: P1
**状态**: 待验证

---

## 目标

通过 USB 数据线连接 Android 手机到 Mac mini，实现自动化控制。

---

## 技术方案

### 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| scrcpy | 开源免费、延迟低 | 仅投屏，不能交互 |
| uiautomator2 | 原生 Android 测试框架 | 需 USB 调试权限 |
| Appium | 跨平台、支持多语言 | 配置复杂 |
| OpenClaw Browser | 已有 MCP 集成 | 需验证兼容性 |

### 推荐: scrcpy + uiautomator2 组合

```
scrcpy  - 画面投屏 + 录制
uiautomator2 - 元素定位 + 操作
```

---

## 实现步骤

### Phase 1: 环境准备 (2h)

- [ ] Android 手机开启 USB 调试
- [ ] Mac mini 安装 scrcpy: `brew install scrcpy`
- [ ] 安装 uiautomator2: `pip install uiautomator2`
- [ ] 验证 USB 连接: `adb devices`

### Phase 2: 基础控制 (3h)

- [ ] 投屏显示
- [ ] 点击/滑动操作
- [ ] 截图/录屏
- [ ] 文本输入

### Phase 3: 集成 OpenClaw (3h)

- [ ] 创建 MCP server
- [ ] 集成到 android-emulator-mcp
- [ ] 添加 OpenClaw 命令: `/android-phone`

---

## 依赖检查

```bash
# 检查 ADB
adb version

# 检查 scrcpy
scrcpy --version

# 检查 uiautomator2
python3 -c "import uiautomator2; print('ok')"
```

---

## 已知项目参考

- `projects/android-emulator-automation/` - 现有模拟器自动化
- `projects/android-emulator-mcp/` - 现有 MCP server
- `skills/android-notes/` - Android 相关 skill

---

## 风险点

1. **USB 调试授权** - 每次连接需手机确认
2. **设备兼容性** - 不同厂商 USB 模式差异
3. **稳定性** - USB 线材质量影响连接

---

*来源: @ssaarrttssee (Telegram, 2026-02-05)*
