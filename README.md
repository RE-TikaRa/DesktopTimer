# DesktopTimer

一个基于 PyQt5 的桌面计时器应用（正计时/倒计时、托盘、音效/闪烁提醒、多语言、外观定制）。

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-## ToDo List

### ✅ 已完成功能（v1.0.1）

- **时钟模式**：显示当前系统时间
  - 支持 12/24 小时制切换
  - 可选显示秒数
  - 可选显示日期
  - 设置页"计时模式"中已加入"时钟模式"选项
- **窗口锁定功能**
  - 锁定后窗口位置固定
  - 鼠标点击穿透到下层应用，不影响使用
  - 快捷键 Ctrl+L、托盘菜单、右键菜单三种方式锁定/解锁

### 📋 计划中的功能

- 自定义快捷键映射：开始/暂停、重置、显示/隐藏、打开设置等按键可自定义
- 结束提醒增强：
  - 提醒音量、循环次数、渐入渐出；支持播放列表/多音频轮播
  - Windows 原生通知按钮（例如"再来5分钟""停止"）
- 托盘与主题：暗/亮主题托盘图标，自定义图标包
- 设置管理：设置导出/导入备份，一键恢复默认
- 自动更新：检查 Releases 新版本并提示下载
- 开机自启动（用户可选）
- 多语言扩展：支持更多语言（日文、韩文等）
- 持续集成/自动化测试：GitHub Actions 自动构建与测试
- 便携模式完善：将设置完全放在程序目录（可选开关）url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />

<p align="center">
  <a href="https://github.com/RE-TikaRa/DesktopTimer">
    <img src="img/ALP_STUDIO-logo-full.svg" alt="Logo" width="200">
  </a>

  <h3 align="center">DesktopTimer | 桌面计时器</h3>
  <p align="center">
    一个基于 PyQt5 的桌面计时器，支持正计时/倒计时、系统托盘、快捷键、音效/闪烁提醒、多语言（中/英）与外观个性化。
    <br />
    <a href="https://github.com/RE-TikaRa/DesktopTimer"><strong>查看源码 »</strong></a>
    <br />
    <br />
    <a href="#上手指南">快速开始</a>
    ·
    <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">报告问题</a>
    ·
    <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">提出新特性</a>
  </p>

</p>




## 目录

