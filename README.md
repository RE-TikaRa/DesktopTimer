# DesktopTimer# DesktopTimer



一个功能丰富的桌面计时器应用，支持正计时/倒计时、时钟模式、系统托盘、音效提醒、多语言与外观自定义。一个功能丰富的桌面计时器应用，支持正计时/倒计时、时钟模式、系统托盘、音效提醒、多语言与外观自定义。



<!-- PROJECT SHIELDS --><!-- PROJECT SHIELDS -->



[![Contributors][contributors-shield]][contributors-url][![Contributors][contributors-shield]][contributors-url]

[![Forks][forks-shield]][forks-url][![Forks][forks-shield]][forks-url]

[![Stargazers][stars-shield]][stars-url][![Stargazers][stars-shield]][stars-url]

[![Issues][issues-shield]][issues-url][![Issues][issues-shield]][issues-url]

[![License][license-shield]][license-url][![License][license-shield]][license-url]

[![Stargazers][stars-shield]][stars-url]

<!-- PROJECT LOGO -->[![Issues][issues-shield]][issues-url]

<br />[![License][license-shield]][license-url]



<p align="center"><!-- PROJECT LOGO -->

  <a href="https://github.com/RE-TikaRa/DesktopTimer"><br />

    <img src="img/timer_icon.ico" alt="Logo" width="80" height="80">

  </a><p align="center">

  <a href="https://github.com/RE-TikaRa/DesktopTimer">

  <h3 align="center">DesktopTimer 桌面计时器</h3>    <img src="img/ALP_STUDIO-logo-full.svg" alt="Logo" width="200">

  <p align="center">  </a>

    一个简洁而强大的桌面计时器工具

    <br />  <h3 align="center">DesktopTimer | 桌面计时器</h3>

    <a href="https://github.com/RE-TikaRa/DesktopTimer"><strong>探索本项目的文档 »</strong></a>  <p align="center">

    <br />    一个基于 PyQt5 的桌面计时器，支持正计时/倒计时、系统托盘、快捷键、音效/闪烁提醒、多语言（中/英）与外观个性化。

    <br />    <br />

    <a href="https://github.com/RE-TikaRa/DesktopTimer/releases">下载最新版本</a>    <a href="https://github.com/RE-TikaRa/DesktopTimer"><strong>查看源码 »</strong></a>

    ·    <br />

    <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">报告Bug</a>    <br />

    ·    <a href="#上手指南">快速开始</a>

    <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">提出新特性</a>    ·

  </p>    <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">报告问题</a>

</p>    ·

    <a href="https://github.com/RE-TikaRa/DesktopTimer/issues">提出新特性</a>

本篇README.md面向开发者和用户  </p>

 

## 目录</p>



