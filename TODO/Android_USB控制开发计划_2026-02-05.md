# Android USB 控制开发计划

**创建日期**: 2026-02-05
**优先级**: P1
**预估时间**: 8 小时

---

## 目标

通过 USB 调试控制真机 Android，补充模拟器无法覆盖的场景。

---

## 开发计划

### Phase 1: 环境准备 (2h)

- [x] Android 手机开启 USB 调试 **（需用户操作）**
- [x] Mac mini 安装 scrcpy + uiautomator2
- [x] 验证 ADB 连接
- [ ] 测试基础投屏（需连接手机）

### Phase 2: MCP Server 开发 (4h)

- [x] 创建 `projects/android-phone-mcp/`
- [x] 实现设备连接/断开
- [x] 实现点击/滑动操作
- [x] 实现截图/录屏
- [x] 实现文本输入
- [x] 测试验证通过

### Phase 3: OpenClaw 集成 (2h)

- [ ] 添加 `/android-phone` 命令
- [ ] 集成到 morning_brief (可选)
- [ ] 编写使用文档

---

## 技术栈

- scrcpy (投屏)
- uiautomator2 (自动化)
- Python + MCP SDK
- OpenClaw Agent

---

## 预期输出

1. `projects/android-phone-mcp/` - MCP server
2. `agents/android_phone/` - Agent 模块
3. `TODO/Android_USB_开发报告_*.md` - 开发记录

---

*Plan created: 2026-02-05*