- [DesktopTimer](#desktoptimer)
    - [✅ 已完成功能（v1.0.1）](#-已完成功能v101)
    - [📋 计划中的功能](#-计划中的功能)
  - [目录](#目录)
  - [运行截图](#运行截图)
  - [安装步骤](#安装步骤)
  - [文件目录说明](#文件目录说明)
  - [功能概览](#功能概览)
  - [开发的架构](#开发的架构)
  - [打包与部署](#打包与部署)
  - [使用到的框架](#使用到的框架)
  - [贡献者](#贡献者)
  - [ToDo List](#todo-list)
    - [如何参与开源项目](#如何参与开源项目)
  - [版本控制](#版本控制)
  - [作者](#作者)
  - [版权说明](#版权说明)
  - [鸣谢](#鸣谢)

## 运行截图

![image-20251008030921868](https://s2.loli.net/2025/10/08/XRWK3MHlhUBTZx2.png)

## 安装步骤

方式 A：直接下载（推荐）

- 前往 Releases 页面下载最新版本：
  - 最新版地址：https://github.com/RE-TikaRa/DesktopTimer/releases/latest
  - 下载安装包：`DesktopTimer-Setup.exe`，双击安装
  - 或下载 ZIP 便携版：`DesktopTimer.zip`，解压后直接运行其中的 `DesktopTimer.exe`

方式 B：自行编译（本地运行/开发）

1) 克隆仓库（或下载源码）

```pwsh
git clone https://github.com/RE-TikaRa/DesktopTimer.git
cd DesktopTimer
```

2) 安装依赖

```pwsh
pip install -r requirements.txt
```

3) 运行应用（源码）

```pwsh
python .\desktop_timer.py
```

4) 打包为 exe（可选）

```pwsh
python -m PyInstaller .\DesktopTimer.spec --noconfirm
```

打包产物位于 `dist\DesktopTimer.exe`。初次运行会生成/更新 `settings/timer_settings.json`，并在项目目录下确保 `sounds/` 文件夹存在。

## 文件目录说明

```
desktop_timer.py               # 主程序入口（UI/托盘/计时/提醒/设置）
DesktopTimer.spec              # PyInstaller 打包配置（含 datas 与图标）
requirements.txt               # 运行依赖（PyQt5、win10toast 等）
README.md                      # 本文件
README-object.md               # 模板示例（供参考）
img/
  ├─ ALP_STUDIO-logo-full.svg  # README 顶部 LOGO
  └─ timer_icon.ico            # 应用与打包图标
lang/
  ├─ en_US.json                # 英文文案
  └─ zh_CN.json                # 中文文案
settings/
  └─ timer_settings.json       # 运行时保存的配置（自动生成/更新）
sounds/                        # 提醒音效目录（wav/mp3/ogg 等）
build/                         # PyInstaller 中间产物（构建后出现）
dist/                          # 打包产物（构建后出现，含 DesktopTimer.exe）
```

## 功能概览

- **三种计时模式**：
  - 正计时模式：无限累加计时
  - 倒计时模式：设定时间倒数提醒（内置番茄钟/短休/长休等快捷预设）
  - **时钟模式**：显示系统当前时间（支持24/12小时制、显示秒数、显示日期）
- **窗口锁定**：锁定后窗口位置固定，鼠标点击可穿透到下层应用，不影响正常使用
  - 三种解锁方式：快捷键 Ctrl+L、托盘菜单、主窗口右键菜单
- **系统托盘常驻**：暂停/继续、重置、快捷预设、显示/隐藏、锁定/解锁、打开设置、退出
- **提醒系统**：自定义音效/系统 Beep、窗口闪烁、托盘气泡提示、Windows 原生通知
- **外观可定制**：字体/字号、文字与背景色、圆角、背景透明度、夜读模式、窗口尺寸
- **多语言**：中文/英文（`lang/zh_CN.json`、`lang/en_US.json`）
- **快捷键**：
  - Ctrl+Space：暂停/继续
  - Ctrl+R：重置
  - Ctrl+H：显示/隐藏窗口
  - Ctrl+,：打开设置
  - **Ctrl+L：锁定/解锁窗口**

## 开发的架构

- `TimerWindow`：主窗口与托盘逻辑、计时状态、提醒与快捷键
- `SettingsDialog`：设置对话框（外观/模式/预设/通用/关于）
- `L18n`：从 `lang/<code>.json` 加载文案；`TimerWindow.tr(key)` 返回当前语言文本
- 计时：`QTimer` 每秒 tick，更新 `elapsed_seconds` 与界面
- 倒计时完成：音效（`QMediaPlayer`）/闪烁/弹窗/托盘气泡/可选 Windows 通知（win10toast）
- 设置持久化：`settings/timer_settings.json`，应用时保存、启动时加载

## 打包与部署

使用项目内置的 `.spec`：已包含资源目录与图标设置。

```pwsh
python -m PyInstaller .\DesktopTimer.spec --noconfirm
```

产物位置：`dist\DesktopTimer.exe`

图标说明：
- `.spec` 内 `icon` 指向绝对路径 `img/timer_icon.ico`（已在本项目配置）
- `timer_icon.ico` 已包含 16/24/32/48/64/128/256 多尺寸位图，确保小图标清晰
- 若资源管理器仍显示旧图标，多数是图标缓存导致：可重命名 exe 或清理图标缓存后再看

## 使用到的框架

- [PyQt5](https://pypi.org/project/PyQt5/)：UI/托盘/多媒体
- [win10toast](https://pypi.org/project/win10toast/)：Windows 通知（可选）

## 贡献者

欢迎提 Issues 或 PR 一起完善！

## ToDo List

- 新增“时钟模式”（Clock）：显示当前系统时间
  - 12/24 小时制切换、是否显示秒、可选日期/星期、时间格式自定义
  - 设置页“计时模式”中加入“时钟模式”选项，托盘菜单提供快速切换入口
- 自定义快捷键映射：开始/暂停、重置、显示/隐藏、打开设置等按键可自定义
- 置顶窗口与位置锁定：支持置顶开关与防误拖动（锁定位置）
- 结束提醒增强：
  - 提醒音量、循环次数、渐入渐出；支持播放列表/多音频轮播
  - Windows 原生通知按钮（例如“再来5分钟”“停止”）
- 托盘与主题：暗/亮主题托盘图标，自定义图标包
- 设置管理：设置导出/导入备份，一键恢复默认
- 自动更新：检查 Releases 新版本并提示下载
- 开机自启动（用户可选）
- 便携模式完善：将设置完全放在程序目录（可选开关）


### 如何参与开源项目

1. Fork 本仓库
2. 新建分支：`git checkout -b feature/your-feature`
3. 提交改动：`git commit -m "feat: your message"`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request


## 版本控制

项目使用 Git 管理版本；发布版本会在仓库的 Releases/Tags 中标注。

## 作者

- 作者：TikaRa  
- 邮箱：163mail@re-TikaRa.fun  
- 个人网站：https://re-tikara.fun  
- GitHub：https://github.com/RE-TikaRa/DesktopTimer  
- B 站主页：https://space.bilibili.com/374412219

## 版权说明

本项目采用「非商用许可」：DesktopTimer Non-Commercial License 1.0（DNCL-1.0）。

- 允许：个人或非商用场景下免费使用、复制、修改与再分发（需保留版权和许可声明，并进行署名）。
- 禁止：任何形式的商用使用（含出售、付费分发、内含付费功能的再打包等）除非获得作者书面授权。
- 商用授权：如需商用，请联系作者获取授权：163mail@re-TikaRa.fun。

完整条款请见仓库中的 `LICENSE` 文件。

## 鸣谢

- [PyInstaller](https://pyinstaller.org/) – Python 打包为可执行文件
- [Qt](https://www.qt.io/) – 强大的跨平台 GUI 框架
- [Shields.io](https://shields.io) – 徽章生成

<!-- links -->
[your-project-path]:RE-TikaRa/DesktopTimer
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