- [关于项目](#关于项目)

  - [主要功能](#主要功能)

  - [运行截图](#运行截图)

- [上手指南](#上手指南)## 目录

  - [开发前的配置要求](#开发前的配置要求)

  - [安装步骤](#安装步骤)- [关于项目](#关于项目)

- [文件目录说明](#文件目录说明)  - [主要功能](#主要功能)

- [使用说明](#使用说明)  - [运行截图](#运行截图)

  - [快捷键](#快捷键)- [上手指南](#上手指南)

- [开发的架构](#开发的架构)  - [安装步骤](#安装步骤)

- [打包与部署](#打包与部署)- [文件目录说明](#文件目录说明)

- [使用到的框架](#使用到的框架)- [使用说明](#使用说明)

- [版本更新日志](#版本更新日志)  - [快捷键](#快捷键)

- [开发路线图](#开发路线图)- [开发架构](#开发架构)

  - [已完成功能](#已完成功能)- [打包与部署](#打包与部署)

  - [计划中的功能](#计划中的功能)- [使用到的技术栈](#使用到的技术栈)

- [贡献者](#贡献者)- [版本更新日志](#版本更新日志)

  # DesktopTimer

  一个功能丰富的桌面计时器应用，支持正计时/倒计时、时钟模式、系统托盘、音效提醒、多语言与外观自定义。

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



  ## 目录

  - [关于项目](#关于项目)
    - [主要功能](#主要功能)
    - [运行截图](#运行截图)
  - [上手指南](#上手指南)
    - [开发前的配置要求](#开发前的配置要求)
    - [安装步骤](#安装步骤)
  - [文件目录说明](#文件目录说明)
  - [使用说明](#使用说明)
    - [快捷键](#快捷键)
  - [开发架构](#开发架构)
  - [打包与部署](#打包与部署)
  - [使用到的技术栈](#使用到的技术栈)
  - [升级指南（内嵌）](#升级指南内嵌)
  - [版本更新日志](#版本更新日志)
  - [开发路线图](#开发路线图)
    - [已完成功能](#已完成功能)
    - [计划中的功能](#计划中的功能)
  - [贡献指南](#贡献指南)
    - [如何参与开源项目](#如何参与开源项目)
  - [版本控制](#版本控制)
  - [作者](#作者)
  - [版权说明](#版权说明)
  - [鸣谢](#鸣谢)

  ## 关于项目

  DesktopTimer 是一个基于 PyQt5 开发的桌面计时器应用程序，提供简洁直观的用户界面和丰富的自定义选项，适合番茄工作法、时间管理、日常计时等多种场景。

  ### 主要功能

  - ⏰ 三种计时模式：正计时、倒计时、时钟模式（12/24 小时制、秒/日期可选）
  - 🔔 多种提醒方式：自定义音效、系统 Beep、窗口闪烁、托盘气泡、Windows 通知
  - 🌍 多语言支持：中文与英文界面切换
  - 🎨 外观自定义：字体/字号、颜色、圆角、透明度、夜读模式、窗口尺寸
  - 📍 系统托盘：暂停/继续、重置、快捷预设、显示/隐藏、锁定/解锁、打开设置、退出
  - 🔒 窗口锁定：位置固定，点击穿透到底层应用
  - ⌨️ 快捷键：提供常用快捷键操作

  ### 运行截图

  ![DesktopTimer 运行截图](https://s2.loli.net/2025/10/08/XRWK3MHlhUBTZx2.png)

  ## 上手指南

  ### 开发前的配置要求

  1. Python 3.13 或更高版本
  2. Windows 10/11
  3. 建议使用虚拟环境

  ### 安装步骤

  【方式一】安装程序（推荐）
  1. 前往 Releases 页面下载 `DesktopTimer-Setup.exe`
  2. 双击安装，按提示完成
  3. 从开始菜单或桌面快捷方式启动

  【方式二】便携版
  1. 下载 `DesktopTimer.zip`
  2. 解压到任意目录
  3. 直接运行 `DesktopTimer.exe`

  【方式三】从源码运行（开发者）
  ```pwsh
  git clone https://github.com/RE-TikaRa/DesktopTimer.git
  cd DesktopTimer
  pip install -r requirements.txt
  python desktop_timer.py
  ```

  【方式四】自行编译可执行文件
  ```pwsh
  python -m PyInstaller DesktopTimer.spec --noconfirm
  ```
  编译完成后，`dist\DesktopTimer.exe` 可执行；将 `img\`、`lang\`、`sounds\` 一并放入 `dist\` 目录。

  ## 文件目录说明

  ```
  DesktopTimer/
  ├── desktop_timer.py           # 主程序文件（UI/托盘/计时/提醒/设置）
  ├── DesktopTimer.spec          # PyInstaller 打包配置
  ├── requirements.txt           # Python 依赖列表
  ├── README.md                  # 项目说明文档（本文件）
  ├── README-object.md           # README 模板参考
  ├── /img/                      # 图标资源目录
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

  ## 使用说明

  1) 设置倒计时：输入小时/分钟/秒
  2) 开始计时：点击“开始”或 `Ctrl+Space`
  3) 暂停/恢复：点击“暂停”或 `Ctrl+Space`
  4) 停止计时：点击“停止”或 `Ctrl+R`
  5) 窗口锁定：点击锁图标、`Ctrl+L`，或托盘/右键菜单
  6) 切换模式：设置中选择正计时/倒计时/时钟
  7) 自定义：外观、透明度、语言、提醒音等；设置自动保存在 `settings/timer_settings.json`

  ### 快捷键

  - `Ctrl+Space`：暂停/继续
  - `Ctrl+R`：重置
  - `Ctrl+H`：显示/隐藏窗口
  - `Ctrl+L`：锁定/解锁窗口
  - `Ctrl+,`：打开设置

  ## 开发架构

  - L18n：多语言加载（lang/*.json）
  - SettingsDialog：设置对话框（外观/模式/预设/通用/关于）
  - TimerWindow：主窗口/计时/托盘/提醒/快捷键
  - 路径管理：自动识别开发/打包环境，动态定位资源
  - 配置管理：JSON 持久化，包含版本兼容处理

  要点：`sys.frozen` 检测打包环境；相对路径存储确保可移植；`QTimer`/`QMediaPlayer`/`QSystemTrayIcon` 组合；自动从 v1.0.0 设置迁移到 v1.0.1。

  ## 打包与部署

  使用 `DesktopTimer.spec`：
  ```pwsh
  python -m PyInstaller DesktopTimer.spec --noconfirm
  ```
  说明：onefile 单文件模式；输出 `dist\DesktopTimer.exe`；将 `img/`、`lang/`、`sounds/` 放入 `dist/`；图标 `img/timer_icon.ico`。

  可用 Inno Setup 生成安装程序（参考本地 `setup/SetUp.iss`）。

  ## 使用到的技术栈

  - PyQt5 - GUI 框架
  - PyInstaller - 打包工具
  - win10toast - Windows 通知（可选）
  - Inno Setup - 安装程序制作

  ## 升级指南（内嵌）

  以下为 v1.0.0 → v1.0.1 的升级说明（已合并自原 UPGRADE_GUIDE.md）：

  ### 🔄 自动兼容处理
  首次运行 v1.0.1 时，程序会自动处理旧版本设置文件，无需手动操作。

  ### ✨ 兼容性功能

  1) 声音文件路径自动转换
  - 旧版（绝对路径）：
    ```json
    "sound_file": "C:/Program Files/DesktopTimer/sounds/Alarm01.wav"
    ```
  - 新版（自动相对路径）：
    ```json
    "sound_file": "sounds/Alarm01.wav"
    ```
  - 逻辑：检测到绝对路径且位于 `sounds/` 内，则转换为相对路径并保存，提高可移植性。

  2) 新配置项自动添加（时钟模式）
  ```json
  "clock_format_24h": true,
  "clock_show_seconds": true,
  "clock_show_date": true
  ```

  3) 用户设置完全保留
  字体/字号、颜色、透明度、预设、语言、铃声、圆角等全部保留。

  ### 📦 安装方式

  方式 1：直接安装（推荐）
  1. 运行 `DesktopTimer-Setup.exe`
  2. 自动检测旧版本并覆盖升级
  3. 首次运行自动转换设置

  方式 2：手动覆盖
  1. 关闭 v1.0.0
  2. 可选备份 `C:\Program Files\DesktopTimer\settings\`
  3. 解压新版本到旧目录，覆盖 `DesktopTimer.exe` 与 `lang/`、`img/`
  4. 保留 `settings/` 以及自定义 `sounds/`

  ### 🛡️ 数据保护

  - settings 文件夹：卸载不删除
  - 自定义铃声：不会被覆盖
  - 用户配置：升级过程完整保留

  ### ⚠️ 注意事项

  - 转换失败可能因不在程序目录 `sounds/` 或跨盘符；此时保留绝对路径仍可用，建议将外部铃声复制到 `sounds/`。
  - 首次运行看到控制台输出“[兼容] 已将声音文件路径从绝对路径转换为相对路径”属正常。

  ### 🔧 故障排除

  - 升级后铃声不响：在设置中检查铃声并点击“测试铃声”；若找不到文件，请重新选择或复制到 `sounds/`。
  - 升级后设置丢失：检查 `settings/timer_settings.json` 是否存在；必要时删除让程序重新生成，或恢复备份。
  - 语言变英文：设置 → 常规 → 语言选择“简体中文”。

  ### 📝 版本对比

  | 功能 | v1.0.0 | v1.0.1 |
  |------|--------|--------|
  | 路径处理 | 绝对路径 | 相对路径（自动转换） |
  | 窗口锁定 | ✅ | ✅（修复翻译） |
  | 时钟模式 | ✅ | ✅ |
  | 编译方式 | onedir | onefile |
  | 便携性 | ❌ | ✅ |

  ### 🎯 推荐操作
  升级后建议：首次运行确认设置加载、测试铃声、倒计时与锁定功能（Ctrl+L）；如无问题，可删除旧版本备份。

  如遇问题请到 Issues 提交反馈：
  https://github.com/RE-TikaRa/DesktopTimer/issues

  ## 版本更新日志

  ### v1.0.1 (2025-01-09)
  - 新增时钟模式（12/24 小时制、显示秒/日期）
  - 新增窗口锁定（位置固定+点击穿透）
  - 路径处理改为相对路径；修复打包后资源路径问题
  - 自动兼容 v1.0.0 设置；onefile 打包 + 外部资源
  - 安装程序保护用户设置与自定义音效

  ### v1.0.0 (2025-01-08)
  - 首次发布：正/倒计时、音效提醒、中英文、窗口外观、系统托盘

  ## 开发路线图

  ### 已完成功能
  - 正/倒计时/时钟
  - 窗口锁定
  - 托盘与快捷操作
  - 多种提醒（音效/闪烁/通知）
  - 中英文双语
  - 外观自定义
  - 快捷键
  - 番茄钟预设

  ### 计划中的功能
  - 自定义快捷键映射
  - 提醒音量/循环/渐入渐出、播放列表
  - Windows 通知按钮（“再来 5 分钟”等）
  - 暗/亮主题托盘图标与自定义图标包
  - 设置导入/导出与一键恢复默认
  - 自动更新（Releases 检查）
  - 开机自启动（可选）
  - 多语言扩展
  - CI/自动化测试
  - 便携模式完善

  ## 贡献指南

  欢迎通过 Issues 或 Pull Requests 参与贡献！

  ### 如何参与开源项目
  1. Fork 本仓库
  2. 新建分支：`git checkout -b feature/your-feature`
  3. 提交改动：`git commit -m "feat: your message"`
  4. 推送分支：`git push origin feature/your-feature`
  5. 发起 Pull Request

  ## 版本控制

  项目使用 Git 管理版本；发布版本在 Releases/Tags 标注。

  ## 作者

  **TikaRa**
  - 邮箱：163mail@re-TikaRa.fun
  - 个人网站：https://re-tikara.fun
  - GitHub：https://github.com/RE-TikaRa/DesktopTimer
  - B 站主页：https://space.bilibili.com/374412219

  ## 版权说明

  本项目采用「非商用许可」：DesktopTimer Non-Commercial License 1.0（DNCL-1.0）。
  - 允许：个人或非商用场景下免费使用、复制、修改与再分发（需保留版权和许可声明，并署名）
  - 禁止：任何形式的商用使用（含出售、付费分发、内含付费功能的再打包等）除非获得作者书面授权
  - 商用授权：如需商用，请联系作者获取授权：163mail@re-TikaRa.fun

  完整条款参见仓库中的 LICENSE 文件。

  ## 鸣谢

  - [PyQt5](https://pypi.org/project/PyQt5/) – GUI 框架
  - [PyInstaller](https://pyinstaller.org/) – 打包工具
  - [Qt](https://www.qt.io/) – 跨平台 GUI 框架
  - [Inno Setup](https://jrsoftware.org/isinfo.php) – 安装程序制作
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
使用 Inno Setup 可创建 Windows 安装程序，配置文件参考 `setup/SetUp.iss`。## 使用到的技术栈



## 使用到的框架- [PyQt5](https://pypi.org/project/PyQt5/) - 强大的跨平台 GUI 框架

- [PyInstaller](https://pyinstaller.org/) - Python 应用打包工具

- [PyQt5](https://pypi.org/project/PyQt5/) - 强大的跨平台 GUI 框架- [win10toast](https://pypi.org/project/win10toast/) - Windows 通知支持（可选）

- [PyInstaller](https://pyinstaller.org/) - Python 应用打包工具- [Inno Setup](https://jrsoftware.org/isinfo.php) - Windows 安装程序制作

- [win10toast](https://pypi.org/project/win10toast/) - Windows 通知支持（可选）

- [Inno Setup](https://jrsoftware.org/isinfo.php) - Windows 安装程序制作## 版本更新日志



## 版本更新日志### v1.0.1 (2025-01-09)

- ✨ 新增时钟模式，支持 12/24 小时制、显示秒数、显示日期

### v1.0.1 (2025-01-09)- ✨ 新增窗口锁定功能，支持点击穿透和多种解锁方式

- ✨ 新增时钟模式，支持 12/24 小时制、显示秒数、显示日期- 🔧 优化路径处理机制，改为相对路径存储

- ✨ 新增窗口锁定功能，支持点击穿透和多种解锁方式- 🔧 修复打包后资源文件路径错误问题

- 🔧 优化路径处理机制，改为相对路径存储- 🔄 添加 v1.0.0 配置自动兼容转换

- 🔧 修复打包后资源文件路径错误问题- 📦 编译模式改为单文件 + 外部资源

- 🔄 添加 v1.0.0 配置自动兼容转换- 🛡️ 安装程序保护用户自定义音效和设置

- 📦 编译模式改为单文件 + 外部资源- 📝 添加详细的升级指南文档（UPGRADE_GUIDE.md）

- 🛡️ 安装程序保护用户自定义音效和设置

- 📝 添加详细的升级指南文档（UPGRADE_GUIDE.md）### v1.0.0 (2025-01-08)

- 🎉 首次发布

### v1.0.0 (2025-01-08)- ⏰ 基础倒计时功能

- 🎉 首次发布- ⏱️ 正计时模式

- ⏰ 基础倒计时功能- 🔔 多种提醒音选择

- ⏱️ 正计时模式- 🌍 中英文双语支持

- 🔔 多种提醒音选择- 🎨 窗口透明度和置顶功能

- 🌍 中英文双语支持- 📍 系统托盘支持

- 🎨 窗口透明度和置顶功能

- 📍 系统托盘支持## 开发路线图



## 开发路线图### ✅ 已完成功能



### ✅ 已完成功能- 正计时/倒计时/时钟三种模式

- 窗口锁定功能（位置固定+点击穿透）

- 正计时/倒计时/时钟三种模式- 系统托盘常驻与快捷操作

- 窗口锁定功能（位置固定+点击穿透）- 多种提醒方式（音效/闪烁/通知）

- 系统托盘常驻与快捷操作- 中英文双语支持

- 多种提醒方式（音效/闪烁/通知）- 外观完全自定义

- 中英文双语支持- 快捷键支持

- 外观完全自定义- 番茄钟快捷预设

- 快捷键支持

- 番茄钟快捷预设### 📋 计划中的功能



### 📋 计划中的功能- 自定义快捷键映射：开始/暂停、重置、显示/隐藏、打开设置等按键可自定义

- 结束提醒增强：

- 自定义快捷键映射：开始/暂停、重置、显示/隐藏、打开设置等按键可自定义  - 提醒音量、循环次数、渐入渐出；支持播放列表/多音频轮播

- 结束提醒增强：  - Windows 原生通知按钮（例如"再来5分钟""停止"）

  - 提醒音量、循环次数、渐入渐出；支持播放列表/多音频轮播- 托盘与主题：暗/亮主题托盘图标，自定义图标包

  - Windows 原生通知按钮（例如"再来5分钟""停止"）- 设置管理：设置导出/导入备份，一键恢复默认

- 托盘与主题：暗/亮主题托盘图标，自定义图标包- 自动更新：检查 Releases 新版本并提示下载

- 设置管理：设置导出/导入备份，一键恢复默认- 开机自启动（用户可选）

- 自动更新：检查 Releases 新版本并提示下载- 多语言扩展：支持更多语言（日文、韩文等）

- 开机自启动（用户可选）- 持续集成/自动化测试：GitHub Actions 自动构建与测试

- 多语言扩展：支持更多语言（日文、韩文等）- 便携模式完善：将设置完全放在程序目录（可选开关）

- 持续集成/自动化测试：GitHub Actions 自动构建与测试

- 便携模式完善：将设置完全放在程序目录（可选开关）## 贡献指南



## 贡献者欢迎提交 Issues 和 Pull Requests 一起完善这个项目！



请阅读 **CONTRIBUTING.md** 查阅为该项目做出贡献的开发者。## ToDo List



*您也可以在贡献者名单中参看所有参与该项目的开发者。*- 新增“时钟模式”（Clock）：显示当前系统时间

  - 12/24 小时制切换、是否显示秒、可选日期/星期、时间格式自定义

### 如何参与开源项目  - 设置页“计时模式”中加入“时钟模式”选项，托盘菜单提供快速切换入口

- 自定义快捷键映射：开始/暂停、重置、显示/隐藏、打开设置等按键可自定义

贡献使开源社区成为一个学习、激励和创造的绝佳场所。你所作的任何贡献都是**非常感谢**的。- 置顶窗口与位置锁定：支持置顶开关与防误拖动（锁定位置）

- 结束提醒增强：

1. Fork 本仓库  - 提醒音量、循环次数、渐入渐出；支持播放列表/多音频轮播

2. 新建分支：`git checkout -b feature/AmazingFeature`  - Windows 原生通知按钮（例如“再来5分钟”“停止”）

3. 提交改动：`git commit -m 'Add some AmazingFeature'`- 托盘与主题：暗/亮主题托盘图标，自定义图标包

4. 推送分支：`git push origin feature/AmazingFeature`- 设置管理：设置导出/导入备份，一键恢复默认

5. 发起 Pull Request- 自动更新：检查 Releases 新版本并提示下载

- 开机自启动（用户可选）

## 版本控制- 便携模式完善：将设置完全放在程序目录（可选开关）



该项目使用 Git 进行版本管理。您可以在 repository 参看当前可用版本。

### 如何参与开源项目

## 作者

1. Fork 本仓库

**TikaRa**2. 新建分支：`git checkout -b feature/your-feature`

3. 提交改动：`git commit -m "feat: your message"`

- 邮箱：163mail@re-TikaRa.fun4. 推送分支：`git push origin feature/your-feature`

- 个人网站：https://re-tikara.fun5. 发起 Pull Request

- GitHub：[@RE-TikaRa](https://github.com/RE-TikaRa)

- B 站主页：https://space.bilibili.com/374412219

## 版本控制

*您也可以在贡献者名单中参看所有参与该项目的开发者。*

项目使用 Git 管理版本；发布版本会在仓库的 Releases/Tags 中标注。

## 版权说明

## 作者

本项目采用「非商用许可」：**DesktopTimer Non-Commercial License 1.0（DNCL-1.0）**。

- 作者：TikaRa  

- **允许**：个人或非商用场景下免费使用、复制、修改与再分发（需保留版权和许可声明，并进行署名）- 邮箱：163mail@re-TikaRa.fun  

- **禁止**：任何形式的商用使用（含出售、付费分发、内含付费功能的再打包等）除非获得作者书面授权- 个人网站：https://re-tikara.fun  

- **商用授权**：如需商用，请联系作者获取授权：163mail@re-TikaRa.fun- GitHub：https://github.com/RE-TikaRa/DesktopTimer  

- B 站主页：https://space.bilibili.com/374412219

完整条款请见仓库中的 [LICENSE](https://github.com/RE-TikaRa/DesktopTimer/blob/main/LICENSE) 文件。

## 版权说明

## 鸣谢

本项目采用「非商用许可」：DesktopTimer Non-Commercial License 1.0（DNCL-1.0）。

- [PyQt5](https://pypi.org/project/PyQt5/) - 提供强大的 GUI 框架

- [PyInstaller](https://pyinstaller.org/) - Python 打包为可执行文件- 允许：个人或非商用场景下免费使用、复制、修改与再分发（需保留版权和许可声明，并进行署名）。

- [Qt](https://www.qt.io/) - 强大的跨平台 GUI 框架- 禁止：任何形式的商用使用（含出售、付费分发、内含付费功能的再打包等）除非获得作者书面授权。

- [Inno Setup](https://jrsoftware.org/isinfo.php) - Windows 安装程序制作工具- 商用授权：如需商用，请联系作者获取授权：163mail@re-TikaRa.fun。

- [Shields.io](https://shields.io) - 提供项目徽章

- [GitHub Pages](https://pages.github.com) - 提供项目文档托管完整条款请见仓库中的 `LICENSE` 文件。



<!-- links -->## 鸣谢

[your-project-path]:RE-TikaRa/DesktopTimer

[contributors-shield]: https://img.shields.io/github/contributors/RE-TikaRa/DesktopTimer.svg?style=flat-square- [PyInstaller](https://pyinstaller.org/) – Python 打包为可执行文件

[contributors-url]: https://github.com/RE-TikaRa/DesktopTimer/graphs/contributors- [Qt](https://www.qt.io/) – 强大的跨平台 GUI 框架

[forks-shield]: https://img.shields.io/github/forks/RE-TikaRa/DesktopTimer.svg?style=flat-square- [Shields.io](https://shields.io) – 徽章生成

[forks-url]: https://github.com/RE-TikaRa/DesktopTimer/network/members

[stars-shield]: https://img.shields.io/github/stars/RE-TikaRa/DesktopTimer.svg?style=flat-square<!-- links -->

[stars-url]: https://github.com/RE-TikaRa/DesktopTimer/stargazers[your-project-path]:RE-TikaRa/DesktopTimer

[issues-shield]: https://img.shields.io/github/issues/RE-TikaRa/DesktopTimer.svg?style=flat-square[contributors-shield]: https://img.shields.io/github/contributors/RE-TikaRa/DesktopTimer.svg?style=flat-square

[issues-url]: https://github.com/RE-TikaRa/DesktopTimer/issues[contributors-url]: https://github.com/RE-TikaRa/DesktopTimer/graphs/contributors

[license-shield]: https://img.shields.io/github/license/RE-TikaRa/DesktopTimer.svg?style=flat-square[forks-shield]: https://img.shields.io/github/forks/RE-TikaRa/DesktopTimer.svg?style=flat-square

[license-url]: https://github.com/RE-TikaRa/DesktopTimer/blob/main/LICENSE[forks-url]: https://github.com/RE-TikaRa/DesktopTimer/network/members

[stars-shield]: https://img.shields.io/github/stars/RE-TikaRa/DesktopTimer.svg?style=flat-square
[stars-url]: https://github.com/RE-TikaRa/DesktopTimer/stargazers
[issues-shield]: https://img.shields.io/github/issues/RE-TikaRa/DesktopTimer.svg?style=flat-square
[issues-url]: https://github.com/RE-TikaRa/DesktopTimer/issues
[license-shield]: https://img.shields.io/github/license/RE-TikaRa/DesktopTimer.svg?style=flat-square
[license-url]: https://github.com/RE-TikaRa/DesktopTimer/blob/main/LICENSE
