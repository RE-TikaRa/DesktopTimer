# DesktopTimer | 桌面计时器

<p align="center">
   <a href="https://github.com/RE-TikaRa/DesktopTimer/graphs/contributors">
      <img src="https://img.shields.io/github/contributors/RE-TikaRa/DesktopTimer.svg?style=flat-square" alt="Contributors" />
   </a>
   <a href="https://github.com/RE-TikaRa/DesktopTimer/network/members">
      <img src="https://img.shields.io/github/forks/RE-TikaRa/DesktopTimer.svg?style=flat-square" alt="Forks" />
   </a>
   <a href="https://github.com/RE-TikaRa/DesktopTimer/stargazers">
      <img src="https://img.shields.io/github/stars/RE-TikaRa/DesktopTimer.svg?style=flat-square" alt="Stars" />
   </a>
   <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">
      <img src="https://img.shields.io/github/issues/RE-TikaRa/DesktopTimer.svg?style=flat-square" alt="Issues" />
   </a>
   <a href="https://github.com/RE-TikaRa/DesktopTimer/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/RE-TikaRa/DesktopTimer.svg?style=flat-square" alt="License" />
   </a>
  
</p>

<p align="center">
   <img src="img/ALP_STUDIO-logo-full.svg" alt="Logo" width="510" height="300" />
</p>

<h3 align="center">DesktopTimer | 桌面计时器</h3>

<p align="center">
基于 PyQt5 的轻量级桌面计时器，支持正计时/倒计时/时钟模式，系统托盘、快捷键、音效与闪烁提醒、多语言（中/英）以及丰富的外观自定义。
</p>

<p align="center">
  <a href="https://github.com/RE-TikaRa/DesktopTimer/releases">下载最新版本</a> •
  <a href="https://github.com/RE-TikaRa/DesktopTimer">查看源码</a> •
  <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">报告 Bug</a> •
  <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">提出新特性</a>
</p>

> 本 README 同时面向“用户”和“开发者”，上来就想用的看“快速开始”，想参与开发的看“开发者指南”。

---

## 🚀 快速开始（用户）

- 支持系统：Windows 10/11（x64）
- 推荐环境：Python 3.13（仅源码运行需用到），普通用户可直接使用安装包或便携版

1) 安装程序（建议）
- 前往 [Releases](https://github.com/RE-TikaRa/DesktopTimer/releases) 下载 DesktopTimer-Setup.exe
- 双击安装，按向导完成；从开始菜单或桌面快捷方式启动

2) 便携版
- 下载 DesktopTimer.zip → 解压 → 直接运行 DesktopTimer.exe

3) 从源码运行（开发者）
- 克隆仓库并安装依赖后运行 `desktop_timer.py`（见下文“开发者指南”）

---

## ✨ 功能一览

- ⏰ 三种计时：正计时、倒计时、时钟（12/24 小时制、可选“秒/日期”）
- 🔔 提醒方式：自定义音效、系统 Beep、窗口闪烁、托盘气泡、Windows 通知
- 🌐 多语言：中文 / English 一键切换
- 🎨 外观：字体/字号、颜色、圆角、透明度、夜读模式、窗口尺寸
- 🧰 系统托盘：暂停/继续、重置、快捷预设、显示/隐藏、锁定/解锁、打开设置、退出
- 🔒 窗口锁定：固定位置并可启用“点击穿透”
- ⌨️ 快捷键：常用操作一键直达

---

## 🧭 使用说明（核心操作）

- 设置倒计时：输入小时/分钟/秒
- 开始计时：点击“开始”或使用快捷键（见下）
- 暂停/恢复：点击“暂停”，或同一快捷键切换
- 停止计时：点击“停止”
- 窗口锁定：点击锁图标、按 Ctrl+L，或通过托盘菜单
- 切换模式：在“设置”中选择“正计时/倒计时/时钟”
- 配置保存：所有设置自动保存至 `settings/timer_settings.json`

### ⌨️ 快捷键

