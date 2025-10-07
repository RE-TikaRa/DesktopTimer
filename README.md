# DesktopTimer

ProjectName and Description

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
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


 本篇 README.md 面向使用者与开发者
 
## 目录

- [DesktopTimer](#desktoptimer)
  - [目录](#目录)
          - [安装步骤](#安装步骤)
    - [文件目录说明](#文件目录说明)
    - [功能概览](#功能概览)
    - [开发的架构](#开发的架构)
    - [打包与部署](#打包与部署)
    - [使用到的框架](#使用到的框架)
    - [贡献者](#贡献者)
      - [如何参与开源项目](#如何参与开源项目)
    - [版本控制](#版本控制)
    - [作者](#作者)
    - [版权说明](#版权说明)
    - [鸣谢](#鸣谢)
- [DesktopTimer](#desktoptimer-1)
  - [功能特性](#功能特性)
  - [目录结构（重要文件）](#目录结构重要文件)
  - [运行](#运行)
  - [打包（Windows）](#打包windows)
  - [设置说明（settings/timer\_settings.json）](#设置说明settingstimer_settingsjson)
  - [多语言机制（i18n）](#多语言机制i18n)
  - [托盘与菜单](#托盘与菜单)
  - [常见问题（FAQ）](#常见问题faq)
  - [开发提示](#开发提示)
  - [许可证](#许可证)

###### 安装步骤

方式 A：直接下载（推荐）

- 前往 Releases 页面下载最新版本：
  - 最新版地址：https://github.com/RE-TikaRa/DesktopTimer/releases/latest
  - 下载安装包（如有）：`DesktopTimer-Setup.exe`，双击安装
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

2) 安装依赖

```pwsh
pip install -r requirements.txt
```

3) 运行应用

```pwsh
python .\desktop_timer.py
```

初次运行会生成/更新 `settings/timer_settings.json`，并在项目目录下确保 `sounds/` 文件夹存在。

### 文件目录说明

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

### 功能概览

- 正计时与倒计时两种模式，内置番茄钟/短休/长休等快捷预设
- 系统托盘常驻：暂停/继续、重置、快速预设、显示/隐藏、打开设置、退出
- 提醒：自定义音效/系统 Beep、窗口闪烁、托盘气泡提示、可选 Windows 通知
- 外观可定制：字体/字号、文字与背景色、圆角、背景透明度、夜读模式、窗口尺寸
- 多语言：中文/英文（`lang/zh_CN.json`、`lang/en_US.json`）
- 快捷键：
  - Ctrl+Space 暂停/继续
  - Ctrl+R 重置
  - Ctrl+H 显示/隐藏窗口
  - Ctrl+, 打开设置

### 开发的架构 

- `TimerWindow`：主窗口与托盘逻辑、计时状态、提醒与快捷键
- `SettingsDialog`：设置对话框（外观/模式/预设/通用/关于）
- `L18n`：从 `lang/<code>.json` 加载文案；`TimerWindow.tr(key)` 返回当前语言文本
- 计时：`QTimer` 每秒 tick，更新 `elapsed_seconds` 与界面
- 倒计时完成：音效（`QMediaPlayer`）/闪烁/弹窗/托盘气泡/可选 Windows 通知（win10toast）
- 设置持久化：`settings/timer_settings.json`，应用时保存、启动时加载

### 打包与部署

使用项目内置的 `.spec`：已包含资源目录与图标设置。

```pwsh
python -m PyInstaller .\DesktopTimer.spec --noconfirm
```

产物位置：`dist\DesktopTimer.exe`

图标说明：
- `.spec` 内 `icon` 指向绝对路径 `img/timer_icon.ico`（已在本项目配置）
- `timer_icon.ico` 已包含 16/24/32/48/64/128/256 多尺寸位图，确保小图标清晰
- 若资源管理器仍显示旧图标，多数是图标缓存导致：可重命名 exe 或清理图标缓存后再看

### 使用到的框架

- [PyQt5](https://pypi.org/project/PyQt5/)：UI/托盘/多媒体
- [win10toast](https://pypi.org/project/win10toast/)：Windows 通知（可选）

### 贡献者

欢迎提 Issues 或 PR 一起完善！

#### 如何参与开源项目

1. Fork 本仓库
2. 新建分支：`git checkout -b feature/your-feature`
3. 提交改动：`git commit -m "feat: your message"`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request

### 版本控制

项目使用 Git 管理版本；发布版本会在仓库的 Releases/Tags 中标注。

### 作者

- 作者：TikaRa  
- 邮箱：163mail@re-TikaRa.fun  
- 个人网站：https://re-tikara.fun  
- GitHub：https://github.com/RE-TikaRa/DesktopTimer  
- B 站主页：https://space.bilibili.com/374412219

### 版权说明

本项目暂未声明许可证。若用于开源发布，建议补充 `LICENSE` 文件并在此注明。

### 鸣谢

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
# DesktopTimer

一个基于 PyQt5 的轻量级桌面计时器，支持正计时/倒计时、系统托盘、快捷键、音效提醒、闪烁提醒、多语言（中/英）与个性化外观设置。

## 功能特性

- 正计时与倒计时两种模式，内置番茄钟/短休/长休等快速预设
- 托盘常驻：暂停/继续、重置、快速预设、显示/隐藏、打开设置、退出
- 提醒方式：自定义音效（或系统 Beep）、窗口闪烁、气泡提示、可选 Windows 通知（win10toast）
- 外观可定制：字体/字号、文字与背景色、圆角、背景透明度、夜读模式、窗口尺寸
- 多语言：`lang/zh_CN.json`、`lang/en_US.json`
- 设置持久化：`settings/timer_settings.json`
- 快捷键：
  - Ctrl+Space 暂停/继续
  - Ctrl+R 重置
  - Ctrl+H 显示/隐藏窗口
  - Ctrl+, 打开设置

## 目录结构（重要文件）

- `desktop_timer.py`：主程序，包含以下核心类
  - `ClickableLabel`：关于页可点击链接
  - `L18n`：简易 i18n 访问器
  - `SettingsDialog`：设置对话框（外观/模式/预设/通用/关于）
  - `TimerWindow`：主窗口与托盘逻辑、计时逻辑、提醒与快捷键
  - `main()`：应用入口
- `lang/`：多语言资源
  - `zh_CN.json`、`en_US.json`
- `settings/timer_settings.json`：运行时保存的用户设置
- `sounds/`：提醒音频（wav/mp3/ogg/m4a/flac，兼容性见常见问题）
- `img/`：图标与 SVG 资源（程序图标 `timer_icon.ico`、关于页 logo）
- `DesktopTimer.spec`：PyInstaller 打包配置（已声明 datas：`lang/`、`sounds/`、`img/`、`settings/`）
- `requirements.txt`：运行依赖

## 运行

1) 安装依赖（建议使用虚拟环境）

```pwsh
pip install -r requirements.txt
```

2) 启动程序

```pwsh
python desktop_timer.py
```

初次运行会在 `settings/` 写入/更新 `timer_settings.json`。声音目录 `sounds/` 会被自动创建（若不存在）。

## 打包（Windows）

项目提供了 `DesktopTimer.spec`，使用 PyInstaller 一键打包：

```pwsh
pip install pyinstaller
pyinstaller .\DesktopTimer.spec
```

完成后在 `dist/` 目录生成可执行文件与资源。若你临时使用命令行打包（不使用 spec），请确保把 `lang/`、`sounds/`、`img/`、`settings/` 一并打包或复制到 `dist/`，否则多语言与资源会缺失。

可选：若你希望单文件（onefile）模式，可改用命令行参数或调整 spec；但请注意 Qt 插件与资源解包时的启动时延。

## 设置说明（settings/timer_settings.json）

- 外观：`font_family`、`font_size`、`text_color`、`bg_color`、`bg_opacity`、`rounded_corners`、`corner_radius`、`night_mode`
- 模式：`timer_mode`（“正计时”或“倒计时”/对应英文）、`countdown_hours`/`minutes`/`seconds`
- 提醒：`countdown_action`（“提示音”“闪烁”“提示音+闪烁”）、`enable_sound`、`enable_popup`、`sound_file`
- 行为：`auto_start_timer`（启动即开始计时）、`language`（`zh_CN`/`en_US`）

你也可以在应用的“设置”对话框中进行可视化修改，点击“应用/确定”会立即保存。

## 多语言机制（i18n）

- 运行时通过 `L18n` 加载 `lang/<code>.json` 内容；`TimerWindow.tr(key)` 返回当前语言的文案
- `SettingsDialog` 里多数字符串通过 `self.tr(key)` 获取
- 切换语言后会重建托盘菜单以应用新文案

若新增文案：同时在 `zh_CN.json` 与 `en_US.json` 增补相同 key；界面代码使用 `tr('your_key')`。

## 托盘与菜单

- 托盘图标会根据状态动态变化（播放/暂停/停止/信息）
- 双击托盘图标：显示/隐藏主窗口
- 右键窗口可打开快捷菜单，含暂停/继续、重置、快速预设、设置、显示/隐藏、退出

## 常见问题（FAQ）

1) 无法播放某些音频格式？
- PyQt5.QtMultimedia 在 Windows 上默认使用 WMF 后端，mp3/wav 支持较好；m4a/ogg/flac 依赖系统编解码器。
- 解决：优先使用 `wav/mp3`，或安装系统编解码支持。回退方案：启用“弹窗/闪烁”或使用系统 Beep。

2) 打包后资源缺失/界面英文？
- 请使用仓库内的 `DesktopTimer.spec` 打包，已包含 `datas`；或手动把 `lang/`、`sounds/`、`img/`、`settings/` 复制到 `dist/`。

3) Windows 通知不弹？
- 依赖 `win10toast`，且系统通知中心需开启。若仍无效，可改用弹窗提示（设置中启用“弹窗”）。

4) 程序窗口“太小/太大”？
- 在“设置-外观”里调字体大小或选择“窗口尺寸”预设；透明度/圆角也可一并调节。

## 开发提示

- 入口：`main()`；启动时加载 Qt 中文翻译（若存在），并设置默认区域为简体中文
- 逻辑节拍：`QTimer` 每秒触发，更新 `elapsed_seconds` 与界面文案
- 倒计时结束的处理：音效/闪烁/弹窗/托盘气泡/可选 Windows 通知
- 资源路径：大多使用 `os.path.dirname(__file__)` 相对项目根；音频目录使用 `os.getcwd()/sounds`（确保存在）

## 许可证

暂未声明许可证。如需开源发布，建议补充 `LICENSE` 文件并在此注明。

---

如需我补一版英文 README 或添加截图/动图演示，请告诉我。