| 快捷键 | 功能 |
| -- | -- |
| Ctrl+Space | 暂停/继续 |
| Ctrl+R | 重置 |
| Ctrl+H | 显示/隐藏窗口 |
| Ctrl+L | 锁定/解锁窗口 |
| Ctrl+, | 打开设置 |

---

## 🛠️ 开发者指南

### 开发环境要求
- Python 3.13 或更高版本
- Windows 10/11
- 建议使用虚拟环境（venv/conda）

### 源码运行
```pwsh
# 克隆与进入目录
git clone https://github.com/RE-TikaRa/DesktopTimer.git
cd DesktopTimer

# 安装依赖
pip install -r requirements.txt

# 运行
python desktop_timer.py
```

### 打包为可执行文件
```pwsh
python -m PyInstaller DesktopTimer.spec --noconfirm
```
打包完成后生成 `dist/DesktopTimer.exe`。请将 `img/`、`lang/`、`sounds/` 一并放入 `dist/` 目录。

### 文件结构
```
DesktopTimer/
├── desktop_timer.py           # 主程序（UI/托盘/计时/提醒/设置）
├── DesktopTimer.spec          # PyInstaller 打包配置
├── requirements.txt           # Python 依赖
├── README.md                  # 项目说明（本文件）
├── README-object.md           # README 模板/参考
├── /img/                      # 图标资源
│   ├── timer_icon.ico         # 应用图标
│   └── ALP_STUDIO-logo-full.svg
├── /lang/                     # 多语言文件
│   ├── zh_CN.json
│   └── en_US.json
├── /sounds/                   # 提醒音效（10 个）
├── /settings/                 # 运行时生成的用户设置
│   └── timer_settings.json
├── /build/                    # 构建临时文件
└── /dist/                     # 编译输出（exe）
```

### 架构与实现要点
- i18n：多语言加载（lang/*.json）
- SettingsDialog：设置对话框（外观/模式/预设/通用/关于）
- TimerWindow：主窗口/计时/托盘/提醒/快捷键
- 路径管理：自动识别开发/打包环境，动态定位资源
- 配置管理：JSON 持久化，包含版本兼容处理

要点：使用 `sys.frozen` 识别打包环境；相对路径存储确保可移植；`QTimer`/`QMediaPlayer`/`QSystemTrayIcon` 组合；自动从 v1.0.0 设置迁移到 v1.0.1。

---

## 📦 打包与发布

- 使用 `DesktopTimer.spec` 进行 onefile 打包，输出 `dist/DesktopTimer.exe`
- 将 `img/`、`lang/`、`sounds/` 复制到 `dist/` 下，确保资源可用
- 可使用 Inno Setup 生成安装程序（参考 `setup/SetUp.iss`）

---

## ❓ 常见问题（FAQ）

1. 打包后没有声音/语言不生效？
   - 请确认已将 `img/`、`lang/`、`sounds/` 整个目录复制到 `dist/`。

2. 托盘图标不显示/找不到？
   - 检查系统托盘的“隐藏的图标”区域；确保 Explorer 正常；程序最小化到托盘时可通过 Ctrl+H 显示/隐藏。

3. 锁定后无法操作窗口怎么办？
   - 使用快捷键 Ctrl+L 解锁，或通过系统托盘菜单解锁。

4. 源码运行报依赖错误？
   - 重新执行 `pip install -r requirements.txt`，确保网络正常；如仍失败，建议新建虚拟环境后再安装。

5. 打包后资源路径异常？
   - 本项目已兼容 `sys.frozen` 场景；若自定义了运行目录，请保持资源与可执行文件同级。

---

## 🧭 开发路线图

### ✅ 已完成功能
- 正计时/倒计时/时钟三种模式
- 系统托盘常驻与快捷操作
- 多种提醒方式（音效/闪烁/通知）
- 中英文双语支持
- 外观完全自定义
- 快捷键支持
- 番茄钟快捷预设
- 窗口锁定功能（位置固定 + 点击穿透）

### 📌 计划中的功能
- 自定义快捷键映射：开始/暂停、重置、显示/隐藏、打开设置等按键可自定义
- 结束提醒增强：音量、循环次数、渐入渐出；播放列表/多音频轮播
- Windows 原生通知按钮（如“再来 5 分钟”“停止”）
- 托盘与主题：暗/亮主题托盘图标，自定义图标包
- 设置管理：设置导出/导入备份，一键恢复默认
- 自动更新：检查 Releases 新版本并提示下载
- 开机自启动（用户可选）
- 多语言扩展：支持更多语言（日文、韩文等）
- 持续集成/自动化测试：GitHub Actions 自动构建与测试
- 便携模式完善：将设置完全放在程序目录（可选开关）

---

## 🧩 使用到的技术栈
- PyQt5 - GUI 框架
- PyInstaller - 打包工具
- win10toast - Windows 通知（可选）
- Inno Setup - 安装程序制作

---

## 🗓️ 版本更新日志

### v1.0.2 (2025-10-09)
- 版本号从 1.0.1 更新为 1.0.2（信息展示与发行准备）

### v1.0.1 (2025-01-09)
- ✨ 新增时钟模式，支持 12/24 小时制、显示秒数、显示日期
- ✨ 新增窗口锁定功能，支持点击穿透和多种解锁方式
- 优化路径处理机制，改为相对路径存储
- 添加 v1.0.0 配置自动兼容转换
- 编译模式改为单文件 + 外部资源
- 安装程序保护用户自定义音效和设置
- 添加详细的升级指南文档（UPGRADE_GUIDE.md）

### v1.0.0 (2025-01-08)
- ⏰ 基础倒计时功能
- ⏱️ 正计时模式
- 多种提醒音选择
- 中英文双语支持
- 窗口透明度和置顶功能
- 系统托盘支持

---

## 🤝 贡献指南
欢迎通过 Issues 或 Pull Requests 参与贡献！

### 如何参与开源项目
1. Fork 本仓库
2. 新建分支：`git checkout -b feature/your-feature`
3. 提交改动：`git commit -m "feat: your message"`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

---

## 🔖 版本控制
项目使用 Git 管理版本；发布版本在 Releases/Tags 标注。

---

## 👤 作者
**TikaRa**  
📧 邮箱：163mail@re-TikaRa.fun  
🌐 个人网站：https://re-tikara.fun  
🐙 GitHub：https://github.com/RE-TikaRa/DesktopTimer  
📺 B 站主页：https://space.bilibili.com/374412219

---

## 📄 版权说明
本项目采用「非商用许可」：DesktopTimer Non-Commercial License 1.0（DNCL-1.0）。

允许：个人或非商用场景下免费使用、复制、修改与再分发（需保留版权和许可声明，并进行署名）

禁止：任何形式的商用使用（含出售、付费分发、内含付费功能的再打包等）除非获得作者书面授权

商用授权：如需商用，请联系作者获取授权：163mail@re-TikaRa.fun

完整条款参见仓库中的 LICENSE 文件。

---

## 🙏 鸣谢
- PyQt5 - 提供强大的 GUI 框架
- PyInstaller - Python 打包为可执行文件
- Qt - 跨平台 GUI 框架
- Inno Setup - Windows 安装程序制作工具
- Shields.io - 项目徽章
- GitHub Pages - 文档托管

[contributors-shield]: https://img.shields.io/github/contributors/RE-TikaRa/DesktopTimer.svg?style=flat-square
[contributors-url]: https://github.com/RE-TikaRa/DesktopTimer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/RE-TikaRa/DesktopTimer.svg?style=flat-square
[forks-url]: https://github.com/RE-TikaRa/DesktopTimer/network/members
[stars-shield]: https://img.shields.io/github/stars/RE-TikaRa/DesktopTimer.svg?style=flat-square
[stars-url]: https://github.com/RE-TikaRa/DesktopTimer/stargazers
[issues-shield]: https://img.shields.io/github/issues/RE-TikaRa/DesktopTimer.svg?style=flat-square
[issues-url]: https://github.com/RE-TikaRa/DesktopTimer/issues
[license-shield]: https://img.shields.io/github/license/RE-TikaRa/DesktopTimer.svg?style=flat-square
[license-url]: https://github.com/RE-TikaRa/DesktopTimer/blob/main/LICENSE